"""Shared helpers for the stage-1 acceptance suite. Black-box: talks to the service only over
HTTP, and to the mock web only through its documented admin API."""
import glob
import json
import os
import sys
import time
import uuid
from datetime import datetime

import httpx
import pytest

sys.path.insert(0, os.path.dirname(__file__))
import oracle  # noqa: E402

SVC = os.environ.get("SVC", "http://svc:8000")
SVC2 = os.environ.get("SVC2", "http://svc2:8001")
SVC1 = os.environ.get("SVC1", "http://svc1:8002")  # the accepted stage-1 image, for the upgrade path
MOCK = os.environ.get("MOCK", "http://web:8080")
ADMIN = os.environ.get("MOCK_ADMIN_TOKEN", "verifier-admin")
CORPUS = os.environ.get("CORPUS", "/corpus")
OUT = os.environ.get("OUT", "/out")

FIELDS = oracle.FIELDS
NOW0 = "2026-03-01T09:00:00+00:00"
PW = "correct horse"
USERS = [
    {"id": "u_ada", "email": "ada@example.com", "password": PW, "display_name": "Ada"},
    {"id": "u_bob", "email": "bob@example.com", "password": PW, "display_name": "Bob"},
]
CUSTOM = ["quillon-dynamics.test", "nullmark-systems.test", "tarnwick-labs.test"]

# One client per thread is created on demand; httpx.Client is thread-safe for requests.
_clients = {}


def client(base=SVC):
    if base not in _clients:
        _clients[base] = httpx.Client(base_url=base, timeout=5.0,
                                      limits=httpx.Limits(max_connections=100))
    return _clients[base]


# "Per-request timeout | 5 s (10 s for POST /_test/reset)" — every call here enforces it.
def call(method, path, token=None, key=None, body=None, raw=None, headers=None, base=SVC,
         timeout=5.0, params=None):
    h = dict(headers or {})
    if token is not None:
        h["Authorization"] = f"Bearer {token}"
    if key is not None:
        h["Idempotency-Key"] = key
    kw = {"headers": h, "timeout": timeout}
    if params is not None:
        kw["params"] = params
    if raw is not None:
        kw["content"] = raw
        h.setdefault("Content-Type", "application/json")
    elif body is not None:
        kw["json"] = body
    r = client(base).request(method, path, **kw)
    assert r.status_code < 500, f"5xx from {method} {path}: {r.status_code} {r.text[:300]}"
    return r


def j(r):
    ct = r.headers.get("content-type", "")
    assert ct.startswith("application/json"), f"content-type {ct!r} for {r.status_code}"
    return r.json()


def assert_err(r, status, code):
    # §5 "Every 4xx and 5xx response carries this body: {"error": {"code", "message"}}"
    assert r.status_code == status, f"want {status} {code}, got {r.status_code} {r.text[:300]}"
    b = j(r)
    assert isinstance(b, dict) and isinstance(b.get("error"), dict), b
    assert b["error"].get("code") == code, b
    assert isinstance(b["error"].get("message"), str), b


def newkey():
    return "k-" + uuid.uuid4().hex


# ---------- service control ----------
def reset(base=SVC, now=NOW0, users=None, expect=204):
    fx = {"now": now, "users": USERS if users is None else users}
    r = call("POST", "/_test/reset", body=fx, base=base, timeout=10.0)
    assert r.status_code == expect, (r.status_code, r.text[:300])
    return r


def set_clock(now, base=SVC):
    return call("POST", "/_test/clock", body={"now": now}, base=base)


def login(email, pw=PW, base=SVC):
    r = call("POST", "/auth/login", body={"email": email, "password": pw}, base=base)
    assert r.status_code == 200, r.text
    return j(r)["token"]


def create(token, domain, key=None, base=SVC):
    return call("POST", "/dossiers", token=token, key=key or newkey(), body={"domain": domain},
                base=base)


def refresh(token, domain, key=None, base=SVC):
    return call("POST", f"/dossiers/{domain}/refresh", token=token, key=key or newkey(), base=base)


def get(token, domain, base=SVC):
    return call("GET", f"/dossiers/{domain}", token=token, base=base)


def wait_done(token, domain, timeout=15.0, base=SVC):
    """Poll until state is not building; returns (body, seconds)."""
    t0 = time.time()
    while True:
        r = get(token, domain, base=base)
        assert r.status_code == 200, r.text
        b = j(r)
        if b["state"] != "building":
            return b, time.time() - t0
        if time.time() - t0 > timeout:
            raise AssertionError(f"{domain} still building after {timeout}s")
        time.sleep(0.2)


# ---------- mock web admin ----------
def _admin(method, path, body=None):
    r = httpx.request(method, MOCK + path, headers={"X-Mock-Admin": ADMIN}, json=body, timeout=10)
    assert r.status_code in (200, 204), (path, r.status_code, r.text)
    return r


