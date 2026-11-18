"""§3.3 reset and seed, §3.4 clock, §3.5 conventions, §4 fixture format."""
import time

import pytest

from conftest import (NOW0, PW, USERS, assert_err, call, create, fresh, get, j, login,
                      mock_fault, mock_reset, newkey, parse_ts, refresh, reset, set_clock,
                      wait_done)


def test_reset_returns_204_and_seeded_users_log_in(fresh):
    # §3.3 "-> 204 No Content"; §4 "Seeded users must be able to log in with the given password immediately."
    r = reset()
    assert r.status_code == 204
    r = call("POST", "/auth/login", body={"email": "bob@example.com", "password": PW})
    assert r.status_code == 200
    # §6 "For a user seeded by the fixture (§3.3), user_id is that user's id in the fixture."
    assert j(r)["user_id"] == "u_bob"
    assert j(r)["display_name"] == "Bob"


def test_reset_removes_other_users_tokens_dossiers_and_keys(fresh):
    # §3.3 "subsequent requests must see only that fixture: no users other than the seeded ones,
    # no dossiers and no stored idempotent responses."
    r = call("POST", "/auth/signup", body={"email": "zed@example.com", "password": PW,
                                           "display_name": "Zed"})
    assert r.status_code == 201
    ztok = j(r)["token"]
    key = newkey()
    r = create(fresh["ada"], "tarnwick-labs.test", key=key)
    assert r.status_code == 202
    wait_done(fresh["ada"], "tarnwick-labs.test")
    reset()
    assert_err(call("POST", "/auth/login", body={"email": "zed@example.com", "password": PW}),
               401, "unauthenticated")
    assert_err(call("GET", "/dossiers", token=ztok), 401, "unauthenticated")
    ada = login("ada@example.com")
    assert_err(get(ada, "tarnwick-labs.test"), 404, "not_found")
    assert j(call("GET", "/dossiers", token=ada))["dossiers"] == []
    # Same key after reset is a first use again: the normal response 202, not a replay 200.
    r = create(ada, "tarnwick-labs.test", key=key)
    assert r.status_code == 202, r.text
    wait_done(ada, "tarnwick-labs.test")


def test_old_seeded_token_invalid_after_reset(fresh):
    # §3.3 "Replace all service state with the fixture" — tokens from before the reset are state.
    old = fresh["ada"]
    reset()
    assert_err(call("GET", "/dossiers", token=old), 401, "unauthenticated")


def test_repeated_resets(fresh):
    # §3.3 "Repeated resets are supported."
    for _ in range(3):
        reset()
    assert login("ada@example.com")


def test_reset_duplicate_email_is_422_and_changes_nothing(fresh):
    # §4 "A fixture with two users sharing an email is a reset error: 422 validation_failed, changing nothing."
    r = create(fresh["ada"], "tarnwick-labs.test")
    assert r.status_code == 202
    wait_done(fresh["ada"], "tarnwick-labs.test")
    bad = [USERS[0], dict(USERS[1], email="ada@example.com")]
    r = call("POST", "/_test/reset", body={"now": NOW0, "users": bad}, timeout=10)
    assert_err(r, 422, "validation_failed")
    # unchanged: old token still valid, dossier still there, bob still logs in
    assert get(fresh["ada"], "tarnwick-labs.test").status_code == 200
    assert login("bob@example.com")


def test_reset_requires_now(fresh):
    # §4 "now is required and sets the clock"; §5 422 "A required field ... is missing"
    r = call("POST", "/_test/reset", body={"users": USERS}, timeout=10)
    assert_err(r, 422, "validation_failed")
    assert get(fresh["ada"], "x.test").status_code == 404  # token still valid: nothing changed


def test_reset_unparseable_body(fresh):
    # §5 400 malformed_request "Unparseable body"
    r = call("POST", "/_test/reset", raw=b"{not json", timeout=10)
    assert_err(r, 400, "malformed_request")


def test_reset_sets_clock_and_build_time_is_request_time(fresh):
    # §3.4 "Reset sets the clock to the fixture's now." §8 "researched_at is the time of the last
    # build that completed ready"; "A build's time is the clock's time when the request that started it was received."
    reset(now="2026-05-05T12:00:00+02:00")
    ada = login("ada@example.com")
    mock_reset(0)
    assert create(ada, "tarnwick-labs.test").status_code == 202
    # Moving the clock while the build runs must not move the build's time.
    set_clock("2026-05-06T00:00:00+00:00")
    b, _ = wait_done(ada, "tarnwick-labs.test")
    assert b["state"] == "ready"
    assert parse_ts(b["researched_at"]) == parse_ts("2026-05-05T12:00:00+02:00")


