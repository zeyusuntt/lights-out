"""Runtime contract, auth, validation and idempotency (§3, §5, §6, §7)."""

import concurrent.futures as cf

import httpx

from conftest import BASE, FIXTURE, NOW, create, key, login, wait_settled


def error_code(response):
    return response.json()["error"]["code"]


def test_health_and_content_type(api):
    r = api.get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok"}
    assert r.headers["content-type"] == "application/json; charset=utf-8"


def test_unknown_route_has_error_body(api):
    r = api.get("/nope")
    assert r.status_code == 404 and error_code(r) == "not_found"


def test_reset_rejects_duplicate_email_and_changes_nothing(api, ada):
    bad = {"now": NOW, "users": [FIXTURE["users"][0], {**FIXTURE["users"][1], "email": "ada@example.com"}]}
    r = api.post("/_test/reset", json=bad)
    assert r.status_code == 422 and error_code(r) == "validation_failed"
    assert api.get("/dossiers", headers=ada).status_code == 200


def test_reset_validation(api):
    assert api.post("/_test/reset", json={"users": []}).status_code == 422
    assert api.post("/_test/reset", json={"now": "2026-03-01T09:00:00"}).status_code == 422
    assert api.post("/_test/reset", json={"now": 5}).status_code == 400
    assert api.post("/_test/reset", content=b"{").status_code == 400


def test_reset_invalidates_tokens(api, ada):
    assert api.post("/_test/reset", json=FIXTURE).status_code == 204
    assert api.get("/dossiers", headers=ada).status_code == 401


def test_clock_rules(api, ada):
    assert api.post("/_test/clock", json={"now": "2026-03-01T10:00:00+01:00"}).status_code == 204
    r = api.post("/_test/clock", json={"now": "2026-03-01T08:59:59+00:00"})
    assert r.status_code == 422 and error_code(r) == "validation_failed"
    assert api.post("/_test/clock", json={}).status_code == 422
    assert api.post("/_test/clock", json={"now": 1}).status_code == 400
    assert api.post("/_test/clock", json={"now": "2026-03-02T09:00:00Z"}).status_code == 204
    domain = "corvid-security.test"
    create(api, ada, domain)
    assert wait_settled(api, ada, domain)["researched_at"] == "2026-03-02T09:00:00+00:00"


def test_signup_and_login(api):
    r = api.post("/auth/signup", json={"email": "c@example.com", "password": "12345678", "display_name": "C"})
    assert r.status_code == 201 and set(r.json()) == {"user_id", "display_name", "token"}
    again = api.post("/auth/signup", json={"email": "c@example.com", "password": "12345678", "display_name": "C"})
    assert again.status_code == 409 and error_code(again) == "email_taken"
    seeded = api.post("/auth/login", json={"email": "ada@example.com", "password": "correct horse"})
    assert seeded.json()["user_id"] == "u_ada"
    wrong = api.post("/auth/login", json={"email": "ada@example.com", "password": "wrong horse"})
    assert wrong.status_code == 401 and error_code(wrong) == "unauthenticated"


def test_signup_validation(api):
    base = {"email": "d@example.com", "password": "12345678", "display_name": "D"}
    for change in ({"password": "1234567"}, {"email": "nope"}, {"display_name": ""},
                   {"display_name": "x" * 101}):
        assert api.post("/auth/signup", json={**base, **change}).status_code == 422
    assert api.post("/auth/signup", json={**base, "password": 12345678}).status_code == 400
    assert api.post("/auth/signup", json={"email": "d@example.com"}).status_code == 422
    assert api.post("/auth/signup", json={**base, "display_name": "x" * 100, "extra": 1}).status_code == 201


def test_auth_precedes_missing_key(api):
    r = api.post("/dossiers", json={"domain": "corvid-security.test"})
    assert r.status_code == 401 and error_code(r) == "unauthenticated"
    r = api.post("/dossiers", headers={"Authorization": "Bearer nope"}, json={"domain": "a.test"})
    assert r.status_code == 401


def test_idempotency_key_rules(api, ada):
    r = api.post("/dossiers", headers=ada, json={"domain": "corvid-security.test"})
    assert r.status_code == 400 and error_code(r) == "missing_idempotency_key"
    r = api.post("/dossiers", headers={**ada, "Idempotency-Key": ""}, json={"domain": "corvid-security.test"})
    assert error_code(r) == "missing_idempotency_key"
    r = api.post("/dossiers", headers={**ada, "Idempotency-Key": "k" * 256}, json={"domain": "corvid-security.test"})
    assert r.status_code == 422


