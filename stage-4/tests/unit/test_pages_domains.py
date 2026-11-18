from app.domains import normalise
from app.domains import host_of
from app.pages import Lineage, PageText, page_kind, published_at, split_served


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


def test_kind_falls_back_to_the_host_and_own_needs_the_registrant():
    for url, kind in (("https://WWW.Acme.test./about", "own"), ("https://acme.test/x", "own"),
                      ("https://shop.acme.test/x", "aggregator"), ("https://news.test/acme", "aggregator")):
        assert page_kind([], url, "acme.test", host_of(url)) == kind, url
    assert page_kind(["Kind: Filing"], "https://acme.test/", "acme.test", "acme.test") == "own"
    assert page_kind(["Kind: filing"], "https://registry.test/", "acme.test", "registry.test") == "filing"
    assert page_kind(["Kind: own"], "https://acme.test/", "acme.test", "domainhold.test") == "aggregator"
    assert page_kind([], "https://acme.test/", "acme.test", "domainhold.test") == "aggregator"
    assert page_kind(["Kind: own"], "https://other.test/", "acme.test", "acme.test") == "own"


def test_lineage_and_lookalike():
    lines = ["Kind: own", "Registrant: Acme.test.", "Canonical: https://Wire.test/a", "First-Published-By: www.wire.test"]
    lineage = Lineage.from_header(lines, "https://acme-copy.test/x")
    assert lineage == Lineage("acme.test", "https://Wire.test/a", "wire.test", True)
    assert Lineage.from_header(["Canonical: https://a.test/x"], "https://a.test/x").canonical is None
    assert Lineage.from_header([], "https://WWW.A.test/x").registrant == "a.test"


def test_bad_publication_time_is_none():
    assert published_at(["Published: 2026-02-20"]) is None
    assert published_at(["Published: soon"]) is None
    assert published_at([]) is None
