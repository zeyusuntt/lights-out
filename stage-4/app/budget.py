"""Units a build may spend (§9), within its batch's shared budget (stage 4): reserve before a
call, settle after it."""

from __future__ import annotations

from collections.abc import Callable

BUILD_LIMIT = 80

COST = {
    ("nimble", "search", "lite"): 1,
    ("nimble", "search", "fast"): 5,
    ("nimble", "search", "deep"): 15,
    ("nimble", "extract", None): 1,
    ("nimble", "render", None): 3,
    ("nimble", "research", None): 25,
}


class SharedBudget:
    """A batch's budget. The first call it cannot afford stops every build in it (R4-6)."""

    def __init__(self, limit: int, spent: Callable[[], int]) -> None:
        self.limit = limit
        self._spent = spent
        self.latched = False

    def affords(self, units: int) -> bool:
        return not self.latched and units <= self.limit - self._spent()

    def admits(self, units: int) -> bool:
        if not self.latched and units > self.limit - self._spent():
            self.latched = True
        return not self.latched


class BuildBudget:
    """One build's units. A reservation counts in the build's spending at once (so a stop
    mid-call still counts it) and is given back if the call turns out to cost nothing."""

    def __init__(self, account: Callable[[int], None], shared: SharedBudget | None = None,
                 limit: int = BUILD_LIMIT, spent: int = 0) -> None:
        self._limit = limit
        self._held = spent
        self._account = account
        self._shared = shared

    def remaining(self) -> int:
        return self._limit - self._held

    def affords(self, units: int) -> bool:
        """Whether the shared budget, if any, still has room for these units."""
        return self._shared is None or self._shared.affords(units)

    def reserve(self, units: int, keep: int = 0) -> bool:
        """Reserve units, leaving `keep` units of this build's own limit unspent."""
        if units + keep > self.remaining():
            return False
        if self._shared is not None and not self._shared.admits(units):
            return False
        self._held += units
        self._account(units)
        return True

    def settle(self, units: int, charged: bool) -> None:
        if not charged:
            self._held -= units
            self._account(-units)
