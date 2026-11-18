"""Stage 4 'Upgrades' from the accepted stage-3 image (svc3)."""
import json
import os
import time

from conftest import FIELDS, FIELDS7, FIELDS8, call, host_domain, j, mock_reset, newkey, parse_ts, reset, set_clock, wait_done

SVC3 = os.environ.get("SVC3", "http://svc3:8004")
D = "harbour-crane.test"
T1 = "2026-04-01T09:00:00+00:00"


def _sub(a, b, path=""):
    """Every key of a (stage-3 answer) is in b with an equal value, recursively (b may add stage-4 keys)."""
    if isinstance(a, dict):
        assert isinstance(b, dict), path
        for k, v in a.items():
            assert k in b, path + "/" + k
            _sub(v, b[k], path + "/" + k)
    elif isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), path
        for i, (x, y) in enumerate(zip(a, b)):
            _sub(x, y, f"{path}[{i}]")
    else:
        assert a == b, (path, a, b)


def test_stage3_export_into_stage4():
    # "A stage-4 service must accept an export produced by the same team's ... stage-3 service, preserving
    # dossiers, candidates, history, the change feed and completed idempotent responses ... A stage-3 export keeps
    # its builds: after the upgrade, ?as_of= and /values answer from them as the stage-3 service did, with the
    # keys this stage adds." "After its import, investors is unknown ... and has no history entry".
    # "Imported candidates whose export records no origin take the host of their URL, normalised".
    reset(base=SVC3)
    tok = j(call("POST", "/auth/login", base=SVC3, body={"email": "ada@example.com", "password": "correct horse"}))["token"]
    mock_reset(0)
    k = newkey()
    r0 = call("POST", "/dossiers", token=tok, key=k, body={"domain": D}, base=SVC3)
    wait_done(tok, D, base=SVC3, timeout=60)
    call("POST", "/_test/clock", body={"now": T1}, base=SVC3)
    mock_reset(1)
    call("POST", f"/dossiers/{D}/refresh", token=tok, key=newkey(), base=SVC3)
    wait_done(tok, D, base=SVC3, timeout=60)
    probes = [(f"/dossiers/{D}", None), (f"/dossiers/{D}/history", None), ("/changes", {"limit": "200"}),
              (f"/dossiers/{D}", {"as_of": "2026-03-01T09:00:00+00:00"}), (f"/dossiers/{D}", {"as_of": T1}),
              (f"/dossiers/{D}/values", {"true_at": "2021-05-01"}),
              (f"/dossiers/{D}/values", {"true_at": "2026-04-01", "as_of": "2026-03-15T00:00:00+00:00"})]
    before = [j(call("GET", p, token=tok, params=q, base=SVC3)) for p, q in probes]
    e = j(call("GET", "/_test/export", base=SVC3, timeout=10))
    reset()
    set_clock(T1)
    mock_reset(0)
    assert call("POST", "/_test/import", body=e, timeout=10).status_code == 204
    time.sleep(0.5)
    from conftest import mock_log
    assert mock_log() == []
    after = [j(call("GET", p, token=tok, params=q)) for p, q in probes]
    for (p, q), a, b in zip(probes, before, after):
        _sub(a, b, f"{p} {q}")
    cur = after[0]
    inv = cur["fields"]["investors"]
    assert inv["value"] is None and inv["status"] == "unknown" and inv["candidates"] == []
    assert after[1]["fields"]["investors"] == []
    for f in FIELDS7:
        for c in cur["fields"][f]["candidates"]:
            assert c["origin"] == host_domain(c["url"]), (f, c["url"], c["origin"])
    r = call("POST", "/dossiers", token=tok, key=k, body={"domain": D})
    assert r.status_code == 200 and j(r) == j(r0)
