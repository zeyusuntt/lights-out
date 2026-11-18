"""Stage 3 'Restarts', phase B (run by run.sh after `docker kill` + `docker start` of the service)."""
import json
import os

import pytest

from conftest import OUT, call, j, mock_reset, newkey, parse_ts, wait_done

SNAP = os.path.join(OUT, "restart_snapshot.json")
D = "harbour-crane.test"


@pytest.fixture(scope="module")
def snap():
    if not os.path.exists(SNAP):
        pytest.fail("phase A did not record a snapshot")
    return json.load(open(SNAP))


def test_answers_same_after_restart(snap):
    # "Every dossier answers GET /dossiers/{domain}, with and without as_of, /values and /history as before, and
    # GET /dossiers lists the same dossiers. The change feed holds the same entries with the same seq."
    t = snap["tokens"]["ada"]
    for m, p, q, want in snap["answers"]:
        assert j(call(m, p, token=t, params=q)) == want, (p, q)


def test_accounts_tokens_replays_after_restart(snap):
    # "Every account signs in with its password, and every bearer token is valid." "A replay of a completed
    # idempotent request answers as §7 requires."
    for tok in snap["tokens"].values():
        assert call("GET", "/dossiers", token=tok).status_code == 200
    for em, pw in (("ada@example.com", "correct horse"), ("rita@example.com", "rita pass 1")):
        assert call("POST", "/auth/login", body={"email": em, "password": pw}).status_code == 200
    t = snap["tokens"]["ada"]
    for m, p, k, body, resp in snap["replays"]:
        r = call(m, p, token=t, key=k, body=body)
        assert r.status_code == 200 and j(r) == resp, p


def test_clock_and_new_seq_after_restart(snap):
    # "The clock reads the time it read before the stop"; "An entry added after the restart has a larger seq
    # than every entry before it."
    t = snap["tokens"]["ada"]
    before = [a for a in snap["answers"] if a[1] == "/changes"][0][3]["changes"]
    mock_reset(0)
    assert call("POST", f"/dossiers/{D}/refresh", token=t, key=newkey()).status_code == 202
    b, _ = wait_done(t, D, timeout=60)
    assert parse_ts(b["researched_at"]) == parse_ts("2026-05-05T05:05:05+00:00")
    after = j(call("GET", "/changes", token=t, params={"limit": "200"}))["changes"]
    assert after[:len(before)] == before
    new = after[len(before):]
    assert new, "epoch 0 again should change ceo back"
    assert min(c["seq"] for c in new) > max(c["seq"] for c in before)


def test_zz_start_build_for_mid_build_kill(snap):
    # Sets up RULING R3-4: run.sh kills the container while this build runs; test_99_restart_c.py checks.
    import time
    from conftest import mock_fault
    t = snap["tokens"]["ada"]
    pre = {"dossier": j(call("GET", f"/dossiers/{D}", token=t)),
           "history": j(call("GET", f"/dossiers/{D}/history", token=t)),
           "changes": j(call("GET", "/changes", token=t, params={"limit": "200"})),
           "other": j(call("GET", "/dossiers/tarnwick-labs.test", token=t))}
    mock_reset(1)
    mock_fault("nimble", ["extract"], "delay", seconds=8)
    k = newkey()
    r = call("POST", f"/dossiers/{D}/refresh", token=t, key=k)
    assert r.status_code == 202
    time.sleep(2)
    assert j(call("GET", f"/dossiers/{D}", token=t))["state"] == "building"
    pre["key"], pre["resp"] = k, j(r)
    json.dump(pre, open(os.path.join(OUT, "midbuild_snapshot.json"), "w"))
