"""One build's research plan: which searches, extracts and research run it makes, and what it learns."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from urllib.parse import urlparse

from .pages import PageText, is_header_line, prose_of
from .providers import Gateway, ResearchClaim, SearchHit, is_live
from .support import FIELDS, STATEMENT_PHRASES, company_name, find_phrase, supported_value

SNIPPET_LIMIT = 300
SNIPPET_MARGIN = 10


@dataclass(frozen=True)
class Citation:
    url: str
    excerpt: str
    provider: str = "nimble"

    def as_json(self) -> dict:
        return {"url": self.url, "excerpt": self.excerpt, "provider": self.provider}


@dataclass
class Findings:
    """Supported values per field, each with the citations that support it, in discovery order."""

    values: dict[str, dict[object, list[Citation]]] = field(
        default_factory=lambda: {f: {} for f in FIELDS})

    def add(self, name: str, value: object, citation: Citation) -> None:
        cites = self.values[name].setdefault(value, [])
        if citation not in cites:
            cites.append(citation)

    def missing(self) -> list[str]:
        return [f for f in FIELDS if not self.values[f]]

    def decide(self, domain: str = "") -> dict[str, dict]:
        decided = {}
        for name in FIELDS:
            options = self.values[name]
            if not options:
                decided[name] = {"value": None, "status": "unknown", "citations": []}
                continue
            value = max(options, key=lambda v: (len(options[v]),
                                                sum(_on_site(c.url, domain) for c in options[v])))
            decided[name] = {"value": value, "status": "known",
                             "citations": [c.as_json() for c in options[value]]}
        return decided


def _on_site(url: str, domain: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return bool(domain) and (host == domain or host.endswith("." + domain))


def unknown_fields() -> dict[str, dict]:
    return Findings().decide()


def names_company(text: str, domain: str) -> bool:
    return bool(find_phrase(text, domain) or find_phrase(text, company_name(domain)))


class BuildResearch:
    """Gathers pages for one company and decides its six fields from them."""

    def __init__(self, gateway: Gateway, domain: str) -> None:
        self.gateway = gateway
        self.domain = domain
        self.findings = Findings()
        self._evidence: dict[str, PageText] = {}
        self._fetched: dict[str, PageText | None] = {}
        self._hits: dict[str, SearchHit] = {}
        self._claims: list[ResearchClaim] = []

    async def run(self) -> dict[str, dict]:
        name = company_name(self.domain).title()
        research = asyncio.ensure_future(self.gateway.research(self.domain))
        await self._searches([self.domain, name], exact_domain=True)
        outcome = await research
        if outcome.answered:
            self._claims = outcome.value
        self._evaluate()
        await self._extract(self._truncated_hits())
        self._evaluate()
        missing = self.findings.missing()
        if missing and self.gateway.may_gather():
            queries = [f"{name} {' '.join(STATEMENT_PHRASES[f])}" for f in missing]
            await self._searches(queries)
            self._evaluate()
            if self.findings.missing():
                await self._extract(self._truncated_hits())
                self._evaluate()
        return self.findings.decide(self.domain)

    async def _searches(self, queries: list[str], exact_domain: bool = False) -> None:
        """Run the searches together; the first is the exact-domain search when so marked."""
        outcomes = await asyncio.gather(*(
            self.gateway.search(q, exact_domain=exact_domain and i == 0) for i, q in enumerate(queries)))
        for outcome in outcomes:
            if outcome.answered:
                self._absorb(outcome.value)

    def _absorb(self, hits: list[SearchHit]) -> None:
        for hit in hits:
            if hit.url in self._hits:
                continue
            self._hits[hit.url] = hit
            fetched = self._fetched.get(hit.url)
            self._evidence[hit.url] = fetched or PageText(hit.url, hit.snippet, self._snippet_complete(hit))

    @staticmethod
    def _snippet_complete(hit: SearchHit) -> bool:
        return not is_live() and len(hit.snippet) < SNIPPET_LIMIT - SNIPPET_MARGIN

    def _truncated_hits(self) -> list[str]:
        if not self.findings.missing():
            return []
        return [url for url, hit in self._hits.items()
                if not self._evidence[url].complete and url not in self._fetched
                and (names_company(f"{hit.title} {hit.snippet}", self.domain)
                     or self.domain.split(".")[0] in url.lower())]

    def _claim_value(self, claim: ResearchClaim) -> object | None:
        value = supported_value(claim.excerpt, claim.field, self.domain)
        return value if value is not None and _same_claim(value, claim.value) else None

    async def _extract(self, urls: list[str]) -> None:
        urls = [u for u in dict.fromkeys(urls) if u not in self._fetched]
        if not urls or not self.gateway.may_gather():
            return
        outcomes = await asyncio.gather(*(self.gateway.extract(u) for u in urls))
        for url, outcome in zip(urls, outcomes):
            if not outcome.answered:
                continue
            page = PageText(url, prose_of(outcome.value), True) if outcome.value else None
            self._fetched[url] = page
            if page and url in self._evidence:
                self._evidence[url] = page

    def _evaluate(self) -> None:
        for page in self._evidence.values():
            for excerpt in page.excerpts():
                for name in FIELDS:
                    value = supported_value(excerpt, name, self.domain)
                    if value is not None:
                        self.findings.add(name, value, Citation(page.url, excerpt))
        for claim in self._claims:
            value = self._claim_value(claim)
            page = self._evidence.get(claim.url)
            if value is not None and _from_prose(claim.excerpt, page):
                self.findings.add(claim.field, value, Citation(claim.url, " ".join(claim.excerpt.split())))


def _from_prose(excerpt: str, page: PageText | None) -> bool:
    """A research excerpt is cited as served unless it reads as a header line, or the
    page's full prose, already gathered in this build, does not contain it."""
    if is_header_line(excerpt.strip()):
        return False
    return page is None or not page.complete or page.contains(excerpt)


def _same_claim(value: object, claimed: object) -> bool:
    if isinstance(value, int):
        if isinstance(claimed, bool):
            return False
        if isinstance(claimed, (int, float)):
            return claimed == value
        return isinstance(claimed, str) and claimed.strip().replace(",", "") == str(value)
    return isinstance(claimed, str) and " ".join(claimed.split()).casefold() == str(value).casefold()
