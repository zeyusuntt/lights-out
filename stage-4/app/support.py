"""Appendix A of the specification: when an excerpt supports a value for a field."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

FIELDS = ("legal_name", "hq_city", "ceo", "founded_year", "headcount_range", "funding_total")
TITLES = ("cfo", "coo", "cto")
PERSON_FIELDS = ("ceo",) + TITLES
INVESTORS = "investors"
INVESTOR_ENDINGS = ("Ventures", "Capital", "Partners", "Fund", "Investments", "Holdings", "Equity")

STATEMENT_PHRASES = {
    "legal_name": ("legal name", "registered name", "registered as", "registered company",
                   "legal entity", "name of record"),
    "hq_city": ("headquartered in", "headquarters in", "head office in", "based in",
                "registered office in", "registered seat in"),
    "ceo": ("chief executive officer", "chief executive", "CEO"),
    "cfo": ("chief financial officer", "CFO"),
    "coo": ("chief operating officer", "COO"),
    "cto": ("chief technology officer", "CTO"),
    "investors": ("investor", "investors", "led by", "backed by", "participated"),
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


Found = tuple[int, int, object]


def _legal_names(text: str, domain: str) -> list[Found]:
    values = []
    words = {s: e for s, e in _words(text, upper_too=True)}
    for start, pos in _name_spans(text, domain):
        while True:
            end = _suffix_end(text, pos)
            if end is not None:
                values.append((start, end, text[start:end]))
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


def _capitalised_runs(text: str) -> list[tuple[int, int, int]]:
    return _runs(text, _words(text, upper_too=False), " -")


def _cities(text: str) -> list[Found]:
    runs = {start: end for start, end, _ in _capitalised_runs(text)}
    values = []
    for phrase in STATEMENT_PHRASES["hq_city"]:
        for _, end in find_phrase(text, phrase):
            if end < len(text) and text[end] == " " and end + 1 in runs:
                values.append((end + 1, runs[end + 1], text[end + 1:runs[end + 1]]))
    return values


def _people(text: str, domain: str, field: str) -> list[Found]:
    """People's names, after taking out the company's name and the field's statement phrases."""
    masked = list(text)
    for start, end in _name_spans(text, domain) + _phrase_spans(text, field):
        masked[start:end] = "\x00" * (end - start)
    plain = "".join(masked)
    return [(s, e, text[s:e]) for s, e, count in _runs(plain, _words(plain, upper_too=False), " ")
            if count in (2, 3)]


def _investors(text: str, domain: str) -> list[Found]:
    """Investor names: runs of two or more capitalised words ending in a fund word, and, in an
    excerpt with an amount, the run directly after `led by` or `backed by`."""
    masked = list(text)
    for start, end in _name_spans(text, domain) + _phrase_spans(text, INVESTORS):
        masked[start:end] = "\x00" * (end - start)
    plain = "".join(masked)
    runs = {s: (e, count) for s, e, count in _runs(plain, _words(plain, upper_too=False), " ")}
    found = {s: e for s, (e, count) in runs.items()
             if count >= 2 and text[s:e].split(" ")[-1] in INVESTOR_ENDINGS}
    if amounts(text):
        for phrase in ("led by", "backed by"):
            for _, end in find_phrase(text, phrase):
                if text[end:end + 1] == " " and end + 1 in runs:
                    found[end + 1] = runs[end + 1][0]
    return [(s, e, text[s:e]) for s, e in sorted(found.items())]


def _headcount_bucket(n: int) -> str:
    for low, high, label in HEADCOUNT_RANGES:
        if low <= n <= high:
            return label
    return "10001+"


def _phrase_spans(text: str, field: str) -> list[tuple[int, int]]:
    return [span for phrase in STATEMENT_PHRASES[field] for span in find_phrase(text, phrase)]


def found_values(field: str, text: str, domain: str) -> list[Found]:
    """Every value in the field's format that the text contains, normalised (A.5), with its span."""
    if field == "legal_name":
        return _legal_names(text, domain)
    if field == "hq_city":
        return _cities(text)
    if field in PERSON_FIELDS:
        return _people(text, domain, field)
    if field == INVESTORS:
        return _investors(text, domain)
    if field == "founded_year":
        return [(s, e, int(v)) for s, e, v in numbers(text)
                if e - s == 4 and isinstance(v, int) and 1800 <= v <= 2099]
    if field == "headcount_range":
        return [(s, e, _headcount_bucket(v)) for s, e, v in numbers(text)
                if isinstance(v, int) and v >= 1]
    if field == "funding_total":
        return [(a.start, a.end, a.dollars) for a in amounts(text) if a.dollars is not None]
    raise ValueError(field)


