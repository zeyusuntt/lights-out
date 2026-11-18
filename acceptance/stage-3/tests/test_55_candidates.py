"""Stage 2: candidates, the selection rule, status, page kind / publication time, page text."""
import time

import pytest

from conftest import (FIELDS, call, check_candidates, check_citations, check_shape, create, fresh, get,
                      j, log_cost, mock_fault, mock_log, mock_reset, parse_ts, refresh, set_clock, wait_done)

D = "rankford-tools.test"
NOW0 = "2026-03-01T09:00:00+00:00"


def build(t, d, epoch=0):
    mock_reset(epoch)
    assert create(t, d).status_code == 202
    b, _ = wait_done(t, d, timeout=40)
    time.sleep(0.5)
    return b, mock_log()


def test_selection_rule_hand_checked(fresh):
    # Stage 2 "The selection rule": 1. Authority (own = filing > news > aggregator), 2. Recency within the
    # same authority (no publication time ranks below), 3. URL by code point, then provider, 4. Value.
    # "A page with no Kind line, or with a value not listed above, is of kind own when the host ... is the
    # company's domain, and of kind aggregator otherwise." "A page with no Published line, or with a value
    # that is not an RFC 3339 timestamp, has no publication time."
    b, calls = build(fresh["ada"], D)
    assert b["state"] == "ready"
    check_shape(b, D)
    ceo = b["fields"]["ceo"]
    got = [(c["value"], c["kind"]) for c in ceo["candidates"]]
    assert got == [("Bruno Keller", "filing"), ("Alma Reyes", "own"), ("Elena Sato", "own"),
                   ("Carla Nunez", "news"), ("Dmitri Volk", "aggregator"), ("Felix Grau", "aggregator")], got
    assert ceo["value"] == "Bruno Keller" and ceo["status"] == "contested"
    assert [c["selected"] for c in ceo["candidates"]] == [True] + [False] * 5
    sato = ceo["candidates"][2]
    assert sato["published_at"] is None  # "Published: yesterday" is not RFC 3339
    assert ceo["candidates"][5]["published_at"] is None and ceo["candidates"][5]["kind"] == "aggregator"
    # "Status: known — The field has candidates, and they all have the same value"; citations are every
    # candidate with the selected value, in rank order.
    fy = b["fields"]["founded_year"]
    assert fy["status"] == "known" and fy["value"] == 2001
    assert [c["url"] for c in fy["candidates"]] == ["https://rankford-tools.test/about",
                                                    "https://dailywire.test/rankford"]
    assert [c["url"] for c in fy["citations"]] == ["https://rankford-tools.test/about",
                                                   "https://dailywire.test/rankford"]
    # 3. URL: equal authority and publication time -> smaller URL first
    hq = b["fields"]["hq_city"]
    assert [c["value"] for c in hq["candidates"]] == ["Oslo", "Bergen"] and hq["value"] == "Oslo"
    assert hq["status"] == "contested"
    # 4. Value: same URL and provider -> smaller value first ("11-50" < "201-500" by code point)
    hc = b["fields"]["headcount_range"]
    assert [c["value"] for c in hc["candidates"]] == ["11-50", "201-500"] and hc["value"] == "11-50"
    # "retrieved_at is the time of the build that gathered the candidate"
    for f in FIELDS:
        for c in b["fields"][f]["candidates"]:
            assert parse_ts(c["retrieved_at"]) == parse_ts(NOW0)
    ln = b["fields"]["legal_name"]
    assert (ln["value"], ln["status"], ln["citations"], ln["candidates"]) == (None, "unknown", [], [])
    probs = check_candidates(b, D, 0, build_time=NOW0)
    assert not probs, probs
    check_citations(b, D, calls)
    # §8 list: "The legal_name it lists is the selected value." (unknown here)
    item = [i for i in j(call("GET", "/dossiers", token=fresh["ada"]))["dossiers"] if i["domain"] == D][0]
    assert item["legal_name"] is None


def test_same_candidates_same_value_across_refresh(fresh):
    # Stage 2 list item 3 "the same candidates always yield the same value"
    t = fresh["ada"]
    b1, _ = build(t, D)
    for _ in range(2):
        mock_reset(0)
        assert refresh(t, D).status_code == 202
        b2, _ = wait_done(t, D, timeout=40)
        assert {f: b2["fields"][f]["value"] for f in FIELDS} == {f: b1["fields"][f]["value"] for f in FIELDS}
        assert [c["url"] for c in b2["fields"]["ceo"]["candidates"]] == \
            [c["url"] for c in b1["fields"]["ceo"]["candidates"]]


def test_retrieved_at_is_build_time_of_refresh(fresh):
    # "retrieved_at is the time of the build that gathered the candidate (§8, Builds)"; "candidates lists the
    # candidates of the last build that completed ready"
    t = fresh["ada"]
    build(t, "tarnwick-labs.test")
    set_clock("2026-03-05T10:00:00+00:00")
    mock_reset(1)
    assert refresh(t, "tarnwick-labs.test").status_code == 202
    b, _ = wait_done(t, "tarnwick-labs.test", timeout=40)
    calls = mock_log()
    assert b["state"] == "ready"
    for f in FIELDS:
        for c in b["fields"][f]["candidates"]:
            assert parse_ts(c["retrieved_at"]) == parse_ts("2026-03-05T10:00:00+00:00")
    assert [c["value"] for c in b["fields"]["ceo"]["candidates"]] == ["Jonas Erikson Vale"]
    probs = check_candidates(b, "tarnwick-labs.test", 1, build_time="2026-03-05T10:00:00+00:00")
    assert not probs, probs
    check_citations(b, "tarnwick-labs.test", calls)


