"""The running service: its state, clock, background builds and durable store (§8, stage 3)."""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from web_router import AsyncWebRouter

from .budget import BuildBudget, SharedBudget
from .builds import Build
from .clock import Clock
from .dossier import Dossier
from .providers import Gateway, Timing, make_router
from .research import BuildResearch
from .state import Batch, State, from_export
from .store import Store

log = logging.getLogger("dossier.builds")
DEFAULT_STATE_PATH = "/srv/data/state.json"


class Service:
    def __init__(self, router: AsyncWebRouter | None = None, store: Store | None = None) -> None:
        self.state = State()
        self.clock = Clock()
        self._router = router
        self._builds: dict[int, asyncio.Task] = {}
        self._shared: dict[str, SharedBudget] = {}
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
        """What survives a stop: the state, a running build kept as failed with its spending so
        far (R4-0), and the clock."""
        return {"document": self.state.export(settled=False), "clock": self.clock.saved()}

    async def persist(self) -> None:
        await self.store.save(self.snapshot)

    def replace(self, state: State) -> None:
        """Swap in a whole new state; builds of the old one can no longer touch anything."""
        for task in self._builds.values():
            task.cancel()
        self._builds.clear()
        self.state = state
        self._shared.clear()

    def start_build(self, dossier: Dossier, batch: Batch | None = None) -> None:
        """Start a build of the dossier, which must not be building already."""
        build = dossier.begin_build(self.clock.iso())
        shared = None
        if batch is not None:
            batch.builds.append((dossier.domain, len(dossier.builds) - 1))
            shared = self._shared_budget(batch)
        task = asyncio.ensure_future(self._build(self.state, dossier, build, shared))
        self._builds[id(task)] = task
        task.add_done_callback(lambda t: self._builds.pop(id(t), None))

    def _shared_budget(self, batch: Batch) -> SharedBudget:
        if batch.id not in self._shared:
            state = self.state
            self._shared[batch.id] = SharedBudget(batch.budget_units,
                                                  lambda: batch.spent_units(state.dossiers))
        return self._shared[batch.id]

    async def _build(self, state: State, dossier: Dossier, build: Build,
                     shared: SharedBudget | None) -> None:
        def current() -> bool:
            return self.state is state and state.dossiers.get(dossier.domain) is dossier

        def account(units: int) -> None:
            build.spent += units

        async def record() -> None:
            if current():
                await self.persist()

        gateway = Gateway(self.router, BuildBudget(account, shared), Timing.for_environment(), record)
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
