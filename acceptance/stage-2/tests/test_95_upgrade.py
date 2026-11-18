"""Stage 2 'Existing clients after an upgrade': a stage-1 export (from the accepted stage-1 image, svc1)
imported into the stage-2 service."""
import json
import re
import time

import pytest

from conftest import (FIELDS, NOW0, SVC, SVC1, USERS, assert_err, call, check_shape, j, mock_log, mock_reset,
                      newkey, parse_ts, rank_key, reset, wait_done)
import oracle

DOMS = ["halvorsen-robotics.test", "tarnwick-labs.test", "rankford-tools.test"]


def _s1_world():
    reset(base=SVC1)
    tok = j(call("POST", "/auth/login", base=SVC1, body={"email": "ada@example.com",
                                                         "password": "correct horse"}))["token"]
    r = call("POST", "/auth/signup", base=SVC1, body={"email": "carol@example.com", "password": "carol pass 1",
                                                      "display_name": "Carol"})
    carol = j(r)["token"]
    served = {}
    for d in DOMS:
        mock_reset(0)
        assert call("POST", "/dossiers", token=tok, key=newkey(), body={"domain": d}, base=SVC1).status_code == 202
        wait_done(tok, d, base=SVC1, timeout=40)
        time.sleep(0.5)
        served[d] = mock_log()
    # a refresh to show the LAST ready build counts
    mock_reset(1)
    rk = newkey()
    rr = call("POST", "/dossiers/tarnwick-labs.test/refresh", token=tok, key=rk, base=SVC1)
    assert rr.status_code == 202
    wait_done(tok, "tarnwick-labs.test", base=SVC1, timeout=40)
    time.sleep(0.5)
    served["tarnwick-labs.test"] = mock_log()
    # a research request whose response the client "lost"
    k = newkey()
    lost = call("POST", "/dossiers", token=carol, key=k, body={"domain": "quillon-dynamics.test"}, base=SVC1)
    assert lost.status_code == 202
    wait_done(tok, "quillon-dynamics.test", base=SVC1, timeout=40)
    time.sleep(0.5)
    served["quillon-dynamics.test"] = mock_log()
    s1 = {d: j(call("GET", f"/dossiers/{d}", token=tok, base=SVC1)) for d in DOMS + ["quillon-dynamics.test"]}
    e = call("GET", "/_test/export", base=SVC1, timeout=10)
    assert e.status_code == 200
    return {"tok": tok, "carol": carol, "served": served, "s1": s1, "export": j(e), "k": k, "lost": j(lost),
            "rk": rk, "rr": j(rr)}


@pytest.fixture(scope="module")
def upgraded():
    w = _s1_world()
    reset()
    mock_reset(0)
    r = call("POST", "/_test/import", body=w["export"], timeout=10)
    # "A stage-2 service must accept an export produced by the same team's stage-1 service."
    assert r.status_code == 204, r.text
    time.sleep(0.5)
    w["import_calls"] = mock_log()
    return w


def test_stage1_export_accepted_tokens_and_retries_survive(upgraded):
    w = upgraded
    # §10 "Import makes no provider call"
    assert w["import_calls"] == []
    # "Imported dossiers appear in the list and on their screens"
    lst = j(call("GET", "/dossiers", token=w["tok"]))["dossiers"]
    assert [i["domain"] for i in lst] == sorted(DOMS + ["quillon-dynamics.test"])
    for d, s1 in w["s1"].items():
        b = j(call("GET", f"/dossiers/{d}", token=w["tok"]))
        check_shape(b, d)
        for k in ("dossier_id", "state", "researched_at", "spent_units"):
            assert b[k] == s1[k], (d, k)
    assert call("GET", "/dossiers", token=w["carol"]).status_code == 200
    r = call("POST", "/auth/login", body={"email": "carol@example.com", "password": "carol pass 1"})
    assert r.status_code == 200
    # "A research or refresh request whose response was lost before export remains retryable after import with
    # the same body and key"
    mock_reset(0)
    r = call("POST", "/dossiers", token=w["carol"], key=w["k"], body={"domain": "quillon-dynamics.test"})
    assert r.status_code == 200 and j(r) == w["lost"]
    r = call("POST", "/dossiers/tarnwick-labs.test/refresh", token=w["tok"], key=w["rk"])
    assert r.status_code == 200 and j(r) == w["rr"]
    time.sleep(0.5)
    assert mock_log() == []


