"""Builds: citations, budget, provider failures and replacement during a build (§4, §8, §9, §10)."""

import re
import sys
import time
from pathlib import Path

from conftest import FIXTURE, create, key, login, wait_settled

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from app.support import supported_value  # noqa: E402

SAMPLE = ["corvid-security.test", "ashgrove-solar.test", "pemberton-analytics.test",
          "quillmate.test", "larkspur-health.test", "windrush-bakery.test",
          "halvorsen-robotics.test", "getferncliff-foods.test"]


def collapse(text):
    return re.sub(r"\s+", " ", text).strip()


def test_ready_builds_cite_served_supporting_prose(api, ada, mock):
    for domain in SAMPLE:
        create(api, ada, domain)
    served = {}
    bodies = [wait_settled(api, ada, d) for d in SAMPLE]
    for call in mock.calls():
        if call["method"] == "extract":
            for item in call.get("served") or []:
                served.setdefault(item["url"], []).append(collapse(item["text"]))
    for body in bodies:
        assert body["state"] == "ready"
        assert 0 < body["spent_units"] <= 80
        for name, field in body["fields"].items():
            assert (field["value"] is None) == (field["status"] == "unknown") == (not field["citations"])
            assert sum(c["selected"] for c in field["candidates"]) == (1 if field["candidates"] else 0)
            for candidate in field["candidates"]:
                assert any(candidate["excerpt"] in text for text in served[candidate["url"]])
                assert supported_value(candidate["excerpt"], name, body["domain"]) == candidate["value"]
                assert candidate["kind"] in ("own", "filing", "news", "aggregator")
                assert candidate["retrieved_at"] == body["researched_at"]
            for citation in field["citations"]:
                assert citation["provider"] == "nimble"
                assert 1 <= len(citation["excerpt"]) <= 500
                assert any(citation["excerpt"] in text for text in served[citation["url"]])
                assert supported_value(citation["excerpt"], name, body["domain"]) == field["value"]
    known = {b["domain"]: sum(f["status"] != "unknown" for f in b["fields"].values()) for b in bodies}
    assert known["corvid-security.test"] == 6 and known["getferncliff-foods.test"] == 0


def test_spent_units_match_provider_log_and_one_exact_domain_search(api, ada, mock):
    domain = "corvid-security.test"
    create(api, ada, domain)
    body = wait_settled(api, ada, domain)
    calls = mock.calls()
    assert body["spent_units"] == sum(c["cost"] for c in calls)
    exact = [c for c in calls if c["method"] == "search" and c["query"] == domain and c["status"] == 200]
    assert len(exact) == 1
    research = [c for c in calls if c["method"] == "research"]
    assert len(research) == 1 and domain in research[0]["query"]
    assert research[0]["fields"] == sorted(body["fields"])
    research_urls = {item["url"] for item in research[0]["served"] or []}
    rendered = {u for c in calls if c["method"] == "extract" for u in c["urls"]}
    assert research_urls <= rendered
    assert all(c["cost"] == 3 for c in calls if c["method"] == "extract")


def test_reads_make_no_provider_call(api, ada, mock):
    create(api, ada, "corvid-security.test")
    wait_settled(api, ada, "corvid-security.test")
    count = len(mock.calls())
    for _ in range(5):
        api.get("/dossiers/corvid-security.test", headers=ada)
        api.get("/dossiers", headers=ada)
        api.get("/health")
        api.get("/_test/export")
    assert len(mock.calls()) == count


def test_all_calls_refused_fails_build_and_keeps_fields(api, ada, mock):
    domain = "corvid-security.test"
    create(api, ada, domain)
    ready = wait_settled(api, ada, domain)
    mock.fault(["search", "extract", "research"], "error")
    started = time.monotonic()
    assert api.post(f"/dossiers/{domain}/refresh", headers={**ada, **key()}).status_code == 202
    failed = wait_settled(api, ada, domain)
    assert time.monotonic() - started < 10
    assert failed["state"] == "failed"
    assert failed["fields"] == ready["fields"] and failed["researched_at"] == ready["researched_at"]
    assert failed["spent_units"] == ready["spent_units"]


