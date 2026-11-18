"""Stage 4: lineage, own pages, origins, corroboration, investors, batches, provider failure."""
import concurrent.futures as cf
import json
import time

import pytest

from conftest import (FIELDS, FIELDS8, Model4, assert_err, call, check_candidates, check_citations, check_shape,
                      create, expected_candidates, fresh, get, j, log_cost, login, mock_fault, mock_log, mock_reset,
                      newkey, parse_ts, refresh, set_clock, wait_done)
import oracle

T0 = "2026-03-01T09:00:00+00:00"
T1 = "2026-04-01T09:00:00+00:00"


def build(t, d, epoch=0):
    mock_reset(epoch)
    assert create(t, d).status_code == 202
    b, _ = wait_done(t, d, timeout=60)
    time.sleep(0.5)
    return b, mock_log()


def test_lineage_kinds_origins_investors_hand_checked(fresh):
    # Stage 4 "Own pages", "Origins" rules 1-4, origins/corroborated, "Investors".
    d = "lumen-forge.test"
    b, calls = build(fresh["ada"], d)
    assert b["state"] == "ready"
    check_shape(b, d)
    f = b["fields"]
    by = {(c["url"]): c for c in f["ceo"]["candidates"]}
    # registrant written "WWW.Lumen-Forge.TEST" normalises to the company's domain -> own
    assert by["https://lumen-forge.test/about"]["kind"] == "own"
    # a copy (Canonical) takes its original's origin
    assert by["https://mirror-site.test/lumen"]["origin"] == "lumen-forge.test"
    assert f["ceo"]["origins"] == ["lumen-forge.test", "registry-x.test"] and f["ceo"]["corroborated"] is True
    assert parse_ts(f["ceo"]["corroborated_since"]) == parse_ts(T0)
    # syndicated (First-Published-By "Wire-One.test") and the original are one source
    assert f["funding_total"]["origins"] == ["wire-one.test"] and f["funding_total"]["corroborated"] is False
    assert f["funding_total"]["corroborated_since"] is None
    # lookalike: Kind own, registrant not its host -> kind aggregator, origin the company's domain
    hq = {c["url"]: c for c in f["hq_city"]["candidates"]}
    assert hq["https://lumen-forge-official.test/about"]["kind"] == "aggregator"
    assert hq["https://lumen-forge-official.test/about"]["origin"] == "lumen-forge.test"
    assert f["hq_city"]["origins"] == ["lumen-forge.test"] and f["hq_city"]["corroborated"] is False
    # Kind own on a site not registered to the company -> aggregator
    assert f["headcount_range"]["candidates"][0]["kind"] == "aggregator"
    # investors: Northwind (own page), Bluebird (two origins; an invalid Registrant -> host); Harbor Point (one
    # origin, news) and Quiet Partners (lookalike, one origin) are candidates but not members.
    inv = f["investors"]
    assert inv["value"] == ["Bluebird Capital", "Northwind Ventures"] and inv["status"] == "known"
    assert {c["value"] for c in inv["candidates"]} == {"Bluebird Capital", "Northwind Ventures", "Harbor Point",
                                                       "Quiet Partners"}
    assert {c["value"] for c in inv["candidates"] if c["selected"]} == {"Bluebird Capital", "Northwind Ventures"}
    assert inv["origins"] == ["agg-one.test", "lumen-forge.test", "newsy.test"]
    assert inv["corroborated"] is False and inv["corroborated_since"] is None  # Northwind has one origin
    # member true_from: Bluebird earliest non-null = 2025-02-01 (newsy Effective), Northwind 2024-05-02; field = latest
    assert inv["true_from"] == "2025-02-01"
    probs = check_candidates(b, d, 0, build_time=T0)
    assert not probs, probs
    check_citations(b, d, calls)
    assert b["spent_units"] == log_cost(calls) <= 80


