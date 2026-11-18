"""Independent implementation of stage-1 Appendix A ("When an excerpt supports a value"),
written from the specification text alone. Used by the acceptance suite to judge citations
and to compute which fields the evidence supports."""
import re

FIELDS = ["legal_name", "hq_city", "ceo", "founded_year", "headcount_range", "funding_total"]
RANGES = ["1-10", "11-50", "51-200", "201-500", "501-1000", "1001-5000", "5001-10000", "10001+"]

# A.3
STATEMENT = {
    "legal_name": ["legal name", "registered name", "registered as", "registered company",
                   "legal entity", "name of record"],
    "hq_city": ["headquartered in", "headquarters in", "head office in", "based in",
                "registered office in", "registered seat in"],
    "ceo": ["chief executive officer", "chief executive", "CEO"],
    "founded_year": ["founded", "founding", "established", "incorporated"],
    "headcount_range": ["employs", "employees", "staff", "people", "headcount", "workforce"],
    "funding_total": ["raised", "funding", "invested", "investment"],
    # stage 3 Executives: each title is a field with the format and normalisation of ceo
    "cfo": ["chief financial officer", "CFO"],
    "coo": ["chief operating officer", "COO"],
    "cto": ["chief technology officer", "CTO"],
}
TITLES = ["cfo", "coo", "cto"]
NEGATING = ["in talks to", "plans to", "planning to", "wants to", "expects to", "hopes to",
            "aims to", "seeking", "could", "would", "might", "reportedly", "rumoured", "former",
            "formerly", "will become", "not"]
# A.4 legal-form suffixes, matched exactly as written
SUFFIXES = ["Inc.", "Corp.", "LLC", "LLP", "L.P.", "Ltd", "Limited", "Pty Ltd", "plc", "PLC",
            "GmbH", "AG", "KG", "SE", "AS", "A/S", "ASA", "AB", "Oy", "Oyj", "B.V.", "N.V.",
            "S.A.", "S.A.S.", "S.L.", "S.r.l.", "S.p.A.", "s.r.o.", "a.s.", "K.K."]
DOT_SUFFIXES = [s for s in SUFFIXES if s.endswith(".")]
CLOSERS = "\"”’)"


def ws1(s):
    return re.sub(r"\s+", " ", s)


def is_an(c):
    return c.isalnum()


# ---------- A.1 sentences ----------
def split_line(line):
    out, start, i, n = [], 0, 0, len(line)
    while i < n:
        c = line[i]
        if c in ".!?":
            j = i + 1
            while j < n and line[j] in CLOSERS:
                j += 1
            if j < n and line[j].isspace():
                stop = True
                if c == ".":
                    head = line[: i + 1]
                    for s in DOT_SUFFIXES:
                        if head.endswith(s):
                            b = len(head) - len(s)
                            if b == 0 or not is_an(head[b - 1]):
                                stop = False
                                break
                if stop:
                    out.append(line[start:j])
                    start = j
                    i = j
                    continue
        i += 1
    out.append(line[start:])
    return [s.strip() for s in out if s.strip()]


def sentences(prose):
    res = []
    for line in prose.split("\n"):
        res.extend(split_line(line))
    return res


def is_single_sentence(excerpt):
    return len(split_line(ws1(excerpt))) == 1


# ---------- pages ----------
HEADER_RE = re.compile(r"^[A-Z][a-z]*(?:-[A-Z][a-z]*)*:( |$)")


def prose_of(text):
    lines = text.split("\n")
    if not lines or not HEADER_RE.match(lines[0]):
        return text
    for k, l in enumerate(lines):
        if l.strip() == "":
            return "\n".join(lines[k + 1:])
    return ""


# ---------- matching helpers ----------
def find_whole(text, phrase):
    """Case-insensitive whole-word occurrences (start, end)."""
    res = []
    tl, pl = text.lower(), phrase.lower()
    i = tl.find(pl)
    while i >= 0:
        e = i + len(pl)
        if (i == 0 or not is_an(text[i - 1])) and (e == len(text) or not is_an(text[e])):
            res.append((i, e))
        i = tl.find(pl, i + 1)
    return res


def company_name(domain):
    return domain.split(".")[0].replace("-", " ")


def names_company(s, domain):
    return bool(find_whole(s, domain) or find_whole(s, company_name(domain)))


def alnum_runs(s):
    return [(m.start(), m.end()) for m in re.finditer(r"[^\W_]+", s)]


def is_cap(w):
    return len(w) >= 2 and w[0].isupper() and w[0].isalpha() and all(c.isalpha() and c.islower() for c in w[1:])


def is_upper(w):
    return len(w) >= 2 and all(c.isalpha() and c.isupper() for c in w)


NUM_TOKEN = re.compile(r"[0-9]+(?:[.,][0-9]+)*")
NUM_OK = re.compile(r"^(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?:\.[0-9]+)?$")


