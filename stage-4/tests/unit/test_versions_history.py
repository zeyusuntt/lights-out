from datetime import datetime, timezone

from app.builds import Build, Version, holding_on
from app.candidates import Candidate, field_view


def executives_view(cands, learned):
    return field_view("executives", cands, learned)
from app.dossier import Dossier, transition_type

T1, T2, T3 = "2026-03-01T09:00:00+00:00", "2026-03-02T09:00:00+00:00", "2026-03-03T09:00:00+00:00"


def cand(value, url="https://acme.test/a", true_from=None, title=None, kind="own"):
    return Candidate(value, url, f"x {value}", "nimble", kind, None, T1, true_from, title)


def version(url, true_from, field="ceo", value=None):
    return Version(url, true_from, {field: [cand(value, url, true_from)]} if value else {})


def test_versions_replace_and_end_by_arrival_order():
    jan, mar, feb = (version("u", d, value=v) for d, v in
                     (("2025-01-01", "Jan"), ("2025-03-01", "Mar"), ("2025-02-01", "Feb")))
    held = lambda day, vs: [v.candidates["ceo"][0].value for v in holding_on(vs, day)]
    assert held("2025-03-15", [jan, mar]) == ["Mar"]
    assert held("2025-03-15", [jan, mar, feb]) == ["Feb"]
    assert held("2025-01-15", [jan, mar, feb]) == ["Jan"]
    assert held("2024-12-31", [jan, mar, feb]) == []


def test_empty_version_ends_and_undated_version_wipes():
    jan = version("u", "2025-01-01", value="Jan")
    empty_apr = Version("u", "2025-04-01", {})
    values = lambda vs, day: [c.value for v in holding_on(vs, day) for c in v.candidates.get("ceo", [])]
    assert values([jan, empty_apr], "2025-05-01") == []
    assert values([jan, empty_apr], "2025-02-01") == ["Jan"]
    assert values([jan, Version("u", None, {})], "2025-02-01") == []
    other = version("v", "2024-01-01", value="Other")
    assert values([other, jan, empty_apr], "2025-05-01") == ["Other"]


def test_executives_members_status_and_true_from():
    view = executives_view([cand("Ana Silva", title="cfo", true_from="2025-09-01"),
                            cand("Ben Okafor", "https://b.test/", "2025-01-01", "cto", "aggregator"),
                            cand("Cy Dee", "https://c.test/", None, "cto", "news")], lambda *_: None)
    assert view["value"] == [{"title": "cfo", "name": "Ana Silva"}, {"title": "cto", "name": "Cy Dee"}]
    assert view["status"] == "contested" and view["true_from"] is None
    assert [c["selected"] for c in view["candidates"]] == [True, True, False]
    assert [c["title"] for c in view["candidates"]] == ["cfo", "cto", "cto"]


def test_executive_correction_counts_only_differing_titles():
    def ex(members):
        return executives_view([cand(n, title=t, true_from=d) for t, n, d in members], lambda *_: None)
    old = ex([("cfo", "Ana", "2025-05-01"), ("cto", "Ben", "2025-01-01")])
    new = ex([("cfo", "Ava", "2025-04-01"), ("cto", "Ben", "2025-06-01")])
    assert transition_type("executives", old, new) == "correction"
    added = ex([("cfo", "Ava", "2025-04-01"), ("coo", "Bo", "2025-04-01"), ("cto", "Ben", "2025-06-01")])
    assert transition_type("executives", old, added) == "change"


def test_history_feed_and_as_of():
    d = Dossier("d_1", "acme.test")
    b1 = d.begin_build(T1)
    b1.versions = [version("https://acme.test/a", "2025-01-01", value="Dana Ruiz")]
    assert d.complete(b1, True) == []
    assert [e.type for e in d.history["ceo"]] == ["initial"]
    b2 = d.begin_build(T2)
    b2.versions = [version("https://acme.test/a", "2024-06-01", value="Lee Park")]
    feed = d.complete(b2, True)
    assert [(f["field"], f["type"], f["from"], f["to"]) for f in feed] == [("ceo", "correction", "Dana Ruiz", "Lee Park")]
    b3 = d.begin_build(T3)
    assert d.complete(b3, False) == []
    b4 = d.begin_build(T3)
    b4.versions = []
    feed = d.complete(b4, True)
    assert feed[0]["type"] == "change" and feed[0]["to"] is None
    assert d.history["ceo"][-1].learned_at == T3 and d.history["ceo"][-1].true_from is None
    moment = datetime(2026, 3, 2, 12, tzinfo=timezone.utc)
    snap = d.view_as_of(moment)
    assert snap["fields"]["ceo"]["value"] == "Lee Park" and snap["fields"]["ceo"]["learned_at"] == T2
    assert snap["researched_at"] == T2
    assert d.view_as_of(datetime(2026, 1, 1, tzinfo=timezone.utc)) is None
    assert d.view()["fields"]["ceo"]["value"] is None
    later = datetime(2026, 4, 1, tzinfo=timezone.utc)
    assert d.values("2025-02-01", later)["ceo"]["value"] == "Lee Park"
    assert d.values("2025-02-01", moment)["ceo"]["value"] == "Lee Park"


def test_corroborated_since_restarts_with_a_new_selected_value():
    def ceo(value, *origins):
        return [Version(f"https://{o}/p", None, {"ceo": [Candidate(value, f"https://{o}/p", "x", "nimble", "news",
                                                                    None, "t", None, None, o)]}) for o in origins]
    d = Dossier("d_1", "acme.test")
    times = ["2026-03-0%dT09:00:00+00:00" % n for n in (1, 5, 8, 9)]
    plan = [ceo("Dana Ruiz", "a.test"), ceo("Dana Ruiz", "b.test"), ceo("Sam Ortiz", "c.test", "d.test"),
            ceo("Sam Ortiz", "c.test")]
    for time, versions in zip(times, plan):
        build = d.begin_build(time)
        build.versions = versions
        d.complete(build, True)
    since = [d.fields_at(i)["ceo"]["corroborated_since"] for i in range(4)]
    assert since == [None, times[1], times[2], times[2]]
    assert d.fields_at(3)["ceo"]["origins"] == ["c.test"] and d.fields_at(3)["ceo"]["corroborated"] is False
