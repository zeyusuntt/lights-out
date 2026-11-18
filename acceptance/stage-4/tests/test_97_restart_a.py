"""Stage 3 'Restarts', phase A: populate and record answers; run.sh then kills and restarts the container,
and test_98_restart_b.py compares. "When no build is running at the stop, the service answers after the
restart exactly as it did before the stop"."""
import json
import os
import time

from conftest import (OUT, call, create, j, login, mock_reset, newkey, refresh, reset, set_clock, wait_done)

D = "harbour-crane.test"
PROBE_CLOCK = "2026-05-05T05:05:05+00:00"


def probes(D):
    ps = [("GET", "/dossiers", None), ("GET", f"/dossiers/{D}", None), ("GET", f"/dossiers/{D}/history", None),
          ("GET", "/changes", {"limit": "200"}), ("GET", f"/dossiers/{D}", {"as_of": "2026-03-01T09:00:00+00:00"}),
          ("GET", f"/dossiers/{D}/values", {"true_at": "2021-05-01"}),
          ("GET", f"/dossiers/{D}/values", {"true_at": "2026-04-01", "as_of": "2026-03-15T00:00:00+00:00"}),
          ("GET", "/dossiers/tarnwick-labs.test", None)]
    return ps


def test_restart_phase_a_populate():
    reset()
    t = login("ada@example.com")
    r = call("POST", "/auth/signup", body={"email": "rita@example.com", "password": "rita pass 1", "display_name": "Rita"})
    rita = j(r)["token"]
    mock_reset(0)
    k = newkey()
    r1 = create(t, D, key=k)
    wait_done(t, D, timeout=60)
    set_clock("2026-04-01T09:00:00+00:00")
    mock_reset(1)
    rk = newkey()
    r2 = refresh(t, D, key=rk)
    wait_done(t, D, timeout=60)
    mock_reset(0)
    create(rita, "tarnwick-labs.test")
    wait_done(t, "tarnwick-labs.test", timeout=60)
    set_clock(PROBE_CLOCK)
    time.sleep(1.5)  # nothing running at the stop
    snap = {"tokens": {"ada": t, "rita": rita}, "replays": [["POST", "/dossiers", k, {"domain": D}, j(r1)],
                                                           ["POST", f"/dossiers/{D}/refresh", rk, None, j(r2)]],
            "answers": [[m, p, q, j(call(m, p, token=t, params=q))] for m, p, q in probes(D)]}
    os.makedirs(OUT, exist_ok=True)
    json.dump(snap, open(os.path.join(OUT, "restart_snapshot.json"), "w"))
