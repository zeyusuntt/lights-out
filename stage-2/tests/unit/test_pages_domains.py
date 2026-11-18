from app.domains import normalise
from app.pages import PageText, prose_of


def test_normalise():
    assert normalise(" Acme-Robotics.TEST. ") == "acme-robotics.test"
    assert normalise("www.acme-robotics.test") == "acme-robotics.test"
    assert normalise("www.www.acme.test") == "www.acme.test"
    assert normalise("a" * 63 + ".test") is not None
    for bad in ("www.com", "acme", "a" * 64 + ".test", "https://acme.test", "acme.test/x",
                "-acme.test", "acme-.test", "acme..test", "acme.test..", ".".join(["a" * 60] * 5)):
        assert normalise(bad) is None, bad


def test_header_and_prose():
    text = 'Kind: news\nFirst-Published-By: wire.test\nFacts: {"ceo": "X"}\n\nAcme raised $1M.\nMore.'
    assert prose_of(text) == "Acme raised $1M.\nMore."
    assert prose_of("Acme Robotics: the story\n\nBody.") == "Acme Robotics: the story\n\nBody."
    assert prose_of("Plain text.") == "Plain text."


def test_truncated_text_drops_its_cut_sentence():
    page = PageText("u", "One whole. Two whole.\nThree is cut at Acme raised $8", complete=False)
    assert page.excerpts() == ["One whole.", "Two whole."]
    assert PageText("u", "A b.  C   d.", complete=True).excerpts() == ["A b.", "C d."]