def numbers(s):
    """(start, end, text) of numbers per A.4 (no letter adjacent)."""
    out = []
    for m in NUM_TOKEN.finditer(s):
        a, b = m.start(), m.end()
        if a > 0 and (s[a - 1].isalpha() or s[a - 1].isdigit()):
            continue
        if b < len(s) and (s[b].isalpha() or s[b].isdigit()):
            continue
        if NUM_OK.match(m.group()):
            out.append((a, b, m.group()))
    return out


def numval(t):
    return float(t.replace(",", ""))


SCALE = {"k": 1e3, "thousand": 1e3, "m": 1e6, "mn": 1e6, "million": 1e6, "bn": 1e9, "billion": 1e9}


def amounts(s):
    """(start, end, dollars-or-None) for amounts per A.4."""
    out = []
    low = s.lower()
    n = len(s)
    for m in NUM_TOKEN.finditer(s):
        a, b = m.start(), m.end()
        tok = m.group()
        if not NUM_OK.match(tok):
            continue
        if a > 0 and s[a - 1].isdigit():
            continue
        v = numval(tok)
        found = None
        # form 1: currency prefix
        for pre in ("us$", "usd", "$"):
            for sp in ("", " "):
                p = a - len(sp) - len(pre)
                if p < 0 or low[p:a] != pre + sp:
                    continue
                if p > 0 and is_an(s[p - 1]):
                    continue
                cands = []
                for sc in ("k", "mn", "m", "bn"):
                    if low[b:b + len(sc)] == sc:
                        cands.append((b + len(sc), SCALE[sc]))
                for sc in ("thousand", "million", "billion"):
                    if low[b:b + 1 + len(sc)] == " " + sc:
                        cands.append((b + 1 + len(sc), SCALE[sc]))
                cands.append((b, 1))
                cands.sort(key=lambda x: -x[0])
                for e, mult in cands:
                    if e == n or not is_an(s[e]):
                        found = (p, e, v * mult)
                        break
                if found:
                    break
            if found:
                break
        if not found:
            # form 2: number [scale] dollars
            if a > 0 and is_an(s[a - 1]):
                continue
            opts = []
            for sc in ("thousand", "million", "billion"):
                if low[b:b + 1 + len(sc)] == " " + sc:
                    opts.append((b + 1 + len(sc), SCALE[sc]))
            opts.append((b, 1))
            for e0, mult in opts:
                for cur in (" us dollars", " dollars"):
                    if low[e0:e0 + len(cur)] == cur:
                        e = e0 + len(cur)
                        if e == n or not is_an(s[e]):
                            found = (a, e, v * mult)
                            break
                if found:
                    break
        if found:
            p, e, val = found
            iv = round(val)
            out.append((p, e, iv if abs(val - iv) < 1e-6 else None))
    return out


def in_any(span, spans):
    return any(span[0] >= x[0] and span[1] <= x[1] for x in spans)


def range_of(k):
    bounds = [(1, 10), (11, 50), (51, 200), (201, 500), (501, 1000), (1001, 5000), (5001, 10000)]
    for (lo, hi), r in zip(bounds, RANGES):
        if lo <= k <= hi:
            return r
    return "10001+" if k >= 10001 else None


# ---------- A.4 value extraction per field ----------
def values(field, s, domain):
    """List of normalised values (None for an in-format value that has no valid
    normalisation) of F's format found in sentence s."""
    if field == "funding_total":
        return [v for (_, _, v) in amounts(s)]
    if field in ("founded_year", "headcount_range"):
        am = [(a, b) for (a, b, _) in amounts(s)]
        res = []
        for a, b, t in numbers(s):
            if in_any((a, b), am):
                continue
            if field == "founded_year":
                if re.fullmatch(r"[0-9]{4}", t) and 1800 <= int(t) <= 2099:
                    res.append(int(t))
            else:
                if "." in t:
                    continue
                k = int(t.replace(",", ""))
                if k >= 1:
                    res.append(range_of(k))
        return res
    if field == "hq_city":
        res = []
        for ph in STATEMENT["hq_city"]:
            for _, e in find_whole(s, ph):
                if s[e:e + 1] != " ":
                    continue
                st = e + 1
                v = cap_run(s, st)
                if v:
                    res.append(v)
        return res
    if field in ("ceo", "cfo", "coo", "cto"):
        t = list(s)
        spans = find_whole(s, company_name(domain)) + find_whole(s, domain)
        for ph in STATEMENT[field]:
            spans += find_whole(s, ph)
        for a, b in spans:
            for k in range(a, b):
                t[k] = "\x00"
        t = "".join(t)
        res = []
        runs = alnum_runs(t)
        i = 0
        while i < len(runs):
            if not is_cap(t[runs[i][0]:runs[i][1]]):
                i += 1
                continue
            j = i
            while (j + 1 < len(runs) and is_cap(t[runs[j + 1][0]:runs[j + 1][1]])
                   and t[runs[j][1]:runs[j + 1][0]] == " "):
                j += 1
            cnt = j - i + 1
            if 2 <= cnt <= 3:
                res.append(t[runs[i][0]:runs[j][1]])
            i = j + 1
        return res
    if field == "legal_name":
        res = []
        starts = find_whole(s, company_name(domain)) + find_whole(s, domain)
        for a, b in sorted(starts):
            v = legal_from(s, a, b)
            if v:
                res.append(v)
        return res
    raise ValueError(field)


