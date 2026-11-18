"""§4 Domains: normalisation and validation, on bodies and paths."""
import pytest

from conftest import assert_err, call, create, fresh, get, j, newkey, refresh, wait_done

D = "tarnwick-labs.test"


@pytest.mark.parametrize("bad", [
    "tarnwick", "http://tarnwick-labs.test", "https://tarnwick-labs.test/", "tarnwick-labs.test/about",
    "-tarnwick.test", "tarnwick-.test", "tarnwick..test", ".tarnwick.test", "tarn_wick.test",
    "tarn wick.test", "a" * 64 + ".test", ".".join(["a" * 50] * 5) + ".tt", "", "   ", "www.",
    "tarnwick-labs.test..", "tarnwick-labs.test:8080", "ümlaut.test", "user@tarnwick-labs.test",
    "www.test",
])
def test_invalid_domain_body_422(fresh, bad):
    # §4 "The normalised domain must then be a valid host name ... Anything else, including a URL with
    # a scheme or a path, is 422 validation_failed." §8 POST /dossiers "domain invalid after normalisation | 422"
    assert_err(create(fresh["ada"], bad), 422, "validation_failed")


def test_domain_missing_or_wrong_type(fresh):
    # §8 "domain missing | 422 validation_failed"; §5 400 "a field of the wrong JSON type"
    t = fresh["ada"]
    assert_err(call("POST", "/dossiers", token=t, key=newkey(), body={}), 422, "validation_failed")
    assert_err(call("POST", "/dossiers", token=t, key=newkey(), body={"domain": 7}), 400,
               "malformed_request")
    assert_err(call("POST", "/dossiers", token=t, key=newkey(), body={"domain": ["a.test"]}), 400,
               "malformed_request")
    assert_err(call("POST", "/dossiers", token=t, key=newkey(), body=["a.test"]), 400,
               "malformed_request")
    assert_err(call("POST", "/dossiers", token=t, key=newkey(), raw=b'{"domain":'), 400,
               "malformed_request")


@pytest.mark.parametrize("ok", ["a.b", "x" * 63 + ".test", ".".join(["a" * 62] * 4) + ".t",
                                "0-9.test", "www.www.tarnwick-labs.test"])
def test_valid_edge_domains_accepted(fresh, ok):
    # §4 "two or more labels ..., each label 1 to 63 characters ..., and 253 characters or fewer in total."
    r = create(fresh["ada"], ok)
    assert r.status_code == 202, (ok, r.text)
    want = ok[4:] if ok.startswith("www.") else ok
    assert j(r)["domain"] == want
    assert len(want) <= 253
    # Amendment: a path domain is normalised again (one more www. removed), so wait via the list.
    import time
    for _ in range(75):
        items = {i["domain"]: i for i in j(call("GET", "/dossiers", token=fresh["ada"]))["dossiers"]}
        if items[want]["state"] != "building":
            break
        time.sleep(0.2)


def test_normalisation_same_dossier(fresh):
    # §4 "Acme-Robotics.TEST., www.acme-robotics.test and acme-robotics.test name the same company
    # and the same dossier. Responses always carry the normalised domain."
    t = fresh["ada"]
    r1 = create(t, "  Tarnwick-Labs.TEST. ")
    assert r1.status_code == 202, r1.text
    b1 = j(r1)
    assert b1["domain"] == D and b1["state"] == "building"
    r2 = create(t, "WWW.tarnwick-labs.test")
    assert r2.status_code == 200, r2.text
    assert j(r2)["dossier_id"] == b1["dossier_id"] and j(r2)["domain"] == D
    for p in ("TARNWICK-LABS.TEST", "www.tarnwick-labs.test", "Tarnwick-Labs.test."):
        r = get(t, p)
        assert r.status_code == 200 and j(r)["domain"] == D and j(r)["dossier_id"] == b1["dossier_id"]
    wait_done(t, D)
    r = refresh(t, "Www.Tarnwick-Labs.Test.")
    assert r.status_code == 202 and j(r)["domain"] == D
    wait_done(t, D)


def test_invalid_path_domain(fresh):
    # §4 "Every domain the API takes, in a body or a path, is first normalised ... Anything else ... 422"
    t = fresh["ada"]
    assert_err(get(t, "nodot"), 422, "validation_failed")
    assert_err(get(t, "bad_label.test"), 422, "validation_failed")
    assert_err(refresh(t, "nodot"), 422, "validation_failed")


def test_unknown_dossier_404(fresh):
    # §8 "No dossier for it is 404 not_found"; refresh "No dossier for the domain | 404 not_found"
    t = fresh["ada"]
    assert_err(get(t, "nobody-here.test"), 404, "not_found")
    assert_err(refresh(t, "nobody-here.test"), 404, "not_found")


def test_post_seal_254_char_domain_rejected(fresh):
    # POST-SEAL ADDITION (fault survivor). §4 "and 253 characters or fewer in total"
    d = ".".join(["a" * 62] * 4) + ".tt"
    assert len(d) == 254
    assert_err(create(fresh["ada"], d), 422, "validation_failed")


@pytest.mark.parametrize("raw", ["https%3A%2F%2Ftarnwick-labs.test", "tarnwick-labs.test%2Fabout",
                                 "tarnwick-labs.test%2F"])
def test_post_seal_encoded_slash_path_domain_422(fresh, raw):
    # POST-SEAL ADDITION (FIX 1 1 F1, missed by the seal). §4 "Every domain the API takes, in a body or a
    # path, is first normalised ... Anything else, including a URL with a scheme or a path, is 422";
    # RULING R1-5 path domains are validated before lookup.
    t = fresh["ada"]
    assert create(t, "tarnwick-labs.test").status_code == 202
    assert_err(call("GET", f"/dossiers/{raw}", token=t), 422, "validation_failed")
    assert_err(call("POST", f"/dossiers/{raw}/refresh", token=t, key=newkey()), 422, "validation_failed")
    wait_done(t, "tarnwick-labs.test")