def test_imported_candidates_follow_rule(upgraded):
    # "Each imported field gains one candidate ... The candidate's excerpt is taken from that text and supports
    # the value; its provider is the provider that served that text, its kind and published_at are as the
    # exported state records them or else null, and its retrieved_at is the dossier's researched_at. Each
    # imported field's value, status and citations then follow from its candidates by the selection rule and
    # Status." "Only an imported candidate has a null kind; it has the authority of aggregator."
    w = upgraded
    for d, s1 in w["s1"].items():
        b = j(call("GET", f"/dossiers/{d}", token=w["tok"]))
        for f in FIELDS:
            fld = b["fields"][f]
            cands = fld["candidates"]
            for c in cands:
                assert oracle.supports(c["excerpt"], f, c["value"], d), (d, f, c)
                assert len(c["excerpt"]) <= 500
                assert c["kind"] in (None, "own", "filing", "news", "aggregator")
                assert parse_ts(c["retrieved_at"]) == parse_ts(s1["researched_at"])
                served = [s["text"] for x in w["served"][d] if x.get("status") == 200 and x["provider"] == c["provider"]
                          for s in (x.get("served") or []) if s.get("url") == c["url"]]
                assert any(oracle.ws1(c["excerpt"]) in oracle.ws1(t) for t in served), (d, f, c)
            assert [rank_key(c) for c in cands] == sorted(rank_key(c) for c in cands), (d, f)
            if cands:
                assert cands[0]["selected"] and sum(c["selected"] for c in cands) == 1
                assert fld["value"] == cands[0]["value"]
                assert fld["citations"] == [{"url": c["url"], "excerpt": c["excerpt"], "provider": c["provider"]}
                                            for c in cands if c["value"] == cands[0]["value"]]
                n = len({json.dumps(c["value"]) for c in cands})
                assert fld["status"] == ("known" if n == 1 else "contested")
            else:
                assert fld["status"] == "unknown" and fld["value"] is None
            # every stage-1 citation's value is still supported by an imported candidate
            if s1["fields"][f]["status"] == "known":
                assert {c["value"] for c in cands} >= {s1["fields"][f]["value"]}, (d, f)


def test_imported_candidates_complete_from_last_build(upgraded):
    # "Each imported field gains one candidate for every value that text the providers served to the dossier's
    # last stage-1 build that completed ready supports", as RULING R2-5 reads it: the surviving served text is
    # the exported citation excerpts; each is tested against every field; one candidate per (page, value);
    # provider from the citation, kind null, published_at null, retrieved_at = researched_at.
    w = upgraded
    problems = {}
    for d, s1 in w["s1"].items():
        b = j(call("GET", f"/dossiers/{d}", token=w["tok"]))
        want = {}
        for f0 in FIELDS:
            for c in s1["fields"][f0]["citations"]:
                for f in FIELDS:
                    r = oracle.best_span(oracle.ws1(c["excerpt"]), f, d)
                    if r:
                        want.setdefault((f, c["url"], r[1]), c["provider"])
        got = {}
        for f in FIELDS:
            for c in b["fields"][f]["candidates"]:
                got[(f, c["url"], c["value"])] = c["provider"]
                if c["kind"] is not None or c["published_at"] is not None:
                    problems.setdefault(d, []).append(("kind/published_at not null", f, c["url"]))
                if parse_ts(c["retrieved_at"]) != parse_ts(s1["researched_at"]):
                    problems.setdefault(d, []).append(("retrieved_at", f, c["retrieved_at"]))
        if set(got) != set(want):
            problems.setdefault(d, []).append({"missing": sorted(map(str, set(want) - set(got))),
                                               "extra": sorted(map(str, set(got) - set(want)))})
        for k in set(got) & set(want):
            if got[k] != want[k]:
                problems.setdefault(d, []).append(("provider", k, got[k], want[k]))
    assert not problems, problems


def test_next_build_replaces_imported_candidates(upgraded):
    # "The candidates of an imported dossier are replaced by those of its next completed build."
    from conftest import check_candidates, set_clock
    w = upgraded
    d = "rankford-tools.test"
    set_clock("2026-03-09T00:00:00+00:00")
    mock_reset(0)
    assert call("POST", f"/dossiers/{d}/refresh", token=w["tok"], key=newkey()).status_code == 202
    b, _ = wait_done(w["tok"], d, timeout=40)
    assert b["state"] == "ready"
    probs = check_candidates(b, d, 0, build_time="2026-03-09T00:00:00+00:00")
    assert not probs, probs
    assert all(c["kind"] is not None for f in FIELDS for c in b["fields"][f]["candidates"])


