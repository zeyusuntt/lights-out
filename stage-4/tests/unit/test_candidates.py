from app.candidates import Candidate, field_view as _field_view


def field_view(cands):
    return _field_view("ceo", cands, lambda *_: None)

T = "2026-03-01T09:00:00+00:00"


def cand(value, url, kind="own", published=None, provider="nimble"):
    return Candidate(value, url, f"excerpt {value}", provider, kind, published, T)


def test_authority_beats_recency_and_status_contested():
    view = field_view([
        cand("Sam Ortiz", "https://agg.test/a", "aggregator", "2026-02-20T00:00:00+00:00"),
        cand("Dana Ruiz", "https://acme.test/about", "own", "2020-01-01T00:00:00+00:00"),
        cand("Lee Chan", "https://news.test/x", "news", "2026-02-01T00:00:00+00:00"),
    ])
    assert view["value"] == "Dana Ruiz" and view["status"] == "contested"
    assert [c["value"] for c in view["candidates"]] == ["Dana Ruiz", "Lee Chan", "Sam Ortiz"]
    assert [c["selected"] for c in view["candidates"]] == [True, False, False]
    assert view["citations"] == [{"url": "https://acme.test/about", "excerpt": "excerpt Dana Ruiz",
                                  "provider": "nimble"}]


def test_own_equals_filing_then_recency_then_undated_last():
    view = field_view([
        cand(2014, "https://acme.test/a", "own", None),
        cand(2015, "https://reg.test/b", "filing", "2025-01-01T00:00:00+00:00"),
        cand(2016, "https://acme.test/c", "own", "2025-01-01T02:00:00+02:00"),
    ])
    assert [c["value"] for c in view["candidates"]] == [2016, 2015, 2014]


def test_url_then_provider_then_value_ties():
    view = field_view([
        cand(10, "https://b.test/", "news"), cand(9, "https://b.test/", "news"),
        cand(9, "https://a.test/", "news", provider="tavily"), cand(9, "https://a.test/", "news"),
    ])
    assert [(c["url"], c["provider"], c["value"]) for c in view["candidates"]] == [
        ("https://a.test/", "nimble", 9), ("https://a.test/", "tavily", 9),
        ("https://b.test/", "nimble", 9), ("https://b.test/", "nimble", 10)]
    assert view["status"] == "contested" and len(view["citations"]) == 3


def test_imported_null_kind_has_aggregator_authority_and_same_values_are_known():
    view = field_view([cand(0, "https://x.test/", None), cand(0, "https://agg.test/", "aggregator")])
    assert view["status"] == "known" and view["value"] == 0
    assert [c["url"] for c in view["candidates"]] == ["https://agg.test/", "https://x.test/"]
    assert field_view([])["status"] == "unknown"


def inv(name, url, kind="news", origin=None, true_from=None):
    return Candidate(name, url, f"x {name}", "nimble", kind, None, T, true_from, None, origin)


def test_investor_membership_value_and_dates():
    view = _field_view("investors", [
        inv("Northwind Ventures", "https://n1.test/", origin="wire.test", true_from="2024-05-02"),
        inv("Northwind Ventures", "https://n2.test/", origin="wire.test"),
        inv("Bluebird Capital", "https://acme.test/", kind="own", true_from="2023-01-01"),
        inv("Oak Fund", "https://o1.test/", origin="a.test", true_from="2022-01-01"),
        inv("Oak Fund", "https://o2.test/", origin="b.test", true_from="2021-01-01"),
    ], lambda *_: None)
    assert view["value"] == ["Bluebird Capital", "Oak Fund"]
    assert view["status"] == "known" and view["true_from"] == "2023-01-01"
    assert [c["selected"] for c in view["candidates"] if c["value"] == "Northwind Ventures"] == [False, False]
    assert view["origins"] == ["a.test", "acme.test", "b.test"] and view["corroborated"] is False
    alone = _field_view("investors", [inv("Northwind Ventures", "https://n1.test/")], lambda *_: None)
    assert alone["status"] == "unknown" and alone["value"] is None and len(alone["candidates"]) == 1


def test_scalar_origins_only_from_the_selected_value():
    view = field_view([cand("Dana Ruiz", "https://acme.test/a", "own"),
                       cand("Lee Park", "https://x.test/", "news"), cand("Lee Park", "https://y.test/", "news")])
    assert view["origins"] == ["acme.test"] and view["corroborated"] is False
