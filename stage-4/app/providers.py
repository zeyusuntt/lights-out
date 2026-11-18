"""Every provider call, through WebRouter's `nimble` provider, priced and reserved (§9)."""

from __future__ import annotations

import asyncio
import os
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

import nimble_python
from web_router import AsyncWebRouter, ConfigurationError, ProviderError, WebRouterError

from .budget import COST, BuildBudget
from .support import FIELDS

PROVIDER = "nimble"
LIVE_HOST = "sdk.nimbleway.com"
RETRY_PAUSE_S = 1.1
MAX_ATTEMPTS = 5


def is_live() -> bool:
    base = os.environ.get("NIMBLE_BASE_URL")
    return base is None or urlparse(base).hostname == LIVE_HOST


@dataclass(frozen=True)
class Timing:
    """How long calls may wait, and until when a build may keep retrying and gathering."""

    call_timeout_s: float
    research_timeout_s: float
    retry_window_s: float
    gather_window_s: float

    @classmethod
    def for_environment(cls) -> Timing:
        if is_live():
            return cls(call_timeout_s=45, research_timeout_s=200, retry_window_s=180,
                       gather_window_s=200)
        return cls(call_timeout_s=30, research_timeout_s=60, retry_window_s=6.5,
                   gather_window_s=60)


@dataclass
class SearchHit:
    url: str
    title: str
    snippet: str


@dataclass
class ResearchClaim:
    field: str
    value: Any
    url: str
    excerpt: str


@dataclass
class Outcome:
    """What one call came to: its answer, and whether a provider answered it without an error."""

    answered: bool = False
    value: Any = None
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Failure:
    charged: bool
    retryable: bool
    throttled: bool = False


def _classify(exc: BaseException) -> Failure:
    if isinstance(exc, ConfigurationError):
        return Failure(charged=False, retryable=False)
    original = getattr(exc, "original", None) or exc.__cause__
    if isinstance(original, nimble_python.APIStatusError):
        status = original.status_code
        return Failure(charged=False, retryable=status == 429 or status >= 500,
                       throttled=status == 429)
    if isinstance(original, (nimble_python.APITimeoutError, nimble_python.APIConnectionError)):
        return Failure(charged=True, retryable=True)
    return Failure(charged=True, retryable=False)


