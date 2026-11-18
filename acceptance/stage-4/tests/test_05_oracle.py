"""Self-check of the suite's Appendix A oracle against the examples the specification gives."""
import pytest

import oracle

D = "acme-robotics.test"


@pytest.mark.parametrize("ex,f,v", [
    # Appendix A.2 table
    ("Dana Ruiz has led Acme Robotics as chief executive since 2021.", "ceo", "Dana Ruiz"),
    ("Acme Robotics CEO: Sam Ortiz.", "ceo", "Sam Ortiz"),
    ("Acme Robotics was founded in 2014.", "founded_year", 2014),
    ("Acme Robotics employs about 120 people.", "headcount_range", "51-200"),
    # §4 examples
    ("Acme Robotics has raised $12M.", "funding_total", 12000000),
    ("Acme Robotics has raised 12 million dollars.", "funding_total", 12000000),
    ("Acme Robotics has raised US$12.5 million.", "funding_total", 12500000),
    ("Acme Robotics has 51-200 employees.", "headcount_range", "51-200"),
    ("Acme Robotics, Inc. is the legal name of acme-robotics.test.", "legal_name", "Acme Robotics, Inc."),
    ("Acme Robotics is headquartered in Lisbon.", "hq_city", "Lisbon"),
    ("Acme Robotics is based in Zürich.", "hq_city", "Zürich"),
])
def test_supports(ex, f, v):
    assert oracle.supports(ex, f, v, D)


@pytest.mark.parametrize("ex,f", [
    ("Acme Robotics is reportedly in talks to raise $40M.", "funding_total"),
    ("Acme Robotics opened a sales office in Porto.", "hq_city"),
    ("Acme Robotics has raised €40M.", "funding_total"),
    ("Acme Robotics was founded in 2014. It employs 9 people.", "founded_year"),
    ("Acme Robotics was founded in 2014 and 2015.", "founded_year"),
    ("Former CEO Dana Ruiz left Acme Robotics.", "ceo"),
    ("Robotics was founded in 2014.", "founded_year"),
])
def test_does_not_support(ex, f):
    s = oracle.ws1(ex)
    assert not oracle.is_single_sentence(s) or oracle.supported_value(s, f, D) is None


def test_sentence_split_rules():
    # A.1 suffix dots do not end a sentence; closers stay with the sentence.
    assert oracle.split_line('Acme Robotics Inc. is here. "Yes!" he said.') == [
        "Acme Robotics Inc. is here.", '"Yes!"', "he said."]
    assert oracle.split_line("Acme Robotics S.A.S. grew. Then") == ["Acme Robotics S.A.S. grew.", "Then"]


def test_r1_7_span_rules():
    # RULING R1-7: short sentences only whole; long-sentence spans keep runs and amounts intact.
    short = "Acme Robotics might say Acme Robotics was founded in 2014."
    assert oracle.best_span(short, "founded_year", D) is None
    filler = " and" + " many plates, bowls and cups" * 20
    long = "The Acme Robotics CEO met Ana Ruiz Silva Costa" + filler + "."
    assert len(long) > 500
    assert oracle.best_span(long, "ceo", D) is None  # "Silva Costa" would cut the 4-word run
    assert oracle.citation_shape_ok("Acme Robotics was founded in 2014.", "Acme Robotics was founded in 2014.")
    assert not oracle.citation_shape_ok("Acme Robotics was founded in 2014", "Yes, Acme Robotics was founded in 2014.")
