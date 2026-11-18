"""One build's research plan: which searches, rendered extracts and research run it makes, and
the candidates it finds."""

from __future__ import annotations

import asyncio
from urllib.parse import urlparse

from .candidates import Candidate, fields_view
from .pages import PageText, sentences
from .providers import PROVIDER, Gateway, SearchHit, is_live
from .support import FIELDS, STATEMENT_PHRASES, citable, company_name, find_phrase

SNIPPET_LIMIT = 300
SNIPPET_MARGIN = 10
ALL_PHRASES = tuple(p for f in FIELDS for p in STATEMENT_PHRASES[f])


def unknown_fields() -> dict[str, dict]:
    return fields_view({})


def names_company(text: str, domain: str) -> bool:
    return bool(find_phrase(text, domain) or find_phrase(text, company_name(domain)))


def page_candidates(page: PageText, domain: str, retrieved_at: str) -> dict[str, list[Candidate]]:
    """One candidate per field and supported value, from the first sentence of the page that
    supports it."""
    found: dict[str, dict[object, Candidate]] = {f: {} for f in FIELDS}
    for sentence in page.excerpts():
        for name in FIELDS:
            hit = citable(sentence, name, domain)
            if hit is not None and hit[0] not in found[name]:
                found[name][hit[0]] = Candidate(hit[0], page.url, hit[1], page.provider, page.kind,
                                                page.published_at, retrieved_at)
    return {f: list(v.values()) for f, v in found.items()}


class BuildResearch:
    """Gathers the browser text of a company's evidence pages and derives its candidates.

    One round of searches is planned up front: the exact domain, the company's name, and the
    name with each field's statement phrases; the research run goes alongside. Then each page
    that may hold evidence is loaded in a browser through Nimble's rendered extract: every page a
    research claim cites, and every search result that names the company unless the text the
    search already served shows a whole page with no statement phrase at all.
    """

    def __init__(self, gateway: Gateway, domain: str, retrieved_at: str) -> None:
        self.gateway = gateway
        self.domain = domain
        self.retrieved_at = retrieved_at
        self._hits: dict[str, SearchHit] = {}
        self._cited: list[str] = []

    async def run(self) -> dict[str, dict]:
        name = company_name(self.domain).title()
        queries = [self.domain, name] + [f"{name} {' '.join(STATEMENT_PHRASES[f])}" for f in FIELDS]
        research = asyncio.ensure_future(self.gateway.research(self.domain))
        outcomes = await asyncio.gather(*(
            self.gateway.search(q, exact_domain=i == 0) for i, q in enumerate(queries)))
        for outcome in outcomes:
            if outcome.answered:
                for hit in outcome.value:
                    self._hits.setdefault(hit.url, hit)
        claims = await research
        if claims.answered:
            self._cited = list(dict.fromkeys(c.url for c in claims.value))
        pages = await self._render(self._to_render())
        by_field: dict[str, list[Candidate]] = {f: [] for f in FIELDS}
        for page in pages:
            for name_, found in page_candidates(page, self.domain, self.retrieved_at).items():
                by_field[name_].extend(found)
        return fields_view(by_field)

    def _to_render(self) -> list[str]:
        own = [u for u, hit in self._hits.items() if self._may_hold_evidence(hit) and self._on_site(u)]
        other = [u for u, hit in self._hits.items() if self._may_hold_evidence(hit) and not self._on_site(u)]
        return list(dict.fromkeys(self._cited + own + other))

    def _on_site(self, url: str) -> bool:
        host = (urlparse(url).hostname or "").lower()
        return host == self.domain or host.endswith("." + self.domain)

    def _may_hold_evidence(self, hit: SearchHit) -> bool:
        if not (names_company(f"{hit.title} {hit.snippet}", self.domain)
                or self.domain.split(".")[0] in hit.url.lower()):
            return False
        whole = not is_live() and len(hit.snippet) < SNIPPET_LIMIT - SNIPPET_MARGIN
        if not whole:
            return True
        return any(find_phrase(s, p) for s in sentences(hit.snippet) for p in ALL_PHRASES)

    async def _render(self, urls: list[str]) -> list[PageText]:
        if not urls or not self.gateway.may_gather():
            return []
        outcomes = await asyncio.gather(*(self.gateway.render(u) for u in urls))
        return [PageText.from_served(url, PROVIDER, outcome.value, self.domain)
                for url, outcome in zip(urls, outcomes) if outcome.answered and outcome.value]
