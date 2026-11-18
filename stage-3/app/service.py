"""The running service: its state, clock, background builds and durable store (§8, stage 3)."""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from web_router import AsyncWebRouter

from .budget import BuildBudget
from .builds import Build
from .clock import Clock
from .dossier import Dossier
from .providers import Gateway, Timing, make_router
from .research import BuildResearch
from .state import State, from_export
from .store import Store

log = logging.getLogger("dossier.builds")
DEFAULT_STATE_PATH = "/srv/data/state.json"


class Service:
    def __init__(self, router: AsyncWebRouter | None = None, store: Store | None = None) -> None:
        self.state = State()
        self.clock = Clock()
        self._router = router
        self._builds: dict[int, asyncio.Task] = {}
        self.store = store or Store(Path(os.environ.get("DOSSIER_STATE_PATH", DEFAULT_STATE_PATH)))
        saved = self.store.load()
        if saved is not None:
            self.state = from_export(saved["document"])
            self.clock.restore(saved["clock"])

    @property
    def router(self) -> AsyncWebRouter:
        if self._router is None:
            self._router = make_router()
        return self._router

    def snapshot(self) -> dict:
        """What survives a restart: the state as an export (a running build left out) and the clock."""
        return {"document": self.state.export(), "clock": self.clock.saved()}

    async def persist(self) -> None:
        await self.store.save(self.snapshot)

    def replace(self, state: State) -> None:
        """Swap in a whole new state; builds of the old one can no longer touch anything."""
        for task in self._builds.values():
            task.cancel()
        self._builds.clear()
        self.state = state

    def start_build(self, dossier: Dossier) -> None:
        """Start a build of the dossier, which must not be building already."""
        build = dossier.begin_build(self.clock.iso())
        task = asyncio.ensure_future(self._build(self.state, dossier, build))
        self._builds[id(task)] = task
        task.add_done_callback(lambda t: self._builds.pop(id(t), None))

    async def _build(self, state: State, dossier: Dossier, build: Build) -> None:
        def current() -> bool:
            return self.state is state and state.dossiers.get(dossier.domain) is dossier

        def charge(units: int) -> None:
            build.spent += units

        gateway = Gateway(self.router, BuildBudget(charge), Timing.for_environment())
        try:
            versions = await BuildResearch(gateway, dossier.domain, build.time).run()
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("build of %s stopped", dossier.domain)
            versions = None
        if not current():
            return
        ready = gateway.succeeded and versions is not None
        if ready:
            build.versions = versions
        state.publish(dossier.complete(build, ready))
        await self.persist()