def test_domain_validation(api, ada):
    for bad in ("https://acme.test", "acme.test/about", "acme", "-a.test", "a-.test",
                "a" * 64 + ".test", "a..test", "acme_robotics.test"):
        r = api.post("/dossiers", headers={**ada, **key()}, json={"domain": bad})
        assert r.status_code == 422, bad
    assert api.post("/dossiers", headers={**ada, **key()}, json={}).status_code == 422
    assert api.post("/dossiers", headers={**ada, **key()}, json={"domain": 3}).status_code == 400
    assert api.post("/dossiers", headers={**ada, **key()}, json=["x"]).status_code == 400
    assert api.get("/dossiers/not_valid", headers=ada).status_code == 422
    assert api.get("/dossiers/absent.test", headers=ada).status_code == 404


def test_replay_and_reuse(api, ada, bob):
    headers = {**ada, "Idempotency-Key": "same"}
    first = api.post("/dossiers", headers=headers, json={"domain": "Corvid-Security.test"})
    assert first.status_code == 202
    assert first.json()["domain"] == "corvid-security.test"
    wait_settled(api, ada, "corvid-security.test")
    replay = api.post("/dossiers", headers=headers, content=b'{ "x": 1, "domain":"Corvid-Security.test"}')
    assert replay.status_code == 200 and replay.json() == first.json()
    reuse = api.post("/dossiers", headers=headers, json={"domain": "corvid-security.test"})
    assert reuse.status_code == 409 and error_code(reuse) == "idempotency_key_reuse"
    invalid = api.post("/dossiers", headers=headers, json={"domain": 7})
    assert invalid.status_code == 409
    other_user = api.post("/dossiers", headers={**bob, "Idempotency-Key": "same"},
                          json={"domain": "corvid-security.test"})
    assert other_user.status_code == 200 and other_user.json()["state"] == "ready"
    other_path = api.post("/dossiers/corvid-security.test/refresh", headers=headers)
    assert other_path.status_code == 202


def test_failed_request_leaves_key_reusable(api, ada):
    headers = {**ada, "Idempotency-Key": "k-fail"}
    assert api.post("/dossiers/corvid-security.test/refresh", headers=headers).status_code == 404
    assert api.post("/dossiers", headers=headers, json={"domain": "bad"}).status_code == 422
    assert api.post("/dossiers", headers=headers, json={"domain": "corvid-security.test"}).status_code == 202
    wait_settled(api, ada, "corvid-security.test")
    assert api.post("/dossiers/corvid-security.test/refresh", headers=headers).status_code == 202


def test_refresh_ignores_body_and_replays(api, ada):
    create(api, ada, "corvid-security.test")
    headers = {**ada, "Idempotency-Key": "r1"}
    first = api.post("/dossiers/corvid-security.test/refresh", headers=headers, content=b"not json")
    assert first.status_code == 202 and first.json()["state"] == "building"
    replay = api.post("/dossiers/corvid-security.test/refresh", headers=headers, json={"a": 1})
    assert replay.status_code == 200 and replay.json() == first.json()


def test_concurrent_identical_requests_take_effect_once(api, ada, mock):
    headers = {**ada, "Idempotency-Key": "race"}
    with httpx.Client(base_url=BASE, timeout=10) as client, cf.ThreadPoolExecutor(20) as pool:
        responses = list(pool.map(lambda _: client.post(
            "/dossiers", headers=headers, json={"domain": "corvid-security.test"}), range(20)))
    statuses = sorted(r.status_code for r in responses)
    assert statuses == [200] * 19 + [202]
    assert len({r.text for r in responses}) == 1
    wait_settled(api, ada, "corvid-security.test")
    assert sum(c["method"] == "research" for c in mock.calls()) == 1


def test_concurrent_creates_with_distinct_keys_build_once(api, ada, bob, mock):
    variants = ["corvid-security.test", "WWW.corvid-security.test", "corvid-security.test.",
                " Corvid-Security.TEST "]
    with httpx.Client(base_url=BASE, timeout=10) as client, cf.ThreadPoolExecutor(40) as pool:
        responses = list(pool.map(lambda i: client.post(
            "/dossiers", headers={**(ada if i % 2 else bob), **key()},
            json={"domain": variants[i % 4]}), range(40)))
    assert sorted(r.status_code for r in responses).count(202) == 1
    assert len({r.json()["dossier_id"] for r in responses}) == 1
    wait_settled(api, ada, "corvid-security.test")
    assert sum(c["method"] == "research" for c in mock.calls()) == 1


