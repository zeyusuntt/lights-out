"""The running service: its state, clock and background builds (§8)."""

from __future__ import annotations

import asyncio
import logging

from web_router import AsyncWebRouter

from .budget import BuildBudget
from .clock import Clock
from .providers import Gateway, Timing, make_router
from .research import BuildResearch
from .state import Dossier, State

log = logging.getLogger("dossier.builds")


class Service:
    def __init__(self, router: AsyncWebRouter | None = None) -> None:
        self.state = State()
        self.clock = Clock()
        self._router = router
        self._builds: dict[int, asyncio.Task] = {}

    @property
    def router(self) -> AsyncWebRouter:
        if self._router is None:
            self._router = make_router()
        return self._router

    def replace(self, state: State) -> None:
        """Swap in a whole new state; builds of the old one can no longer touch anything."""
        for task in self._builds.values():
            task.cancel()
        self._builds.clear()
        self.state = state

    def start_build(self, dossier: Dossier) -> None:
        """Start a build of the dossier, which must not be building already."""
        dossier.before_build = (dossier.state if dossier.state != "building" else "failed",
                                dossier.spent_units)
        dossier.state = "building"
        build_time = self.clock.iso()
        task = asyncio.ensure_future(self._build(self.state, dossier, build_time))
        self._builds[id(task)] = task
        task.add_done_callback(lambda t: self._builds.pop(id(t), None))

    async def _build(self, state: State, dossier: Dossier, build_time: str) -> None:
        def current() -> bool:
            return self.state is state and state.dossiers.get(dossier.domain) is dossier

        def charge(units: int) -> None:
            if current():
                dossier.spent_units += units

        gateway = Gateway(self.router, BuildBudget(charge), Timing.for_environment())
        try:
            fields = await BuildResearch(gateway, dossier.domain, build_time).run()
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("build of %s stopped", dossier.domain)
            fields = None
        if not current():
            return
        if gateway.succeeded and fields is not None:
            dossier.fields, dossier.researched_at, dossier.state = fields, build_time, "ready"
        else:
            dossier.state = "failed"