def mock_reset(epoch=0):
    _admin("POST", "/_mock/reset", {"epoch": epoch})


def mock_epoch(epoch):
    _admin("POST", "/_mock/epoch", {"epoch": epoch})


def mock_fault(provider, methods, mode, seconds=None):
    b = {"provider": provider, "methods": methods, "mode": mode}
    if seconds is not None:
        b["seconds"] = seconds
    _admin("POST", "/_mock/faults", b)


def mock_log():
    return _admin("GET", "/_mock/log").json()["calls"]


def log_cost(calls):
    return sum(c.get("cost") or 0 for c in calls)


# ---------- evidence oracle (from the corpus served by the mock) ----------
_corpus = None


def corpus():
    global _corpus
    if _corpus is None:
        _corpus = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(CORPUS, "*.test.json")))]
    return _corpus


KINDS = ("own", "filing", "news", "aggregator")
AUTH = {"own": 3, "filing": 3, "news": 2, "aggregator": 1, None: 1}
PROV = {"nimble": 0, "tavily": 1, "kernel": 2, "browserbase": 3}


def browser_text(p):
    """Stage 2 'Page text': the text a browser shows once loaded, no control activated."""
    t = p["text"]
    for d in p.get("disclosures") or []:
        pass  # graded/sample corpora carry none (stage-2 'Page text')
    return t


def host_domain(url):
    from urllib.parse import urlparse
    h = (urlparse(url).hostname or "").strip().lower()
    if h.endswith("."):
        h = h[:-1]
    return h[4:] if h.startswith("www.") else h


def page_kind(p, domain):
    # Stage 2 "A page with no Kind line, or with a value not listed above, is of kind own when the host
    # of its URL, normalised ..., is the company's domain, and of kind aggregator otherwise."
    k = p.get("kind")
    if k in KINDS:
        return k
    return "own" if host_domain(p["url"]) == domain else "aggregator"


def page_published(p):
    # Stage 2 "A page with no Published line, or with a value that is not an RFC 3339 timestamp, has no
    # publication time."
    v = p.get("published_at")
    if not isinstance(v, str):
        return None
    import re as _re
    if not _re.fullmatch(r"\d{4}-\d{2}-\d{2}[Tt ]\d{2}:\d{2}:\d{2}(\.\d+)?([Zz]|[+-]\d{2}:\d{2})", v):
        return None
    try:
        return datetime.fromisoformat(v[:10] + "T" + v[11:].replace("Z", "+00:00").replace("z", "+00:00"))
    except ValueError:
        return None


def evidence_pages(domain, epoch):
    """Stage 2 evidence: searchable pages of the epoch, plus every page a research claim of the company
    cites ('The evidence now also holds the page that each research claim of the evidence cites')."""
    pages = {}
    for c in corpus():
        for p in c["pages"]:
            if epoch in p["epochs"] and p.get("searchable", True):
                pages[p["url"]] = p
    cited = set()
    for c in corpus():
        if c["domain"] == domain:
            for r in c.get("research", {}).get("nimble", {}).get(str(epoch), []):
                cited.add(r["url"])
    for c in corpus():
        for p in c["pages"]:
            if epoch in p["epochs"] and p["url"] in cited:
                pages[p["url"]] = p
    return pages


def expected_candidates(domain, epoch):
    """{(url, value)}: every value a page of the evidence supports, once per page, plus supported
    research claims (on the page they cite)."""
    out = set()
    pages = evidence_pages(domain, epoch)
    for url, p in pages.items():
        for f, vs in oracle.supported_in_text(browser_text(p), domain).items():
            for v in vs:
                out.add((f, url, v))
    for c in corpus():
        if c["domain"] == domain:
            for r in c.get("research", {}).get("nimble", {}).get(str(epoch), []):
                if oracle.supports(r["excerpt"], r["field"], r["value"], domain):
                    out.add((r["field"], r["url"], r["value"]))
    return out, pages


def evidence_values(domain, epoch):
    agg = {f: set() for f in FIELDS}
    for f, _, v in expected_candidates(domain, epoch)[0]:
        agg.setdefault(f, set()).add(v)  # amendment: stage-4 investors candidates carried too
    return agg


def rank_key(c):
    """Stage 2 'The selection rule' as a sort key (ascending = highest rank first)."""
    pub = parse_ts(c["published_at"]).timestamp() if c.get("published_at") else None
    v = c["value"].strip() if isinstance(c["value"], str) else c["value"]
    return (-AUTH[c.get("kind")], 0 if pub is not None else 1, -(pub or 0), c["url"],
            PROV.get(c["provider"], 9), v)


