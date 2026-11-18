"""Candidates, the selection rule and field status (stage 2)."""

from __future__ import annotations

from dataclasses import dataclass

from .clock import parse_rfc3339
from .support import FIELDS

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

    def rank_key(self) -> tuple:
        published = parse_rfc3339(self.published_at) if self.published_at else None
        recency = (1, 0.0) if published is None else (0, -published.timestamp())
        value = self.value.strip() if isinstance(self.value, str) else self.value
        return (AUTHORITY[self.kind], recency, self.url, PROVIDER_ORDER.get(self.provider, 9),
                _value_key(value))

    def as_json(self, selected: bool) -> dict:
        return {"value": self.value, "url": self.url, "excerpt": self.excerpt,
                "provider": self.provider, "kind": self.kind, "published_at": self.published_at,
                "retrieved_at": self.retrieved_at, "selected": selected}

    @classmethod
    def from_json(cls, data: dict) -> Candidate:
        return cls(data["value"], data["url"], data["excerpt"], data["provider"], data["kind"],
                   data["published_at"], data["retrieved_at"])


def _value_key(value: object) -> tuple:
    return (0, value, "") if isinstance(value, int) else (1, 0, value)


def same_value(a: object, b: object) -> bool:
    if isinstance(a, str) and isinstance(b, str):
        return a.strip() == b.strip()
    return type(a) is type(b) and a == b


def field_view(candidates: list[Candidate]) -> dict:
    """A field as the API shows it: selected value, status, citations and ranked candidates."""
    ranked = sorted(candidates, key=Candidate.rank_key)
    if not ranked:
        return {"value": None, "status": "unknown", "citations": [], "candidates": []}
    chosen = ranked[0].value
    distinct = []
    for c in ranked:
        if not any(same_value(c.value, d) for d in distinct):
            distinct.append(c.value)
    return {
        "value": chosen,
        "status": "known" if len(distinct) == 1 else "contested",
        "citations": [{"url": c.url, "excerpt": c.excerpt, "provider": c.provider}
                      for c in ranked if same_value(c.value, chosen)],
        "candidates": [c.as_json(i == 0) for i, c in enumerate(ranked)],
    }


def fields_view(by_field: dict[str, list[Candidate]]) -> dict[str, dict]:
    return {name: field_view(by_field.get(name, [])) for name in FIELDS}