def test_first_build_failing_is_failed_and_unknown(api, ada, mock):
    mock.fault(["search", "extract", "research"], "error")
    create(api, ada, "quillmate.test")
    body = wait_settled(api, ada, "quillmate.test")
    assert body["state"] == "failed" and body["researched_at"] is None
    assert all(f["status"] == "unknown" for f in body["fields"].values())


def test_throttled_provider_still_builds(api, ada, mock):
    mock.fault(["search", "extract", "research"], "throttle")
    started = time.monotonic()
    create(api, ada, "corvid-security.test")
    body = wait_settled(api, ada, "corvid-security.test")
    assert time.monotonic() - started < 10
    assert body["state"] == "ready"
    assert sum(f["status"] != "unknown" for f in body["fields"].values()) == 6
    calls = mock.calls()
    assert body["spent_units"] == sum(c["cost"] for c in calls)
    exact = [c for c in calls if c["method"] == "search" and c["query"] == "corvid-security.test"
             and c["status"] == 200]
    assert len(exact) == 1


def test_reset_during_build_leaves_new_state_untouched(api, ada, mock):
    mock.fault(["research"], "delay", seconds=2)
    create(api, ada, "corvid-security.test")
    assert api.post("/_test/reset", json=FIXTURE).status_code == 204
    time.sleep(2.5)
    fresh = login(api)
    assert api.get("/dossiers", headers=fresh).json() == {"dossiers": [], "has_more": False}


def test_export_during_first_build_imports_failed(api, ada, mock):
    mock.fault(["research"], "delay", seconds=2)
    headers = {**ada, "Idempotency-Key": "mid"}
    first = api.post("/dossiers", headers=headers, json={"domain": "corvid-security.test"}).json()
    document = api.get("/_test/export").json()
    wait_settled(api, ada, "corvid-security.test")
    assert api.post("/_test/import", json=document).status_code == 204
    body = api.get("/dossiers/corvid-security.test", headers=ada).json()
    assert body["state"] == "failed" and body["spent_units"] == 0
    assert all(f["status"] == "unknown" for f in body["fields"].values())
    replay = api.post("/dossiers", headers=headers, json={"domain": "corvid-security.test"})
    assert replay.status_code == 200 and replay.json() == first


def test_refresh_while_building_starts_no_second_build(api, ada, mock):
    mock.fault(["research"], "delay", seconds=2)
    first = create(api, ada, "corvid-security.test")
    again = api.post("/dossiers/corvid-security.test/refresh", headers={**ada, **key()})
    assert again.status_code == 202 and again.json() == first
    wait_settled(api, ada, "corvid-security.test")
    assert sum(c["method"] == "research" for c in mock.calls()) == 1


def test_refresh_researches_again_and_accumulates(api, ada, mock):
    create(api, ada, "corvid-security.test")
    first = wait_settled(api, ada, "corvid-security.test")
    api.post("/_test/clock", json={"now": "2026-03-05T00:00:00+00:00"})
    api.post("/dossiers/corvid-security.test/refresh", headers={**ada, **key()})
    second = wait_settled(api, ada, "corvid-security.test")
    assert second["spent_units"] == 2 * first["spent_units"]
    assert second["researched_at"] == "2026-03-05T00:00:00+00:00"
    listed = api.get("/dossiers", headers=ada).json()["dossiers"][0]
    assert listed["legal_name"] == second["fields"]["legal_name"]["value"]


def test_throttled_render_after_slow_research_is_retried(api, ada, mock):
    mock.fault(["research"], "delay", seconds=7)
    mock.fault(["extract"], "throttle")
    create(api, ada, "corvid-security.test")
    body = wait_settled(api, ada, "corvid-security.test", timeout=40)
    assert body["state"] == "ready"
    assert sum(f["status"] != "unknown" for f in body["fields"].values()) == 6
    renders = [c for c in mock.calls() if c["method"] == "extract"]
    assert any(c["status"] == 429 for c in renders) and any(c["status"] == 200 for c in renders)
    assert body["spent_units"] == sum(c["cost"] for c in mock.calls())