class Gateway:
    """One build's access to the providers: spends from its budget, retries refusals."""

    def __init__(self, router: AsyncWebRouter, budget: BuildBudget, timing: Timing,
                 record: Callable[[], Awaitable[None]]) -> None:
        self._router = router
        self._budget = budget
        self._timing = timing
        self._record = record
        self._started = time.monotonic()
        self._throttled_wait = 0.0
        self._waiting = 0
        self._waiting_since = 0.0
        self.succeeded = False

    async def _pause(self, throttled: bool) -> None:
        """Wait before calling again; while any wait after a 429 is pending, the time is not counted."""
        if not throttled:
            await asyncio.sleep(RETRY_PAUSE_S)
            return
        if self._waiting == 0:
            self._waiting_since = time.monotonic()
        self._waiting += 1
        try:
            await asyncio.sleep(RETRY_PAUSE_S)
        finally:
            self._waiting -= 1
            if self._waiting == 0:
                self._throttled_wait += time.monotonic() - self._waiting_since

    def elapsed(self) -> float:
        """Time the build has run, less the time it spent waiting out 429 answers."""
        return time.monotonic() - self._started - self._throttled_wait

    def affords(self, units: int) -> bool:
        return self._budget.affords(units)

    def may_gather(self) -> bool:
        return self.elapsed() < self._timing.gather_window_s

    async def _call(self, units: int, make_call, retry_lost: bool = False, keep: int = 0) -> Outcome:
        """Make a call: reserve its units and record them durably first, then settle them."""
        outcome = Outcome()
        for attempt in range(MAX_ATTEMPTS):
            if not self._budget.reserve(units, keep):
                outcome.errors.append("budget")
                return outcome
            await self._record()
            try:
                outcome.value = await make_call()
            except (WebRouterError, nimble_python.NimbleError, OSError, ValueError) as exc:
                failure = _classify(exc)
                self._budget.settle(units, failure.charged)
                outcome.errors.append(type(exc).__name__)
                if not failure.retryable or (failure.charged and not retry_lost):
                    return outcome
                if attempt + 1 == MAX_ATTEMPTS:
                    return outcome
                if not failure.throttled and self.elapsed() > self._timing.retry_window_s:
                    return outcome
                await self._pause(failure.throttled)
                continue
            self._budget.settle(units, True)
            outcome.answered = True
            self.succeeded = True
            return outcome
        return outcome

    async def search(self, query: str, exact_domain: bool = False) -> Outcome:
        async def call() -> list[SearchHit]:
            response = await self._router.search(
                query, provider=PROVIDER, search_depth="lite", max_results=10)
            return [SearchHit(r.url, r.title or "", r.content or r.description or "")
                    for r in response.results]
        return await self._call(COST[(PROVIDER, "search", "lite")], call, retry_lost=exact_domain)

    async def _extract(self, url: str, render: bool, keep: int = 0) -> Outcome:
        async def call() -> str | None:
            options = {"provider_options": {"render": True}} if render else {}
            try:
                response = await self._router.extract([url], provider=PROVIDER, **options)
            except ProviderError as exc:
                if _classify(exc) == Failure(charged=True, retryable=False):
                    return None
                raise
            return next((d.content for d in response.documents if d.url == url and d.content), None)
        return await self._call(COST[(PROVIDER, "render" if render else "extract", None)], call,
                                keep=keep)

    async def render(self, url: str, keep: int = 0) -> Outcome:
        """The text a browser shows once the page has loaded, or an answered outcome with None
        when there is no page. `keep` units of the build's limit stay unspent."""
        return await self._extract(url, True, keep)

    async def served_text(self, url: str) -> Outcome:
        """The page's served text without loading it in a browser, for its header lines."""
        return await self._extract(url, False)

    async def research(self, domain: str) -> Outcome:
        async def call() -> list[ResearchClaim]:
            response = await self._router.research(
                research_query(domain), provider=PROVIDER, output_schema=RESEARCH_SCHEMA,
                timeout=self._timing.research_timeout_s)
            return research_claims(response.structured, response.citations)
        return await self._call(COST[(PROVIDER, "research", None)], call)


def research_query(domain: str) -> str:
    return (f"Company profile of {domain}: its registered legal name, headquarters city, "
            f"chief executive, founding year, employee headcount and total equity funding in US dollars.")


RESEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "legal_name": {"type": ["string", "null"], "description": "Registered legal name"},
        "hq_city": {"type": ["string", "null"], "description": "Headquarters city only"},
        "ceo": {"type": ["string", "null"], "description": "Chief executive's full name"},
        "founded_year": {"type": ["integer", "null"], "description": "Year founded"},
        "headcount_range": {
            "type": ["string", "null"],
            "enum": ["1-10", "11-50", "51-200", "201-500", "501-1000", "1001-5000",
                     "5001-10000", "10001+", None]},
        "funding_total": {"type": ["integer", "null"], "description": "Total equity funding, USD"},
    },
    "required": list(FIELDS),
}


def research_claims(structured: Any, citations: list) -> list[ResearchClaim]:
    if not isinstance(structured, dict):
        return []
    claims = []
    for name in FIELDS:
        value = structured.get(name)
        if value is None:
            continue
        for citation in citations:
            if citation.field not in (f"$.{name}", name):
                continue
            excerpts = list((citation.extra or {}).get("excerpts") or []) or [citation.snippet]
            claims.extend(ResearchClaim(name, value, citation.url, e)
                          for e in excerpts if isinstance(e, str) and e.strip())
    return claims


def make_router() -> AsyncWebRouter:
    config: dict[str, Any] = {PROVIDER: {"max_retries": 0,
                                         "timeout": Timing.for_environment().call_timeout_s}}
    return AsyncWebRouter(provider_config=config)
