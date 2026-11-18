"""§10 export and import."""
import time

import pytest

from conftest import (SVC, SVC2, assert_err, call, create, fresh, get, j, login, mock_fault,
                      mock_log, mock_reset, newkey, parse_ts, refresh, reset, set_clock, wait_done)

D = "tarnwick-labs.test"


def export(base=SVC):
    r = call("GET", "/_test/export", base=base, timeout=10)
    assert r.status_code == 200, r.text
    return j(r)


def imp(obj=None, raw=None, base=SVC):
    return call("POST", "/_test/import", body=obj, raw=raw, base=base, timeout=10)


@pytest.fixture
def world(fresh):
    t = fresh["ada"]
    r = call("POST", "/auth/signup", body={"email": "carol@example.com", "password": "carol pass 1",
                                           "display_name": "Carol"})
    assert r.status_code == 201
    carol = j(r)
    kc = newkey()
    rc = create(t, D, key=kc)
    assert rc.status_code == 202
    wait_done(t, D)
    kr = newkey()
    rr = refresh(t, D, key=kr)
    assert rr.status_code == 202
    wait_done(t, D)
    kq = newkey()
    rq = call("POST", "/dossiers", token=carol["token"], key=kq, body={"domain": "quillon-dynamics.test"})
    assert rq.status_code == 202
    wait_done(t, "quillon-dynamics.test")
    kfail = newkey()
    assert create(t, "bad domain", key=kfail).status_code == 422
    return {"ada": t, "carol": carol, "kc": kc, "rc": j(rc), "kr": kr, "rr": j(rr), "kq": kq, "rq": j(rq),
            "kfail": kfail}


def snapshot(t):
    lst = j(call("GET", "/dossiers", token=t))
    return lst, {i["domain"]: j(get(t, i["domain"])) for i in lst["dossiers"]}


def test_export_shape(world):
    # §10 "Return 200 from export with a JSON object containing track: "dossier", format_version: 1 and state"
    e = export()
    assert e["track"] == "dossier" and e["format_version"] == 1 and isinstance(e["state"], dict)


def _check_restored(w, base, before):
    t = w["ada"]
    # §10 "Existing tokens and retries must remain valid after import"
    lst = j(call("GET", "/dossiers", token=t, base=base))
    assert lst == before[0]
    for d, full in before[1].items():
        assert j(call("GET", f"/dossiers/{d}", token=t, base=base)) == full
    # hashed-password login and carol's token
    r = call("POST", "/auth/login", body={"email": "carol@example.com", "password": "carol pass 1"}, base=base)
    assert r.status_code == 200 and j(r)["user_id"] == w["carol"]["user_id"]
    assert call("GET", "/dossiers", token=w["carol"]["token"], base=base).status_code == 200
    # §10 "all completed idempotent request bodies and original responses"
    mock_reset(0)
    r = call("POST", "/dossiers", token=t, key=w["kc"], body={"domain": D}, base=base)
    assert r.status_code == 200 and j(r) == w["rc"]
    r = call("POST", f"/dossiers/{D}/refresh", token=t, key=w["kr"], base=base)
    assert r.status_code == 200 and j(r) == w["rr"]
    r = call("POST", "/dossiers", token=w["carol"]["token"], key=w["kq"],
             body={"domain": "quillon-dynamics.test"}, base=base)
    assert r.status_code == 200 and j(r) == w["rq"]
    assert_err(call("POST", "/dossiers", token=t, key=w["kc"], body={"domain": "other.test"}, base=base),
               409, "idempotency_key_reuse")
    time.sleep(1)
    # §10 "Import makes no provider call"; replays make none either (§7)
    assert mock_log() == []
    # §10 "Failed request keys remain reusable."
    r = call("POST", "/dossiers", token=t, key=w["kfail"], body={"domain": "nullmark-systems.test"}, base=base)
    assert r.status_code == 202, r.text
    wait_done(t, "nullmark-systems.test", base=base)


def test_roundtrip_same_service(world):
    # §10 "Import takes that entire object and atomically replaces the service's state, returning 204."
    # "Preserve accounts ..., existing bearer tokens, dossiers with their ids, states, fields, citations,
    # researched_at and spent_units, all completed idempotent request bodies and original responses."
    t = world["ada"]
    before = snapshot(t)
    e = export()
    reset()
    mock_reset(0)
    r = imp(e)
    assert r.status_code == 204, r.text
    time.sleep(0.5)
    assert mock_log() == []
    # "repeating it restores the exported state without duplicating anything"
    assert imp(e).status_code == 204
    _check_restored(world, SVC, before)


def test_import_into_other_container(world):
    # §10 "No dependency on the source process, files, volume, port or network address is allowed."
    # "Import removes all previous destination data and credentials."
    t = world["ada"]
    before = snapshot(t)
    e = export()
    reset(base=SVC2)
    r = call("POST", "/auth/signup", base=SVC2, body={"email": "dest@example.com", "password": "dest pass 1",
                                                      "display_name": "Dest"})
    dest_tok = j(r)["token"]
    mock_reset(0)
    assert imp(e, base=SVC2).status_code == 204
    assert_err(call("POST", "/auth/login", base=SVC2, body={"email": "dest@example.com",
                                                            "password": "dest pass 1"}), 401, "unauthenticated")
    assert_err(call("GET", "/dossiers", token=dest_tok, base=SVC2), 401, "unauthenticated")
    _check_restored(world, SVC2, before)