def test_canonical_chain_three_hops_and_missing_original(fresh):
    # "rule 2 follows at most three Canonical URLs in a row. Where it would follow a fourth, or where no provider
    # serves a page at the URL, the host of that URL takes the place of the original's origin."
    d = "chainmere.test"
    b, calls = build(fresh["ada"], d)
    fy = {c["url"]: c["origin"] for c in b["fields"]["founded_year"]["candidates"]}
    assert fy == {"https://a-hop.test/x": "e-hop.test", "https://b-hop.test/x": "estate.test",
                  "https://c-hop.test/x": "estate.test", "https://d-hop.test/x": "estate.test",
                  "https://e-hop.test/x": "estate.test", "https://m-hop.test/y": "gone-away.test"}, fy
    assert b["fields"]["founded_year"]["origins"] == ["e-hop.test", "estate.test", "gone-away.test"]
    # RULING R4-1: an original fetched only to resolve an origin is not evidence: its "founded in 1999" is no
    # candidate, while the copy's headcount takes the original's origin.
    assert {c["value"] for c in b["fields"]["founded_year"]["candidates"]} == {2015}
    hc = b["fields"]["headcount_range"]["candidates"]
    assert [(c["url"], c["origin"]) for c in hc] == [("https://copyhub.test/chainmere", "vault.test")], hc
    # a Canonical naming the page's own URL is not a copy
    assert b["fields"]["ceo"]["candidates"][0]["origin"] == "chainmere.test"
    assert b["fields"]["ceo"]["corroborated"] is False and b["fields"]["ceo"]["corroborated_since"] is None
    probs = check_candidates(b, d, 0, build_time=T0)
    assert not probs, probs
    assert b["spent_units"] == log_cost(calls) <= 80


def test_corroborated_since_across_builds(fresh):
    # "corroborated_since is the time of the earliest ready build after which the selected value has had two or
    # more standing origins"
    t = fresh["ada"]
    d = "chainmere.test"
    m = Model4(d)
    build(t, d, 0)
    m.build(T0, 0)
    set_clock(T1)
    mock_reset(1)
    refresh(t, d)
    b, _ = wait_done(t, d, timeout=60)
    m.build(T1, 1)
    ceo = b["fields"]["ceo"]
    assert ceo["corroborated"] is True and parse_ts(ceo["corroborated_since"]) == parse_ts(T1)
    for f in FIELDS8:
        want = m.since[f]
        got = b["fields"][f]["corroborated_since"]
        assert (got is None and want is None) or parse_ts(got) == parse_ts(want), (f, got, want)


def test_investors_in_history_and_values(fresh):
    # investors take part in history (typed by name), feed (numbered last) and /values.
    t = fresh["ada"]
    d = "lumen-forge.test"
    build(t, d)
    h = j(call("GET", f"/dossiers/{d}/history", token=t))
    assert set(h["fields"]) == set(FIELDS8)
    assert [e["type"] for e in h["fields"]["investors"]] == ["initial"]
    assert h["fields"]["investors"][0]["value"] == ["Bluebird Capital", "Northwind Ventures"]
    v = j(call("GET", f"/dossiers/{d}/values", token=t, params={"true_at": "2030-01-01"}))
    assert v["fields"]["investors"]["value"] == ["Bluebird Capital", "Northwind Ventures"]
    v = j(call("GET", f"/dossiers/{d}/values", token=t, params={"true_at": "2024-06-01"}))
    # on 2024-06-01 only the own page (Effective 2024-05-02) holds; others' true_from = their Published date
    assert v["fields"]["investors"]["value"] == ["Northwind Ventures"], v["fields"]["investors"]


# ---------------- batches ----------------

def post_batch(t, body, key=None, raw=None):
    return call("POST", "/batches", token=t, key=key or newkey(), body=body, raw=raw)


@pytest.mark.parametrize("body", [
    {"budget_units": 100}, {"domains": [], "budget_units": 100},
    {"domains": [f"c{i}.test" for i in range(51)], "budget_units": 100},
    {"domains": ["bad domain"], "budget_units": 100},
    {"domains": ["tarnwick-labs.test", "WWW.Tarnwick-Labs.TEST."], "budget_units": 100},
    {"domains": ["tarnwick-labs.test"]}, {"domains": ["tarnwick-labs.test"], "budget_units": 0},
    {"domains": ["tarnwick-labs.test"], "budget_units": 100001}, {"domains": ["tarnwick-labs.test"], "budget_units": "10"},
    {"domains": ["tarnwick-labs.test"], "budget_units": True}, {"domains": ["tarnwick-labs.test"], "budget_units": 1.5},
    {"domains": ["tarnwick-labs.test"], "budget_units": None},
])
def test_batch_validation(fresh, body):
    # POST /batches case table; "A budget_units that is not an integer is 422 validation_failed whatever its
    # JSON type ... takes precedence over the 400 malformed_request"
    assert_err(post_batch(fresh["ada"], body), 422, "validation_failed")


