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
        if legacy["fields"][name]["value"] is not None:
            assert legacy["fields"][name]["value"] in [c["value"] for c in field["candidates"]]
    replay = api.post("/dossiers", headers=headers, json={"domain": "corvid-security.test"})
    assert replay.status_code == 200 and replay.json() == first
    assert api.post("/_test/import", json=api.get("/_test/export").json()).status_code == 204
    assert api.get("/dossiers/corvid-security.test", headers=auth).json() == body
    api.post("/dossiers/corvid-security.test/refresh", headers={**auth, **key()})
    refreshed = wait_settled(api, auth, "corvid-security.test")
    assert all(c["kind"] is not None for f in refreshed["fields"].values() for c in f["candidates"])