def test_ui_session_and_lost_research_survive_export_import(upgraded):
    # "A browser signed in before that export/import upgrade must remain signed in afterwards. Imported
    # dossiers appear in the list and on their screens." "the UI must recover the original response and show
    # the imported dossier." Read here as: a browser signed in to this service, an export, a replacing import
    # of that export, then the browser carries on without a page reload or a new sign-in.
    import asyncio
    pw_api = pytest.importorskip("playwright.async_api")
    w = upgraded
    reset()
    assert call("POST", "/_test/import", body=w["export"], timeout=10).status_code == 204

    async def go():
        async with pw_api.async_playwright() as p:
            br = await p.chromium.launch(args=["--no-sandbox"])
            ctx = await br.new_context(base_url=SVC)
            ctx.set_default_timeout(15000)
            page = await ctx.new_page()
            await page.goto("/login")
            await page.get_by_test_id("login-email").fill("ada@example.com")
            await page.get_by_test_id("login-password").fill("correct horse")
            await page.get_by_test_id("login-submit").click()
            await page.get_by_test_id("current-user").wait_for(state="visible")
            await page.goto("/")
            await page.get_by_test_id("research-domain").fill("ironvale-pottery.test")
            pat = re.compile(r".*/dossiers/?$")

            async def lose(route):
                if route.request.method == "POST":
                    await route.fetch()
                    await route.abort("connectionreset")
                else:
                    await route.continue_()
            mock_reset(0)
            await page.route(pat, lose)
            await page.get_by_test_id("research-submit").click()
            await page.get_by_test_id("research-uncertain").wait_for(state="visible")
            await page.unroute(pat)
            await asyncio.to_thread(lambda: wait_done(login_tok(), "ironvale-pottery.test", timeout=40))
            e = await asyncio.to_thread(lambda: j(call("GET", "/_test/export", timeout=10)))
            await asyncio.to_thread(lambda: reset())
            r = await asyncio.to_thread(lambda: call("POST", "/_test/import", body=e, timeout=10))
            assert r.status_code == 204
            n_before = len([c for c in mock_log() if c["method"] == "search" and c.get("query") == "ironvale-pottery.test"
                            and c.get("status") == 200])
            if not (await page.get_by_test_id("research-domain").input_value()).strip():
                await page.get_by_test_id("research-domain").fill("ironvale-pottery.test")
            await page.get_by_test_id("research-submit").click()
            await page.wait_for_url(re.compile(r"/dossiers/ironvale-pottery\.test$"))
            await page.get_by_test_id("current-user").wait_for(state="visible")
            st = page.get_by_test_id("dossier-state")
            for _ in range(100):
                if (await st.inner_text()).strip() == "ready":
                    break
                await asyncio.sleep(0.2)
            assert (await st.inner_text()).strip() == "ready"
            assert await page.get_by_test_id("research-uncertain").count() == 0
            await asyncio.sleep(1)
            n_after = len([c for c in mock_log() if c["method"] == "search" and c.get("query") == "ironvale-pottery.test"
                           and c.get("status") == 200])
            assert n_after == n_before == 1, (n_before, n_after)
            await page.goto("/")
            await page.get_by_test_id(f"dossier-item-halvorsen-robotics.test").wait_for(state="visible")
            await br.close()
    asyncio.run(asyncio.wait_for(go(), 150))


def login_tok():
    return j(call("POST", "/auth/login", body={"email": "ada@example.com", "password": "correct horse"}))["token"]


def test_stage2_export_round_trips_candidates(fresh):
    # RULING R2-5 "a stage-2 export round-trips candidates, kinds and publication times exactly."
    from conftest import create
    t = fresh["ada"]
    mock_reset(0)
    create(t, "rankford-tools.test")
    wait_done(t, "rankford-tools.test", timeout=40)
    before = j(call("GET", "/dossiers/rankford-tools.test", token=t))
    e = j(call("GET", "/_test/export", timeout=10))
    reset()
    assert call("POST", "/_test/import", body=e, timeout=10).status_code == 204
    assert j(call("GET", "/dossiers/rankford-tools.test", token=t)) == before
