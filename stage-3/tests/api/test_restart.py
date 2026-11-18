"""Abrupt stop and start of the service container (RESTART_CONTAINER names it)."""

import os
import subprocess
import time

import httpx
import pytest

from conftest import BASE, create, key, wait_settled

CONTAINER = os.environ.get("RESTART_CONTAINER")
pytestmark = pytest.mark.skipif(not CONTAINER, reason="no container to restart")


def kill_and_start():
    subprocess.run(["docker", "kill", CONTAINER], check=True, capture_output=True)
    subprocess.run(["docker", "start", CONTAINER], check=True, capture_output=True)
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            if httpx.get(f"{BASE}/health", timeout=2).status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.3)
    raise AssertionError("no health after restart")


def surfaces(api, auth, domain):
    return {
        "dossier": api.get(f"/dossiers/{domain}", headers=auth).json(),
        "as_of": api.get(f"/dossiers/{domain}", params={"as_of": "2030-01-01T00:00:00Z"}, headers=auth).json(),
        "values": api.get(f"/dossiers/{domain}/values?true_at=2026-01-01", headers=auth).json(),
        "history": api.get(f"/dossiers/{domain}/history", headers=auth).json(),
        "list": api.get("/dossiers", headers=auth).json(),
        "changes": api.get("/changes", headers=auth).json(),
    }


def test_idle_restart_keeps_everything(api, ada, mock):
    api.post("/_test/clock", json={"now": "2026-03-01T11:30:00+02:00"})
    signup = api.post("/auth/signup", json={"email": "r@example.com", "password": "12345678", "display_name": "R"}).json()
    headers = {**ada, "Idempotency-Key": "kept"}
    first = api.post("/dossiers", headers=headers, json={"domain": "corvid-security.test"}).json()
    wait_settled(api, ada, "corvid-security.test")
    before = surfaces(api, ada, "corvid-security.test")
    calls = len(mock.calls())
    kill_and_start()
    assert surfaces(api, ada, "corvid-security.test") == before
    assert api.get("/dossiers", headers={"Authorization": f"Bearer {signup['token']}"}).status_code == 200
    assert api.post("/auth/login", json={"email": "r@example.com", "password": "12345678"}).status_code == 200
    replay = api.post("/dossiers", headers=headers, json={"domain": "corvid-security.test"})
    assert replay.status_code == 200 and replay.json() == first
    assert len(mock.calls()) == calls
    create(api, ada, "quillmate.test")
    assert wait_settled(api, ada, "quillmate.test")["researched_at"] == "2026-03-01T11:30:00+02:00"


def test_restart_during_a_build_rolls_it_back(api, ada, mock):
    create(api, ada, "corvid-security.test")
    ready = wait_settled(api, ada, "corvid-security.test")
    mock.fault(["research"], "delay", seconds=5)
    assert api.post("/dossiers/corvid-security.test/refresh", headers={**ada, **key()}).status_code == 202
    time.sleep(0.5)
    kill_and_start()
    after = api.get("/dossiers/corvid-security.test", headers=ada).json()
    assert after["state"] == "ready" and after["fields"] == ready["fields"]
    assert after["spent_units"] == ready["spent_units"]
    assert api.post("/dossiers/corvid-security.test/refresh", headers={**ada, **key()}).status_code == 202
    time.sleep(5)