def values_in_format(field: str, text: str, domain: str) -> list[object]:
    return [v for _, _, v in found_values(field, text, domain)]


# A.2 the rule --------------------------------------------------------------------

def supported_values(excerpt: str, field: str, domain: str) -> list[object]:
    """The values this excerpt supports for the field of the company: by A.2 the one value all
    its values normalise to; for investors, each investor name it contains."""
    text = collapse(excerpt)
    if not text or not is_single_sentence(text) or not _name_spans(text, domain):
        return []
    if not _phrase_spans(text, field) or any(find_phrase(text, p) for p in NEGATING_PHRASES):
        return []
    values = values_in_format(field, text, domain)
    if field == INVESTORS:
        return list(dict.fromkeys(values))
    if not values or any(v != values[0] for v in values):
        return []
    return values[:1]


def supported_value(excerpt: str, field: str, domain: str) -> str | int | None:
    """The value V this excerpt supports for the field of the company, or None."""
    values = supported_values(excerpt, field, domain)
    return values[0] if values else None


MAX_CITATION = 500



def _edges(text: str) -> tuple[list[int], list[int]]:
    """For each position, the furthest a citation edge there must move left or right so as
    not to cut a word, an amount or a run of capitalised words."""
    protected = [m.span() for m in re.finditer(r"\S+", text)]
    protected += [(a.start, a.end) for a in amounts(text)]
    protected += [(s, e) for s, e, _ in _capitalised_runs(text)]
    left, right = list(range(len(text) + 1)), list(range(len(text) + 1))
    for s, e in protected:
        for i in range(s + 1, e):
            left[i], right[i] = min(left[i], s), max(right[i], e)
    return left, right


def _widen(start: int, end: int, left: list[int], right: list[int]) -> tuple[int, int]:
    while (left[start], right[end]) != (start, end):
        start, end = left[start], right[end]
    return start, end


def _nearest(spans: list[tuple[int, int]], start: int, end: int) -> list[tuple[int, int]]:
    """The occurrences closest to a value on each side, and any overlapping it. A farther
    occurrence on the same side only widens the span around these, adding text, so it can
    support the value only if one of these does."""
    before = max((s for s in spans if s[1] <= start), key=lambda s: s[1], default=None)
    after = min((s for s in spans if s[0] >= end), key=lambda s: s[0], default=None)
    overlapping = [s for s in spans if s[0] < end and start < s[1]]
    return [s for s in dict.fromkeys([before, after, *overlapping]) if s is not None]


@lru_cache(maxsize=8192)
def citable(excerpt: str, field: str, domain: str, want: object | None = None) -> tuple[object, str] | None:
    """(value, citation text) for a sentence (R1-6, R1-7). A sentence of at most 500
    characters is judged and cited whole. A longer one is cited by the shortest span of at
    most 500 characters that covers a value with one of the nearest names and statement
    phrases on either side of it, cuts no word, amount or capitalised run, and supports that
    value on its own."""
    text = collapse(excerpt)
    if len(text) <= MAX_CITATION:
        values = supported_values(text, field, domain)
        value = values[0] if want is None and values else want
        return (value, text) if value is not None and value in values else None
    if not is_single_sentence(text):
        return None
    names, phrases = _name_spans(text, domain), _phrase_spans(text, field)
    values = [v for v in found_values(field, text, domain) if want in (None, v[2])]
    left, right = _edges(text)
    best: tuple[object, str] | None = None
    for vs, ve, value in values:
        for ns, ne in _nearest(names, vs, ve):
            for ps, pe in _nearest(phrases, vs, ve):
                start, end = _widen(min(vs, ns, ps), max(ve, ne, pe), left, right)
                if end - start > MAX_CITATION or (best and end - start >= len(best[1])):
                    continue
                span = text[start:end].strip()
                if value in supported_values(span, field, domain):
                    best = (value, span)
    return best


def citations_in(sentence: str, field: str, domain: str) -> list[tuple[object, str]]:
    """(value, citation text) for every value a sentence supports for the field."""
    if field != INVESTORS:
        hit = citable(sentence, field, domain)
        return [hit] if hit else []
    names = dict.fromkeys(v for _, _, v in found_values(field, collapse(sentence), domain))
    return [hit for name in names if (hit := citable(sentence, field, domain, name))]
