"""Served page texts: header lines, prose, and the excerpts a page can be cited by."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .support import collapse, split_line

_HEADER_LINE = re.compile(r"[^\W\d_][^\W\d_]+(?:-[^\W\d_][^\W\d_]+)*:(?: |$)")
MAX_EXCERPT = 500


def _is_header_line(line: str) -> bool:
    m = _HEADER_LINE.match(line)
    if not m:
        return False
    name = line[:line.index(":")]
    return all(part[0].isupper() and part[1:].islower() for part in name.split("-"))


def prose_of(served_text: str) -> str:
    """The prose of a served text: everything after the header, if it has one."""
    lines = served_text.split("\n")
    if not lines or not _is_header_line(lines[0].rstrip("\r")):
        return served_text
    for i, line in enumerate(lines):
        if not line.strip():
            return "\n".join(lines[i + 1:])
    return ""


@dataclass
class PageText:
    """Text a provider served for one URL, as prose to cite from."""

    url: str
    prose: str
    complete: bool

    def excerpts(self) -> list[str]:
        """Each complete sentence of the prose, whitespace collapsed, within the length limit."""
        lines = self.prose.splitlines()
        result = []
        for index, line in enumerate(lines):
            sentences = split_line(line)
            if not self.complete and index == len(lines) - 1:
                sentences = sentences[:-1]
            result.extend(c for c in map(collapse, sentences) if 1 <= len(c) <= MAX_EXCERPT)
        return result

    def contains(self, excerpt: str) -> bool:
        return collapse(excerpt) in collapse(self.prose)