def check_candidates(b, domain, epoch, build_time=None, strict=True):
    """Stage 2 Candidates, selection rule and Status, and (strict) the candidate set against the evidence."""
    problems = []
    exp, pages = expected_candidates(domain, epoch)
    for f in FIELDS:
        fld = b["fields"][f]
        cands = fld["candidates"]
        keys = [(c["url"], json.dumps(c["value"])) for c in cands]
        if len(keys) != len(set(keys)):
            problems.append((f, "a page/value candidate listed twice"))
        for c in cands:
            for k in ("value", "url", "excerpt", "provider", "kind", "published_at", "retrieved_at", "selected"):
                if k not in c:
                    problems.append((f, "candidate lacks " + k))
            if not oracle.supports(c["excerpt"], f, c["value"], domain):
                problems.append((f, "candidate excerpt does not support", c["value"], c["excerpt"]))
            p = pages.get(c["url"])
            if p is not None:
                if c["kind"] != page_kind(p, domain):
                    problems.append((f, "kind", c["url"], c["kind"], page_kind(p, domain)))
                pp = page_published(p)
                got = parse_ts(c["published_at"]) if c["published_at"] else None
                if got != pp:
                    problems.append((f, "published_at", c["url"], c["published_at"], pp))
                if oracle.ws1(c["excerpt"]) not in oracle.ws1(browser_text(p)):
                    problems.append((f, "excerpt not in the page's browser text", c["url"], c["excerpt"]))
            if build_time is not None and parse_ts(c["retrieved_at"]) != parse_ts(build_time):
                problems.append((f, "retrieved_at", c["retrieved_at"], build_time))
        ranked = sorted(cands, key=rank_key)
        if [rank_key(c) for c in cands] != [rank_key(c) for c in ranked]:
            problems.append((f, "candidates not in rank order", [(c["kind"], c["published_at"], c["url"], c["value"]) for c in cands]))
        sel = [c for c in cands if c["selected"]]
        if cands:
            if len(sel) != 1 or not cands[0]["selected"]:
                problems.append((f, "selected must be exactly the first candidate"))
            if fld["value"] != cands[0]["value"]:
                problems.append((f, "value is not the selected candidate's", fld["value"], cands[0]["value"]))
            want_c = [{"url": c["url"], "excerpt": c["excerpt"], "provider": c["provider"]}
                      for c in cands if c["value"] == cands[0]["value"]]
            if fld["citations"] != want_c:
                problems.append((f, "citations are not every candidate with the value, in rank order"))
            nvals = len({json.dumps(c["value"].strip() if isinstance(c["value"], str) else c["value"]) for c in cands})
            want_s = "known" if nvals == 1 else "contested"
            if fld["status"] != want_s:
                problems.append((f, "status", fld["status"], want_s))
        else:
            if fld["status"] != "unknown" or fld["value"] is not None or fld["citations"]:
                problems.append((f, "no candidates but not unknown"))
        if strict:
            got = {(f, c["url"], c["value"]) for c in cands}
            want = {x for x in exp if x[0] == f}
            if got != want:
                problems.append((f, "candidate set differs from the evidence",
                                 "missing", sorted(map(str, want - got)), "extra", sorted(map(str, got - want))))
        # stage 3: candidate true_from from Effective / Published; selected true_from is the selected candidate's
        for c in cands:
            p = pages.get(c["url"])
            if p is not None and "true_from" in c and c["true_from"] != page_true_from(p):
                problems.append((f, "candidate true_from", c["url"], c["true_from"], page_true_from(p)))
        if cands and "true_from" in fld and fld["true_from"] != cands[0].get("true_from"):
            problems.append((f, "field true_from is not the selected candidate's"))
    if "executives" in b["fields"]:
        problems += check_executives(b, domain, epoch, pages, strict)
    if "investors" in b["fields"]:
        problems += check_stage4_fields(b, domain, epoch)
    return problems


def check_executives(b, domain, epoch, pages, strict=True):
    """Stage 3 Executives."""
    pr = []
    ex = b["fields"]["executives"]
    cands = ex["candidates"]
    order = [(TITLES.index(c["title"]),) + rank_key(c) for c in cands]
    if order != sorted(order):
        pr.append(("executives", "candidates not by title then rank"))
    members, cites, tfs = [], [], []
    for t in TITLES:
        ct = [c for c in cands if c["title"] == t]
        if not ct:
            continue
        if [c["selected"] for c in ct] != [True] + [False] * (len(ct) - 1):
            pr.append(("executives", "selected must be the first of each title", t))
        members.append({"title": t, "name": ct[0]["value"]})
        tfs.append(ct[0].get("true_from"))
        cites += [{"url": c["url"], "excerpt": c["excerpt"], "provider": c["provider"]}
                  for c in ct if c["value"] == ct[0]["value"]]
    for c in cands:
        if not oracle.supports(c["excerpt"], c["title"], c["value"], domain):
            pr.append(("executives", "candidate excerpt does not support", c["title"], c["value"], c["excerpt"]))
        p = pages.get(c["url"])
        if p is not None:
            if oracle.ws1(c["excerpt"]) not in oracle.ws1(browser_text(p)):
                pr.append(("executives", "excerpt not in browser text", c["url"]))
            if c.get("true_from") != page_true_from(p):
                pr.append(("executives", "candidate true_from", c["url"], c.get("true_from"), page_true_from(p)))
    want_v = members or None
    if ex["value"] != want_v:
        pr.append(("executives", "value", ex["value"], want_v))
    if ex["citations"] != cites:
        pr.append(("executives", "citations are not each member's candidates in rank order"))
    if not members:
        want_s = "unknown"
    elif any(len({c["value"] for c in cands if c["title"] == t}) > 1 for t in TITLES):
        want_s = "contested"
    else:
        want_s = "known"
    if ex["status"] != want_s:
        pr.append(("executives", "status", ex["status"], want_s))
    want_tf = None if not members or any(x is None for x in tfs) else max(tfs)
    if ex.get("true_from") != want_tf:
        pr.append(("executives", "true_from", ex.get("true_from"), want_tf))
    if strict:
        want = set()
        for url, p in pages.items():
            for t, vs in oracle.supported_in_text(browser_text(p), domain, titles=True).items():
                if t in TITLES:
                    want |= {(t, url, v) for v in vs}
        got = {(c["title"], c["url"], c["value"]) for c in cands}
        if got != want:
            pr.append(("executives", "candidate set differs", "missing", sorted(map(str, want - got)),
                       "extra", sorted(map(str, got - want))))
    return pr


