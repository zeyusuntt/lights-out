"""Served page texts: header lines, prose, and the excerpts a page can be cited by."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timezone

from .candidates import KINDS
from .clock import parse_rfc3339
from .domains import host_of, normalise
from .support import collapse, split_line

_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_HEADER_LINE = re.compile(r"[^\W\d_][^\W\d_]+(?:-[^\W\d_][^\W\d_]+)*:(?: |$)")


def is_header_line(line: str) -> bool:
    m = _HEADER_LINE.match(line)
    if not m:
        return False
    name = line[:line.index(":")]
    return all(part[0].isupper() and part[1:].islower() for part in name.split("-"))


def split_served(served_text: str) -> tuple[list[str], str]:
    """(header lines, prose) of a served text (§4, Pages)."""
    lines = served_text.split("\n")
    if not lines or not is_header_line(lines[0].rstrip("\r")):
        return [], served_text
    for i, line in enumerate(lines):
        if not line.strip():
            return lines[:i], "\n".join(lines[i + 1:])
    return lines, ""


def _header(lines: list[str], name: str) -> str | None:
    prefix = name + ":"
    return next((l[len(prefix):].strip() for l in lines if l.startswith(prefix)), None)


@dataclass(frozen=True)
class Lineage:
    """What a page's header says about who published it (stage 4)."""

    registrant: str
    canonical: str | None
    first_published_by: str | None
    lookalike: bool

    @classmethod
    def from_header(cls, lines: list[str], url: str) -> Lineage:
        registrant = normalise(_header(lines, "Registrant") or "") or host_of(url)
        canonical = _header(lines, "Canonical") or None
        first = normalise(_header(lines, "First-Published-By") or "")
        lookalike = _header(lines, "Kind") == "own" and registrant != host_of(url)
        return cls(registrant, canonical if canonical != url else None, first, lookalike)


def page_kind(lines: list[str], url: str, domain: str, registrant: str) -> str:
    """The page's kind: `own` only when the company's domain is the registrant."""
    kind = _header(lines, "Kind")
    if kind not in KINDS:
        kind = "own" if host_of(url) == domain else "aggregator"
    return "aggregator" if kind == "own" and registrant != domain else kind


def published_at(lines: list[str]) -> str | None:
    moment = parse_rfc3339(_header(lines, "Published") or "")
    return moment.isoformat() if moment else None


def valid_date(text: str | None) -> str | None:
    """A YYYY-MM-DD calendar date, or None."""
    if not text or not _DATE.fullmatch(text):
        return None
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        return None


def true_from(lines: list[str]) -> str | None:
    """The Effective date, else the UTC date of the publication time, else None."""
    effective = valid_date(_header(lines, "Effective"))
    if effective:
        return effective
    moment = parse_rfc3339(_header(lines, "Published") or "")
    return moment.astimezone(timezone.utc).date().isoformat() if moment else None


def sentences(prose: str) -> list[str]:
    """Each sentence of the prose, whitespace collapsed."""
    return [c for line in prose.splitlines() for c in map(collapse, split_line(line)) if c]


@dataclass
class PageText:
    """The browser text a provider served for one URL, with its kind and publication time."""

    url: str
    provider: str
    prose: str
    kind: str
    published_at: str | None
    true_from: str | None
    lineage: Lineage

    @classmethod
    def from_served(cls, url: str, provider: str, served_text: str, domain: str) -> PageText:
        lines, prose = split_served(served_text)
        lineage = Lineage.from_header(lines, url)
        return cls(url, provider, prose, page_kind(lines, url, domain, lineage.registrant),
                   published_at(lines), true_from(lines), lineage)

    def excerpts(self) -> list[str]:
        return sentences(self.prose)
