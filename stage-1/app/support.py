"""Appendix A of the specification: when an excerpt supports a value for a field."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

FIELDS = ("legal_name", "hq_city", "ceo", "founded_year", "headcount_range", "funding_total")

STATEMENT_PHRASES = {
    "legal_name": ("legal name", "registered name", "registered as", "registered company",
                   "legal entity", "name of record"),
    "hq_city": ("headquartered in", "headquarters in", "head office in", "based in",
                "registered office in", "registered seat in"),
    "ceo": ("chief executive officer", "chief executive", "CEO"),
    "founded_year": ("founded", "founding", "established", "incorporated"),
    "headcount_range": ("employs", "employees", "staff", "people", "headcount", "workforce"),
    "funding_total": ("raised", "funding", "invested", "investment"),
}

NEGATING_PHRASES = ("in talks to", "plans to", "planning to", "wants to", "expects to",
                    "hopes to", "aims to", "seeking", "could", "would", "might", "reportedly",
                    "rumoured", "former", "formerly", "will become", "not")

LEGAL_SUFFIXES = ("Inc.", "Corp.", "LLC", "LLP", "L.P.", "Ltd", "Limited", "Pty Ltd", "plc",
                  "PLC", "GmbH", "AG", "KG", "SE", "AS", "A/S", "ASA", "AB", "Oy", "Oyj",
                  "B.V.", "N.V.", "S.A.", "S.A.S.", "S.L.", "S.r.l.", "S.p.A.", "s.r.o.",
                  "a.s.", "K.K.")
_DOTTED_SUFFIXES = tuple(s for s in LEGAL_SUFFIXES if s.endswith("."))

HEADCOUNT_RANGES = ((1, 10, "1-10"), (11, 50, "11-50"), (51, 200, "51-200"),
                    (201, 500, "201-500"), (501, 1000, "501-1000"), (1001, 5000, "1001-5000"),
                    (5001, 10000, "5001-10000"))

_TERMINATORS = ".!?"
_CLOSERS = "\"”’)"


def is_alnum(ch: str) -> bool:
    return ch.isalpha() or ch.isdigit()


def _bounded(text: str, start: int, end: int) -> bool:
    before = text[start - 1] if start > 0 else ""
    after = text[end] if end < len(text) else ""
    return not (before and is_alnum(before)) and not (after and is_alnum(after))


def find_phrase(text: str, phrase: str) -> list[tuple[int, int]]:
    """Case-insensitive whole-word occurrences of a phrase, as (start, end) spans."""
    pattern = re.compile(re.escape(phrase), re.IGNORECASE)
    spans, pos = [], 0
    while (m := pattern.search(text, pos)) is not None:
        if _bounded(text, *m.span()):
            spans.append(m.span())
        pos = m.start() + 1
    return spans


def collapse(text: str) -> str:
    return " ".join(text.split())


# A.1 sentences ---------------------------------------------------------------

def _ends_with_suffix(line: str, dot: int) -> bool:
    for suffix in _DOTTED_SUFFIXES:
        start = dot + 1 - len(suffix)
        if start >= 0 and line[start:dot + 1] == suffix and (start == 0 or not is_alnum(line[start - 1])):
            return True
    return False


def split_line(line: str) -> list[str]:
    sentences, start, i, n = [], 0, 0, len(line)
    while i < n:
        if line[i] in _TERMINATORS:
            j = i + 1
            while j < n and line[j] in _CLOSERS:
                j += 1
            if j < n and line[j].isspace() and not (line[i] == "." and _ends_with_suffix(line, i)):
                sentences.append(line[start:j])
                start = j
            i = j
        else:
            i += 1
    sentences.append(line[start:])
    return [s.strip() for s in sentences if s.strip()]


def split_prose(prose: str) -> list[str]:
    return [s for line in prose.splitlines() for s in split_line(line)]


def is_single_sentence(excerpt: str) -> bool:
    return len(split_line(collapse(excerpt))) == 1


# A.4 value formats -------------------------------------------------------------

def _words(text: str, upper_too: bool) -> list[tuple[int, int]]:
    """Spans of capitalised (and, optionally, uppercase) words."""
    spans, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch.isupper() and (i == 0 or not is_alnum(text[i - 1])):
            j = i + 1
            while j < n and text[j].islower():
                j += 1
            if j - i >= 2 and (j == n or not is_alnum(text[j])):
                spans.append((i, j))
                i = j
                continue
            if upper_too:
                k = i + 1
                while k < n and text[k].isupper():
                    k += 1
                if k - i >= 2 and (k == n or not is_alnum(text[k])):
                    spans.append((i, k))
                    i = k
                    continue
        i += 1
    return spans


def _runs(text: str, words: list[tuple[int, int]], joiners: str) -> list[tuple[int, int, int]]:
    """Maximal runs of words joined by one joiner character: (start, end, word count)."""
    runs: list[tuple[int, int, int]] = []
    for start, end in words:
        if runs and start - runs[-1][1] == 1 and text[runs[-1][1]] in joiners:
            runs[-1] = (runs[-1][0], end, runs[-1][2] + 1)
        else:
            runs.append((start, end, 1))
    return runs


_NUMBER_TOKEN = re.compile(r"\d+(?:[.,]\d+)*")
_VALID_NUMBER = re.compile(r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?")
_NUM = r"(?<!\d[.,])(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?![.,]?\d)"
_AMOUNT_PREFIXED = re.compile(
    r"(?<![^\W_])(?:US\$|USD|\$) ?(?P<num>" + _NUM + r")"
    r"(?:(?P<short>mn|bn|k|m)|(?: (?P<word>thousand|million|billion)))?(?![^\W_])",
    re.IGNORECASE)
_AMOUNT_DOLLARS = re.compile(
    r"(?<![^\W_])(?P<num>" + _NUM + r")(?: (?P<word>thousand|million|billion))? (?:US )?dollars(?![^\W_])",
    re.IGNORECASE)
_SCALES = {"k": 1_000, "thousand": 1_000, "m": 1_000_000, "mn": 1_000_000,
           "million": 1_000_000, "bn": 1_000_000_000, "billion": 1_000_000_000}


@dataclass(frozen=True)
class Amount:
    start: int
    end: int
    dollars: int | None


def _number_value(token: str) -> float | int:
    plain = token.replace(",", "")
    return float(plain) if "." in plain else int(plain)


def amounts(text: str) -> list[Amount]:
    found = []
    for pattern in (_AMOUNT_PREFIXED, _AMOUNT_DOLLARS):
        for m in pattern.finditer(text):
            scale_word = (m.groupdict().get("short") or m.group("word") or "").lower()
            number = m.group("num").replace(",", "")
            whole, _, fraction = number.partition(".")
            scale = _SCALES.get(scale_word, 1)
            total = int(whole) * scale
            frac_value = int(fraction) * scale if fraction else 0
            frac_digits = 10 ** len(fraction) if fraction else 1
            dollars = total + frac_value // frac_digits if frac_value % frac_digits == 0 else None
            found.append(Amount(m.start(), m.end(), dollars))
    return found


def numbers(text: str) -> list[tuple[int, int, float | int]]:
    """Numbers (A.4) outside amounts, with their spans."""
    inside = [(a.start, a.end) for a in amounts(text)]
    result = []
    for m in _NUMBER_TOKEN.finditer(text):
        start, end = m.span()
        if not _VALID_NUMBER.fullmatch(m.group()):
            continue
        if (start > 0 and text[start - 1].isalpha()) or (end < len(text) and text[end].isalpha()):
            continue
        if any(a <= start and end <= b for a, b in inside):
            continue
        result.append((start, end, _number_value(m.group())))
    return result


def _name_spans(text: str, domain: str) -> list[tuple[int, int]]:
    return find_phrase(text, domain) + find_phrase(text, company_name(domain))


def company_name(domain: str) -> str:
    return domain.split(".")[0].replace("-", " ")


def _legal_names(text: str, domain: str) -> list[str]:
    values = []
    words = {s: e for s, e in _words(text, upper_too=True)}
    for start, pos in _name_spans(text, domain):
        while True:
            end = _suffix_end(text, pos)
            if end is not None:
                values.append(text[start:end])
                break
            if pos < len(text) and text[pos] == " " and pos + 1 in words:
                pos = words[pos + 1]
            else:
                break
    return values


def _suffix_end(text: str, pos: int) -> int | None:
    rest = text[pos:]
    lead = 2 if rest.startswith(", ") else 1 if rest.startswith(" ") else 0
    if not lead:
        return None
    best = None
    for suffix in LEGAL_SUFFIXES:
        end = pos + lead + len(suffix)
        if text[pos + lead:end] == suffix and (end == len(text) or not is_alnum(text[end])):
            best = end if best is None else min(best, end)
    return best


def _cities(text: str) -> list[str]:
    runs = {start: end for start, end, _ in _runs(text, _words(text, upper_too=False), " -")}
    values = []
    for phrase in STATEMENT_PHRASES["hq_city"]:
        for _, end in find_phrase(text, phrase):
            if end < len(text) and text[end] == " " and end + 1 in runs:
                values.append(text[end + 1:runs[end + 1]])
    return values


def _people(text: str, domain: str) -> list[str]:
    masked = list(text)
    for start, end in _name_spans(text, domain) + [
            span for phrase in STATEMENT_PHRASES["ceo"] for span in find_phrase(text, phrase)]:
        masked[start:end] = "\x00" * (end - start)
    plain = "".join(masked)
    return [text[s:e] for s, e, count in _runs(plain, _words(plain, upper_too=False), " ")
            if count in (2, 3)]


def _headcount_bucket(n: int) -> str:
    for low, high, label in HEADCOUNT_RANGES:
        if low <= n <= high:
            return label
    return "10001+"


def values_in_format(field: str, text: str, domain: str) -> list[str | int]:
    """Every value in the field's format that the text contains, normalised (A.5)."""
    if field == "legal_name":
        return _legal_names(text, domain)
    if field == "hq_city":
        return _cities(text)
    if field == "ceo":
        return _people(text, domain)
    if field == "founded_year":
        return [int(v) for s, e, v in numbers(text)
                if e - s == 4 and isinstance(v, int) and 1800 <= v <= 2099]
    if field == "headcount_range":
        return [_headcount_bucket(v) for _, _, v in numbers(text) if isinstance(v, int) and v >= 1]
    if field == "funding_total":
        return [a.dollars for a in amounts(text) if a.dollars is not None]
    raise ValueError(field)