def header_lines():
    """{url: [rendered header line, ...]} as the mock renders them (README 'Served text')."""
    out = {}
    for c in corpus():
        for p in c["pages"]:
            lines = [f"Kind: {p['kind']}"] if p.get("kind") else []
            if p.get("facts"):
                lines.append("Facts: " + json.dumps(p["facts"], ensure_ascii=False, separators=(",", ":")))
                lines.append("Facts: " + json.dumps(p["facts"], ensure_ascii=False))
            out.setdefault(p["url"], []).extend(oracle.ws1(l) for l in lines)
    return out


def corpus_domains():
    return [c["domain"] for c in corpus()]


def served_index(calls):
    idx = {}
    for c in calls:
        if c.get("status") != 200:
            continue
        for s in c.get("served") or []:
            if isinstance(s, dict) and s.get("url") is not None:
                idx.setdefault((c["provider"], s["url"]), []).append(s.get("text") or "")
    return idx


def check_shape(b, domain=None):
    """§8 GET /dossiers/{domain} shape and §4 field shape."""
    for k in ("dossier_id", "domain", "state", "researched_at", "spent_units", "fields"):
        assert k in b, (k, b)
    assert isinstance(b["dossier_id"], str) and 0 < len(b["dossier_id"]) <= 64
    if domain:
        assert b["domain"] == domain
    assert b["state"] in ("building", "ready", "failed")
    assert isinstance(b["spent_units"], int) and b["spent_units"] >= 0
    assert set(b["fields"]) == set(FIELDS) | {"executives", "investors"}, b["fields"].keys()  # stages 3, 4
    for f, v in ((k, x) for k, x in b["fields"].items() if k not in ("executives", "investors")):
        assert v["status"] in ("known", "unknown", "contested")
        assert isinstance(v.get("candidates"), list), (f, "stage 2: each field gains candidates")
        if v["status"] == "unknown":
            assert v["value"] is None and v["citations"] == [], (f, v)
        else:
            assert v["value"] is not None and len(v["citations"]) >= 1, (f, v)
            if f in ("founded_year", "funding_total"):
                assert isinstance(v["value"], int) and not isinstance(v["value"], bool), (f, v)
            else:
                assert isinstance(v["value"], str), (f, v)
                assert v["value"] == v["value"].strip()
            if f == "headcount_range":
                assert v["value"] in oracle.RANGES
    if b["researched_at"] is not None:
        parse_ts(b["researched_at"])
    check_stage3_shape(b)


