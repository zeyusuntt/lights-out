"""§1, §4 evidence and support, §8 builds, §9 providers and cost."""
import time

import pytest

from conftest import (check_candidates, CUSTOM, FIELDS, SVC2, assert_err, call, check_citations, check_shape,
                      corpus_domains, create, evidence_values, fresh, get, j, log_cost, login,
                      mock_epoch, mock_fault, mock_log, mock_reset, newkey, parse_ts, refresh,
                      report, reset, wait_done)
import oracle

RESULTS = {}


def company_name(d):
    return oracle.company_name(d)


def check_provider_rules(calls, domain, units_spent_by_build):
    """§4 / §9 rules readable from the call log of one build."""
    ok_search = [c for c in calls if c["method"] == "search" and c.get("status") == 200]
    # §4 "Of the searches that a provider answers without an error, every build makes exactly one whose
    # query is exactly the company's normalised domain ...; its other such searches use other queries."
    dom = [c for c in ok_search if c.get("query") == domain]
    assert len(dom) == 1, f"{len(dom)} successful searches with query == {domain!r}"
    # §1.2 / §9 "No build of a dossier spends more than 80 units"
    assert units_spent_by_build <= 80, units_spent_by_build
    for c in calls:
        if c["method"] == "research":
            # §9 "A research request names the company by its domain in its query, and names the fields it
            # asks for by the field names in §4, as the property names of its output schema."
            if c.get("query") is not None:
                assert domain in c["query"].lower(), c["query"]
            assert c.get("fields") and set(c["fields"]) <= set(FIELDS), c.get("fields")
            assert c["provider"] == "nimble"
        if c["method"] == "extract" and c["provider"] == "nimble" and c.get("status") == 200:
            # §9 extract 1 per URL; stage 2 "Extract through nimble that loads the page in a browser | 3 per URL"
            assert c["cost"] in (len(c.get("urls") or []), 3 * len(c.get("urls") or [])), c
        assert c["provider"] in ("nimble", "tavily", "kernel", "browserbase"), c["provider"]


def build_and_check(t, domain, epoch, first=True):
    mock_reset(epoch)
    t0 = time.time()
    r = create(t, domain) if first else refresh(t, domain)
    assert r.status_code == 202, r.text
    b0 = j(r)
    assert b0["domain"] == domain and b0["state"] == "building"
    b, took = wait_done(t, domain, timeout=30)
    took = time.time() - t0
    time.sleep(0.5)
    calls = mock_log()
    return b, took, calls


def assert_fields_match_evidence(b, domain, epoch, build_time=None):
    # §8 "each field is known exactly when the evidence (§4) supports a value for it", now read through
    # stage 2: "Every value that a page of the evidence supports for a field is a candidate of that field,
    # once for each such page"; the selection rule; Status. Returns (problems-by-field, evidence values).
    ev = evidence_values(domain, epoch)
    probs = check_candidates(b, domain, epoch, build_time=build_time)
    wrong = {}
    for pr in probs:
        wrong.setdefault(pr[0], []).append(pr[1:])
    return wrong, ev


@pytest.mark.parametrize("domain", sorted(set(
    __import__("conftest").corpus_domains())))
def test_build_is_correct_cited_and_within_budget(fresh, domain):
    t = fresh["ada"]
    b, took, calls = build_and_check(t, domain, 0)
    check_shape(b, domain)
    assert b["state"] == "ready", b["state"]
    # §8 "A build whose provider calls each answer within one second ends within 10 seconds of the
    # request that started it."
    assert took <= 10.5, took
    # §8 "researched_at is the time of the last build that completed ready"
    assert parse_ts(b["researched_at"]) == parse_ts("2026-03-01T09:00:00+00:00")
    spent = log_cost(calls)
    # §8 "spent_units is the total cost (§9) of every provider call made for this dossier"
    assert b["spent_units"] == spent, (b["spent_units"], spent)
    check_provider_rules(calls, domain, spent)
    # §1.1 every value cites a served, supporting excerpt
    check_citations(b, domain, calls)
    wrong, ev = assert_fields_match_evidence(b, domain, 0, build_time="2026-03-01T09:00:00+00:00")
    RESULTS[domain] = {"spent": spent, "known": sum(1 for f in FIELDS if b["fields"][f]["status"] == "known"),
                       "correct": sum(1 for f in FIELDS if f not in wrong and ev[f]),
                       "supportable": sum(1 for f in FIELDS if ev[f]), "wrong": wrong,
                       "calls": [(c["provider"], c["method"], c.get("depth"), c.get("cost")) for c in calls]}
    report("units", RESULTS)
    assert not wrong, wrong