def test_list_filter_order_and_paging(api, ada):
    for d in ("quillmate.test", "corvid-security.test", "ashgrove-solar.test"):
        create(api, ada, d)
    for d in ("quillmate.test", "corvid-security.test", "ashgrove-solar.test"):
        wait_settled(api, ada, d)
    listed = api.get("/dossiers", headers=ada).json()
    assert [d["domain"] for d in listed["dossiers"]] == [
        "ashgrove-solar.test", "corvid-security.test", "quillmate.test"]
    assert listed["has_more"] is False
    assert set(listed["dossiers"][0]) == {"dossier_id", "domain", "state", "legal_name",
                                          "researched_at", "spent_units"}
    page = api.get("/dossiers?limit=1&offset=1&zzz=1", headers=ada).json()
    assert [d["domain"] for d in page["dossiers"]] == ["corvid-security.test"] and page["has_more"]
    assert [d["domain"] for d in api.get("/dossiers?q=LTD", headers=ada).json()["dossiers"]] == ["quillmate.test"]
    assert len(api.get("/dossiers?q=", headers=ada).json()["dossiers"]) == 3
    for bad in ("0", "201", "1e9", "4.0", "+4", "", "-1", " 4"):
        assert api.get(f"/dossiers?limit={bad}", headers=ada).status_code == 422, bad
    for bad in ("-1", "1.0", "x"):
        assert api.get(f"/dossiers?offset={bad}", headers=ada).status_code == 422, bad
    assert api.get("/dossiers?offset=99", headers=ada).json() == {"dossiers": [], "has_more": False}


def test_export_import_round_trip(api, ada, mock):
    signup = api.post("/auth/signup", json={"email": "e@example.com", "password": "12345678",
                                            "display_name": "E"}).json()
    headers = {**ada, "Idempotency-Key": "exp"}
    first = api.post("/dossiers", headers=headers, json={"domain": "corvid-security.test"}).json()
    ready = wait_settled(api, ada, "corvid-security.test")
    exported = api.get("/_test/export")
    assert exported.status_code == 200
    document = exported.json()
    assert document["track"] == "dossier" and document["format_version"] == 1
    assert api.post("/_test/reset", json=FIXTURE).status_code == 204
    calls_before = len(mock.calls())
    assert api.post("/_test/import", json=document).status_code == 204
    assert api.post("/_test/import", json=document).status_code == 204
    assert api.get("/dossiers/corvid-security.test", headers=ada).json() == ready
    replay = api.post("/dossiers", headers=headers, json={"domain": "corvid-security.test"})
    assert replay.status_code == 200 and replay.json() == first
    assert api.get("/dossiers", headers={"Authorization": f"Bearer {signup['token']}"}).status_code == 200
    relogin = api.post("/auth/login", json={"email": "e@example.com", "password": "12345678"})
    assert relogin.status_code == 200 and relogin.json()["user_id"] == signup["user_id"]
    assert len(mock.calls()) == calls_before
    assert len(api.get("/dossiers", headers=ada).json()["dossiers"]) == 1


def test_import_rejects_bad_documents_without_change(api, ada):
    create(api, ada, "corvid-security.test")
    wait_settled(api, ada, "corvid-security.test")
    good = api.get("/_test/export").json()
    for bad in ({}, {**good, "track": "other"}, {**good, "format_version": 2},
                {**good, "state": {"users": 1}}, [1]):
        r = api.post("/_test/import", json=bad)
        assert r.status_code == 422, bad
    assert api.post("/_test/import", content=b"{oops").status_code == 400
    assert api.get("/dossiers/corvid-security.test", headers=ada).status_code == 200


def test_encoded_slash_in_path_domain_is_validated(api, ada):
    for raw in ("https%3A%2F%2Fvalid.test", "valid.test%2Fpath"):
        r = api.get(f"/dossiers/{raw}", headers=ada)
        assert r.status_code == 422 and error_code(r) == "validation_failed", raw
        r = api.post(f"/dossiers/{raw}/refresh", headers={**ada, **key()})
        assert r.status_code == 422 and error_code(r) == "validation_failed", raw
    assert api.get("/dossiers/a.test/extra", headers=ada).status_code == 404


def test_fixture_user_id_longer_than_64_is_rejected(api, ada):
    user = {**FIXTURE["users"][0]}
    assert api.post("/_test/reset", json={"now": NOW, "users": [{**user, "id": "u" * 65}]}).status_code == 422
    assert api.get("/dossiers", headers=ada).status_code == 200
    assert api.post("/_test/reset", json={"now": NOW, "users": [{**user, "id": "u" * 64}]}).status_code == 204
    assert login(api)
