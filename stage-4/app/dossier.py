"""A dossier: its builds, the views they give, its history and the feed entries it adds (stage 3)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime

from .builds import Build, holding_on
from .candidates import (ALL_FIELDS, EXECUTIVES, INVESTORS, Candidate, fields_view, member_groups,
                         ranked, same_value, unknown_view, values_view)
from .clock import parse_rfc3339
from .support import FIELDS, TITLES


@dataclass
class Entry:
    """One history entry: the selected value a ready build made, and the build that made it."""

    type: str
    value: object
    true_from: str | None
    learned_at: str
    citations: list[dict]
    build: int

    def as_json(self) -> dict:
        return {"type": self.type, "value": self.value, "true_from": self.true_from,
                "learned_at": self.learned_at, "citations": self.citations}

    def to_record(self) -> dict:
        return {**self.as_json(), "build": self.build}

    @classmethod
    def from_record(cls, data: dict) -> Entry:
        return cls(data["type"], data["value"], data["true_from"], data["learned_at"],
                   data["citations"], data["build"])


def _at_or_before(time: str | None, moment: datetime) -> bool:
    parsed = parse_rfc3339(time) if time else None
    return parsed is not None and parsed <= moment


def _member_dates(view: dict) -> dict[str, tuple[str, str | None]]:
    """title -> (name, true_from) of each selected executive."""
    return {c["title"]: (c["value"], c["true_from"]) for c in view["candidates"] if c["selected"]}


def _differs(name: str, old: object, new: object) -> bool:
    if name in (EXECUTIVES, INVESTORS):
        return (old or []) != (new or [])
    if old is None or new is None:
        return (old is None) != (new is None)
    return not same_value(old, new)


def transition_type(name: str, old: dict, new: dict) -> str:
    """`correction` or `change` for a selected value that differs (stage 3, Changes)."""
    if name == INVESTORS:
        earlier = set(old["value"] or [])
        changed = earlier.symmetric_difference(new["value"] or [])
        added_dates = {n: min((c["true_from"] for c in new["candidates"] if c["value"] == n and c["true_from"]),
                              default=None) for n in changed}
        return "correction" if all(
            n not in earlier and added_dates[n] and old["true_from"] and added_dates[n] <= old["true_from"]
            for n in changed) else "change"
    if name == EXECUTIVES:
        before, after = _member_dates(old), _member_dates(new)
        for title in TITLES:
            a, b = before.get(title), after.get(title)
            if a == b or (a and b and a[0] == b[0]):
                continue
            if not (a and b and a[1] and b[1] and b[1] <= a[1]):
                return "change"
        return "correction"
    if old["value"] is None or new["value"] is None:
        return "change"
    if old["true_from"] and new["true_from"] and new["true_from"] <= old["true_from"]:
        return "correction"
    return "change"


@dataclass
class Dossier:
    id: str
    domain: str
    state: str = "building"
    builds: list[Build] = field(default_factory=list)
    history: dict[str, list[Entry]] = field(default_factory=lambda: {f: [] for f in ALL_FIELDS})
    before_build: str = "failed"

    @property
    def spent_units(self) -> int:
        return sum(b.shown for b in self.builds)

    def last_ready(self, moment: datetime | None = None) -> int | None:
        """Index of the latest ready build, or of the latest whose time is at or before a moment."""
        for i in range(len(self.builds) - 1, -1, -1):
            b = self.builds[i]
            if b.ready and (moment is None or _at_or_before(b.time, moment)):
                return i
        return None

    def _learned(self, upto: int):
        first: dict[tuple, str] = {}
        for b in self.builds[:upto + 1]:
            if b.ready:
                for name, cands in b.candidates().items():
                    for c in cands:
                        first.setdefault(c.identity(name), b.time)
        return lambda name, c: first.get(c.identity(name))

    def fields_at(self, index: int | None) -> dict[str, dict]:
        """The fields as ready build `index` left them, with learned_at from history up to it."""
        if index is None:
            return {f: unknown_view() for f in ALL_FIELDS}
        views = fields_view(self.builds[index].candidates(), self._learned(index))
        for name, view in views.items():
            if view["value"] is not None:
                entries = [e for e in self.history[name] if e.build <= index]
                view["learned_at"] = entries[-1].learned_at if entries else None
                view["corroborated_since"] = self._corroborated_since(name, index)
        return views

    def _corroborated_since(self, name: str, index: int) -> str | None:
        """The time of the first ready build of the run, ending at `index`, after each of which
        every member had two or more standing origins (R4-4). A new selected value of a scalar
        field starts a new run, with no standing origins."""
        standing: dict[str, set[str]] = {}
        since: str | None = None
        for build in self.builds[:index + 1]:
            if not build.ready:
                continue
            groups = member_groups(name, build.candidates()[name])
            keys = [self._key(key) for key, _ in groups]
            if name in FIELDS and keys != list(standing):
                since = None
            standing = {k: standing.get(k, set()) | {c.source for c in cands}
                        for k, (_, cands) in zip(keys, groups)}
            holds = bool(standing) and all(len(origins) >= 2 for origins in standing.values())
            since = (since or build.time) if holds else None
        return since

    @staticmethod
    def _key(key: object) -> str:
        return json.dumps(key.strip() if isinstance(key, str) else key)

    def summary(self) -> dict:
        return {"dossier_id": self.id, "domain": self.domain, "state": self.state}

    def _body(self, index: int | None, state: str, spent: int) -> dict:
        return {"dossier_id": self.id, "domain": self.domain, "state": state,
                "researched_at": self.builds[index].time if index is not None else None,
                "spent_units": spent, "fields": self.fields_at(index)}

    def view(self) -> dict:
        return self._body(self.last_ready(), self.state, self.spent_units)

    def view_as_of(self, moment: datetime) -> dict | None:
        index = self.last_ready(moment)
        if index is None:
            return None
        spent = sum(b.shown for b in self.builds if _at_or_before(b.time, moment))
        return self._body(index, "ready", spent)

    def values(self, day: str, moment: datetime) -> dict[str, dict] | None:
        if self.last_ready(moment) is None:
            return None
        versions = [v for b in self.builds if b.ready and _at_or_before(b.time, moment)
                    for v in b.versions]
        by_field: dict[str, list[Candidate]] = {f: [] for f in ALL_FIELDS}
        for version in holding_on(versions, day):
            for name, cands in version.candidates.items():
                by_field[name].extend(cands)
        return values_view(by_field)

    def listing(self) -> dict:
        index = self.last_ready()
        legal = ranked(self.builds[index].candidates()["legal_name"]) if index is not None else []
        return {**self.summary(), "legal_name": legal[0].value if legal else None,
                "researched_at": self.builds[index].time if index is not None else None,
                "spent_units": self.spent_units}

    def history_json(self) -> dict:
        return {"domain": self.domain,
                "fields": {f: [e.as_json() for e in self.history[f]] for f in ALL_FIELDS}}

    def begin_build(self, time: str) -> Build:
        self.before_build = self.state if self.state != "building" else "failed"
        self.state = "building"
        build = Build(time, durable=0)
        self.builds.append(build)
        return build

    def complete(self, build: Build, ready: bool) -> list[dict]:
        """Record a build's outcome; for a ready one, its history entries. The feed entries
        (without seq) that it adds, in field order."""
        if not ready:
            build.outcome, self.state = "failed", "failed"
            return []
        index = self.builds.index(build)
        previous = self.last_ready()
        build.outcome, self.state = "ready", "ready"
        return self.record_transitions(previous, index)

    def record_transitions(self, previous: int | None, index: int) -> list[dict]:
        old_views = self.fields_at(previous) if previous is not None else None
        new_views = fields_view(self.builds[index].candidates(), lambda *_: None)
        time = self.builds[index].time
        feed = []
        for name in ALL_FIELDS:
            new = new_views[name]
            if old_views is None:
                if new["value"] is not None:
                    self.history[name].append(Entry("initial", new["value"], new["true_from"], time,
                                                    new["citations"], index))
                continue
            old = old_views[name]
            if not _differs(name, old["value"], new["value"]):
                continue
            kind = transition_type(name, old, new)
            self.history[name].append(Entry(kind, new["value"], new["true_from"], time,
                                            new["citations"], index))
            feed.append({"domain": self.domain, "field": name, "type": kind, "from": old["value"],
                         "to": new["value"], "true_from": new["true_from"], "learned_at": time})
        return feed

    def recorded_builds(self, settled: bool) -> list[Build]:
        """The builds to export: a running one left out when settled, else kept as failed."""
        if settled:
            return [Build(b.time, b.outcome, b.shown, b.versions) for b in self.builds
                    if b.outcome != "building"]
        return [Build(b.time, "failed", b.spent) if b.outcome == "building" else b for b in self.builds]

    def recorded_state(self, settled: bool) -> str:
        if self.state != "building":
            return self.state
        return self.before_build if settled else "failed"