def test_export_is_snapshot(world):
    # §10 "Export is an atomic, read-only snapshot; subsequent source writes do not change it."
    import copy, json
    e = export()
    frozen = json.dumps(e, sort_keys=True)
    t = world["ada"]
    assert create(t, "ferncliff-foods.test").status_code == 202
    wait_done(t, "ferncliff-foods.test")
    assert json.dumps(e, sort_keys=True) == frozen
    reset()
    assert imp(e).status_code == 204
    assert_err(get(t, "ferncliff-foods.test"), 404, "not_found")
    assert get(t, D).status_code == 200


@pytest.mark.parametrize("mut", ["no_state", "no_track", "bad_track", "bad_version", "no_version",
                                 "state_garbage"])
def test_invalid_import_is_422_and_changes_nothing(world, mut):
    # §10 "missing fields, wrong track/version or an invalid state give 422 validation_failed without
    # changing the destination."
    e = export()
    t = world["ada"]
    before = snapshot(t)
    bad = dict(e)
    if mut == "no_state":
        bad.pop("state")
    elif mut == "no_track":
        bad.pop("track")
    elif mut == "bad_track":
        bad["track"] = "pocket"
    elif mut == "bad_version":
        bad["format_version"] = 2
    elif mut == "no_version":
        bad.pop("format_version")
    elif mut == "state_garbage":
        bad["state"] = {"nonsense": [1, 2, 3]}
    assert_err(imp(bad), 422, "validation_failed")
    assert snapshot(t) == before


def test_import_unparseable_400(world):
    # §10 "Invalid JSON follows §5" -> 400 malformed_request
    t = world["ada"]
    before = snapshot(t)
    assert_err(imp(raw=b"{oops"), 400, "malformed_request")
    assert snapshot(t) == before


def test_reset_clears_imported_state(world):
    # §10 "Reset clears all state, including imported state."
    e = export()
    reset()
    assert imp(e).status_code == 204
    reset()
    assert_err(call("GET", "/dossiers", token=world["ada"]), 401, "unauthenticated")
    assert_err(call("GET", "/dossiers", token=world["carol"]["token"]), 401, "unauthenticated")
    t = login("ada@example.com")
    assert j(call("GET", "/dossiers", token=t))["dossiers"] == []


def test_export_import_do_not_change_clock(world):
    # §10 "Export and import do not change the clock."
    e = export()
    set_clock("2026-04-01T00:00:00+00:00")
    assert imp(e).status_code == 204
    t = world["ada"]
    assert refresh(t, D).status_code == 202
    b, _ = wait_done(t, D)
    assert parse_ts(b["researched_at"]) == parse_ts("2026-04-01T00:00:00+00:00")


def test_export_during_build(fresh):
    # §10 "An export taken while a build is running holds the dossier as it was before that build; after
    # import, that dossier is in the state of its last completed build, or failed with every field unknown
    # when no build had completed."
    t = fresh["ada"]
    assert create(t, D).status_code == 202
    done, _ = wait_done(t, D)
    for p, m in (("nimble", ["search", "extract", "research"]), ("tavily", ["search", "extract"])):
        mock_fault(p, m, "delay", seconds=3)
    assert refresh(t, D).status_code == 202
    assert create(t, "quillon-dynamics.test").status_code == 202
    time.sleep(0.3)
    e = export()
    wait_done(t, D, timeout=30)
    wait_done(t, "quillon-dynamics.test", timeout=30)
    mock_reset(0)
    reset()
    assert imp(e).status_code == 204
    b = j(get(t, D))
    assert b["state"] == "ready" and b["fields"] == done["fields"]
    assert b["researched_at"] == done["researched_at"]
    # RULING R1-4: the snapshot carries the pre-build spent_units (0 for a first build).
    assert b["spent_units"] == done["spent_units"], (b["spent_units"], done["spent_units"])
    q = j(get(t, "quillon-dynamics.test"))
    assert q["state"] == "failed" and q["researched_at"] is None
    assert q["spent_units"] == 0, q["spent_units"]
    assert all(v["status"] == "unknown" and v["citations"] == [] for v in q["fields"].values())
    time.sleep(0.5)
    assert mock_log() == []
    # No build is running after import: a refresh starts one.
    assert refresh(t, D).status_code == 202
    b2, _ = wait_done(t, D)
    assert b2["state"] == "ready"


def test_post_seal_export_after_spending_keeps_prebuild_units(fresh):
    # POST-SEAL ADDITION (fault survivor). §10 "An export taken while a build is running holds the dossier
    # as it was before that build"; RULING R1-4: pre-build spent_units (0 for a first build).
    t = fresh["ada"]
    assert create(t, D).status_code == 202
    done, _ = wait_done(t, D)
    mock_reset(0)
    mock_fault("nimble", ["search", "extract"], "delay", seconds=4)
    mock_fault("tavily", ["search", "extract"], "delay", seconds=4)
    assert refresh(t, D).status_code == 202
    assert create(t, "quillon-dynamics.test").status_code == 202
    deadline = time.time() + 3.5
    while time.time() < deadline and not any(c["cost"] for c in mock_log() if c["method"] == "research"):
        time.sleep(0.1)
    time.sleep(0.3)
    live = j(get(t, D))["spent_units"]
    e = export()
    wait_done(t, D, timeout=30)
    wait_done(t, "quillon-dynamics.test", timeout=30)
    if live == done["spent_units"]:
        pytest.skip("no spending incurred before the export; cannot discriminate")
    mock_reset(0)
    reset()
    assert imp(e).status_code == 204
    assert j(get(t, D))["spent_units"] == done["spent_units"]
    assert j(get(t, "quillon-dynamics.test"))["spent_units"] == 0
