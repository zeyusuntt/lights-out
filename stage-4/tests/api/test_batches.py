"""Batches under one shared budget (stage 4)."""

import concurrent.futures as cf
import time

import httpx

from conftest import BASE, create, key, wait_settled


def wait_batch(api, auth, batch_id, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        body = api.get(f"/batches/{batch_id}", headers=auth).json()
        if body["state"] == "done":
            return body
        time.sleep(0.2)
    raise AssertionError("batch still running")


def test_batch_validation(api, ada):
    def post(body):
        return api.post("/batches", headers={**ada, **key()}, json=body)
    good = {"domains": ["corvid-security.test"], "budget_units": 10}
    for change in ({"domains": []}, {"domains": ["x"] * 51}, {"domains": ["https://a.test"]},
                   {"domains": ["a.test", "WWW.A.test"]}, {"budget_units": 0}, {"budget_units": 100001},
                   {"budget_units": 1.5}, {"budget_units": "1"}, {"budget_units": True}, {"budget_units": 1.0}):
        assert post({**good, **change}).status_code == 422, change
    assert post({"budget_units": 10}).status_code == 422
    assert post({"domains": "a.test", "budget_units": 10}).status_code == 400
    assert api.post("/batches", json=good).status_code == 401
    assert api.post("/batches", headers=ada, json=good).status_code == 400
    assert api.get("/dossiers", headers=ada).json()["dossiers"] == []


def test_batch_spends_within_budget_and_reports(api, ada, bob, mock):
    create(api, ada, "quillmate.test")
    wait_settled(api, ada, "quillmate.test")
    headers = {**ada, "Idempotency-Key": "batch-1"}
    body = {"domains": ["Corvid-Security.test", "quillmate.test", "halvorsen-robotics.test"], "budget_units": 70}
    first = api.post("/batches", headers=headers, json=body)
    assert first.status_code == 202
    data = first.json()
    assert data["state"] == "running" and data["budget_units"] == 70
    assert [d["domain"] for d in data["dossiers"]] == ["corvid-security.test", "quillmate.test", "halvorsen-robotics.test"]
    assert data["dossiers"][1]["state"] == "ready"
    done = wait_batch(api, ada, data["batch_id"])
    assert 0 < done["spent_units"] <= 70
    built = [api.get(f"/dossiers/{d}", headers=ada).json() for d in ("corvid-security.test", "halvorsen-robotics.test")]
    assert done["spent_units"] == sum(b["spent_units"] for b in built)
    assert all(b["state"] in ("ready", "failed") for b in built)
    replay = api.post("/batches", headers=headers, json=body)
    assert replay.status_code == 200 and replay.json() == data
    assert api.get(f"/batches/{data['batch_id']}", headers=bob).status_code == 404
    assert api.get("/batches/b_999", headers=ada).status_code == 404


def test_tiny_budget_latches_and_builds_complete(api, ada, mock):
    data = api.post("/batches", headers={**ada, **key()},
                    json={"domains": ["corvid-security.test", "halvorsen-robotics.test"], "budget_units": 5}).json()
    done = wait_batch(api, ada, data["batch_id"])
    assert done["spent_units"] <= 5
    assert sum(c["cost"] for c in mock.calls()) <= 5


def test_existing_dossiers_cost_the_batch_nothing(api, ada, mock):
    create(api, ada, "corvid-security.test")
    wait_settled(api, ada, "corvid-security.test")
    calls = len(mock.calls())
    data = api.post("/batches", headers={**ada, **key()},
                    json={"domains": ["corvid-security.test"], "budget_units": 100}).json()
    assert data["state"] == "done" and data["spent_units"] == 0
    assert len(mock.calls()) == calls


def test_concurrent_identical_batches_take_effect_once(api, ada, mock):
    headers = {**ada, "Idempotency-Key": "race"}
    body = {"domains": ["corvid-security.test"], "budget_units": 80}
    with httpx.Client(base_url=BASE, timeout=10) as client, cf.ThreadPoolExecutor(10) as pool:
        responses = list(pool.map(lambda _: client.post("/batches", headers=headers, json=body), range(10)))
    assert sorted(r.status_code for r in responses) == [200] * 9 + [202]
    assert len({r.text for r in responses}) == 1
    wait_batch(api, ada, responses[0].json()["batch_id"])
    assert sum(c["method"] == "research" for c in mock.calls()) == 1


def test_native_export_import_keeps_batches(api, ada, bob, mock):
    headers = {**ada, "Idempotency-Key": "kept-batch"}
    body = {"domains": ["corvid-security.test"], "budget_units": 80}
    first = api.post("/batches", headers=headers, json=body).json()
    done = wait_batch(api, ada, first["batch_id"])
    document = api.get("/_test/export").json()
    calls = len(mock.calls())
    assert api.post("/_test/import", json=document).status_code == 204
    assert api.get(f"/batches/{first['batch_id']}", headers=ada).json() == done
    assert api.get(f"/batches/{first['batch_id']}", headers=bob).status_code == 404
    replay = api.post("/batches", headers=headers, json=body)
    assert replay.status_code == 200 and replay.json() == first
    assert len(mock.calls()) == calls