def check_citations(b, domain, calls):
    """§1.1 / §4 citations: served to this service, verbatim modulo whitespace, from prose,
    1..500 chars, by the provider named, and supporting the value by Appendix A."""
    idx = served_index([c for c in calls if c["method"] != "research"])
    ridx = served_index([c for c in calls if c["method"] == "research"])
    headers = header_lines()
    problems = []
    for f in FIELDS:
        v = b["fields"][f]
        for c in v["citations"] + v.get("candidates", []):
            val = c["value"] if "selected" in c else v["value"]
            ex = c.get("excerpt")
            if c.get("provider") not in ("nimble", "tavily", "kernel", "browserbase"):
                problems.append((f, "bad provider", c))
                continue
            if not isinstance(ex, str) or not 1 <= len(ex) <= 500:
                problems.append((f, "excerpt length", c))
                continue
            if any(oracle.ws1(ex) in h for h in headers.get(c.get("url"), [])) and not any(
                    oracle.ws1(ex) in oracle.ws1(oracle.prose_of(t)) for t in idx.get((c["provider"], c.get("url")), [])):
                problems.append((f, "excerpt from a header line", c))
            if not oracle.supports(ex, f, val, domain):
                problems.append((f, "does not support " + repr(val), ex))
            texts = idx.get((c["provider"], c.get("url")), [])
            n = oracle.ws1(ex)
            # Amendment: a research run serves bare excerpts, which are prose of the page, not pages
            # with headers; RULING via FIX 1 2 F3. Page-level header lines are checked separately.
            raw = ridx.get((c["provider"], c.get("url")), [])
            proses = [oracle.prose_of(t) for t in texts] + raw
            if any(n in oracle.ws1(x) for x in proses) and not any(
                    oracle.citation_shape_ok(ex, x) for x in proses):
                # RULING R1-7: whole sentences only, spans only of sentences over 500 chars
                problems.append((f, "not a whole sentence nor an edge-intact span of a long one", ex))
            if not (any(n in oracle.ws1(oracle.prose_of(t)) for t in texts)
                    or any(n in oracle.ws1(t) for t in raw)):
                problems.append((f, "excerpt not served by that provider for that url", c))
    # Stage 2 "a citation's excerpt must appear in the page's text" (browser text)
    for f in FIELDS:
        for c in b["fields"][f]["citations"] + b["fields"][f].get("candidates", []):
            bt = [browser_text(p) for cc in corpus() for p in cc["pages"] if p["url"] == c.get("url")]
            if bt and not any(oracle.ws1(c["excerpt"]) in oracle.ws1(t) for t in bt):
                problems.append((f, "excerpt not in the page's browser text", c.get("url"), c["excerpt"]))
    assert not problems, problems


def parse_ts(s):
    # §3.5 "Timestamps in responses are RFC 3339 with an explicit offset"
    assert isinstance(s, str) and ("+" in s[10:] or "-" in s[10:] or s.endswith("Z")), s
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    assert d.tzinfo is not None, s
    return d


def report(name, data):
    try:
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, name + ".json"), "w") as fh:
            json.dump(data, fh, indent=1, default=str)
    except OSError:
        pass


@pytest.fixture
def fresh():
    """Reset service and mock; returns {'ada': token, 'bob': token}."""
    reset()
    mock_reset(0)
    return {"ada": login("ada@example.com"), "bob": login("bob@example.com")}


# ======================= stage 3 =======================
FIELDS7 = FIELDS + ["executives"]
TITLES = oracle.TITLES


def page_true_from(p):
    """Stage 3 'Two times per value': Effective YYYY-MM-DD, else the UTC date of published_at, else null."""
    import datetime as _dt
    import re as _re
    e = p.get("true_from")
    if isinstance(e, str) and _re.fullmatch(r"\d{4}-\d{2}-\d{2}", e):
        try:
            _dt.date.fromisoformat(e)
            return e
        except ValueError:
            pass
    pub = page_published(p)
    if pub is not None:
        return pub.astimezone(_dt.timezone.utc).date().isoformat()
    return None


def build_versions(domain, epoch):
    """{url: {"true_from": d, "cands": [(field, title, value, url, kind, published_at_dt, true_from)]}} for the
    pages one ready build gathers (the evidence pages that carry candidates)."""
    exp, pages = expected_candidates(domain, epoch)
    out = {}
    for f, url, v in exp:
        p = pages.get(url)
        if p is None:
            p = next((pp for c in corpus() for pp in c["pages"] if pp["url"] == url and epoch in pp["epochs"]), None)
        tf = page_true_from(p) if p else None
        out.setdefault(url, {"true_from": tf, "cands": []})["cands"].append(
            (f, None, v, url, page_kind(p, domain) if p else None, page_published(p) if p else None, tf))
    # Stage 3 "A gathered version with no candidates still replaces or ends earlier versions" (RULING R3 on C2):
    # an evidence page that names the company and has a statement phrase is read by every build (R1-2), so it
    # is gathered even when it carries no candidate.
    for url, p in pages.items():
        txt = browser_text(p)
        if url not in out and oracle.names_company(txt, domain) and any(
                oracle.find_whole(txt, ph) for f_ in oracle.STATEMENT for ph in oracle.STATEMENT[f_]):
            out[url] = {"true_from": page_true_from(p), "cands": []}
    for url, p in pages.items():
        for t, vs in oracle.supported_in_text(browser_text(p), domain, titles=True).items():
            if t in TITLES:
                for v in vs:
                    out.setdefault(url, {"true_from": page_true_from(p), "cands": []})["cands"].append(
                        ("executives", t, v, url, page_kind(p, domain), page_published(p), page_true_from(p)))
    return out


def _rk(c):
    f, t, v, url, kind, pub, tf = c
    return (-AUTH[kind], 0 if pub is not None else 1, -(pub.timestamp() if pub else 0), url,
            v.strip() if isinstance(v, str) else v)


