"""Units one build may spend (§9): reserve before a call, settle after it."""

from __future__ import annotations

from collections.abc import Callable

BUILD_LIMIT = 80

COST = {
    ("nimble", "search", "lite"): 1,
    ("nimble", "search", "fast"): 5,
    ("nimble", "search", "deep"): 15,
    ("nimble", "render", None): 3,
    ("nimble", "research", None): 25,
}


class BuildBudget:
    def __init__(self, on_charge: Callable[[int], None], limit: int = BUILD_LIMIT) -> None:
        self._limit = limit
        self._spent = 0
        self._reserved = 0
        self._on_charge = on_charge

    @property
    def spent(self) -> int:
        return self._spent

    def remaining(self) -> int:
        return self._limit - self._spent - self._reserved

    def reserve(self, units: int) -> bool:
        if units > self.remaining():
            return False
        self._reserved += units
        return True

    def settle(self, units: int, charged: bool) -> None:
        """Release a reservation, charging it when the call costs its units."""
        self._reserved -= units
        if charged:
            self._spent += units
            self._on_charge(units)
