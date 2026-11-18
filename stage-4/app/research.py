"""One build's research plan: which searches, rendered extracts and research run it makes, and
the candidates it finds."""

from __future__ import annotations

import asyncio
from urllib.parse import urlparse

from .builds import Version
from .candidates import ALL_FIELDS, EXECUTIVES, Candidate
from .budget import COST
from .lineage import Origins
from .pages import Lineage, PageText, sentences, split_served
from .providers import PROVIDER, Gateway, Outcome, SearchHit, is_live
from .support import (FIELDS, INVESTORS, STATEMENT_PHRASES, TITLES, citations_in, company_name,
                      find_phrase)

SNIPPET_LIMIT = 300
SNIPPET_MARGIN = 10
ALL_PHRASES = tuple(p for f in FIELDS + TITLES + (INVESTORS,) for p in STATEMENT_PHRASES[f])
RESEARCH_UNITS = COST[(PROVIDER, "research", None)]


def names_company(text: str, domain: str) -> bool:
    return bool(find_phrase(text, domain) or find_phrase(text, company_name(domain)))


def page_candidates(page: PageText, domain: str, retrieved_at: str, origin: str) -> dict[str, list[Candidate]]:
    """One candidate per field (per title for executives) and supported value, from the first
    sentence of the page that supports it."""
    found: dict[tuple[str, str | None], dict[object, Candidate]] = {}
    targets = [(f, f, None) for f in FIELDS] + [(EXECUTIVES, t, t) for t in TITLES] + [(INVESTORS, INVESTORS, None)]
    for sentence in page.excerpts():
        for name, rule, title in targets:
            seen = found.setdefault((name, title), {})
            for value, excerpt in citations_in(sentence, rule, domain):
                if value not in seen:
                    seen[value] = Candidate(value, page.url, excerpt, page.provider, page.kind,
                                            page.published_at, retrieved_at, page.true_from, title,
                                            origin)
    return {f: [c for (name, _), cs in found.items() if name == f for c in cs.values()]
            for f in ALL_FIELDS}


class BuildResearch:
    """Gathers the browser text of a company's evidence pages and derives its candidates.

    One round of searches is planned up front: the exact domain, the company's name, the name
    with each field's statement phrases, with the executive titles' phrases and with the
    investors' phrases; the research run goes alongside unless a batch budget is too short. Then each page
    that may hold evidence is loaded in a browser through Nimble's rendered extract: every page a
    research claim cites, and every search result that names the company unless the text the
    search already served shows a whole page with no statement phrase at all. Last, the
    originals that gathered pages' `Canonical` lines name are fetched, for each page's origin.
    """

    def __init__(self, gateway: Gateway, domain: str, retrieved_at: str) -> None:
        self.gateway = gateway
        self.domain = domain
        self.retrieved_at = retrieved_at
        self._hits: dict[str, SearchHit] = {}
        self._cited: list[str] = []

    async def run(self) -> list[Version]:
        """The page versions this build gathered."""
        name = company_name(self.domain).title()
        queries = [self.domain, name] + [f"{name} {' '.join(STATEMENT_PHRASES[f])}" for f in FIELDS]
        queries.append(f"{name} {' '.join(p for t in TITLES for p in STATEMENT_PHRASES[t])}")
        queries.append(f"{name} {' '.join(STATEMENT_PHRASES[INVESTORS])}")
        research = asyncio.ensure_future(self._research())
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
        origins = Origins(self.domain, self._lineage_of, {p.url: p.lineage for p in pages})
        found = await asyncio.gather(*(origins.origin(p.lineage) for p in pages))
        return [Version(page.url, page.true_from,
                        page_candidates(page, self.domain, self.retrieved_at, origin))
                for page, origin in zip(pages, found)]

    async def _research(self) -> Outcome:
        """The research run, unless a batch's shared budget can no longer pay for it."""
        if not self.gateway.affords(RESEARCH_UNITS):
            return Outcome()
        return await self.gateway.research(self.domain)

    async def _lineage_of(self, url: str) -> Lineage | None:
        outcome = await self.gateway.served_text(url)
        if not (outcome.answered and outcome.value):
            return None
        lines, _ = split_served(outcome.value)
        return Lineage.from_header(lines, url)

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
