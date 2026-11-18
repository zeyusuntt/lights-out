"""Stage 3 'Upgrades': stage-1 (svc1) and stage-2 (svcp) exports into the stage-3 service."""
import json
import time

import pytest

from conftest import (FIELDS, FIELDS7, SVC1, assert_err, call, check_shape, j, mock_reset, newkey, parse_ts,
                      reset, set_clock, wait_done)
import os

SVCP = os.environ.get("SVCP", "http://svcp:8003")
D = "harbour-crane.test"


def _populate(base):
    reset(base=base)
    tok = j(call("POST", "/auth/login", base=base, body={"email": "ada@example.com", "password": "correct horse"}))["token"]
    mock_reset(0)
    k = newkey()
    r = call("POST", "/dossiers", token=tok, key=k, body={"domain": D}, base=base)
    assert r.status_code == 202
    wait_done(tok, D, base=base, timeout=60)
    time.sleep(0.5)
    s = j(call("GET", f"/dossiers/{D}", token=tok, base=base))
    e = j(call("GET", "/_test/export", base=base, timeout=10))
    return tok, k, j(r), s, e


@pytest.mark.parametrize("src", ["stage1", "stage2"])
def test_upgrade_import(src):
    # "A stage-3 service must accept an export produced by the same team's stage-1 or stage-2 service. Every
    # imported field that has a value gets one history entry of type initial, with learned_at the dossier's
    # researched_at ... The feed starts empty". "After its import, executives is unknown ... and has no
    # history entry". Imported state counts as a build that completed ready at researched_at: "An as_of at or
    # after that time and before the next build returns the imported fields, and an earlier as_of is 404".
    base = SVC1 if src == "stage1" else SVCP
    tok, k, orig, s, e = _populate(base)
    reset()
    mock_reset(0)
    assert call("POST", "/_test/import", body=e, timeout=10).status_code == 204
    b = j(call("GET", f"/dossiers/{D}", token=tok))
    check_shape(b, D)
    for key in ("dossier_id", "state", "researched_at", "spent_units"):
        assert b[key] == s[key]
    for f in FIELDS:
        assert json.dumps(b["fields"][f]["value"]) == json.dumps(s["fields"][f]["value"]), f
        for c in b["fields"][f]["candidates"]:
            # "imported candidates have learned_at equal to their retrieved_at" (stage-1 import)
            assert c["learned_at"] == c["retrieved_at"]   # stage-1 spec text; stage-2 by RULING R3-3
            if src == "stage2":
                # RULING R3-3: true_from is the UTC date of the exported published_at, or null
                from datetime import timezone
                want_tf = parse_ts(c["published_at"]).astimezone(timezone.utc).date().isoformat() if c["published_at"] else None
                assert c["true_from"] == want_tf, (f, c["url"], c["true_from"], want_tf)
            else:
                assert c["true_from"] is None
    ex = b["fields"]["executives"]
    assert ex["value"] is None and ex["status"] == "unknown" and ex["candidates"] == []
    h = j(call("GET", f"/dossiers/{D}/history", token=tok))
    assert set(h["fields"]) == set(FIELDS7)
    assert h["fields"]["executives"] == []
    for f in FIELDS:
        hv = h["fields"][f]
        if s["fields"][f]["value"] is None:
            assert hv == [], (f, hv)
        else:
            assert len(hv) == 1 and hv[0]["type"] == "initial", (f, hv)
            assert json.dumps(hv[0]["value"]) == json.dumps(s["fields"][f]["value"])
            assert parse_ts(hv[0]["learned_at"]) == parse_ts(s["researched_at"])
            if src == "stage1":
                assert hv[0]["true_from"] is None
            else:
                # RULING R3-3: the initial row's true_from is the selected candidate's
                assert hv[0]["true_from"] == b["fields"][f]["candidates"][0]["true_from"], (f, hv[0])
    assert j(call("GET", "/changes", token=tok)) == {"changes": [], "has_more": False}
    ra = parse_ts(s["researched_at"])
    assert_err(call("GET", f"/dossiers/{D}", token=tok, params={"as_of": "2026-03-01T08:59:59+00:00"}),
               404, "not_found")
    a = j(call("GET", f"/dossiers/{D}", token=tok, params={"as_of": s["researched_at"]}))
    assert a["state"] == "ready" and a["spent_units"] == s["spent_units"]
    for f in FIELDS:
        assert json.dumps(a["fields"][f]["value"]) == json.dumps(s["fields"][f]["value"])
    v = call("GET", f"/dossiers/{D}/values", token=tok, params={"true_at": "2026-01-01"})
    assert v.status_code == 200
    if src == "stage1":
        # stage-1 exports record no dates: every version holds from no date
        assert all(x["value"] is None for x in j(v)["fields"].values())
    else:
        # RULING R3-3: one version per candidate URL with true_from from published_at; far in the future every
        # dated candidate holds, so each field's value is the rule's pick among them.
        from conftest import rank_key
        vf = j(call("GET", f"/dossiers/{D}/values", token=tok, params={"true_at": "2099-01-01"}))["fields"]
        for f in FIELDS:
            dated = sorted([c for c in b["fields"][f]["candidates"] if c["true_from"]], key=rank_key)
            want = dated[0]["value"] if dated else None
            assert json.dumps(vf[f]["value"]) == json.dumps(want), (f, vf[f], want)
    # §7 replay survives
    r = call("POST", "/dossiers", token=tok, key=k, body={"domain": D})
    assert r.status_code == 200 and j(r) == orig
    # "the first build after import compares its selected values with the imported ones"; executives' first
    # value after import is a change (not the dossier's first ready build).
    set_clock("2026-04-01T09:00:00+00:00")
    mock_reset(1)
    assert call("POST", f"/dossiers/{D}/refresh", token=tok, key=newkey()).status_code == 202
    wait_done(tok, D, timeout=60)
    ch = j(call("GET", "/changes", token=tok, params={"limit": "200"}))["changes"]
    got = [(c["field"], c["type"]) for c in ch]
    assert ("executives", "change") in got and ("ceo", "change") in got, got
    assert ("founded_year", "change") not in got and ("founded_year", "correction") not in got
    hx = j(call("GET", f"/dossiers/{D}/history", token=tok))["fields"]["executives"]
    assert [e_["type"] for e_ in hx] == ["change"]
