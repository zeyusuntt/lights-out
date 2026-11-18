"""Stage 3: two times per value, executives, history, the change feed, ?as_of= and /values."""
import concurrent.futures as cf
import json
import time

import pytest

from conftest import (FIELDS, FIELDS7, TITLES, Model, assert_err, call, check_candidates, check_citations,
                      check_shape, create, fresh, get, j, log_cost, mock_fault, mock_log, mock_reset, newkey,
                      parse_ts, refresh, reset, set_clock, wait_done)
import oracle

D = "harbour-crane.test"
T0 = "2026-03-01T09:00:00+00:00"
T1 = "2026-04-01T09:00:00+00:00"


def feed(t, since=0, limit=200):
    out = []
    while True:
        b = j(call("GET", "/changes", token=t, params={"since": str(since), "limit": str(limit)}))
        out += b["changes"]
        if not b["has_more"]:
            return out
        since = b["changes"][-1]["seq"]


def run_builds(t):
    """build 0 at T0 (epoch 0); build 1 at T1 (epoch 1); build 2 also at T1 (epoch 2, clock not moved)."""
    m = Model(D)
    spent = []
    mock_reset(0)
    assert create(t, D).status_code == 202
    b0, _ = wait_done(t, D, timeout=60)
    m.build(T0, 0)
    spent.append(b0["spent_units"])
    set_clock(T1)
    mock_reset(1)
    assert refresh(t, D).status_code == 202
    b1, _ = wait_done(t, D, timeout=60)
    m.build(T1, 1)
    spent.append(b1["spent_units"])
    mock_reset(2)
    assert refresh(t, D).status_code == 202
    b2, _ = wait_done(t, D, timeout=60)
    m.build(T1, 2)
    spent.append(b2["spent_units"])
    return m, (b0, b1, b2), spent


@pytest.fixture(scope="module")
def built():
    reset()
    mock_reset(0)
    from conftest import login
    t = login("ada@example.com")
    m, bs, spent = run_builds(t)
    return {"t": t, "m": m, "bs": bs, "spent": spent}


def _v(x):
    return json.dumps(x, sort_keys=True)


def test_fields_true_from_learned_at_and_executives(built):
    # "Each field of GET /dossiers/{domain} also carries the selected value's true_from and learned_at";
    # learned_at of a selected value is "the time of the build that made it the selected value"; of a candidate
    # "the time of the first build that gathered a candidate with the same field, value, URL and provider".
    t, m = built["t"], built["m"]
    b = j(get(t, D))
    check_shape(b, D)
    assert b["state"] == "ready"
    sel = m.current
    for f in FIELDS7:
        fld = b["fields"][f]
        assert _v(fld["value"]) == _v(sel[f][0]), (f, fld["value"], sel[f][0])
        assert fld["true_from"] == sel[f][1], (f, fld["true_from"], sel[f][1])
        made = [h for h in m.history[f]][-1][3] if m.history[f] else None
        if fld["value"] is not None:
            assert parse_ts(fld["learned_at"]) == parse_ts(made), (f, fld["learned_at"], made)
    # founded_year's candidate was first gathered by build 0 though retrieved by build 2
    fy = b["fields"]["founded_year"]["candidates"][0]
    assert parse_ts(fy["learned_at"]) == parse_ts(T0) and parse_ts(fy["retrieved_at"]) == parse_ts(T1)
    assert fy["true_from"] == "2025-07-01"   # UTC date of 2025-06-30T23:30:00-02:00
    assert b["fields"]["legal_name"]["true_from"] == "2026-02-01"  # invalid Effective -> Published date
    ex = b["fields"]["executives"]
    assert ex["value"] == [{"title": "cfo", "name": "Ana Silva"}, {"title": "cto", "name": "Ben Okafor"}]
    assert ex["status"] == "known" and ex["true_from"] == "2026-01-01"
    assert [c["title"] for c in ex["candidates"]] == ["cfo", "cto"]
    probs = check_candidates(b, D, 2, build_time=T1)
    assert not probs, probs


