"""Builds and page versions (stage 3): what each build gathered, and what held on a date."""

from __future__ import annotations

from dataclasses import dataclass, field

from .candidates import ALL_FIELDS, Candidate


@dataclass
class Version:
    """What one ready build gathered from one URL."""

    url: str
    true_from: str | None
    candidates: dict[str, list[Candidate]]

    def to_record(self) -> dict:
        return {"url": self.url, "true_from": self.true_from,
                "candidates": {f: [c.to_record() for c in cs] for f, cs in self.candidates.items() if cs}}

    @classmethod
    def from_record(cls, data: dict) -> Version:
        return cls(data["url"], data["true_from"],
                   {f: [Candidate.from_record(c) for c in data["candidates"].get(f, [])]
                    for f in ALL_FIELDS})


@dataclass
class Build:
    time: str | None
    outcome: str = "building"
    spent: int = 0
    versions: list[Version] = field(default_factory=list)
    durable: int | None = None

    @property
    def shown(self) -> int:
        """The spending as last written to disk: what responses report (R4-8)."""
        return self.spent if self.durable is None else self.durable

    @property
    def ready(self) -> bool:
        return self.outcome == "ready"

    def candidates(self) -> dict[str, list[Candidate]]:
        return {f: [c for v in self.versions for c in v.candidates.get(f, [])] for f in ALL_FIELDS}

    def to_record(self) -> dict:
        return {"time": self.time, "outcome": self.outcome, "spent": self.spent,
                "versions": [v.to_record() for v in self.versions]}

    @classmethod
    def from_record(cls, data: dict) -> Build:
        return cls(data["time"], data["outcome"], data["spent"],
                   [Version.from_record(v) for v in data["versions"]])


@dataclass
class _Held:
    version: Version
    end: str | None = None

    def holds_on(self, day: str) -> bool:
        start = self.version.true_from
        return start is not None and start <= day and (self.end is None or day < self.end)


def holding_on(versions_in_order: list[Version], day: str) -> list[Version]:
    """The versions that hold on a date, after each URL's later versions replace or end its
    earlier ones (stage 3, /values)."""
    by_url: dict[str, list[_Held]] = {}
    for version in versions_in_order:
        earlier = by_url.setdefault(version.url, [])
        start = version.true_from
        if start is None:
            earlier.clear()
        else:
            earlier[:] = [h for h in earlier if h.version.true_from is None or h.version.true_from < start]
            if earlier:
                last = earlier[-1]
                last.end = start if last.end is None else min(last.end, start)
        earlier.append(_Held(version))
    return [h.version for held in by_url.values() for h in held if h.holds_on(day)]