def test_clock_moves_forward_and_stands_still(fresh):
    # §3.4 "The clock stands still between calls"; "only reset and POST /_test/clock move" it.
    ada = fresh["ada"]
    assert create(ada, "tarnwick-labs.test").status_code == 202
    b1, _ = wait_done(ada, "tarnwick-labs.test")
    time.sleep(1.5)
    assert refresh(ada, "tarnwick-labs.test").status_code == 202
    b2, _ = wait_done(ada, "tarnwick-labs.test")
    assert parse_ts(b1["researched_at"]) == parse_ts(NOW0) == parse_ts(b2["researched_at"])
    r = set_clock("2026-03-01T09:30:00+00:00")
    assert r.status_code == 204
    assert refresh(ada, "tarnwick-labs.test").status_code == 202
    b3, _ = wait_done(ada, "tarnwick-labs.test")
    assert parse_ts(b3["researched_at"]) == parse_ts("2026-03-01T09:30:00+00:00")


def test_clock_same_time_accepted_earlier_rejected(fresh):
    # §3.4 "A now earlier than the clock's current time is 422 validation_failed and changes nothing."
    ada = fresh["ada"]
    assert set_clock(NOW0).status_code == 204  # equal: not earlier
    assert set_clock("2026-03-01T10:00:00+00:00").status_code == 204
    # same instant written with another offset is not earlier
    assert set_clock("2026-03-01T11:00:00+01:00").status_code == 204
    assert_err(set_clock("2026-03-01T09:59:59+00:00"), 422, "validation_failed")
    assert create(ada, "tarnwick-labs.test").status_code == 202
    b, _ = wait_done(ada, "tarnwick-labs.test")
    assert parse_ts(b["researched_at"]) == parse_ts("2026-03-01T10:00:00+00:00")


@pytest.mark.parametrize("now", ["2026-03-02T09:30:00", "2026-03-02", "tomorrow", ""])
def test_clock_requires_rfc3339_with_offset(fresh, now):
    # §3.4 "now is an RFC 3339 timestamp with an explicit offset."
    assert_err(set_clock(now), 422, "validation_failed")


def test_clock_wrong_type_and_missing(fresh):
    # §5 400 "a field of the wrong JSON type"; 422 "A required field ... is missing"
    assert_err(call("POST", "/_test/clock", body={"now": 12345}), 400, "malformed_request")
    assert_err(call("POST", "/_test/clock", body={}), 422, "validation_failed")
    assert_err(call("POST", "/_test/clock", raw=b"nope"), 400, "malformed_request")


def test_reset_during_build_does_not_leak(fresh):
    # §3.3 "A build still running when reset is called must not change the state that follows the reset."
    ada = fresh["ada"]
    mock_fault("nimble", ["search", "extract", "research"], "delay", seconds=2)
    mock_fault("tavily", ["search", "extract"], "delay", seconds=2)
    assert create(ada, "quillon-dynamics.test").status_code == 202
    time.sleep(0.5)
    reset()
    mock_reset(0)
    ada = login("ada@example.com")
    time.sleep(7)
    assert_err(get(ada, "quillon-dynamics.test"), 404, "not_found")
    assert j(call("GET", "/dossiers", token=ada))["dossiers"] == []
    # A new dossier for the same domain starts from nothing: unknown fields until its own build.
    r = create(ada, "quillon-dynamics.test")
    assert r.status_code == 202, r.text
    b, _ = wait_done(ada, "quillon-dynamics.test")
    assert b["state"] == "ready"


def test_unknown_fields_and_query_params_ignored(fresh):
    # §3.5 "Unknown fields in a request body are ignored"; "Unknown query parameters are ignored."
    r = call("POST", "/auth/signup", body={"email": "x1@example.com", "password": PW,
                                           "display_name": "X", "role": "admin", "extra": [1]})
    assert r.status_code == 201
    r = call("POST", "/_test/reset", body={"now": NOW0, "users": USERS, "junk": True}, timeout=10)
    assert r.status_code == 204
    ada = login("ada@example.com")
    r = call("GET", "/dossiers", token=ada, params={"zzz": "1", "sort": "nope"})
    assert r.status_code == 200
    r = call("GET", "/health", params={"x": "y"})
    assert r.status_code == 200


def test_reset_wrong_types_400_changes_nothing(fresh):
    # RULING R1-5 "A fixture with a wrong-typed field is 400. In every case nothing changes."
    for bad in ({"now": NOW0, "users": "nope"}, {"now": 5, "users": USERS}):
        r = call("POST", "/_test/reset", body=bad, timeout=10)
        assert_err(r, 400, "malformed_request")
    assert call("GET", "/dossiers", token=fresh["ada"]).status_code == 200


def test_post_seal_fixture_user_id_over_64_rejected(fresh):
    # POST-SEAL ADDITION (FIX 1 1 F2, missed by the seal). §3.5 "IDs are opaque strings of at most 64
    # characters"; §6 seeded user_id is the fixture id; a rejected reset changes nothing (R1-5).
    long = [dict(USERS[0], id="u" * 65)]
    r = call("POST", "/_test/reset", body={"now": NOW0, "users": long}, timeout=10)
    assert_err(r, 422, "validation_failed")
    assert call("GET", "/dossiers", token=fresh["ada"]).status_code == 200
    ok = [dict(USERS[0], id="u" * 64)]
    assert call("POST", "/_test/reset", body={"now": NOW0, "users": ok}, timeout=10).status_code == 204
    r = call("POST", "/auth/login", body={"email": "ada@example.com", "password": PW})
    assert j(r)["user_id"] == "u" * 64
