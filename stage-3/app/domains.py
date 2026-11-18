"""Domain normalisation and validation (§4)."""

from __future__ import annotations

import re

_LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?")


def normalise(raw: str) -> str | None:
    """The normalised domain, or None when it is not a valid host name."""
    domain = raw.strip().lower()
    if domain.endswith("."):
        domain = domain[:-1]
    if domain.startswith("www."):
        domain = domain[4:]
    labels = domain.split(".")
    if len(domain) > 253 or len(labels) < 2 or not all(_LABEL.fullmatch(l) for l in labels):
        return None
    return domain
