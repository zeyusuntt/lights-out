"""Import of a stage-1 export (STAGE1_URL: the accepted stage-1 service on the same mock web)."""

import os

import httpx
import pytest

from conftest import FIXTURE, key, wait_settled

STAGE1 = os.environ.get("STAGE1_URL")
pytestmark = pytest.mark.skipif(not STAGE1, reason="stage-1 service not running")


def test_stage1_export_imports_with_candidates_tokens_and_replays(api, mock):
    old = httpx.Client(base_url=STAGE1, timeout=10)
    assert old.post("/_test/reset", json=FIXTURE).status_code == 204
    token = old.post("/auth/login", json={"email": "ada@example.com", "password": "correct horse"}).json()["token"]
    auth = {"Authorization": f"Bearer {token}"}
    headers = {**auth, "Idempotency-Key": "before-upgrade"}
    first = old.post("/dossiers", headers=headers, json={"domain": "corvid-security.test"}).json()
    legacy = wait_settled(old, auth, "corvid-security.test")
    document = old.get("/_test/export").json()
    calls = len(mock.calls())

    assert api.post("/_test/import", json=document).status_code == 204
    assert len(mock.calls()) == calls
    body = api.get("/dossiers/corvid-security.test", headers=auth).json()
    assert body["researched_at"] == legacy["researched_at"] and body["spent_units"] == legacy["spent_units"]
    for name, field in body["fields"].items():
        for candidate in field["candidates"]:
            assert candidate["kind"] is None and candidate["published_at"] is None
            assert candidate["retrieved_at"] == legacy["researched_at"]
        exported = {c["excerpt"] for f in legacy["fields"].values() for c in f["citations"]}
        assert all(c["excerpt"] in exported for c in field["candidates"])
        if name in legacy["fields"] and legacy["fields"][name]["value"] is not None:
            assert legacy["fields"][name]["value"] in [c["value"] for c in field["candidates"]]
    replay = api.post("/dossiers", headers=headers, json={"domain": "corvid-security.test"})
    assert replay.status_code == 200 and replay.json() == first
    assert api.post("/_test/import", json=api.get("/_test/export").json()).status_code == 204
    assert api.get("/dossiers/corvid-security.test", headers=auth).json() == body
    history = api.get("/dossiers/corvid-security.test/history", headers=auth).json()["fields"]
    assert all(e["type"] == "initial" and e["true_from"] is None for es in history.values() for e in es)
    assert history["executives"] == []
    api.post("/dossiers/corvid-security.test/refresh", headers={**auth, **key()})
    refreshed = wait_settled(api, auth, "corvid-security.test")
    assert all(c["kind"] is not None for f in refreshed["fields"].values() for c in f["candidates"])


STAGE2 = os.environ.get("STAGE2_URL")


@pytest.mark.skipif(not STAGE2, reason="stage-2 service not running")
def test_stage2_export_imports_as_one_ready_build(api, mock):
    old = httpx.Client(base_url=STAGE2, timeout=10)
    assert old.post("/_test/reset", json=FIXTURE).status_code == 204
    token = old.post("/auth/login", json={"email": "ada@example.com", "password": "correct horse"}).json()["token"]
    auth = {"Authorization": f"Bearer {token}"}
    old.post("/dossiers", headers={**auth, **key()}, json={"domain": "halvorsen-robotics.test"})
    legacy = wait_settled(old, auth, "halvorsen-robotics.test")
    document = old.get("/_test/export").json()
    calls = len(mock.calls())

    assert api.post("/_test/import", json=document).status_code == 204
    assert len(mock.calls()) == calls, mock.calls()[calls:]
    body = api.get("/dossiers/halvorsen-robotics.test", headers=auth).json()
    assert body["fields"]["executives"]["status"] == "unknown"
    for name, field in legacy["fields"].items():
        assert body["fields"][name]["value"] == field["value"]
        assert [c["url"] for c in body["fields"][name]["candidates"]] == [c["url"] for c in field["candidates"]]
        for c in body["fields"][name]["candidates"]:
            assert c["learned_at"] == c["retrieved_at"]
            assert c["true_from"] == (c["published_at"][:10] if c["published_at"] else None)
    history = api.get("/dossiers/halvorsen-robotics.test/history", headers=auth).json()["fields"]
    for name, field in legacy["fields"].items():
        expected = [] if field["value"] is None else [field["value"]]
        assert [e["value"] for e in history[name]] == expected
        assert all(e["type"] == "initial" and e["learned_at"] == legacy["researched_at"] for e in history[name])
    assert history["executives"] == []
    assert api.get("/changes", headers=auth).json()["changes"] == []
    as_of = api.get("/dossiers/halvorsen-robotics.test", params={"as_of": legacy["researched_at"]}, headers=auth).json()
    assert as_of["spent_units"] == legacy["spent_units"] and as_of["state"] == "ready"
    before = api.get("/dossiers/halvorsen-robotics.test", params={"as_of": "2026-02-01T00:00:00Z"}, headers=auth)
    assert before.status_code == 404
    api.post("/dossiers/halvorsen-robotics.test/refresh", headers={**auth, **key()})
    wait_settled(api, auth, "halvorsen-robotics.test")
    feed = api.get("/changes", headers=auth).json()["changes"]
    assert [c["field"] for c in feed] == ["executives"] and feed[0]["type"] == "change"