def select_fields(cands):
    """{field: (value, true_from)} by the stage-2 rule, executives per title (stage 3)."""
    out = {}
    for f in FIELDS:
        cs = sorted([c for c in cands if c[0] == f], key=_rk)
        out[f] = (cs[0][2], cs[0][6]) if cs else (None, None)
    members, tfs = [], []
    for t in TITLES:
        cs = sorted([c for c in cands if c[0] == "executives" and c[1] == t], key=_rk)
        if cs:
            members.append({"title": t, "name": cs[0][2]})
            tfs.append(cs[0][6])
    if members:
        out["executives"] = (members, None if any(x is None for x in tfs) else max(tfs), dict(zip([m["title"] for m in members], tfs)))
    else:
        out["executives"] = (None, None, {})
    return out


def entry_type(f, old, new):
    """Stage 3 'Changes and corrections' (executives typed by title)."""
    if f != "executives":
        (ov, otf), (nv, ntf) = old[:2], new[:2]
        if ov is not None and nv is not None and otf is not None and ntf is not None and ntf <= otf:
            return "correction"
        return "change"
    om = {m["title"]: m["name"] for m in (old[0] or [])}
    nm = {m["title"]: m["name"] for m in (new[0] or [])}
    otf, ntf = old[2] if len(old) > 2 else {}, new[2] if len(new) > 2 else {}
    diff = [t for t in TITLES if (t in om) != (t in nm) or (t in om and om[t] != nm[t])]
    ok = all(t in om and t in nm and otf.get(t) is not None and ntf.get(t) is not None and ntf[t] <= otf[t]
             for t in diff)
    return "correction" if diff and ok else "change"


class Model:
    """Expected history, feed, as_of and values for one dossier over a sequence of ready builds."""

    def __init__(self, domain):
        self.d = domain
        self.builds = []      # (time_iso, epoch, versions, selected)
        self.history = {f: [] for f in FIELDS7}
        self.feed = []        # (field, type, from, to, true_from, learned_at)
        self.current = None

    def build(self, time_iso, epoch):
        vers = build_versions(self.d, epoch)
        cands = [c for v in vers.values() for c in v["cands"]]
        sel = select_fields(cands)
        first = self.current is None
        for f in FIELDS7:
            new = sel[f]
            if first:
                if new[0] is not None:
                    self.history[f].append(("initial", new[0], new[1], time_iso))
                continue
            old = self.current[f]
            if json.dumps(old[0], sort_keys=True) != json.dumps(new[0], sort_keys=True):
                typ = "change" if not self.history[f] else entry_type(f, old, new)
                self.history[f].append((typ, new[0], new[1], time_iso))
                self.feed.append((f, typ, old[0], new[0], new[1], time_iso))
        self.current = sel
        self.builds.append((time_iso, epoch, vers, sel))

    def values_at(self, true_at, as_of_dt):
        """Stage 3 page-version rule."""
        per_url = {}
        for t, _, vers, _ in self.builds:
            if parse_ts(t) > as_of_dt:
                continue
            for url, v in vers.items():
                lst = per_url.setdefault(url, [])
                tf = v["true_from"]
                keep = []
                for old in lst:
                    if tf is None or (old["tf"] is not None and old["tf"] >= tf):
                        continue  # replaced
                    keep.append(old)
                if tf is not None:
                    live = [o for o in keep if o["tf"] is not None]
                    if live:
                        last = live[-1]
                        last["end"] = tf if last["end"] is None or tf < last["end"] else last["end"]
                keep.append({"tf": tf, "end": None, "cands": v["cands"]})
                per_url[url] = keep
        cands = [c for lst in per_url.values() for o in lst
                 if o["tf"] is not None and o["tf"] <= true_at and (o["end"] is None or true_at < o["end"])
                 for c in o["cands"]]
        return select_fields(cands, getattr(self, "_oo", None))


def check_stage3_shape(b):
    assert list(b["fields"].keys())[-1] == "executives" or "executives" in b["fields"]
    assert set(b["fields"]) == set(FIELDS7) | {"investors"}, b["fields"].keys()
    for f in FIELDS7 + ["investors"]:
        v = b["fields"][f]
        assert "true_from" in v and "learned_at" in v, (f, v.keys())
        if v["status"] == "unknown":
            assert v["value"] is None and v["true_from"] is None and v["learned_at"] is None, (f, v)
        for c in v["candidates"]:
            assert "true_from" in c and "learned_at" in c, (f, c.keys())
    ex = b["fields"]["executives"]
    if ex["value"] is not None:
        titles = [m["title"] for m in ex["value"]]
        assert titles == [t for t in TITLES if t in titles] and len(set(titles)) == len(titles)
        assert all(set(m) == {"title", "name"} for m in ex["value"])
    for c in ex["candidates"]:
        assert c.get("title") in TITLES, c


# ======================= stage 4 =======================
FIELDS8 = FIELDS7 + ["investors"]
from domains_norm import norm_domain  # noqa: E402


