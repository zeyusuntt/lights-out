"""Research citations against the edge corpus in tests/corpus (EDGE_MOCK_URL / EDGE_DOSSIER_URL)."""

import os

import httpx
import pytest

from conftest import ADMIN, FIXTURE, create, login, wait_settled

EDGE_MOCK = os.environ.get("EDGE_MOCK_URL")
EDGE_BASE = os.environ.get("EDGE_DOSSIER_URL")
pytestmark = pytest.mark.skipif(not (EDGE_MOCK and EDGE_BASE), reason="edge corpus not running")


@pytest.fixture
def edge():
    httpx.post(f"{EDGE_MOCK}/_mock/reset", json={"epoch": 0}, headers=ADMIN)
    client = httpx.Client(base_url=EDGE_BASE, timeout=10)
    assert client.post("/_test/reset", json=FIXTURE).status_code == 204
    yield client, login(client)
    client.close()


def built(edge, domain):
    client, auth = edge
    create(client, auth, domain)
    return wait_settled(client, auth, domain)


def test_header_shaped_research_prose_is_cited(edge):
    ceo = built(edge, "edge-prose.test")["fields"]["ceo"]
    assert ceo["value"] == "Dana Ruiz"
    assert ceo["citations"][0]["excerpt"] == "Profile: Edge Prose CEO: Dana Ruiz."


def test_research_excerpt_from_a_header_is_not_cited(edge):
    assert built(edge, "edge-header.test")["fields"]["ceo"]["status"] == "unknown"


def test_long_sentences_are_cited_by_spans_within_500(edge):
    fields = built(edge, "edge-long.test")["fields"]
    assert fields["ceo"]["value"] == "Dana Ruiz"
    assert fields["founded_year"]["value"] == 2014
    for field in fields.values():
        assert all(1 <= len(c["excerpt"]) <= 500 for c in field["citations"])


def test_supporting_span_at_the_end_of_a_long_research_sentence(edge):
    ceo = built(edge, "edge-tail.test")["fields"]["ceo"]
    assert ceo["value"] == "Dana Ruiz"
    assert ceo["citations"][0]["excerpt"] == "Edge Tail CEO: Dana Ruiz."


def test_supporting_span_late_in_a_long_page_sentence(edge):
    year = built(edge, "edge-late.test")["fields"]["founded_year"]
    assert year["value"] == 1952
    assert all(len(c["excerpt"]) <= 500 for c in year["citations"])


def test_page_cited_by_an_unsupported_claim_is_still_read(edge):
    fields = built(edge, "edge-claim.test")["fields"]
    assert fields["ceo"]["status"] == "unknown"
    year = fields["founded_year"]
    assert year["value"] == 1990
    assert year["candidates"][0]["kind"] == "news"
    assert year["candidates"][0]["published_at"] == "2025-05-01T10:00:00+02:00"
