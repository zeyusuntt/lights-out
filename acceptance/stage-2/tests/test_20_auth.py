"""§6 authentication."""
import concurrent.futures as cf
import json

import pytest

from conftest import (PW, assert_err, call, create, fresh, get, j, newkey, refresh)


def signup(email, pw=PW, name="Ada"):
    return call("POST", "/auth/signup", body={"email": email, "password": pw, "display_name": name})


def test_signup_and_login_shape(fresh):
    # §6 "POST /auth/signup -> 201 {user_id, display_name, token}"; "POST /auth/login -> 200 {...}"
    r = signup("new@example.com", name="Newt")
    assert r.status_code == 201, r.text
    b = j(r)
    assert isinstance(b["user_id"], str) and 0 < len(b["user_id"]) <= 64
    assert b["display_name"] == "Newt" and isinstance(b["token"], str) and b["token"]
    r = call("POST", "/auth/login", body={"email": "new@example.com", "password": PW})
    assert r.status_code == 200
    b2 = j(r)
    assert b2["user_id"] == b["user_id"] and b2["display_name"] == "Newt"
    # §6 "An account may have multiple valid tokens and concurrent sessions."
    for t in (b["token"], b2["token"]):
        assert call("GET", "/dossiers", token=t).status_code == 200


def test_email_taken(fresh):
    # §6 "Email already registered | 409 email_taken"
    assert_err(signup("ada@example.com"), 409, "email_taken")
    assert signup("c@example.com").status_code == 201
    assert_err(signup("c@example.com"), 409, "email_taken")


def test_concurrent_signups_same_email(fresh):
    # §11 "Concurrent requests must produce the same results as executing them one at a time"
    with cf.ThreadPoolExecutor(20) as ex:
        rs = list(ex.map(lambda _: signup("race@example.com"), range(20)))
    codes = sorted(r.status_code for r in rs)
    assert codes.count(201) == 1 and codes.count(409) == 19, codes


@pytest.mark.parametrize("pw,ok", [("1234567", False), ("", False), ("12345678", True)])
def test_password_length(fresh, pw, ok):
    # §6 "Password shorter than 8 characters | 422 validation_failed"
    r = signup(f"p{len(pw)}@example.com", pw=pw)
    if ok:
        assert r.status_code == 201
    else:
        assert_err(r, 422, "validation_failed")


@pytest.mark.parametrize("email", ["plain", "a@", "@example.com", "", "a b"])
def test_email_format(fresh, email):
    # §6 "email not of the form local@domain | 422 validation_failed"
    assert_err(signup(email), 422, "validation_failed")


@pytest.mark.parametrize("name,ok", [("", False), ("x" * 101, False), ("x" * 100, True), ("Å", True)])
def test_display_name_bounds(fresh, name, ok):
    # §6 "display_name empty or longer than 100 characters | 422 validation_failed"
    r = signup(f"n{len(name)}{ok}@example.com", name=name)
    if ok:
        assert r.status_code == 201 and j(r)["display_name"] == name
    else:
        assert_err(r, 422, "validation_failed")


def test_signup_missing_and_wrong_types(fresh):
    # §5 422 "A required field ... is missing"; 400 "a field of the wrong JSON type"; 400 "Unparseable body"
    assert_err(call("POST", "/auth/signup", body={"password": PW, "display_name": "A"}),
               422, "validation_failed")
    assert_err(call("POST", "/auth/signup", body={"email": 5, "password": PW, "display_name": "A"}),
               400, "malformed_request")
    assert_err(call("POST", "/auth/signup", body={"email": "q@example.com", "password": 12345678,
                                                  "display_name": "A"}), 400, "malformed_request")
    assert_err(call("POST", "/auth/signup", raw=b'{"email": '), 400, "malformed_request")
    assert_err(call("POST", "/auth/login", raw=b"[1,2"), 400, "malformed_request")
    assert_err(call("POST", "/auth/login", body={"email": "ada@example.com"}), 422, "validation_failed")


def test_login_failures(fresh):
    # §6 "Wrong password or unknown email on login | 401 unauthenticated"
    assert_err(call("POST", "/auth/login", body={"email": "ada@example.com", "password": "wrong pass"}),
               401, "unauthenticated")
    assert_err(call("POST", "/auth/login", body={"email": "ghost@example.com", "password": PW}),
               401, "unauthenticated")


@pytest.mark.parametrize("hdr", [None, "Bearer", "Bearer nope-token", "Basic YTpi", "nope"])
def test_bearer_required_everywhere(fresh, hdr):
    # §6 "Every other endpoint requires a bearer token ... lacks a valid token is 401 unauthenticated,
    # even when it also lacks a required Idempotency-Key."
    h = {} if hdr is None else {"Authorization": hdr}
    for m, p, body, key in (("GET", "/dossiers", None, None),
                            ("GET", "/dossiers/acme-robotics.test", None, None),
                            ("POST", "/dossiers", {"domain": "acme-robotics.test"}, None),
                            ("POST", "/dossiers", {"domain": "acme-robotics.test"}, newkey()),
                            ("POST", "/dossiers/acme-robotics.test/refresh", None, None),
                            ("POST", "/dossiers/acme-robotics.test/refresh", None, newkey())):
        r = call(m, p, headers=h, body=body, key=key)
        assert_err(r, 401, "unauthenticated")


def test_tokens_do_not_expire_with_clock(fresh):
    # §6 "Tokens do not expire."
    from conftest import set_clock
    assert set_clock("2099-01-01T00:00:00+00:00").status_code == 204
    assert call("GET", "/dossiers", token=fresh["ada"]).status_code == 200


def test_passwords_not_stored_in_plaintext(fresh):
    # §6 "Plaintext password storage is not permitted." Checked through the state export (§10).
    assert signup("plain@example.com", pw="zebra-unique-pw-9").status_code == 201
    r = call("GET", "/_test/export", timeout=10)
    assert r.status_code == 200
    s = json.dumps(j(r))
    assert "zebra-unique-pw-9" not in s
    assert "correct horse" not in s
