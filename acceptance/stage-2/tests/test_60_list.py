"""§8 GET /dossiers, §5 shared ranges for limit and offset."""
import pytest

from conftest import assert_err, call, create, fresh, get, j, wait_done

DOMS = ["tarnwick-labs.test", "quillon-dynamics.test", "nullmark-systems.test", "a.b", "zz-top.test"]


@pytest.fixture
def populated(fresh):
    t = fresh["ada"]
    for d in DOMS:
        assert create(t, d).status_code == 202
    for d in DOMS:
        wait_done(t, d, timeout=30)
    return t


def lst(t, **params):
    r = call("GET", "/dossiers", token=t, params=params)
    return r


def test_order_shape_and_defaults(populated):
    # §8 "Dossiers are ordered by domain ascending." item shape; "legal_name is the value of the
    # dossier's legal_name field, or null."
    t = populated
    r = lst(t)
    assert r.status_code == 200
    b = j(r)
    items = b["dossiers"]
    assert [i["domain"] for i in items] == sorted(DOMS)
    assert b["has_more"] is False
    for i in items:
        full = j(get(t, i["domain"]))
        assert i == {"dossier_id": full["dossier_id"], "domain": full["domain"], "state": full["state"],
                     "legal_name": full["fields"]["legal_name"]["value"],
                     "researched_at": full["researched_at"], "spent_units": full["spent_units"]}
    byd = {i["domain"]: i for i in items}
    assert byd["tarnwick-labs.test"]["legal_name"] == "Tarnwick Labs S.A.S."
    assert byd["nullmark-systems.test"]["legal_name"] is None


def test_q_filters_domain_and_legal_name_case_insensitive(populated):
    # §8 "only dossiers whose domain or legal_name contains q, compared case-insensitively"; "An empty q
    # lists every dossier."
    t = populated
    names = lambda **p: [i["domain"] for i in j(lst(t, **p))["dossiers"]]
    assert names(q="TARN") == ["tarnwick-labs.test"]
    assert names(q="s.a.s") == ["tarnwick-labs.test"]          # legal_name only
    assert names(q="gmbh") == ["quillon-dynamics.test"]        # legal_name only
    assert names(q=".test") == sorted(d for d in DOMS if ".test" in d)
    assert names(q="") == sorted(DOMS)
    assert names(q="no-such-thing") == []


def test_pagination(populated):
    # §8 "limit defaults to 50, range 1 to 200. offset defaults to 0. has_more is true when items exist
    # beyond the last one returned."
    t = populated
    s = sorted(DOMS)
    b = j(lst(t, limit="2"))
    assert [i["domain"] for i in b["dossiers"]] == s[:2] and b["has_more"] is True
    b = j(lst(t, limit="2", offset="2"))
    assert [i["domain"] for i in b["dossiers"]] == s[2:4] and b["has_more"] is True
    b = j(lst(t, limit="2", offset="4"))
    assert [i["domain"] for i in b["dossiers"]] == s[4:] and b["has_more"] is False
    b = j(lst(t, limit="5"))
    assert len(b["dossiers"]) == 5 and b["has_more"] is False
    b = j(lst(t, offset="5"))
    assert b["dossiers"] == [] and b["has_more"] is False
    b = j(lst(t, offset="1000"))
    assert b["dossiers"] == [] and b["has_more"] is False
    assert lst(t, limit="200").status_code == 200
    assert lst(t, limit="1").status_code == 200
    b = j(lst(t, q="test", limit="1", offset="1"))
    assert len(b["dossiers"]) == 1 and b["has_more"] is True


@pytest.mark.parametrize("name,val", [
    ("limit", "0"), ("limit", "201"), ("limit", "-1"), ("limit", "1e9"), ("limit", "4.0"),
    ("limit", "+4"), ("limit", "abc"), ("limit", ""), ("limit", " 4"), ("offset", "-1"),
    ("offset", "1e9"), ("offset", "4.0"), ("offset", "+4"), ("offset", "x"), ("offset", ""),
])
def test_bad_limit_offset(fresh, name, val):
    # §5 "An integer-valued query parameter is written as plain decimal digits: 1e9, 4.0 and +4 are 422
    # validation_failed"; "limit | integer 1 to 200"; "offset | integer 0 or more"
    assert_err(lst(fresh["ada"], **{name: val}), 422, "validation_failed")


def test_list_empty_after_reset(fresh):
    # §3.3 "no dossiers"
    b = j(lst(fresh["ada"]))
    assert b == {"dossiers": [], "has_more": False}