def test_history_matches_model(built):
    # "GET /dossiers/{domain}/history": all seven fields, oldest first; initial / change / correction.
    t, m = built["t"], built["m"]
    h = j(call("GET", f"/dossiers/{D}/history", token=t))
    assert h["domain"] == D and set(h["fields"]) == set(FIELDS7)
    for f in FIELDS7:
        got = [(e["type"], _v(e["value"]), e["true_from"], parse_ts(e["learned_at"])) for e in h["fields"][f]]
        want = [(ty, _v(v), tf, parse_ts(la)) for ty, v, tf, la in m.history[f]]
        assert got == want, (f, got, want)
        for e in h["fields"][f]:
            if e["value"] is None:
                assert e["true_from"] is None and e["citations"] == []
            else:
                assert e["citations"], (f, e)
                for c in e["citations"]:
                    assert 1 <= len(c["excerpt"]) <= 500
    # epoch 2's /about page carries no candidate (negated): a change to null, learned at that build (R3-2)
    assert [e["type"] for e in h["fields"]["hq_city"]] == ["initial", "correction", "change"]
    assert h["fields"]["hq_city"][2]["value"] is None and parse_ts(h["fields"]["hq_city"][2]["learned_at"]) == parse_ts(T1)
    assert [e["type"] for e in h["fields"]["ceo"]] == ["initial", "change"]
    assert [e["type"] for e in h["fields"]["legal_name"]] == ["change"]
    assert [e["type"] for e in h["fields"]["funding_total"]] == ["initial", "change"]
    assert h["fields"]["funding_total"][1]["value"] is None


def test_feed_matches_model(built):
    # "GET /changes": every change and correction, seq increasing, per-build order by field then executives.
    t, m = built["t"], built["m"]
    ch = [c for c in feed(t) if c["domain"] == D]
    got = [(c["field"], c["type"], _v(c["from"]), _v(c["to"]), c["true_from"], parse_ts(c["learned_at"])) for c in ch]
    want = [(f, ty, _v(a), _v(b), tf, parse_ts(la)) for f, ty, a, b, tf, la in m.feed]
    assert got == want, (got, want)
    seqs = [c["seq"] for c in ch]
    assert all(isinstance(s, int) and s > 0 for s in seqs) and seqs == sorted(set(seqs))


def test_feed_paging_and_validation(built):
    # "since defaults to 0 ... integer, 0 or more"; "limit defaults to 50, range 1 to 200"; has_more.
    t = built["t"]
    allc = feed(t)
    b = j(call("GET", "/changes", token=t))
    assert b["changes"] == allc[:50]
    one = j(call("GET", "/changes", token=t, params={"limit": "1"}))
    assert one["changes"] == allc[:1] and one["has_more"] == (len(allc) > 1)
    nxt = j(call("GET", "/changes", token=t, params={"since": str(allc[0]["seq"]), "limit": "200"}))
    assert nxt["changes"] == allc[1:] and nxt["has_more"] is False
    assert j(call("GET", "/changes", token=t, params={"since": str(allc[-1]["seq"])}))["changes"] == []
    for k, v in (("since", "-1"), ("since", "1e9"), ("since", "+1"), ("since", "x"), ("limit", "0"),
                 ("limit", "201"), ("limit", "4.0")):
        assert_err(call("GET", "/changes", token=t, params={k: v}), 422, "validation_failed")
    assert_err(call("GET", "/changes"), 401, "unauthenticated")


def test_as_of_snapshots(built):
    # "GET /dossiers/{domain}?as_of=": latest ready build with time at or before as_of; ties -> last in build
    # order (also across offsets); state ready; spent_units = total of builds at or before as_of; 404 before.
    t, bs, spent = built["t"], built["bs"], built["spent"]
    assert_err(call("GET", f"/dossiers/{D}", token=t, params={"as_of": "2026-03-01T08:59:59+00:00"}), 404, "not_found")
    for as_of, idx in (("2026-03-01T09:00:00+00:00", 0), ("2026-03-01T10:00:00+01:00", 0),
                       ("2026-03-20T00:00:00+00:00", 0), (T1, 2), ("2026-04-01T11:00:00+02:00", 2),
                       ("2027-01-01T00:00:00+00:00", 2)):
        r = call("GET", f"/dossiers/{D}", token=t, params={"as_of": as_of})
        assert r.status_code == 200, (as_of, r.text)
        b = j(r)
        want = bs[idx]
        assert b["state"] == "ready"
        assert parse_ts(b["researched_at"]) == parse_ts(want["researched_at"])
        assert b["spent_units"] == spent[idx], (as_of, b["spent_units"], spent)
        for f in FIELDS7:
            assert _v(b["fields"][f]["value"]) == _v(want["fields"][f]["value"]), (as_of, f)
            assert [(c["url"], _v(c["value"])) for c in b["fields"][f]["candidates"]] == \
                [(c["url"], _v(c["value"])) for c in want["fields"][f]["candidates"]], (as_of, f)
    # "In an as_of response these describe the selected value at that snapshot, using no later history."
    b = j(call("GET", f"/dossiers/{D}", token=t, params={"as_of": "2026-03-20T00:00:00+00:00"}))
    assert parse_ts(b["fields"]["ceo"]["learned_at"]) == parse_ts(T0) and b["fields"]["ceo"]["true_from"] == "2021-04-01"
    for bad in ("2026-03-01", "2026-03-01T09:00:00", "yesterday", ""):
        assert_err(call("GET", f"/dossiers/{D}", token=t, params={"as_of": bad}), 422, "validation_failed")
    assert_err(call("GET", "/dossiers/nobody-home.test", token=t, params={"as_of": T1}), 404, "not_found")