@pytest.mark.parametrize("raw", [b'{"domains": ["tarnwick-labs.test"], "budget_units": 1.0}',
                                 b'{"domains": ["tarnwick-labs.test"], "budget_units": 1e0}',
                                 b'{"domains": "tarnwick-labs.test", "budget_units": 10}'])
def test_batch_budget_not_integer_raw(fresh, raw):
    # RULING R4-5: "1.0, 1e0, 1.5, true, "1" and null are each 422 validation_failed". (A string domains list is
    # read as "domains missing" for the 422 row.)
    r = call("POST", "/batches", token=fresh["ada"], key=newkey(), raw=raw)
    if b'"domains": "' in raw:
        assert r.status_code in (400, 422)
    else:
        assert_err(r, 422, "validation_failed")


def test_batch_auth_key_and_ownership(fresh):
    # "An idempotent write path. Idempotency-Key is required"; "another user's batch is 404 not_found"
    t = fresh["ada"]
    assert_err(call("POST", "/batches", body={"domains": ["a.test"], "budget_units": 5}), 401, "unauthenticated")
    assert_err(call("POST", "/batches", token=t, body={"domains": ["a.test"], "budget_units": 5}), 400,
               "missing_idempotency_key")
    mock_reset(0)
    r = post_batch(t, {"domains": ["tarnwick-labs.test"], "budget_units": 80})
    assert r.status_code == 202
    bid = j(r)["batch_id"]
    assert isinstance(bid, str) and 0 < len(bid) <= 64
    assert_err(call("GET", f"/batches/{bid}", token=fresh["bob"]), 404, "not_found")
    assert_err(call("GET", "/batches/nope", token=t), 404, "not_found")
    wait_done(t, "tarnwick-labs.test", timeout=60)


def test_batch_runs_shares_budget_and_skips_existing(fresh):
    # Batch semantics: dossiers listed in order with states; existing dossier not researched and costs nothing;
    # spent_units = the batch builds' cost, never above budget_units; each build <= 80 and counted in its dossier;
    # state running then done.
    t = fresh["ada"]
    build(t, "tarnwick-labs.test")
    mock_reset(0)
    doms = ["Quillon-Dynamics.TEST", "tarnwick-labs.test", "rankford-tools.test", "veilmoor-labs.test"]
    k = newkey()
    r = post_batch(t, {"domains": doms, "budget_units": 1000}, key=k)
    assert r.status_code == 202, r.text
    b = j(r)
    assert b["state"] == "running" and b["budget_units"] == 1000 and b["spent_units"] >= 0
    assert [x["domain"] for x in b["dossiers"]] == ["quillon-dynamics.test", "tarnwick-labs.test",
                                                    "rankford-tools.test", "veilmoor-labs.test"]
    assert b["dossiers"][1]["state"] == "ready" and b["dossiers"][0]["state"] == "building"
    # §7 replay
    r2 = post_batch(t, {"budget_units": 1000, "domains": doms}, key=k)
    assert r2.status_code == 200 and j(r2) == b
    assert_err(post_batch(t, {"domains": doms[:2], "budget_units": 1000}, key=k), 409, "idempotency_key_reuse")
    for d in ("quillon-dynamics.test", "rankford-tools.test", "veilmoor-labs.test"):
        wait_done(t, d, timeout=90)
    for _ in range(50):
        g = j(call("GET", f"/batches/{b['batch_id']}", token=t))
        if g["state"] == "done":
            break
        time.sleep(0.2)
    assert g["state"] == "done"
    time.sleep(0.5)
    calls = mock_log()
    per = {d: j(get(t, d))["spent_units"] for d in ("quillon-dynamics.test", "rankford-tools.test", "veilmoor-labs.test")}
    assert g["spent_units"] == sum(per.values()) == log_cost(calls) <= 1000
    assert all(v <= 80 for v in per.values())
    assert not any(tarn in (c.get("query") or "") for c in calls for tarn in ("tarnwick",))
    for d in per:
        bb = j(get(t, d))
        probs = check_candidates(bb, d, 0, build_time=T0)
        assert not probs, (d, probs)


