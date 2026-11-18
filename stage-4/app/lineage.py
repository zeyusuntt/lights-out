"""Origins (stage 4): the independent source behind each page."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from .domains import host_of
from .pages import Lineage

MAX_HOPS = 3

Fetch = Callable[[str], Awaitable[Lineage | None]]


class Origins:
    """Resolves pages' origins for one build, fetching each needed original once."""

    def __init__(self, domain: str, fetch: Fetch, known: dict[str, Lineage]) -> None:
        self.domain = domain
        self._fetch = fetch
        self._known: dict[str, asyncio.Future] = {}
        for url, lineage in known.items():
            self._known[url] = asyncio.get_running_loop().create_future()
            self._known[url].set_result(lineage)

    async def _lineage(self, url: str) -> Lineage | None:
        if url not in self._known:
            self._known[url] = asyncio.ensure_future(self._fetch(url))
        return await self._known[url]

    async def origin(self, lineage: Lineage, hops: int = 0) -> str:
        """The origin of a page: first publisher, else its original's origin (at most three
        Canonical URLs in a row), else the company for a lookalike, else its registrant."""
        if lineage.first_published_by:
            return lineage.first_published_by
        if lineage.canonical:
            if hops == MAX_HOPS:
                return host_of(lineage.canonical)
            original = await self._lineage(lineage.canonical)
            if original is None:
                return host_of(lineage.canonical)
            return await self.origin(original, hops + 1)
        if lineage.lookalike:
            return self.domain
        return lineage.registrant