def _page_at(url, epoch):
    for c in corpus():
        for p in c["pages"]:
            if p["url"] == url and epoch in p["epochs"]:
                return p
    return None


def registrant(p):
    # Stage 4 "A page with no valid Registrant line has the host of its own URL, normalised, as its registrant."
    r = norm_domain((p.get("lineage") or {}).get("registrant") or "")
    return r or host_domain(p["url"])


def page_origin(p, domain, epoch, follows=0):
    """Stage 4 Origins rules 1-4, following at most three Canonical URLs in a row."""
    lin = p.get("lineage") or {}
    fpb = norm_domain(lin.get("first_published_by") or "")
    if fpb:
        return fpb
    can = lin.get("canonical")
    if can and can != p["url"]:
        if follows == 3:
            return host_domain(can)
        orig = _page_at(can, epoch)
        if orig is None:
            return host_domain(can)
        return page_origin(orig, domain, epoch, follows + 1)
    if p.get("kind") == "own" and registrant(p) != host_domain(p["url"]):
        return domain  # lookalike
    return registrant(p)


_stage2_kind = page_kind


def page_kind(p, domain):  # noqa: F811 — stage 4 "Own pages" overrides stage 2's kind
    k = _stage2_kind(p, domain)
    if k == "own" and registrant(p) != domain:
        return "aggregator"
    return k


_stage3_expected = expected_candidates


def expected_candidates(domain, epoch):  # noqa: F811 — adds investors (never from research claims)
    out, pages = _stage3_expected(domain, epoch)
    for url, p in pages.items():
        for n in _investors_in(browser_text(p), domain):
            out.add(("investors", url, n))
    return out, pages


def _investors_in(text, domain):
    names = []
    for snt in oracle.sentences(text):
        names += oracle.investor_support(snt, domain)
    return list(dict.fromkeys(names))


def investor_view(cands):
    """cands: list of dicts with value, kind, origin, true_from (+ rank fields). Stage 4 Investors rules."""
    by = {}
    for c in cands:
        by.setdefault(c["value"], []).append(c)
    members = sorted(n for n, cs in by.items()
                     if any(c["kind"] in ("own", "filing") for c in cs) or len({c["origin"] for c in cs}) >= 2)
    if not members:
        return None, None, {}
    tfs = {}
    for n in members:
        nn = [c["true_from"] for c in by[n] if c["true_from"]]
        tfs[n] = min(nn) if nn else None
    ftf = None if any(v is None for v in tfs.values()) else max(tfs.values())
    return members, ftf, tfs


def check_stage4_fields(b, domain, epoch):
    """Stage 4: kinds, origins, corroborated, investors."""
    pr = []
    pages = evidence_pages(domain, epoch)
    for f in FIELDS8:
        fld = b["fields"][f]
        for k in ("origins", "corroborated", "corroborated_since"):
            if k not in fld:
                pr.append((f, "lacks " + k))
        for c in fld.get("candidates", []):
            p = pages.get(c["url"]) or _page_at(c["url"], epoch)
            if p is not None:
                if c.get("origin") != page_origin(p, domain, epoch):
                    pr.append((f, "origin", c["url"], c.get("origin"), page_origin(p, domain, epoch)))
                if c.get("kind") != page_kind(p, domain):
                    pr.append((f, "kind", c["url"], c.get("kind"), page_kind(p, domain)))
        if f in FIELDS:
            sel = [c for c in fld["candidates"] if fld["value"] is not None and c["value"] == fld["value"]]
            want_o = sorted({c["origin"] for c in sel})
            if fld.get("origins") != want_o:
                pr.append((f, "origins", fld.get("origins"), want_o))
            if fld.get("corroborated") != (len(want_o) >= 2):
                pr.append((f, "corroborated"))
    ex = b["fields"]["executives"]
    if ex["value"]:
        mo = {(m["title"], m["name"]): {c["origin"] for c in ex["candidates"]
                                        if c["title"] == m["title"] and c["value"] == m["name"]} for m in ex["value"]}
        want_o = sorted(set().union(*mo.values()))
        if ex.get("origins") != want_o or ex.get("corroborated") != all(len(v) >= 2 for v in mo.values()):
            pr.append(("executives", "origins/corroborated", ex.get("origins"), want_o))
    elif ex.get("origins") != [] or ex.get("corroborated") is not False:
        pr.append(("executives", "unknown origins/corroborated"))
    inv = b["fields"]["investors"]
    members, ftf, tfs = investor_view(inv["candidates"])
    if inv["value"] != members:
        pr.append(("investors", "value", inv["value"], members))
    if inv["status"] != ("known" if members else "unknown"):
        pr.append(("investors", "status", inv["status"]))
    if inv.get("true_from") != ftf:
        pr.append(("investors", "true_from", inv.get("true_from"), ftf))
    if [rank_key(c) for c in inv["candidates"]] != sorted(rank_key(c) for c in inv["candidates"]):
        pr.append(("investors", "candidates not in rank order"))
    for c in inv["candidates"]:
        if c["selected"] != (members is not None and c["value"] in members):
            pr.append(("investors", "selected", c["value"]))
        if c["value"] not in oracle.investor_support(c["excerpt"], domain):
            pr.append(("investors", "excerpt does not support", c["value"], c["excerpt"]))
    want_c = [{"url": c["url"], "excerpt": c["excerpt"], "provider": c["provider"]}
              for n in (members or []) for c in inv["candidates"] if c["value"] == n]
    if inv["citations"] != want_c:
        pr.append(("investors", "citations"))
    mo = {n: {c["origin"] for c in inv["candidates"] if c["value"] == n} for n in (members or [])}
    want_o = sorted(set().union(*mo.values())) if mo else []
    if inv.get("origins") != want_o:
        pr.append(("investors", "origins", inv.get("origins"), want_o))
    if inv.get("corroborated") != (bool(mo) and all(len(v) >= 2 for v in mo.values())):
        pr.append(("investors", "corroborated"))
    got = {(c["url"], c["value"]) for c in inv["candidates"]}
    want = {(u, n) for f, u, n in expected_candidates(domain, epoch)[0] if f == "investors"}
    if got != want:
        pr.append(("investors", "candidate set", "missing", sorted(map(str, want - got)), "extra", sorted(map(str, got - want))))
    return pr