def test_page_text_is_browser_text(fresh):
    # Stage 2 "a page's text is the text a browser shows once the page has loaded"; "Evidence (§4) is read
    # from page text so defined, and a citation's excerpt must appear in the page's text."
    # veilmoor-labs.test serves a different static text to search/extract than its browser text.
    b, calls = build(fresh["ada"], "veilmoor-labs.test")
    assert b["state"] == "ready"
    assert b["fields"]["ceo"]["value"] == "Nora Quist", b["fields"]["ceo"]
    assert [c["value"] for c in b["fields"]["ceo"]["candidates"]] == ["Nora Quist"]
    check_citations(b, "veilmoor-labs.test", calls)
    probs = check_candidates(b, "veilmoor-labs.test", 0, build_time=NOW0)
    assert not probs, probs
    assert b["spent_units"] == log_cost(calls) <= 80


def test_research_cited_page_is_evidence(fresh):
    # Stage 2 "The evidence now also holds the page that each research claim of the evidence cites, whether
    # or not the citation supports its claim: a build reads that page as it reads any other. A research claim
    # whose citation does not support it is still not a candidate."
    t = fresh["ada"]
    b, calls = build(t, "tarnwick-labs.test")
    fy = b["fields"]["founded_year"]
    assert [c["url"] for c in fy["candidates"]] == ["https://registry-north.test/tarnwick-labs"]
    b2, calls2 = build(t, "nullmark-systems.test")
    assert all(b2["fields"][f]["candidates"] == [] for f in FIELDS)
    for d, bb, cc in (("tarnwick-labs.test", b, calls), ("nullmark-systems.test", b2, calls2)):
        probs = check_candidates(bb, d, 0, build_time=NOW0)
        assert not probs, probs
        check_citations(bb, d, cc)


def test_weather_on_builds_stay_correct(fresh):
    # Stage 2 "Rate limits: From this stage a provider may answer any call with 429. A call answered 429 costs
    # nothing." "Time a build spends waiting to make a call again after a 429 does not count toward the 10
    # seconds". §5 no 5xx.
    import httpx
    from conftest import ADMIN, MOCK
    t = fresh["ada"]
    for d in ("rankford-tools.test", "halvorsen-robotics.test", "quillon-dynamics.test"):
        mock_reset(0)
        httpx.post(MOCK + "/_mock/weather", json={"on": True}, headers={"X-Mock-Admin": ADMIN}, timeout=5)
        assert create(t, d).status_code == 202
        b, _ = wait_done(t, d, timeout=60)
        time.sleep(0.5)
        calls = mock_log()
        assert b["state"] == "ready"
        assert b["spent_units"] == log_cost(calls) <= 80
        check_citations(b, d, calls)
        probs = check_candidates(b, d, 0, build_time=NOW0)
        assert not probs, (d, probs)


def test_throttled_everything_builds_stay_correct(fresh):
    # Stage 2 "No call is answered 429 more than three times in a row"; a build that retries after the
    # one-second wait completes with the same candidates.
    t = fresh["ada"]
    d = "tarnwick-labs.test"
    mock_reset(0)
    mock_fault("nimble", ["search", "extract", "research"], "throttle")
    mock_fault("tavily", ["search", "extract"], "throttle")
    assert create(t, d).status_code == 202
    b, _ = wait_done(t, d, timeout=60)
    time.sleep(0.5)
    calls = mock_log()
    assert b["state"] == "ready"
    assert any(c["status"] == 429 for c in calls)
    assert b["spent_units"] == log_cost(calls) <= 80
    probs = check_candidates(b, d, 0, build_time=NOW0)
    assert not probs, probs
    check_citations(b, d, calls)


def test_post_seal_throttled_extract_after_slow_research(fresh):
    # POST-SEAL ADDITION (FIX 2 1 S2-F1, missed by the seal). Stage 2 "Rate limits": a call answered 429 may be
    # made again after a second; "Time a build spends waiting to make a call again after a 429 does not count
    # toward the 10 seconds". A slow research run followed by throttled extracts must still yield the exact
    # candidate set (§8 known exactly when the evidence supports; R1-2).
    t = fresh["ada"]
    d = "tarnwick-labs.test"
    mock_reset(0)
    mock_fault("nimble", ["research"], "delay", seconds=8)
    mock_fault("nimble", ["extract"], "throttle")
    assert create(t, d).status_code == 202
    b, _ = wait_done(t, d, timeout=90)
    time.sleep(0.5)
    calls = mock_log()
    assert b["state"] == "ready"
    assert any(c["method"] == "extract" and c["status"] == 429 for c in calls)
    probs = check_candidates(b, d, 0, build_time=NOW0)
    assert not probs, probs
    check_citations(b, d, calls)
    assert b["spent_units"] == log_cost(calls) <= 80
