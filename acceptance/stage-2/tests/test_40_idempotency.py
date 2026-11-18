"""§7 idempotency on POST /dossiers and POST /dossiers/{domain}/refresh."""
import concurrent.futures as cf
import json
import time

import pytest

from conftest import (assert_err, call, create, fresh, get, j, mock_log, mock_reset, newkey,
                      refresh, wait_done)

D = "tarnwick-labs.test"


def post_d(t, key, body=None, raw=None, headers=None):
    return call("POST", "/dossiers", token=t, key=key, body=body, raw=raw, headers=headers)


def test_missing_or_empty_key(fresh):
    # §7 "Header absent or empty | 400 missing_idempotency_key"
    t = fresh["ada"]
    assert_err(post_d(t, None, {"domain": D}), 400, "missing_idempotency_key")
    assert_err(post_d(t, "", {"domain": D}), 400, "missing_idempotency_key")
    assert_err(call("POST", f"/dossiers/{D}/refresh", token=t), 400, "missing_idempotency_key")
    assert_err(call("POST", f"/dossiers/{D}/refresh", token=t, key=""), 400, "missing_idempotency_key")


def test_key_length_range(fresh):
    # §5 "Idempotency-Key | 1 to 255 characters | 422 validation_failed"
    t = fresh["ada"]
    assert_err(post_d(t, "k" * 256, {"domain": D}), 422, "validation_failed")
    assert_err(call("POST", f"/dossiers/{D}/refresh", token=t, key="k" * 256), 422, "validation_failed")
    r = post_d(t, "k" * 255, {"domain": D})
    assert r.status_code == 202, r.text
    r = post_d(t, "q", {"domain": "quillon-dynamics.test"})
    assert r.status_code == 202, r.text
    wait_done(t, D)
    wait_done(t, "quillon-dynamics.test")


def test_replay_returns_original_even_after_change_and_calls_nothing(fresh):
    # §7 "Replay: same key, same body | 200, body identical to the original response as a JSON value";
    # "A successful replay returns the original response, even after the dossier has changed. It starts
    # no build and makes no provider call."
    t = fresh["ada"]
    k = newkey()
    r1 = post_d(t, k, {"domain": D})
    assert r1.status_code == 202
    wait_done(t, D)
    time.sleep(0.5)
    n = len(mock_log())
    # same JSON value: other key order / whitespace / unknown fields
    r2 = post_d(t, k, raw=b'  {"extra": {"a": 1},   "domain" : "tarnwick-labs.test"}  ')
    assert r2.status_code == 200, r2.text
    assert j(r2) == j(r1) and j(r2)["state"] == "building"
    rk = newkey()
    rr1 = refresh(t, D, key=rk)
    assert rr1.status_code == 202
    wait_done(t, D)
    time.sleep(0.5)
    n = len(mock_log())
    before = j(get(t, D))
    rr2 = refresh(t, D, key=rk)
    assert rr2.status_code == 200 and j(rr2) == j(rr1)
    time.sleep(1.5)
    assert len(mock_log()) == n, "replay made provider calls"
    after = j(get(t, D))
    assert after["state"] == "ready" and after["spent_units"] == before["spent_units"]


def test_different_body_409_and_claimed_key_beats_validation(fresh):
    # §7 "Same key, different body | 409 idempotency_key_reuse"; "an already claimed key is resolved before
    # field validation. Thus changing a successful request to an invalid body with the same key still
    # returns 409 idempotency_key_reuse."
    t = fresh["ada"]
    k = newkey()
    assert post_d(t, k, {"domain": D}).status_code == 202
    assert_err(post_d(t, k, {"domain": "quillon-dynamics.test"}), 409, "idempotency_key_reuse")
    assert_err(post_d(t, k, {"domain": "not a domain"}), 409, "idempotency_key_reuse")
    assert_err(post_d(t, k, {}), 409, "idempotency_key_reuse")
    # §7 "Acme-Robotics.test and acme-robotics.test in a path or body are different requests for this rule"
    assert_err(post_d(t, k, {"domain": "Tarnwick-Labs.test"}), 409, "idempotency_key_reuse")
    # unauthenticated still wins (§6)
    assert_err(call("POST", "/dossiers", key=k, body={"domain": "x"}), 401, "unauthenticated")
    wait_done(t, D)


def test_key_scoped_per_user(fresh):
    # §7 "The key is scoped to the authenticated user. Two different users may use the same key string
    # with no interaction between them."
    k = newkey()
    ra = post_d(fresh["ada"], k, {"domain": D})
    assert ra.status_code == 202
    rb = post_d(fresh["bob"], k, {"domain": "quillon-dynamics.test"})
    assert rb.status_code == 202, rb.text
    # Bob with same key and Ada's body: Bob's first use is his own, so 409 for different body
    assert_err(post_d(fresh["bob"], k, {"domain": D}), 409, "idempotency_key_reuse")
    # Same body under the other user's key is not a replay of the other's: dossier exists -> 200 current
    k2 = newkey()
    assert post_d(fresh["ada"], k2, {"domain": "ferncliff-foods.test"}).status_code == 202
    rb2 = post_d(fresh["bob"], k2, {"domain": "ferncliff-foods.test"})
    assert rb2.status_code == 200
    for d in (D, "quillon-dynamics.test", "ferncliff-foods.test"):
        wait_done(fresh["ada"], d)


