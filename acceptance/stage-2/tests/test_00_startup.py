"""§2 delivery, §3.1-3.2 listening and health, §3.4 clock before first reset."""
import os
import time
from datetime import datetime, timezone

import httpx

from conftest import (SVC, SVC2, call, j, mock_log, mock_reset, newkey, parse_ts, wait_done)


def _wait_health(base, started):
    deadline = started + 60
    while time.time() < deadline + 1:
        try:
            r = httpx.get(base + "/health", timeout=5)
            if r.status_code == 200:
                return r, time.time() - started
        except httpx.HTTPError:
            pass
        time.sleep(0.25)
    raise AssertionError(f"{base} not healthy within 60s of container start")


def test_health_within_60s_both_containers():
    # §3.2 "Return 200 once the service ... can serve requests, within 60 seconds of container start."
    # §2 "The image must run on its own with -e PORT=<port> and a port mapping." (svc on 8000, svc2 on 8001)
    for base, env in ((SVC, "SVC_STARTED"), (SVC2, "SVC2_STARTED")):
        started = float(os.environ.get(env, time.time()))
        r, took = _wait_health(base, started)
        assert took <= 60, took
        # §3.2 "GET /health -> 200 {"status": "ok"}"
        assert j(r) == {"status": "ok"}


def test_clock_follows_system_time_before_first_reset():
    # §3.4 "Before the first reset the clock follows the system time."
    # svc2 has never been reset at this point; a signup + build reads its clock.
    r = call("POST", "/auth/signup", base=SVC2,
             body={"email": "early@example.com", "password": "correct horse", "display_name": "E"})
    assert r.status_code == 201, r.text
    tok = j(r)["token"]
    r = call("POST", "/dossiers", token=tok, key=newkey(), body={"domain": "tarnwick-labs.test"},
             base=SVC2)
    assert r.status_code == 202, r.text
    b, _ = wait_done(tok, "tarnwick-labs.test", base=SVC2)
    assert b["state"] == "ready", b
    t = parse_ts(b["researched_at"])
    skew = abs((t - datetime.now(timezone.utc)).total_seconds())
    assert skew < 300, (b["researched_at"], skew)


def test_health_makes_no_provider_call():
    # §3.2 "/health makes no provider call."
    time.sleep(1)
    mock_reset(0)
    for _ in range(5):
        assert httpx.get(SVC + "/health", timeout=5).status_code == 200
    time.sleep(0.5)
    assert mock_log() == []


def test_clock_call_before_first_reset_freezes_clock():
    # RULING R1-1: before any reset, a valid POST /_test/clock sets the clock and it then stands still;
    # the backwards check compares with system time. §3.4 "A now earlier than the clock's current time is 422"
    r = call("POST", "/_test/clock", body={"now": "2001-01-01T00:00:00+00:00"}, base=SVC2)
    assert r.status_code == 422, r.text
    r = call("POST", "/_test/clock", body={"now": "2030-06-01T08:00:00+02:00"}, base=SVC2)
    assert r.status_code == 204, r.text
    tok = j(call("POST", "/auth/login", body={"email": "early@example.com", "password": "correct horse"},
                 base=SVC2))["token"]
    for _ in range(2):
        time.sleep(1.1)
        r = call("POST", "/dossiers/tarnwick-labs.test/refresh", token=tok, key=newkey(), base=SVC2)
        assert r.status_code == 202, r.text
        b, _ = wait_done(tok, "tarnwick-labs.test", base=SVC2)
        assert parse_ts(b["researched_at"]) == parse_ts("2030-06-01T08:00:00+02:00"), b["researched_at"]
