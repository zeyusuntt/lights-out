from app.domains import normalise
from app.pages import PageText, page_kind, published_at, split_served


def test_normalise():
    assert normalise(" Acme-Robotics.TEST. ") == "acme-robotics.test"
    assert normalise("www.acme-robotics.test") == "acme-robotics.test"
    assert normalise("www.www.acme.test") == "www.acme.test"
    assert normalise("a" * 63 + ".test") is not None
    for bad in ("www.com", "acme", "a" * 64 + ".test", "https://acme.test", "acme.test/x",
                "-acme.test", "acme-.test", "acme..test", "acme.test..", ".".join(["a" * 60] * 5)):
        assert normalise(bad) is None, bad


def test_header_and_prose():
    text = 'Kind: news\nPublished: 2026-02-20T00:00:00Z\nFacts: {"ceo": "X"}\n\nAcme raised $1M.\nMore.'
    page = PageText.from_served("https://wire.test/a", "nimble", text, "acme.test")
    assert page.prose == "Acme raised $1M.\nMore."
    assert (page.kind, page.published_at) == ("news", "2026-02-20T00:00:00+00:00")
    assert split_served("Acme Robotics: the story\n\nBody.") == ([], "Acme Robotics: the story\n\nBody.")
    assert PageText.from_served("u", "nimble", "A b.  C   d.", "a.test").excerpts() == ["A b.", "C d."]


def test_kind_falls_back_to_the_host():
    for url, kind in (("https://WWW.Acme.test./about", "own"), ("https://acme.test/x", "own"),
                      ("https://shop.acme.test/x", "aggregator"), ("https://news.test/acme", "aggregator")):
        assert page_kind([], url, "acme.test") == kind, url
    assert page_kind(["Kind: Filing"], "https://acme.test/", "acme.test") == "own"
    assert page_kind(["Kind: filing"], "https://registry.test/", "acme.test") == "filing"


def test_bad_publication_time_is_none():
    assert published_at(["Published: 2026-02-20"]) is None
    assert published_at(["Published: soon"]) is None
    assert published_at([]) is None
