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


def evidence_values(domain, epoch):
    """{field: set(values)} supported by the evidence (§4 'Evidence and support'): searchable
    pages of the epoch, plus nimble research claims whose excerpt supports them."""
    agg = {f: set() for f in FIELDS}
    for c in corpus():
        for p in c["pages"]:
            if epoch in p["epochs"] and p.get("searchable", True):
                # Amendment (after code seen): the mock serves a page's static_text when present
                # (search/extract text); "text" is only what a browser shows.
                served = p["static_text"] if p.get("static_text") is not None else p["text"]
                for f, vs in oracle.supported_in_text(served, domain).items():
                    agg[f] |= set(vs)
    for c in corpus():
        if c["domain"] != domain:
            continue
        for r in c.get("research", {}).get("nimble", {}).get(str(epoch), []):
            if oracle.supports(r["excerpt"], r["field"], r["value"], domain):
                agg[r["field"]].add(r["value"])
    return agg


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
    assert set(b["fields"]) == set(FIELDS), b["fields"].keys()
    for f, v in b["fields"].items():
        assert v["status"] in ("known", "unknown")
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


def check_citations(b, domain, calls):
    """§1.1 / §4 citations: served to this service, verbatim modulo whitespace, from prose,
    1..500 chars, by the provider named, and supporting the value by Appendix A."""
    idx = served_index([c for c in calls if c["method"] != "research"])
    ridx = served_index([c for c in calls if c["method"] == "research"])
    headers = header_lines()
    problems = []
    for f in FIELDS:
        v = b["fields"][f]
        for c in v["citations"]:
            ex = c.get("excerpt")
            if c.get("provider") not in ("nimble", "tavily"):
                problems.append((f, "bad provider", c))
                continue
            if not isinstance(ex, str) or not 1 <= len(ex) <= 500:
                problems.append((f, "excerpt length", c))
                continue
            if any(oracle.ws1(ex) in h for h in headers.get(c.get("url"), [])) and not any(
                    oracle.ws1(ex) in oracle.ws1(oracle.prose_of(t)) for t in idx.get((c["provider"], c.get("url")), [])):
                problems.append((f, "excerpt from a header line", c))
            if not oracle.supports(ex, f, v["value"], domain):
                problems.append((f, "does not support " + repr(v["value"]), ex))
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