def test_custom_expected_values_hand_checked(fresh):
    # Hand-derived from Appendix A for the suite's own corpus (independent of the oracle).
    exp = {
        "quillon-dynamics.test": {"legal_name": "Quillon Dynamics GmbH", "hq_city": "Saint-Étienne",
                                  "ceo": "Hana Okafor", "founded_year": 1998,
                                  "headcount_range": "1001-5000", "funding_total": 12500000},
        "nullmark-systems.test": {f: None for f in FIELDS},
        "tarnwick-labs.test": {"legal_name": "Tarnwick Labs S.A.S.", "hq_city": "Zürich",
                               "ceo": "Mira Solberg", "founded_year": 1987,
                               "headcount_range": "1-10", "funding_total": 4500000},
    }
    t = fresh["ada"]
    for d, want in exp.items():
        b, _, calls = build_and_check(t, d, 0)
        assert b["state"] == "ready"
        got = {f: b["fields"][f]["value"] for f in FIELDS}
        assert got == want, (d, got)
        check_citations(b, d, calls)


def test_refresh_researches_again_and_replaces_fields(fresh):
    # §8 refresh "Starts a new build"; "A refresh researches again: its build makes provider calls whether
    # or not anything has changed since the last build, and its spending counts in spent_units."
    # §8 "replaces the dossier's fields with the result when it completes"
    t = fresh["ada"]
    d = "tarnwick-labs.test"
    b1, _, c1 = build_and_check(t, d, 0)
    assert b1["fields"]["ceo"]["value"] == "Mira Solberg"
    b2, _, c2 = build_and_check(t, d, 0, first=False)  # nothing changed
    assert log_cost(c2) > 0
    assert b2["spent_units"] == log_cost(c1) + log_cost(c2)
    check_provider_rules(c2, d, log_cost(c2))
    b3, _, c3 = build_and_check(t, d, 1, first=False)  # epoch 1: new CEO
    assert b3["state"] == "ready"
    assert b3["fields"]["ceo"]["value"] == "Jonas Erikson Vale"
    check_citations(b3, d, c3)
    assert b3["spent_units"] == log_cost(c1) + log_cost(c2) + log_cost(c3)


@pytest.mark.parametrize("domain", ["halvorsen-robotics.test", "ashgrove-solar.test", "pemberton-analytics.test"])
def test_refresh_in_new_epoch_matches_new_evidence(fresh, domain):
    # §8 "When a build completes ready, each field is known exactly when the evidence supports a value"
    # — applied to a refresh after the web changed, including fields that become unknown.
    if domain not in corpus_domains():
        pytest.skip("not in corpus")
    t = fresh["ada"]
    build_and_check(t, domain, 0)
    b, _, calls = build_and_check(t, domain, 1, first=False)
    assert b["state"] == "ready"
    check_citations(b, domain, calls)
    check_provider_rules(calls, domain, log_cost(calls))
    wrong, _ = assert_fields_match_evidence(b, domain, 1)
    assert not wrong, wrong


def test_while_building_fields_unknown_then_previous(fresh):
    # §8 "Before the first build completes ready, every field is unknown. While a later build runs, fields
    # are those of the last build that completed ready." "researched_at ... or null." "state is building
    # while a build runs"
    t = fresh["ada"]
    d = "quillon-dynamics.test"
    mock_fault("nimble", ["search", "extract", "research"], "delay", seconds=1)
    mock_fault("tavily", ["search", "extract"], "delay", seconds=1)
    r = create(t, d)
    assert r.status_code == 202
    b = j(get(t, d))
    check_shape(b, d)
    assert b["state"] == "building" and b["researched_at"] is None
    assert all(b["fields"][f]["status"] == "unknown" for f in FIELDS)
    # A second POST for the existing dossier: §8 "starts no build and returns 200 with that dossier's
    # dossier_id, domain and current state."
    r2 = create(t, d)
    assert r2.status_code == 200 and j(r2) == {"dossier_id": j(r)["dossier_id"], "domain": d,
                                               "state": "building"}
    done, _ = wait_done(t, d, timeout=30)
    assert done["state"] == "ready"
    r3 = create(t, d)
    assert r3.status_code == 200 and j(r3)["state"] == "ready"
    rr = refresh(t, d)
    assert rr.status_code == 202 and j(rr) == {"dossier_id": j(r)["dossier_id"], "domain": d,
                                               "state": "building"}
    # §8 "A refresh received while a build of the dossier is running starts no second build and returns
    # 202 with the same body."
    rr2 = refresh(t, d)
    assert rr2.status_code == 202 and j(rr2) == j(rr)
    mid = j(get(t, d))
    assert mid["state"] == "building"
    assert mid["fields"] == done["fields"] and mid["researched_at"] == done["researched_at"]
    wait_done(t, d, timeout=30)


