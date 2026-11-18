"""Candidates, the selection rule, members, status and origins (stages 2 to 4)."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, replace

from .clock import parse_rfc3339
from .domains import host_of
from .support import FIELDS, INVESTORS, TITLES

EXECUTIVES = "executives"
ALL_FIELDS = FIELDS + (EXECUTIVES, INVESTORS)
MEMBER_KINDS = ("own", "filing")
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
    origin: str | None = None

    @property
    def source(self) -> str:
        """The candidate's origin; for an imported one that records none, its URL's host."""
        return self.origin or host_of(self.url)

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
                     "true_from": self.true_from, "learned_at": learned_at, "origin": self.source,
                     "selected": selected})
        return data

    def to_record(self) -> dict:
        return {"value": self.value, "url": self.url, "excerpt": self.excerpt,
                "provider": self.provider, "kind": self.kind, "published_at": self.published_at,
                "retrieved_at": self.retrieved_at, "true_from": self.true_from, "title": self.title,
                "origin": self.source}

    @classmethod
    def from_record(cls, data: dict) -> Candidate:
        return cls(data["value"], data["url"], data["excerpt"], data["provider"], data.get("kind"),
                   data.get("published_at"), data["retrieved_at"], data.get("true_from"),
                   data.get("title"), data.get("origin"))


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


Groups = list[tuple[object, list[Candidate]]]


def member_groups(name: str, candidates: list[Candidate]) -> Groups:
    """The selected value's members, each with its candidates in rank order: the selected value
    of a scalar field, each title's selected person, or each investor that is a member."""
    order = ranked(candidates)
    if name == EXECUTIVES:
        groups = []
        for title in TITLES:
            mine = [c for c in order if c.title == title]
            if mine:
                groups.append(((title, mine[0].value), [c for c in mine if same_value(c.value, mine[0].value)]))
        return groups
    if name == INVESTORS:
        names = sorted({c.value for c in order})
        groups = [(n, [c for c in order if c.value == n]) for n in names]
        return [(n, cs) for n, cs in groups
                if any(c.kind in MEMBER_KINDS for c in cs) or len({c.source for c in cs}) >= 2]
    if not order:
        return []
    return [(order[0].value, [c for c in order if same_value(c.value, order[0].value)])]


def unknown_view() -> dict:
    return {"value": None, "status": "unknown", "true_from": None, "learned_at": None,
            "citations": [], "candidates": [], "origins": [], "corroborated": False,
            "corroborated_since": None}


def _origins(groups: Groups) -> dict:
    origins = sorted({c.source for _, cs in groups for c in cs})
    corroborated = bool(groups) and all(len({c.source for c in cs}) >= 2 for _, cs in groups)
    return {"origins": origins, "corroborated": corroborated, "corroborated_since": None}


def _status(groups: Groups, order: list[Candidate], name: str) -> str:
    if name == INVESTORS:
        return "known"
    keys = {(c.title, json.dumps(_stripped(c.value))) for c in order}
    titles = {c.title for c in order}
    return "contested" if len(keys) > len(titles) else "known"


def _true_from(name: str, groups: Groups) -> str | None:
    if name == INVESTORS:
        dates = [min((c.true_from for c in cs if c.true_from), default=None) for _, cs in groups]
    else:
        dates = [cs[0].true_from for _, cs in groups]
    if name in FIELDS:
        return dates[0]
    return None if None in dates else max(dates)


def _value(name: str, groups: Groups) -> object:
    if name == EXECUTIVES:
        return [{"title": t, "name": n} for (t, n), _ in groups]
    if name == INVESTORS:
        return [n for n, _ in groups]
    return groups[0][0]


def field_view(name: str, candidates: list[Candidate], learned: Learned) -> dict:
    """A field: selected value, status, true_from, citations, ranked candidates and origins."""
    groups = member_groups(name, candidates)
    order = ranked(candidates)
    if name == EXECUTIVES:
        order = [c for t in TITLES for c in order if c.title == t]
    selected = {id(c) for _, cs in groups for c in (cs if name == INVESTORS else cs[:1])}
    candidates_json = [c.as_json(id(c) in selected, learned(name, c)) for c in order]
    if not groups:
        return {**unknown_view(), "candidates": candidates_json}
    return {
        "value": _value(name, groups),
        "status": _status(groups, order, name),
        "true_from": _true_from(name, groups),
        "learned_at": None,
        "citations": [cite for _, cs in groups for cite in _cite(cs)],
        "candidates": candidates_json,
        **_origins(groups),
    }


def fields_view(by_field: dict[str, list[Candidate]], learned: Learned) -> dict[str, dict]:
    return {name: field_view(name, by_field.get(name, []), learned) for name in ALL_FIELDS}


def values_view(by_field: dict[str, list[Candidate]]) -> dict[str, dict]:
    """The value, true_from and citations of each field chosen from the given candidates."""
    views = fields_view(by_field, lambda _n, _c: None)
    return {name: {"value": v["value"], "true_from": v["true_from"], "citations": v["citations"]}
            for name, v in views.items()}