# A.2 the rule --------------------------------------------------------------------

def supported_value(excerpt: str, field: str, domain: str) -> str | int | None:
    """The value V this excerpt supports for the field of the company, or None."""
    text = collapse(excerpt)
    if not text or not is_single_sentence(text):
        return None
    if not _name_spans(text, domain):
        return None
    if not any(find_phrase(text, p) for p in STATEMENT_PHRASES[field]):
        return None
    if any(find_phrase(text, p) for p in NEGATING_PHRASES):
        return None
    values = values_in_format(field, text, domain)
    if not values or any(v != values[0] for v in values):
        return None
    return values[0]


def supports(excerpt: str, field: str, domain: str, value: str | int) -> bool:
    found = supported_value(excerpt, field, domain)
    return found is not None and found == value


MAX_CITATION = 500
MAX_SPAN_CHECKS = 2000


def _word_bounds(text: str) -> tuple[list[int], list[int]]:
    starts = [i for i in range(len(text)) if text[i] != " " and (i == 0 or text[i - 1] == " ")]
    ends = [i + 1 for i in range(len(text)) if text[i] != " " and (i + 1 == len(text) or text[i + 1] == " ")]
    return starts, ends


@lru_cache(maxsize=8192)
def citable(excerpt: str, field: str, domain: str, want: object | None = None) -> tuple[object, str] | None:
    """(value, citation text) for a sentence: the sentence itself when it fits in 500
    characters, else the longest span of whole words of it, at most 500 characters,
    that on its own supports a value (the wanted one, when given)."""
    text = collapse(excerpt)
    if len(text) <= MAX_CITATION:
        value = supported_value(text, field, domain)
        return (value, text) if value is not None and want in (None, value) else None
    if not _name_spans(text, domain) or not any(find_phrase(text, p) for p in STATEMENT_PHRASES[field]):
        return None
    starts, ends = _word_bounds(text)
    best: tuple[object, str] | None = None
    checks = 0
    for start in starts:
        fitting = [e for e in ends if start < e <= start + MAX_CITATION]
        for end in reversed(fitting):
            if best is not None and end - start <= len(best[1]):
                break
            checks += 1
            if checks > MAX_SPAN_CHECKS:
                return best
            value = supported_value(text[start:end], field, domain)
            if value is not None and want in (None, value):
                best = (value, text[start:end])
                break
    return best
