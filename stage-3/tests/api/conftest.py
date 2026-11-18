import os
import time
import uuid

import httpx
import pytest

BASE = os.environ.get("DOSSIER_URL", "http://localhost:8000")
MOCK = os.environ.get("MOCK_URL", "http://localhost:8080")
ADMIN = {"X-Mock-Admin": os.environ.get("MOCK_ADMIN_TOKEN", "local-admin")}
NOW = "2026-03-01T09:00:00+00:00"
FIXTURE = {"now": NOW, "users": [
    {"id": "u_ada", "email": "ada@example.com", "password": "correct horse", "display_name": "Ada"},
    {"id": "u_bob", "email": "bob@example.com", "password": "correct horse", "display_name": "Bob"}]}


class Mock:
    def __init__(self) -> None:
        self.http = httpx.Client(base_url=MOCK, headers=ADMIN, timeout=10)

    def reset(self, epoch: int = 0) -> None:
        assert self.http.post("/_mock/reset", json={"epoch": epoch}).status_code == 204

    def fault(self, methods, mode, provider="nimble", **extra) -> None:
        body = {"provider": provider, "methods": methods, "mode": mode, **extra}
        assert self.http.post("/_mock/faults", json=body).status_code == 204

    def calls(self) -> list[dict]:
        return self.http.get("/_mock/log").json()["calls"]


@pytest.fixture
def mock():
    m = Mock()
    m.reset()
    yield m
    m.reset()


@pytest.fixture
def api(mock):
    client = httpx.Client(base_url=BASE, timeout=10)
    assert client.post("/_test/reset", json=FIXTURE).status_code == 204
    yield client
    client.close()


def login(api, email="ada@example.com"):
    r = api.post("/auth/login", json={"email": email, "password": "correct horse"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


@pytest.fixture
def ada(api):
    return login(api)


@pytest.fixture
def bob(api):
    return login(api, "bob@example.com")


def key():
    return {"Idempotency-Key": uuid.uuid4().hex}


def wait_settled(api, auth, domain, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        body = api.get(f"/dossiers/{domain}", headers=auth).json()
        if body["state"] != "building":
            return body
        time.sleep(0.2)
    raise AssertionError(f"{domain} still building")


def create(api, auth, domain):
    r = api.post("/dossiers", headers={**auth, **key()}, json={"domain": domain})
    assert r.status_code == 202, r.text
    return r.json()
