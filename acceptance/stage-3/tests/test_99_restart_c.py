"""Stage 3 restart while a build runs (RULING R3-4), phase C after `docker kill` mid-build + `docker start`."""
import json
import os

import pytest

from conftest import OUT, call, j, mock_reset, newkey, wait_done

D = "harbour-crane.test"


@pytest.fixture(scope="module")
def pre():
    p = os.path.join(OUT, "midbuild_snapshot.json")
    if not os.path.exists(p):
        pytest.fail("phase B did not start the build")
    s = json.load(open(p))
    s["tok"] = json.load(open(os.path.join(OUT, "restart_snapshot.json")))["tokens"]["ada"]
    return s


def test_rolled_back_to_pre_build(pre):
    # "The dossier is as it was before that build: its fields, candidates, researched_at, history and feed ...
    # not stuck in building"; spent_units is the pre-build value or that plus what was recorded, at most 80 more.
    t = pre["tok"]
    b = j(call("GET", f"/dossiers/{D}", token=t))
    p = pre["dossier"]
    assert b["state"] == p["state"] != "building"
    assert b["fields"] == p["fields"] and b["researched_at"] == p["researched_at"]
    assert p["spent_units"] <= b["spent_units"] <= p["spent_units"] + 80
    assert j(call("GET", f"/dossiers/{D}/history", token=t)) == pre["history"]
    assert j(call("GET", "/changes", token=t, params={"limit": "200"})) == pre["changes"]
    assert j(call("GET", "/dossiers/tarnwick-labs.test", token=t)) == pre["other"]


def test_replay_and_new_refresh_after_mid_build_kill(pre):
    # "The 202 that started the interrupted build stays replayable as recorded." "a new refresh starts a new
    # build normally."
    t = pre["tok"]
    r = call("POST", f"/dossiers/{D}/refresh", token=t, key=pre["key"])
    assert r.status_code == 200 and j(r) == pre["resp"]
    mock_reset(1)
    assert call("POST", f"/dossiers/{D}/refresh", token=t, key=newkey()).status_code == 202
    b, _ = wait_done(t, D, timeout=60)
    assert b["state"] == "ready"