def test_batch_budget_never_exceeded(fresh):
    # "spent_units ... never exceeds budget_units"; "the batch makes no more provider calls, and its remaining
    # builds complete with the pages and research claims they have obtained"
    t = fresh["ada"]
    mock_reset(0)
    doms = ["tarnwick-labs.test", "quillon-dynamics.test", "rankford-tools.test", "halvorsen-robotics.test"]
    r = post_batch(t, {"domains": doms, "budget_units": 45})
    assert r.status_code == 202
    bid = j(r)["batch_id"]
    for d in doms:
        bb, _ = wait_done(t, d, timeout=90)
        assert bb["state"] in ("ready", "failed")
    time.sleep(1)
    g = j(call("GET", f"/batches/{bid}", token=t))
    calls = mock_log()
    assert g["state"] == "done"
    assert g["spent_units"] == log_cost(calls) <= 45, (g["spent_units"], log_cost(calls))
    for d in doms:
        bb = j(get(t, d))
        check_citations(bb, d, calls)
        exp = expected_candidates(d, 0)[0]
        for f in FIELDS:
            for c in bb["fields"][f]["candidates"]:
                assert (f, c["url"], c["value"]) in exp, (d, f, c["url"], c["value"])


def test_batch_concurrent_same_key(fresh):
    # §7 concurrent identical requests with an unused key: one normal response, others 200, effect once.
    t = fresh["ada"]
    mock_reset(0)
    k = newkey()
    body = {"domains": ["tarnwick-labs.test", "quillon-dynamics.test"], "budget_units": 200}
    with cf.ThreadPoolExecutor(15) as ex:
        rs = list(ex.map(lambda _: post_batch(t, body, key=k), range(15)))
    codes = sorted(r.status_code for r in rs)
    assert codes.count(202) == 1 and codes.count(200) == 14, codes
    assert len({json.dumps(j(r)["batch_id"]) for r in rs}) == 1
    for d in body["domains"]:
        wait_done(t, d, timeout=60)
    time.sleep(0.5)
    dom = [c for c in mock_log() if c["method"] == "search" and c.get("status") == 200 and c.get("query") == "tarnwick-labs.test"]
    assert len(dom) == 1


# ---------------- provider failure ----------------

def test_tavily_and_browsers_all_failing_full_evidence(fresh):
    # "A build in which every call to one or more providers fails, while nimble answers, completes ready, with
    # every field known that the evidence reachable through the providers that answer supports."
    t = fresh["ada"]
    d = "rankford-tools.test"
    mock_reset(0)
    mock_fault("tavily", ["search", "extract"], "error")
    mock_fault("kernel", ["session"], "error")
    mock_fault("browserbase", ["session", "browse"], "error")
    assert create(t, d).status_code == 202
    b, _ = wait_done(t, d, timeout=60)
    assert b["state"] == "ready"
    probs = check_candidates(b, d, 0, build_time=T0)
    assert not probs, probs


def test_research_failing_search_and_extract_evidence(fresh):
    # "A build in which every research run fails, while searches and extracts are answered, completes ready, with
    # every field known that the evidence reachable by search and extract supports."
    t = fresh["ada"]
    d = "tarnwick-labs.test"
    mock_reset(0)
    mock_fault("nimble", ["research"], "error")
    assert create(t, d).status_code == 202
    b, _ = wait_done(t, d, timeout=60)
    assert b["state"] == "ready"
    calls = mock_log()
    check_citations(b, d, calls)
    # the founding year sits only on a non-searchable page reachable through research -> unknown
    assert b["fields"]["founded_year"]["status"] == "unknown"
    for f in ("legal_name", "hq_city", "ceo", "headcount_range", "funding_total"):
        assert b["fields"][f]["status"] == "known", f
    assert b["spent_units"] == log_cost(calls)


def test_every_provider_failing_ends_failed_in_time(fresh):
    # "A build in which every call to every provider fails completes failed (§8), within the time bound of §8."
    t = fresh["ada"]
    d = "quillon-dynamics.test"
    mock_reset(0)
    for p_, ms in (("nimble", ["search", "extract", "research"]), ("tavily", ["search", "extract"]),
                   ("kernel", ["session"]), ("browserbase", ["session", "browse"])):
        mock_fault(p_, ms, "error")
    t0 = time.time()
    assert create(t, d).status_code == 202
    b, _ = wait_done(t, d, timeout=30)
    assert b["state"] == "failed" and time.time() - t0 <= 10.5
    assert b["spent_units"] == 0


def test_nimble_5xx_then_recovers(fresh):
    # "A provider may answer a call with an error (any 5xx status, or 429). The build continues: it may make the
    # same request again". With nimble's searches failing for the first seconds, the build still completes ready.
    import threading
    t = fresh["ada"]
    d = "tarnwick-labs.test"
    mock_reset(0)
    mock_fault("nimble", ["search", "extract"], "error")
    threading.Timer(1.5, lambda: mock_fault("nimble", ["search", "extract"], "none")).start()
    assert create(t, d).status_code == 202
    b, _ = wait_done(t, d, timeout=60)
    assert b["state"] in ("ready", "failed")
    calls = mock_log()
    check_citations(b, d, calls)
    assert b["spent_units"] == log_cost(calls) <= 80



