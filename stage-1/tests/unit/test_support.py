import pytest

from app.support import is_single_sentence, split_prose, supported_value

D = "acme-robotics.test"


@pytest.mark.parametrize("excerpt, field, value", [
    ("Dana Ruiz has led Acme Robotics as chief executive since 2021.", "ceo", "Dana Ruiz"),
    ("Acme Robotics CEO: Sam Ortiz.", "ceo", "Sam Ortiz"),
    ("Acme Robotics was founded in 2014.", "founded_year", 2014),
    ("Acme Robotics employs about 120 people.", "headcount_range", "51-200"),
    ("Acme Robotics has raised $12M.", "funding_total", 12_000_000),
    ("Acme Robotics has raised 12 million dollars.", "funding_total", 12_000_000),
    ("Acme Robotics has raised US$12.5 million to date.", "funding_total", 12_500_000),
    ("Acme Robotics has raised USD 12 million.", "funding_total", 12_000_000),
    ("Acme Robotics raised $12,000,000 in total.", "funding_total", 12_000_000),
    ("Acme Robotics raised 12,000,000 US dollars.", "funding_total", 12_000_000),
    ("Acme Robotics raised $1.2bn.", "funding_total", 1_200_000_000),
    ("Acme Robotics raised $250k.", "funding_total", 250_000),
    ("Acme Robotics, Inc. is the registered name of the firm.", "legal_name", "Acme Robotics, Inc."),
    ("Acme Robotics Holdings Inc. is listed as the legal entity for Acme Robotics.",
     "legal_name", "Acme Robotics Holdings Inc."),
    ("The legal entity is Acme Robotics S.A.S. in France.", "legal_name", "Acme Robotics S.A.S."),
    ("Acme Robotics Pty Ltd is the registered company.", "legal_name", "Acme Robotics Pty Ltd"),
    ("Acme Robotics AG Inc. is the legal name.", "legal_name", "Acme Robotics AG"),
    ("Acme Robotics is headquartered in Lisbon, Portugal.", "hq_city", "Lisbon"),
    ("Acme Robotics is based in São Paulo.", "hq_city", "São Paulo"),
    ("Acme Robotics is based in Winston-Salem today.", "hq_city", "Winston-Salem"),
    ("Acme Robotics is based in Zürich.", "hq_city", "Zürich"),
    ("acme-robotics.test lists 51-200 employees.", "headcount_range", "51-200"),
    ("ACME ROBOTICS employs 1,575 staff.", "headcount_range", "1001-5000"),
    ("Acme Robotics employs 20000 people.", "headcount_range", "10001+"),
    ("The CEO of Acme Robotics is Jan Van Der Berg.", "ceo", None),
    ("Acme Robotics chief executive officer Ana María López spoke.", "ceo", "Ana María López"),
    ("Acme Robotics chief executive officer Ana Lopez Diaz spoke.", "ceo", "Ana Lopez Diaz"),
    ("Acme Robotics is reportedly in talks to raise $40M.", "funding_total", None),
    ("Acme Robotics opened a sales office in Porto.", "hq_city", None),
    ("Acme Robotics did not raise funding of $5M.", "funding_total", None),
    ("Acme Robotics raised $5M and later $7M.", "funding_total", None),
    ("Acme Robotics raised $5M, or 5 million dollars.", "funding_total", 5_000_000),
    ("Acme Robotics raised $12.3456 thousand.", "funding_total", None),
    ("Acme Robotics raised €12M.", "funding_total", None),
    ("Acme Robotics was founded in 2014 and raised $2015 million.", "founded_year", 2014),
    ("Acme Robotics was founded in 2014 and employs 120 people.", "headcount_range", None),
    ("Acme Robotics was founded in FY2014.", "founded_year", None),
    ("Acme Robotics was founded in 2014. It grew.", "founded_year", None),
    ("Acme Robotix was founded in 2014.", "founded_year", None),
    ("Acme Robotics was founded in 1799.", "founded_year", None),
    ("Acme Robotics employs 1.5 thousand people.", "headcount_range", None),
    ("Acme Robotics is headquartered in New York.", "hq_city", "New York"),
    ("Acme Robotics Headquartered In Lisbon.", "hq_city", None),
    ("Acme Robotics established 2014-2016 offices.", "founded_year", None),
    ("Acme Roboticsx was founded in 2014.", "founded_year", None),
    ("The former CEO of Acme Robotics was Dana Ruiz.", "ceo", None),
    ("Acme Robotics is not based in Paris.", "hq_city", None),
    ("Acme Robotics cannot say where it is based in Paris.", "hq_city", "Paris"),
])
def test_appendix_examples(excerpt, field, value):
    assert supported_value(excerpt, field, D) == value


def test_sentence_split_respects_suffix_and_closers():
    prose = 'Acme Robotics, Inc. is here. "Quoted!" Next one?) Last\nSecond line.'
    assert split_prose(prose) == ["Acme Robotics, Inc. is here.", '"Quoted!"', "Next one?)",
                                  "Last", "Second line."]


def test_decimal_does_not_split():
    assert split_prose("It raised 12.5 million. Yes.") == ["It raised 12.5 million.", "Yes."]


def test_single_sentence_collapses_whitespace():
    assert is_single_sentence("Acme   Robotics\nwas founded in 2014.")
    assert not is_single_sentence("One. Two.")


def test_long_sentence_is_cited_by_a_supporting_span():
    from app.support import citable
    sentence = "Acme Robotics CEO: Dana Ruiz" + " with published company background" * 30 + "."
    value, span = citable(sentence, "ceo", D)
    assert value == "Dana Ruiz" and len(span) <= 500 and span in sentence
    assert supported_value(span, "ceo", D) == "Dana Ruiz"
    assert citable(sentence, "ceo", D, want="Sam Ortiz") is None
    far = "Acme Robotics" + " and partners" * 60 + " named Dana Ruiz as CEO."
    assert citable(far, "ceo", D) is None