def test_one_build_at_a_time_concurrent_refreshes(fresh):
    # §8 "A dossier has at most one build running at a time."
    import concurrent.futures as cf
    t = fresh["ada"]
    d = "tarnwick-labs.test"
    build_and_check(t, d, 0)
    mock_reset(0)
    with cf.ThreadPoolExecutor(20) as ex:
        rs = list(ex.map(lambda _: refresh(t, d), range(20)))
    assert all(r.status_code == 202 for r in rs), [r.status_code for r in rs]
    wait_done(t, d)
    time.sleep(0.5)
    dom = [c for c in mock_log() if c["method"] == "search" and c["status"] == 200 and c["query"] == d]
    assert len(dom) == 1, len(dom)


def test_all_providers_failing_first_build_fails(fresh):
    # §8 "A build ends ... failed when none of its provider calls succeeded. A failed build leaves the fields
    # as they were." §5 "Requests must not produce 5xx responses, ... when a provider endpoint answers with
    # an error." §9 "A call that a provider refuses with an error status costs nothing."
    t = fresh["ada"]
    d = "quillon-dynamics.test"
    mock_fault("nimble", ["search", "extract", "research"], "error")
    mock_fault("tavily", ["search", "extract"], "error")
    assert create(t, d).status_code == 202
    b, _ = wait_done(t, d, timeout=30)
    check_shape(b, d)
    assert b["state"] == "failed"
    assert b["researched_at"] is None and b["spent_units"] == 0
    assert all(b["fields"][f]["status"] == "unknown" for f in FIELDS)
    lst = j(call("GET", "/dossiers", token=t))["dossiers"]
    assert lst[0]["state"] == "failed" and lst[0]["legal_name"] is None


def test_failed_refresh_keeps_fields(fresh):
    # §8 "A failed build leaves the fields as they were." "state is ... the outcome of the latest build"
    t = fresh["ada"]
    d = "tarnwick-labs.test"
    b1, _, _ = build_and_check(t, d, 0)
    from conftest import set_clock
    set_clock("2026-03-02T00:00:00+00:00")
    mock_fault("nimble", ["search", "extract", "research"], "error")
    mock_fault("tavily", ["search", "extract"], "error")
    assert refresh(t, d).status_code == 202
    b2, _ = wait_done(t, d, timeout=30)
    assert b2["state"] == "failed"
    assert b2["fields"] == b1["fields"]
    assert b2["researched_at"] == b1["researched_at"]
    assert b2["spent_units"] == b1["spent_units"]
    lst = j(call("GET", "/dossiers", token=t))["dossiers"][0]
    assert lst["state"] == "failed" and lst["legal_name"] == b1["fields"]["legal_name"]["value"]


def test_tavily_failing_nimble_alone_suffices(fresh):
    # §2 "every service must be able to research companies using Nimble alone ... its absence must not
    # prevent research while Nimble answers."
    t = fresh["ada"]
    d = "quillon-dynamics.test"
    mock_reset(0)
    mock_fault("tavily", ["search", "extract"], "error")
    assert create(t, d).status_code == 202
    b, _ = wait_done(t, d, timeout=30)
    assert b["state"] == "ready"
    calls = mock_log()
    check_citations(b, d, calls)
    wrong, _ = assert_fields_match_evidence(b, d, 0)
    assert not wrong, wrong
    assert b["spent_units"] == log_cost(calls) <= 80


def test_without_tavily_configured(fresh):
    # §2 / event rules: "Tavily ... their absence must not prevent research while Nimble answers."
    # svc2 runs with no TAVILY_* variables at all.
    reset(base=SVC2)
    tok = login("ada@example.com", base=SVC2)
    d = "tarnwick-labs.test"
    mock_reset(0)
    r = call("POST", "/dossiers", token=tok, key=newkey(), body={"domain": d}, base=SVC2)
    assert r.status_code == 202
    b, _ = wait_done(tok, d, base=SVC2, timeout=30)
    assert b["state"] == "ready"
    calls = mock_log()
    assert all(c["provider"] == "nimble" for c in calls)
    check_citations(b, d, calls)
    wrong, _ = assert_fields_match_evidence(b, d, 0)
    assert not wrong, wrong


def test_nimble_search_faulted_no_5xx_and_honest(fresh):
    # §5 "Requests must not produce 5xx responses ... when a provider endpoint answers with an error."
    # §1.1 still holds for whatever the build asserts.
    t = fresh["ada"]
    d = "halvorsen-robotics.test"
    mock_reset(0)
    mock_fault("nimble", ["search"], "error")
    assert create(t, d).status_code == 202
    b, _ = wait_done(t, d, timeout=30)
    assert b["state"] in ("ready", "failed")
    calls = mock_log()
    check_citations(b, d, calls)
    assert b["spent_units"] == log_cost(calls) <= 80


