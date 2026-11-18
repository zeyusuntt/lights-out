"""Restart while builds run, phase C after `docker kill` mid-build + `docker start`.
Stage 4 'Restarts' supersedes RULING R3-4's rollback-only reading: each running build "Does not stay
building. It ends ready or failed within 10 seconds of GET /health first answering 200 after the restart ...
It may end failed although some of its calls succeeded; it then leaves the fields as they were (§8)."
"""
import json
import os
import time

import pytest

from conftest import OUT, call, check_candidates, check_citations, j, log_cost, mock_log, mock_reset, newkey, wait_done

D = "harbour-crane.test"


@pytest.fixture(scope="module")
def pre():
    p = os.path.join(OUT, "midbuild_snapshot.json")
    if not os.path.exists(p):
        pytest.fail("phase B did not start the builds")
    s = json.load(open(p))
    s["tok"] = json.load(open(os.path.join(OUT, "restart_snapshot.json")))["tokens"]["ada"]
    return s


def test_running_builds_end_within_10s_of_health(pre):
    t = pre["tok"]
    health_at = float(os.environ.get("HEALTH_AT", time.time()))
    doms = [D, "veilmoor-labs.test", "chainmere.test"]
    end = {}
    while time.time() < health_at + 12 and len(end) < len(doms):
        for d in doms:
            if d not in end and j(call("GET", f"/dossiers/{d}", token=t))["state"] != "building":
                end[d] = time.time()
        time.sleep(0.2)
    assert set(end) == set(doms), ("still building", set(doms) - set(end))
    assert max(end.values()) <= health_at + 10.5, {d: v - health_at for d, v in end.items()}


def test_outcome_fields_and_spending(pre):
    # failed -> fields as they were; ready -> a correct build. Every billed unit counted; at most 80 per build;
    # the batch within its budget.
    t = pre["tok"]
    time.sleep(1)
    calls = mock_log()
    b = j(call("GET", f"/dossiers/{D}", token=t))
    p = pre["dossier"]
    assert b["state"] in ("ready", "failed")
    if b["state"] == "failed":
        assert b["fields"] == p["fields"] and b["researched_at"] == p["researched_at"]
        assert j(call("GET", f"/dossiers/{D}/history", token=t)) == pre["history"]
    else:
        probs = check_candidates(b, D, 1, strict=False)
        assert not probs, probs
        check_citations(b, D, calls)
    g = j(call("GET", f"/batches/{pre['batch']['batch_id']}", token=t))
    for _ in range(50):
        if g["state"] == "done":
            break
        time.sleep(0.2)
        g = j(call("GET", f"/batches/{pre['batch']['batch_id']}", token=t))
    assert g["state"] == "done"
    assert g["spent_units"] <= 60
    delta = b["spent_units"] - p["spent_units"]
    assert 0 <= delta <= 80
    per = {d: j(call("GET", f"/dossiers/{d}", token=t))["spent_units"] for d in ("veilmoor-labs.test", "chainmere.test")}
    assert all(v <= 80 for v in per.values())
    # RULING R4-0 (tightened): billed units count in the dossier AND, for a batch build, in the batch.
    billed = billed_by_domain(calls)
    assert delta >= billed.get(D, 0), (delta, billed)
    for d in per:
        assert per[d] >= billed.get(d, 0), (d, per[d], billed)
    assert g["spent_units"] >= billed.get("veilmoor-labs.test", 0) + billed.get("chainmere.test", 0), (g, billed)


def test_replay_and_new_refresh_after_mid_build_kill(pre):
    # "The 202 that started the interrupted build stays replayable as recorded." "After the restart, POST
    # /dossiers/{domain}/refresh starts a new build of each such dossier as it does for any other."
    t = pre["tok"]
    r = call("POST", f"/dossiers/{D}/refresh", token=t, key=pre["key"])
    assert r.status_code == 200 and j(r) == pre["resp"]
    mock_reset(1)
    assert call("POST", f"/dossiers/{D}/refresh", token=t, key=newkey()).status_code == 202
    b, _ = wait_done(t, D, timeout=60)
    assert b["state"] == "ready"



def billed_by_domain(calls):
    """Attribute each billed call to a company: a query naming its domain or name, or a URL of one of its pages."""
    from conftest import corpus
    import oracle
    url_owner = {}
    for c in corpus():
        for p in c["pages"]:
            url_owner.setdefault(p["url"], c["domain"])
    doms = [c["domain"] for c in corpus()]
    out = {}
    for x in calls:
        owner = None
        q = (x.get("query") or "").lower()
        for d in doms:
            if d in q or oracle.company_name(d).lower() in q:
                owner = d
                break
        if owner is None:
            for u in x.get("urls") or []:
                if u in url_owner:
                    owner = url_owner[u]
                    break
        if owner:
            out[owner] = out.get(owner, 0) + (x.get("cost") or 0)
    return out