def _origin_of(domain, epoch):
    def f(url):
        p = _page_at(url, epoch)
        return page_origin(p, domain, epoch) if p else host_domain(url)
    return f


_stage3_select = select_fields


def select_fields(cands, origin_of=None):  # noqa: F811 — adds investors
    out = _stage3_select(cands)
    inv = [{"value": c[2], "kind": c[4], "origin": origin_of(c[3]) if origin_of else host_domain(c[3]),
            "true_from": c[6]} for c in cands if c[0] == "investors"]
    members, ftf, tfs = investor_view(inv)
    out["investors"] = (members, ftf, tfs)
    return out


_stage3_entry_type = entry_type


def entry_type(f, old, new):  # noqa: F811 — investors typed by name
    if f != "investors":
        return _stage3_entry_type(f, old, new)
    o, n = set(old[0] or []), set(new[0] or [])
    diff = o ^ n
    otf = old[1]
    ok = all(x in n and new[2].get(x) is not None and otf is not None and new[2][x] <= otf for x in diff)
    return "correction" if diff and ok else "change"


class Model4(Model):
    """Model plus investors and corroborated_since (stage 4)."""

    def __init__(self, domain):
        super().__init__(domain)
        self.history["investors"] = []
        self.standing = {}
        self.since = {f: None for f in FIELDS8}

    def build(self, time_iso, epoch):
        vers = build_versions(self.d, epoch)
        cands = [c for v in vers.values() for c in v["cands"]]
        oo = _origin_of(self.d, epoch)
        self._oo = oo
        sel = select_fields(cands, oo)
        first = self.current is None
        for f in FIELDS8:
            new = sel[f]
            if first:
                if new[0] is not None:
                    self.history[f].append(("initial", new[0], new[1], time_iso))
            else:
                old = self.current[f]
                if json.dumps(old[0], sort_keys=True) != json.dumps(new[0], sort_keys=True):
                    typ = "change" if not self.history[f] else entry_type(f, old, new)
                    self.history[f].append(("initial" if False else typ, new[0], new[1], time_iso))
                    self.feed.append((f, typ, old[0], new[0], new[1], time_iso))
            # standing origins (per member for executives / investors)
            if f in FIELDS:
                keys = [new[0]] if new[0] is not None else []
                got = {json.dumps(new[0]): {oo(c[3]) for c in cands if c[0] == f and c[2] == new[0]}}
            elif f == "executives":
                keys = [(m["title"], m["name"]) for m in (new[0] or [])]
                got = {json.dumps(k): {oo(c[3]) for c in cands if c[0] == "executives" and (c[1], c[2]) == k} for k in keys}
            else:
                keys = list(new[0] or [])
                got = {json.dumps(k): {oo(c[3]) for c in cands if c[0] == "investors" and c[2] == k} for k in keys}
            prev = self.standing.get(f, {})
            st = {}
            for k in keys:
                kk = json.dumps(k)
                st[kk] = (prev.get(kk, set()) if kk in prev else set()) | got.get(kk, set())
            if f in FIELDS and not first and json.dumps(self.current[f][0]) != json.dumps(new[0]):
                st = {json.dumps(k): got.get(json.dumps(k), set()) for k in keys}
            self.standing[f] = st
            cond = bool(keys) and all(len(v) >= 2 for v in st.values())
            if not cond:
                self.since[f] = None
            elif self.since[f] is None:
                self.since[f] = time_iso
        self.current = sel
        self.builds.append((time_iso, epoch, vers, sel))