def test_slow_provider_within_one_second_build_within_10s(fresh):
    # §8 "A build whose provider calls each answer within one second ends within 10 seconds of the request"
    t = fresh["ada"]
    d = "halvorsen-robotics.test"
    mock_reset(0)
    for p, m in (("nimble", ["search", "extract", "research"]), ("tavily", ["search", "extract"])):
        mock_fault(p, m, "delay", seconds=0.9)
    t0 = time.time()
    assert create(t, d).status_code == 202
    b, _ = wait_done(t, d, timeout=30)
    took = time.time() - t0
    assert b["state"] == "ready"
    assert took <= 10.5, took


def test_reads_make_no_provider_calls(fresh):
    # §8 "Reading a dossier, listing dossiers and every other request except POST /dossiers and POST
    # /dossiers/{domain}/refresh make no provider call."
    t = fresh["ada"]
    d = "tarnwick-labs.test"
    build_and_check(t, d, 0)
    mock_reset(0)
    for _ in range(3):
        get(t, d)
        call("GET", "/dossiers", token=t)
        call("GET", "/dossiers", token=t, params={"q": "tarn"})
        create(t, d)  # existing dossier: §8 "starts no build"
    call("GET", "/_test/export", timeout=10)
    call("POST", "/auth/login", body={"email": "ada@example.com", "password": "correct horse"})
    time.sleep(1)
    assert mock_log() == []


def test_units_report():
    # Not a requirement: records units per correct field (§9 "Research spend per correct field is judged")
    if RESULTS:
        tot = sum(v["spent"] for v in RESULTS.values())
        cor = sum(v["correct"] for v in RESULTS.values())
        report("units_summary", {"units": tot, "correct_fields": cor,
                                 "supportable_fields": sum(v["supportable"] for v in RESULTS.values()),
                                 "units_per_correct": tot / cor if cor else None})


def test_refused_domain_search_retried_exactly_one_success(fresh):
    # §4 "Of the searches that a provider answers without an error, every build makes exactly one whose query
    # is exactly the company's normalised domain"; "A search that a provider answers with an error does not
    # count." RULING R1-3: retry on refusal; exactly one success counting all providers.
    t = fresh["ada"]
    d = "tarnwick-labs.test"
    mock_reset(0)
    mock_fault("nimble", ["search"], "throttle")
    mock_fault("tavily", ["search"], "throttle")
    assert create(t, d).status_code == 202
    b, _ = wait_done(t, d, timeout=40)
    assert b["state"] == "ready"
    time.sleep(0.5)
    calls = mock_log()
    check_provider_rules(calls, d, log_cost(calls))
    check_citations(b, d, calls)
    assert b["spent_units"] == log_cost(calls)
    wrong, _ = assert_fields_match_evidence(b, d, 0)
    assert not wrong, wrong


def test_post_seal_long_sentence_cited_by_short_span(fresh):
    # POST-SEAL ADDITION (RULING R1-6). A supporting sentence over 500 characters is cited by a contiguous
    # span of at most 500 characters that on its own satisfies A.2; §4 "It is 1 to 500 characters long."
    t = fresh["ada"]
    d = "brackwater-kilns.test"
    b, _, calls = build_and_check(t, d, 0)
    assert b["state"] == "ready"
    assert b["fields"]["founded_year"]["value"] == 1952, b["fields"]["founded_year"]
    assert b["fields"]["ceo"]["value"] == "Orla Venn"
    check_citations(b, d, calls)
    assert all(len(c["excerpt"]) <= 500 for f in b["fields"].values() for c in f["citations"])


@pytest.mark.parametrize("domain,field,want", [
    # POST-SEAL ADDITIONS (round 3). RULING R1-6: an 800-char supporting sentence whose supporting span lies
    # at its end must still yield a known field; §8 "each field is known exactly when the evidence supports"
    ("ironvale-pottery.test", "founded_year", 1952),
    # FIX 1 2 F3: research prose shaped like a header line ("Profile: ...") is prose (§4 header ends at the
    # first empty line), so the supported claim is known.
    ("copperleaf-studio.test", "ceo", "Ines Marlow"),
    # FIX 1 2 F4 / R1-6: a research excerpt over 500 chars is cited by a supporting span of at most 500.
    ("saltmarsh-works.test", "founded_year", 1961),
])
def test_post_seal_round3_edge_evidence(fresh, domain, field, want):
    t = fresh["ada"]
    b, _, calls = build_and_check(t, domain, 0)
    assert b["state"] == "ready"
    assert b["fields"][field]["value"] == want, b["fields"][field]
    check_citations(b, domain, calls)
    assert all(len(c["excerpt"]) <= 500 for f in b["fields"].values() for c in f["citations"])