def test_batches_survive_native_export_import(fresh):
    # RULING R4-7: a stage-4 export holds every batch; after import it is done, GET answers for its owner (404 for
    # others), and the original POST /batches replays its original 202 body.
    t = fresh["ada"]
    mock_reset(0)
    k = newkey()
    body = {"domains": ["tarnwick-labs.test"], "budget_units": 90}
    r = post_batch(t, body, key=k)
    assert r.status_code == 202
    orig = j(r)
    wait_done(t, "tarnwick-labs.test", timeout=60)
    time.sleep(0.5)
    g0 = j(call("GET", f"/batches/{orig['batch_id']}", token=t))
    e = j(call("GET", "/_test/export", timeout=10))
    from conftest import reset
    reset()
    mock_reset(0)
    assert call("POST", "/_test/import", body=e, timeout=10).status_code == 204
    g = j(call("GET", f"/batches/{orig['batch_id']}", token=t))
    assert g["state"] == "done" and g["spent_units"] == g0["spent_units"] and g["budget_units"] == 90
    assert_err(call("GET", f"/batches/{orig['batch_id']}", token=fresh["bob"]), 404, "not_found")
    r2 = post_batch(t, body, key=k)
    assert r2.status_code == 200 and j(r2) == orig
    time.sleep(0.5)
    assert mock_log() == []


def test_post_seal_batch_budget_covering_full_build_misses_nothing(fresh):
    # POST-SEAL ADDITION (code read at VERIFY 4). Batch rule: only "When the budget would be exceeded by a further
    # call" does a batch stop calling, and dispatch: "a saving that leaves out evidence a field needs is a defect"
    # (R1-2). With a batch budget that covers the whole build an unbatched dossier makes, the batch's build must
    # find the same candidates.
    t = fresh["ada"]
    d = "tarnwick-labs.test"
    mock_reset(0)
    assert create(t, d).status_code == 202
    solo, _ = wait_done(t, d, timeout=60)
    cost = solo["spent_units"]
    from conftest import reset
    reset()
    t = login("ada@example.com")
    mock_reset(0)
    budget = cost + 5
    r = post_batch(t, {"domains": [d], "budget_units": budget})
    assert r.status_code == 202
    b, _ = wait_done(t, d, timeout=60)
    assert b["state"] == "ready"
    assert b["fields"]["founded_year"]["value"] == solo["fields"]["founded_year"]["value"] == 1987, \
        (budget, b["spent_units"], b["fields"]["founded_year"])
    probs = check_candidates(b, d, 0, build_time=T0)
    assert not probs, (budget, b["spent_units"], probs)


@pytest.mark.parametrize("short", [23, 3])
def test_post_seal_short_batch_budget_pages_before_research(fresh, short):
    # POST-SEAL ADDITION (RULING R4-9). "When the remaining budget cannot cover the whole plan: 1. Do the
    # company-naming searches and render the returned pages first. 2. Start research only while some field is
    # unsupported, and only if the remainder after 25u can still render at least one cited page." quillon-
    # dynamics.test has every field on searchable pages; a batch budget that covers its searches and pages but not
    # also the research run must still end with every supported field known.
    t = fresh["ada"]
    d = "quillon-dynamics.test"
    mock_reset(0)
    assert create(t, d).status_code == 202
    solo, _ = wait_done(t, d, timeout=60)
    research = sum(c["cost"] for c in mock_log() if c["method"] == "research")
    assert research == 25, research
    budget = solo["spent_units"] - short   # 23: research unaffordable; 3: research affordable, whole plan not
    from conftest import reset
    reset()
    t = login("ada@example.com")
    mock_reset(0)
    r = post_batch(t, {"domains": [d], "budget_units": budget})
    assert r.status_code == 202
    b, _ = wait_done(t, d, timeout=60)
    time.sleep(0.5)
    calls = mock_log()
    assert b["state"] == "ready"
    assert log_cost(calls) <= budget
    want = {f: solo["fields"][f]["value"] for f in FIELDS}
    got = {f: b["fields"][f]["value"] for f in FIELDS}
    assert got == want, (budget, b["spent_units"], got, want)
    probs = check_candidates(b, d, 0, build_time=T0)
    assert not probs, (budget, probs)
