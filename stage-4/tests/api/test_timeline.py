"""History, feed, as_of and values across refreshes (stage 3)."""

import httpx

from conftest import ADMIN, MOCK, create, key, wait_settled

T1, T2 = "2026-03-01T09:00:00+00:00", "2026-04-01T09:00:00+00:00"
DOMAIN = "halvorsen-robotics.test"


def epoch(n):
    assert httpx.post(f"{MOCK}/_mock/epoch", json={"epoch": n}, headers=ADMIN).status_code == 204


def values_of(body):
    return {name: f["value"] for name, f in body["fields"].items()}


def two_builds(api, auth):
    create(api, auth, DOMAIN)
    first = wait_settled(api, auth, DOMAIN)
    epoch(1)
    api.post("/_test/clock", json={"now": T2})
    api.post(f"/dossiers/{DOMAIN}/refresh", headers={**auth, **key()})
    second = wait_settled(api, auth, DOMAIN)
    return first, second


def test_history_and_feed_follow_selected_values(api, ada, mock):
    first, second = two_builds(api, ada)
    history = api.get(f"/dossiers/{DOMAIN}/history", headers=ada).json()
    assert list(history["fields"]) == list(first["fields"])
    feed = api.get("/changes", headers=ada).json()
    before, after = values_of(first), values_of(second)
    changed = [name for name in first["fields"] if before[name] != after[name]]
    assert [c["field"] for c in feed["changes"]] == changed
    for c in feed["changes"]:
        assert (c["from"], c["to"], c["learned_at"]) == (before[c["field"]], after[c["field"]], T2)
        assert c["type"] in ("change", "correction") and c["domain"] == DOMAIN
        assert c["true_from"] == second["fields"][c["field"]]["true_from"]
    for name, entries in history["fields"].items():
        if before[name] is not None:
            assert entries[0]["type"] == "initial" and entries[0]["learned_at"] == first["researched_at"]
            assert entries[0]["value"] == before[name]
        assert len(entries) == (before[name] is not None) + (name in changed)
        field = second["fields"][name]
        assert field["learned_at"] == (entries[-1]["learned_at"] if field["value"] is not None else None)
    seqs = [c["seq"] for c in feed["changes"]]
    assert seqs == sorted(set(seqs)) and all(s > 0 for s in seqs)
    if seqs:
        rest = api.get(f"/changes?since={seqs[0]}&limit=1", headers=ada).json()
        assert [c["seq"] for c in rest["changes"]] == seqs[1:2] and rest["has_more"] == (len(seqs) > 2)


def test_as_of_answers_with_the_earlier_build(api, ada, mock):
    first, second = two_builds(api, ada)
    old = api.get(f"/dossiers/{DOMAIN}", params={"as_of": "2026-03-15T00:00:00+01:00"}, headers=ada).json()
    assert old["state"] == "ready" and old["researched_at"] == first["researched_at"]
    assert values_of(old) == values_of(first) and old["spent_units"] == first["spent_units"]
    now = api.get(f"/dossiers/{DOMAIN}", params={"as_of": T2}, headers=ada).json()
    assert values_of(now) == values_of(second) and now["spent_units"] == second["spent_units"]
    assert api.get(f"/dossiers/{DOMAIN}?as_of=2026-02-01T00:00:00Z", headers=ada).status_code == 404
    assert api.get(f"/dossiers/{DOMAIN}?as_of=2026-03-15", headers=ada).status_code == 422
    assert api.get(f"/dossiers/absent.test?as_of=2026-03-15T00:00:00Z", headers=ada).status_code == 404


def test_values_by_true_date(api, ada, mock):
    two_builds(api, ada)
    body = api.get(f"/dossiers/{DOMAIN}/values?true_at=2030-01-01", headers=ada).json()
    assert body["domain"] == DOMAIN and body["true_at"] == "2030-01-01" and len(body["fields"]) == 8
    for field in body["fields"].values():
        assert set(field) == {"value", "true_from", "citations"}
        assert (field["value"] is None) == (field["citations"] == [])
        if field["true_from"]:
            assert field["true_from"] <= "2030-01-01"
    early = api.get(f"/dossiers/{DOMAIN}/values?true_at=1900-01-01", headers=ada).json()
    assert all(f["value"] is None for f in early["fields"].values())
    for bad in ("", "2025-1-01", "2025-02-30", "soon"):
        assert api.get(f"/dossiers/{DOMAIN}/values?true_at={bad}", headers=ada).status_code == 422
    assert api.get(f"/dossiers/{DOMAIN}/values", headers=ada).status_code == 422
    assert api.get(f"/dossiers/{DOMAIN}/values?true_at=2025-01-01&as_of=2026-01-01T00:00:00Z", headers=ada).status_code == 404


def test_changes_validation_and_auth(api, ada):
    assert api.get("/changes").status_code == 401
    for bad in ("since=-1", "since=1.0", "limit=0", "limit=201", "since=+1"):
        assert api.get(f"/changes?{bad}", headers=ada).status_code == 422, bad
    assert api.get("/changes", headers=ada).json() == {"changes": [], "has_more": False}


def test_same_selection_adds_nothing(api, ada, mock):
    create(api, ada, DOMAIN)
    wait_settled(api, ada, DOMAIN)
    api.post(f"/dossiers/{DOMAIN}/refresh", headers={**ada, **key()})
    wait_settled(api, ada, DOMAIN)
    assert api.get("/changes", headers=ada).json()["changes"] == []
    history = api.get(f"/dossiers/{DOMAIN}/history", headers=ada).json()
    assert all(len(entries) <= 1 for entries in history["fields"].values())
