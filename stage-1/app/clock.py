"""The service clock (§3.4): system time until set, then still until moved."""

from __future__ import annotations

import re
from datetime import datetime, timezone

_RFC3339 = re.compile(
    r"\d{4}-\d{2}-\d{2}[Tt ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})")


def parse_rfc3339(text: str) -> datetime | None:
    """An RFC 3339 timestamp with an explicit offset, or None."""
    if not _RFC3339.fullmatch(text):
        return None
    normal = text[:10] + "T" + text[11:]
    if normal[-1] in "Zz":
        normal = normal[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(normal)
    except ValueError:
        return None


class Clock:
    def __init__(self) -> None:
        self._fixed: datetime | None = None

    def now(self) -> datetime:
        return self._fixed or datetime.now(timezone.utc)

    def set(self, moment: datetime) -> None:
        self._fixed = moment

    def iso(self) -> str:
        return self.now().isoformat()