def test_same_key_other_path_is_not_replay(fresh):
    # §7 "The same key with the same body on a different path is a different request, not a replay,
    # and must succeed normally."
    t = fresh["ada"]
    k = newkey()
    assert post_d(t, k, {"domain": D}).status_code == 202
    wait_done(t, D)
    r = refresh(t, D, key=k)
    assert r.status_code == 202, r.text
    wait_done(t, D)
    # Path case differs: a different request (§7), so a normal response not a replay.
    r2 = refresh(t, "TARNWICK-LABS.TEST", key=k)
    assert r2.status_code == 202, r2.text
    assert j(r2)["domain"] == D
    wait_done(t, D)


def test_key_reusable_after_4xx(fresh):
    # §7 "Key reused after the original request failed with 4xx | Treated as a first use"
    t = fresh["ada"]
    k = newkey()
    assert_err(post_d(t, k, {"domain": "bad domain"}), 422, "validation_failed")
    assert post_d(t, k, {"domain": D}).status_code == 202
    k2 = newkey()
    assert_err(refresh(t, "quillon-dynamics.test", key=k2), 404, "not_found")
    assert post_d(t, newkey(), {"domain": "quillon-dynamics.test"}).status_code == 202
    wait_done(t, "quillon-dynamics.test")
    assert refresh(t, "quillon-dynamics.test", key=k2).status_code == 202
    wait_done(t, D)
    wait_done(t, "quillon-dynamics.test")


def test_refresh_body_ignored(fresh):
    # §7 "POST /dossiers/{domain}/refresh takes no body; any body sent to it is ignored and plays no part
    # in deciding a replay."
    t = fresh["ada"]
    assert post_d(t, newkey(), {"domain": D}).status_code == 202
    wait_done(t, D)
    k = newkey()
    r1 = call("POST", f"/dossiers/{D}/refresh", token=t, key=k, body={"a": 1})
    assert r1.status_code == 202, r1.text
    r2 = call("POST", f"/dossiers/{D}/refresh", token=t, key=k, body={"b": [2]})
    assert r2.status_code == 200 and j(r2) == j(r1)
    r3 = call("POST", f"/dossiers/{D}/refresh", token=t, key=k, raw=b"not json at all")
    assert r3.status_code == 200 and j(r3) == j(r1)
    wait_done(t, D)
    r4 = call("POST", f"/dossiers/{D}/refresh", token=t, key=newkey(), raw=b"{{{")
    assert r4.status_code == 202, r4.text
    wait_done(t, D)


def test_concurrent_identical_unused_key(fresh):
    # §7 "For concurrent identical requests with an unused key, exactly one returns the normal response.
    # The others return 200 with the same body. The operation takes effect only once."
    t = fresh["ada"]
    mock_reset(0)
    k = newkey()
    with cf.ThreadPoolExecutor(25) as ex:
        rs = list(ex.map(lambda _: post_d(t, k, {"domain": D}), range(25)))
    codes = sorted(r.status_code for r in rs)
    assert codes.count(202) == 1 and codes.count(200) == 24, codes
    bodies = {json.dumps(j(r), sort_keys=True) for r in rs}
    assert len(bodies) == 1, bodies
    wait_done(t, D)
    lst = j(call("GET", "/dossiers", token=t))["dossiers"]
    assert len(lst) == 1
    dom = [c for c in mock_log() if c["method"] == "search" and c["status"] == 200 and c["query"] == D]
    assert len(dom) == 1, f"{len(dom)} domain searches: more than one build started"


def test_concurrent_identical_refresh_key(fresh):
    # §7 same rule on the refresh path, applied independently.
    t = fresh["ada"]
    assert post_d(t, newkey(), {"domain": D}).status_code == 202
    wait_done(t, D)
    mock_reset(0)
    k = newkey()
    with cf.ThreadPoolExecutor(20) as ex:
        rs = list(ex.map(lambda _: refresh(t, D, key=k), range(20)))
    codes = sorted(r.status_code for r in rs)
    assert codes.count(202) == 1 and codes.count(200) == 19, codes
    assert len({json.dumps(j(r), sort_keys=True) for r in rs}) == 1
    wait_done(t, D)
    dom = [c for c in mock_log() if c["method"] == "search" and c["status"] == 200 and c["query"] == D]
    assert len(dom) == 1, len(dom)