def cap_run(s, st):
    """Longest run of capitalised words joined by single spaces or '-' starting at st."""
    runs = [r for r in alnum_runs(s) if r[0] >= st]
    if not runs or runs[0][0] != st or not is_cap(s[runs[0][0]:runs[0][1]]):
        return None
    end = runs[0][1]
    for k in range(1, len(runs)):
        gap = s[runs[k - 1][1]:runs[k][0]]
        if gap in (" ", "-") and is_cap(s[runs[k][0]:runs[k][1]]):
            end = runs[k][1]
        else:
            break
    return s[st:end]


def legal_from(s, a, b):
    pos = b
    while True:
        # try suffix at pos
        q = pos
        for comma in (",", ""):
            if comma and s[q:q + 1] != ",":
                continue
            r = q + len(comma)
            if s[r:r + 1] != " ":
                continue
            r += 1
            best = None
            for suf in SUFFIXES:
                if s.startswith(suf, r):
                    e = r + len(suf)
                    if e == len(s) or not is_an(s[e]):
                        if best is None or e < best:
                            best = e
            if best is not None:
                return s[a:best]
        # extend by one capitalised/uppercase word after one space
        if s[pos:pos + 1] != " ":
            return None
        m = re.match(r"[^\W_]+", s[pos + 1:])
        if not m:
            return None
        w = m.group()
        if not (is_cap(w) or is_upper(w)):
            return None
        pos = pos + 1 + len(w)


# ---------- A.2 ----------
def supports(excerpt, field, value, domain):
    s = ws1(excerpt).strip()
    if not is_single_sentence(s):
        return False
    return supported_value(s, field, domain) == ("ok", value)


def supported_value(s, field, domain):
    """('ok', V) if sentence s supports exactly one value V for field, else None."""
    if not names_company(s, domain):
        return None
    if not any(find_whole(s, p) for p in STATEMENT[field]):
        return None
    if any(find_whole(s, p) for p in NEGATING):
        return None
    vals = values(field, s, domain)
    if not vals or any(v is None for v in vals):
        return None
    if len(set(vals)) != 1:
        return None
    return ("ok", vals[0])


def best_span(s, field, domain, limit=500):
    """RULING R1-6: for a sentence over 500 chars, a contiguous span of at most 500 chars that on
    its own satisfies A.2. Returns ('ok', V, span) or None. Spans start/end at word boundaries."""
    if len(s) <= limit:
        r = supported_value(s, field, domain)
        return (r[0], r[1], s) if r else None
    prot = protected(s)
    ok_edge = lambda k: not any(x < k < y for x, y in prot)
    starts = [k for k in [0] + [i + 1 for i, c in enumerate(s) if c == " "] if ok_edge(k)]
    ends = [k for k in [i for i, c in enumerate(s) if c == " "] + [len(s)] if ok_edge(k)]
    for a in starts:
        for b in ends:
            if b <= a:
                continue
            if b - a > limit:
                break
            span = s[a:b].strip()
            r = supported_value(span, field, domain)
            if r:
                return (r[0], r[1], span)
    return None


def supported_in_text(prose, domain, titles=False):
    """{field: {value: [sentence,...]}} for every sentence of a prose text (R1-6 for long ones)."""
    fs = FIELDS + (TITLES if titles else [])
    out = {f: {} for f in fs}
    for snt in sentences(prose):
        s = ws1(snt)
        for f in fs:
            r = best_span(s, f, domain)
            if r:
                out[f].setdefault(r[1], []).append(r[2])
    return out


def protected(s):
    """RULING R1-7: spans whose inside a span edge must not cut: amounts, numbers, and runs of
    capitalised words joined by single spaces or '-'."""
    out = [(a, b) for a, b, _ in amounts(s)] + [(a, b) for a, b, _ in numbers(s)]
    runs = alnum_runs(s)
    i = 0
    while i < len(runs):
        if not is_cap(s[runs[i][0]:runs[i][1]]):
            i += 1
            continue
        k = i
        while (k + 1 < len(runs) and is_cap(s[runs[k + 1][0]:runs[k + 1][1]])
               and s[runs[k][1]:runs[k + 1][0]] in (" ", "-")):
            k += 1
        out.append((runs[i][0], runs[k][1]))
        i = k + 1
    return out


def citation_shape_ok(excerpt, served_prose):
    """RULING R1-7: an excerpt is a whole sentence of the served prose (<= 500 chars), or an edge-intact
    span of a served sentence longer than 500 chars."""
    e = ws1(excerpt).strip()
    for snt in sentences(served_prose):
        t = ws1(snt)
        if t == e:
            return len(t) <= 500
        if len(t) > 500:
            k = t.find(e)
            while k >= 0:
                prot = protected(t)
                if not any(x < k < y or x < k + len(e) < y for x, y in prot):
                    return True
                k = t.find(e, k + 1)
    return False