@pytest.mark.parametrize("true_at", ["2019-01-01", "2019-07-01", "2021-05-01", "2025-02-01", "2026-01-15",
                                     "2026-03-19", "2026-03-20", "2026-04-01", "2026-04-14", "2026-04-15",
                                     "2030-01-01"])
@pytest.mark.parametrize("as_of", ["2026-03-15T00:00:00+00:00", None])
def test_values_page_versions(built, true_at, as_of):
    # "GET /dossiers/{domain}/values?true_at=": page versions known at as_of; a later version replaces earlier
    # ones whose true_from is on or after its own and ends the latest earlier one it does not replace.
    t, m = built["t"], built["m"]
    params = {"true_at": true_at}
    if as_of:
        params["as_of"] = as_of
    r = call("GET", f"/dossiers/{D}/values", token=t, params=params)
    assert r.status_code == 200, r.text
    b = j(r)
    assert b["domain"] == D and b["true_at"] == true_at
    if as_of:
        assert parse_ts(b["as_of"]) == parse_ts(as_of)
    from datetime import datetime, timezone
    a = parse_ts(as_of) if as_of else datetime(2100, 1, 1, tzinfo=timezone.utc)
    want = m.values_at(true_at, a)
    assert set(b["fields"]) == set(FIELDS7)
    for f in FIELDS7:
        fld = b["fields"][f]
        assert _v(fld["value"]) == _v(want[f][0]), (true_at, as_of, f, fld["value"], want[f][0])
        assert fld["true_from"] == want[f][1], (true_at, as_of, f, fld["true_from"], want[f][1])
        if fld["value"] is None:
            assert fld["citations"] == []
        elif f != "executives":
            assert fld["citations"] and all(oracle.supports(c["excerpt"], f, fld["value"], D) for c in fld["citations"])


def test_values_validation(built):
    # true_at missing / not YYYY-MM-DD, as_of not RFC 3339 -> 422; unknown dossier or no ready build -> 404.
    t = built["t"]
    for p in ({}, {"true_at": "2026-3-1"}, {"true_at": "2026-02-30"}, {"true_at": "2026-03-01T00:00:00+00:00"},
              {"true_at": "2026-03-01", "as_of": "2026-03-01"}, {"true_at": "2026-03-01", "as_of": "x"}):
        assert_err(call("GET", f"/dossiers/{D}/values", token=t, params=p), 422, "validation_failed")
    assert_err(call("GET", "/dossiers/nobody-home.test/values", token=t, params={"true_at": "2026-01-01"}), 404,
               "not_found")
    assert_err(call("GET", f"/dossiers/{D}/values", token=t,
                    params={"true_at": "2026-01-01", "as_of": "2026-02-01T00:00:00+00:00"}), 404, "not_found")
    assert_err(call("GET", "/dossiers/nobody-home.test/history", token=t), 404, "not_found")


def test_stage3_export_import_round_trip(built):
    # "the history and feed of a stage-3 export survive a stage-3 import unchanged. So do its builds: after a
    # stage-3 import, ?as_of= and /values answer as they did in the exporting service."
    t = built["t"]
    probes = [("GET", f"/dossiers/{D}", None), ("GET", f"/dossiers/{D}/history", None),
              ("GET", "/changes", {"limit": "200"})]
    for a in ("2026-03-01T09:00:00+00:00", T1):
        probes.append(("GET", f"/dossiers/{D}", {"as_of": a}))
    for ta in ("2021-05-01", "2026-04-01"):
        for a in (None, "2026-03-15T00:00:00+00:00"):
            probes.append(("GET", f"/dossiers/{D}/values", dict({"true_at": ta}, **({"as_of": a} if a else {}))))
    before = [j(call(m_, p, token=t, params=q)) for m_, p, q in probes]
    e = j(call("GET", "/_test/export", timeout=10))
    reset()
    # Amendment (code seen): reset moves the clock to the fixture's now, and /values defaults as_of to the
    # clock; put the clock back where the exporter's was (export/import do not change it).
    set_clock(T1)
    assert call("POST", "/_test/import", body=e, timeout=10).status_code == 204
    after = [j(call(m_, p, token=t, params=q)) for m_, p, q in probes]
    for (m_, p, q), x, y in zip(probes, before, after):
        assert x == y, (p, q)


