"""Candidates, the selection rule and field status (stages 2 and 3)."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, replace

from .clock import parse_rfc3339
from .support import FIELDS, TITLES

EXECUTIVES = "executives"
ALL_FIELDS = FIELDS + (EXECUTIVES,)
KINDS = ("own", "filing", "news", "aggregator")
AUTHORITY = {"own": 0, "filing": 0, "news": 1, "aggregator": 2, None: 2}
PROVIDER_ORDER = {"nimble": 0, "tavily": 1, "kernel": 2, "browserbase": 3}


@dataclass(frozen=True)
class Candidate:
    value: object
    url: str
    excerpt: str
    provider: str
    kind: str | None
    published_at: str | None
    retrieved_at: str
    true_from: str | None = None
    title: str | None = None

    def rank_key(self) -> tuple:
        published = parse_rfc3339(self.published_at) if self.published_at else None
        recency = (1, 0.0) if published is None else (0, -published.timestamp())
        value = self.value.strip() if isinstance(self.value, str) else self.value
        return (AUTHORITY[self.kind], recency, self.url, PROVIDER_ORDER.get(self.provider, 9),
                _value_key(value))

    def identity(self, field: str) -> tuple:
        """Field, title, value, URL and provider: what makes two candidates the same one."""
        return (field, self.title, json.dumps(_stripped(self.value)), self.url, self.provider)

    def retrieved(self, at: str) -> Candidate:
        return replace(self, retrieved_at=at)

    def as_json(self, selected: bool, learned_at: str | None) -> dict:
        data = {"title": self.title} if self.title else {}
        data.update({"value": self.value, "url": self.url, "excerpt": self.excerpt,
                     "provider": self.provider, "kind": self.kind,
                     "published_at": self.published_at, "retrieved_at": self.retrieved_at,
                     "true_from": self.true_from, "learned_at": learned_at, "selected": selected})
        return data

    def to_record(self) -> dict:
        return {"value": self.value, "url": self.url, "excerpt": self.excerpt,
                "provider": self.provider, "kind": self.kind, "published_at": self.published_at,
                "retrieved_at": self.retrieved_at, "true_from": self.true_from, "title": self.title}

    @classmethod
    def from_record(cls, data: dict) -> Candidate:
        return cls(data["value"], data["url"], data["excerpt"], data["provider"], data.get("kind"),
                   data.get("published_at"), data["retrieved_at"], data.get("true_from"),
                   data.get("title"))


Learned = Callable[[str, Candidate], str | None]


def _stripped(value: object) -> object:
    return value.strip() if isinstance(value, str) else value


def _value_key(value: object) -> tuple:
    return (0, value, "") if isinstance(value, int) else (1, 0, value)


def same_value(a: object, b: object) -> bool:
    if isinstance(a, str) and isinstance(b, str):
        return a.strip() == b.strip()
    return type(a) is type(b) and a == b


def ranked(candidates: list[Candidate]) -> list[Candidate]:
    return sorted(candidates, key=Candidate.rank_key)


def _distinct(values: list[object]) -> list[object]:
    out: list[object] = []
    for v in values:
        if not any(same_value(v, d) for d in out):
            out.append(v)
    return out


def _cite(candidates: list[Candidate]) -> list[dict]:
    return [{"url": c.url, "excerpt": c.excerpt, "provider": c.provider} for c in candidates]


def unknown_view() -> dict:
    return {"value": None, "status": "unknown", "true_from": None, "learned_at": None,
            "citations": [], "candidates": []}


def field_view(name: str, candidates: list[Candidate], learned: Learned) -> dict:
    """One of the six fields: selected value, status, true_from, citations and ranked candidates."""
    order = ranked(candidates)
    if not order:
        return unknown_view()
    chosen = order[0]
    return {
        "value": chosen.value,
        "status": "known" if len(_distinct([c.value for c in order])) == 1 else "contested",
        "true_from": chosen.true_from,
        "learned_at": None,
        "citations": _cite([c for c in order if same_value(c.value, chosen.value)]),
        "candidates": [c.as_json(i == 0, learned(name, c)) for i, c in enumerate(order)],
    }


def executives_view(candidates: list[Candidate], learned: Learned) -> dict:
    """The executives field: one member per title that has a selected person."""
    by_title = {t: ranked([c for c in candidates if c.title == t]) for t in TITLES}
    members = [(t, cands[0]) for t, cands in by_title.items() if cands]
    if not members:
        return unknown_view()
    dates = [c.true_from for _, c in members]
    contested = any(len(_distinct([c.value for c in cands])) > 1 for cands in by_title.values())
    return {
        "value": [{"title": t, "name": c.value} for t, c in members],
        "status": "contested" if contested else "known",
        "true_from": None if None in dates else max(dates),
        "learned_at": None,
        "citations": [cite for t, chosen in members
                      for cite in _cite([c for c in by_title[t] if same_value(c.value, chosen.value)])],
        "candidates": [c.as_json(i == 0, learned(EXECUTIVES, c))
                       for cands in by_title.values() for i, c in enumerate(cands)],
    }


def fields_view(by_field: dict[str, list[Candidate]], learned: Learned) -> dict[str, dict]:
    views = {name: field_view(name, by_field.get(name, []), learned) for name in FIELDS}
    views[EXECUTIVES] = executives_view(by_field.get(EXECUTIVES, []), learned)
    return views


def values_view(by_field: dict[str, list[Candidate]]) -> dict[str, dict]:
    """The value, true_from and citations of each field chosen from the given candidates."""
    views = fields_view(by_field, lambda _n, _c: None)
    return {name: {"value": v["value"], "true_from": v["true_from"], "citations": v["citations"]}
            for name, v in views.items()}
