"""§11 concurrency, §2 resource limits (50 in flight, 5 s per request), §8 one dossier per domain."""
import concurrent.futures as cf
import time

from conftest import (FIELDS, call, check_citations, create, fresh, get, j, log_cost, mock_log,
                      mock_reset, newkey, refresh, wait_done)


def test_concurrent_creates_same_domain_one_dossier_one_build(fresh):
    # §8 "Concurrent requests for the same domain create one dossier and start one build, whatever their keys."
    # §8 "When a dossier already exists for the domain, the service starts no build and returns 200"
    t = fresh["ada"]
    d = "halvorsen-robotics.test"
    mock_reset(0)
    spellings = [d, "WWW." + d, d.upper() + ".", " " + d]
    with cf.ThreadPoolExecutor(50) as ex:
        rs = list(ex.map(lambda i: create(fresh["ada" if i % 2 else "bob"], spellings[i % 4]), range(50)))
    codes = [r.status_code for r in rs]
    assert codes.count(202) == 1 and codes.count(200) == 49, sorted(codes)
    ids = {j(r)["dossier_id"] for r in rs}
    assert len(ids) == 1
    assert all(j(r)["domain"] == d for r in rs)
    b, _ = wait_done(t, d, timeout=30)
    time.sleep(0.5)
    calls = mock_log()
    dom = [c for c in calls if c["method"] == "search" and c["status"] == 200 and c["query"] == d]
    assert len(dom) == 1, len(dom)
    assert b["spent_units"] == log_cost(calls) <= 80
    assert len(j(call("GET", "/dossiers", token=t))["dossiers"]) == 1


def test_fifty_in_flight_mixed_no_5xx_within_5s(fresh):
    # §2 "Concurrent requests | up to 50 in flight"; "Per-request timeout | 5 s"; §5 no 5xx under load.
    # call() enforces the 5 s timeout and the no-5xx rule on every request.
    t = fresh["ada"]
    doms = ["tarnwick-labs.test", "quillon-dynamics.test", "nullmark-systems.test",
            "ferncliff-foods.test", "mosaic-freight.test"]
    for d in doms:
        create(t, d)

    def op(i):
        d = doms[i % len(doms)]
        k = i % 5
        if k == 0:
            return get(t, d)
        if k == 1:
            return call("GET", "/dossiers", token=t, params={"q": "o"})
        if k == 2:
            return create(t, d)
        if k == 3:
            return call("POST", "/auth/login", body={"email": "bob@example.com", "password": "correct horse"})
        return refresh(t, d)

    t0 = time.time()
    with cf.ThreadPoolExecutor(50) as ex:
        rs = list(ex.map(op, range(200)))
    assert all(r.status_code in (200, 202) for r in rs), sorted({r.status_code for r in rs})
    for d in doms:
        b, _ = wait_done(t, d, timeout=40)
        assert b["state"] == "ready"


def test_reads_during_build_always_consistent(fresh):
    # §11 "The requirements above hold at every read."
    t = fresh["ada"]
    d = "tarnwick-labs.test"
    mock_reset(0)
    assert create(t, d).status_code == 202
    seen = []
    t0 = time.time()
    while time.time() - t0 < 12:
        b = j(get(t, d))
        seen.append(b)
        if b["state"] != "building":
            break
    calls = mock_log()
    for b in seen:
        assert b["state"] in ("building", "ready")
        if b["state"] == "building":
            assert all(b["fields"][f]["status"] == "unknown" for f in FIELDS)
        else:
            check_citations(b, d, calls)
    assert seen[-1]["state"] == "ready"


def test_post_seal_fifty_concurrent_durable_writes_within_5s(fresh):
    # POST-SEAL ADDITION (stage 3 durability puts a disk write behind every write). §2 "Concurrent requests |
    # up to 50 in flight", "Per-request timeout | 5 s"; call() enforces the 5 s bound and no 5xx.
    t = fresh["ada"]
    for d in ("tarnwick-labs.test", "quillon-dynamics.test", "rankford-tools.test", "harbour-crane.test"):
        mock_reset(0)
        create(t, d)
        wait_done(t, d, timeout=60)
    from conftest import PW
    t0 = time.time()
    with cf.ThreadPoolExecutor(50) as ex:
        rs = list(ex.map(lambda i: call("POST", "/auth/signup", body={"email": f"w{i}@example.com", "password": PW,
                                                                     "display_name": f"W{i}"}), range(50)))
    assert all(r.status_code == 201 for r in rs)
    with cf.ThreadPoolExecutor(50) as ex:
        rs = list(ex.map(lambda i: create(t, "tarnwick-labs.test"), range(50)))
    assert all(r.status_code == 200 for r in rs)
    assert time.time() - t0 < 30