def test_same_value_adds_nothing_and_failed_adds_nothing(built):
    # "A build that completes with the same selected value for a field adds nothing for it"; "A failed build adds
    # nothing."
    t = built["t"]
    before = feed(t)
    hb = j(call("GET", f"/dossiers/{D}/history", token=t))
    mock_reset(2)
    assert refresh(t, D).status_code == 202
    wait_done(t, D, timeout=60)
    mock_reset(2)
    mock_fault("nimble", ["search", "extract", "research"], "error")
    mock_fault("tavily", ["search", "extract"], "error")
    assert refresh(t, D).status_code == 202
    b, _ = wait_done(t, D, timeout=60)
    assert b["state"] == "failed"
    mock_reset(2)
    assert feed(t) == before
    assert j(call("GET", f"/dossiers/{D}/history", token=t)) == hb


def test_concurrent_refreshes_add_entries_once(fresh):
    # "Concurrent refreshes of one dossier run one build (§8) and so add each entry once."
    t = fresh["ada"]
    mock_reset(0)
    create(t, D)
    wait_done(t, D, timeout=60)
    mock_reset(1)
    for p, ms in (("nimble", ["search", "extract", "research"]), ("tavily", ["search", "extract"])):
        mock_fault(p, ms, "delay", seconds=1)
    with cf.ThreadPoolExecutor(20) as ex:
        list(ex.map(lambda _: refresh(t, D), range(20)))
    wait_done(t, D, timeout=60)
    ch = [c for c in feed(t) if c["domain"] == D]
    keys = [(c["field"], _v(c["to"])) for c in ch]
    assert len(keys) == len(set(keys)) and len(ch) == 5, ch  # legal_name, hq_city, ceo, funding_total, executives


def test_reset_clears_history_and_feed(fresh):
    # §3.3 reset replaces all state: no history, no feed.
    t = fresh["ada"]
    mock_reset(0)
    create(t, D)
    wait_done(t, D, timeout=60)
    mock_reset(1)
    refresh(t, D)
    wait_done(t, D, timeout=60)
    assert feed(t)
    reset()
    from conftest import login
    t2 = login("ada@example.com")
    assert j(call("GET", "/changes", token=t2)) == {"changes": [], "has_more": False}
    assert_err(call("GET", f"/dossiers/{D}/history", token=t2), 404, "not_found")


@pytest.mark.parametrize("domain", ["halvorsen-robotics.test", "pemberton-analytics.test", "ashgrove-solar.test",
                                    "tarnwick-labs.test"])
def test_sample_epoch_change_history_and_feed(fresh, domain):
    # The model of history/feed/values on corpus companies whose pages change between epochs.
    t = fresh["ada"]
    m = Model(domain)
    mock_reset(0)
    create(t, domain)
    wait_done(t, domain, timeout=60)
    m.build(T0, 0)
    set_clock(T1)
    mock_reset(1)
    refresh(t, domain)
    b, _ = wait_done(t, domain, timeout=60)
    m.build(T1, 1)
    probs = check_candidates(b, domain, 1, build_time=T1)
    assert not probs, probs
    h = j(call("GET", f"/dossiers/{domain}/history", token=t))
    for f in FIELDS7:
        got = [(e["type"], _v(e["value"]), e["true_from"]) for e in h["fields"][f]]
        assert got == [(ty, _v(v), tf) for ty, v, tf, _ in m.history[f]], (f, got, m.history[f])
    ch = [(c["field"], c["type"], _v(c["to"])) for c in feed(t) if c["domain"] == domain]
    assert ch == [(f, ty, _v(b_)) for f, ty, a, b_, tf, la in m.feed]
    from datetime import datetime, timezone
    for ta in ("2015-01-01", "2024-01-01", "2026-02-15", "2026-06-01"):
        v = j(call("GET", f"/dossiers/{domain}/values", token=t, params={"true_at": ta}))
        want = m.values_at(ta, datetime(2100, 1, 1, tzinfo=timezone.utc))
        for f in FIELDS7:
            assert _v(v["fields"][f]["value"]) == _v(want[f][0]), (ta, f, v["fields"][f]["value"], want[f][0])


def test_as_of_spent_includes_in_flight(fresh):
    # RULING R3-1: "With as_of at or after the current time, the as_of total equals the current spent_units",
    # including what an in-flight build has incurred.
    t = fresh["ada"]
    mock_reset(0)
    create(t, D)
    wait_done(t, D, timeout=60)
    mock_reset(1)
    mock_fault("nimble", ["extract"], "delay", seconds=4)
    assert refresh(t, D).status_code == 202
    for _ in range(40):
        cur = j(get(t, D))
        if cur["state"] == "building" and cur["spent_units"] > j(call("GET", f"/dossiers/{D}", token=t,
                                                                        params={"as_of": T0}))["spent_units"]:
            break
        time.sleep(0.2)
    a = j(call("GET", f"/dossiers/{D}", token=t, params={"as_of": "2030-01-01T00:00:00+00:00"}))
    assert a["spent_units"] == j(get(t, D))["spent_units"]
    wait_done(t, D, timeout=60)
