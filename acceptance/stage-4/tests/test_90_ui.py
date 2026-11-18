"""Stage 2 Screens: browser tests (playwright, chromium) against the service's own UI."""
import asyncio
import json
import re
import time

import httpx
import pytest

from conftest import (FIELDS, SVC, call, create, fresh, get, j, login, mock_epoch, mock_fault, mock_log,
                      mock_reset, newkey, refresh, wait_done)

pw_api = pytest.importorskip("playwright.async_api")
D = "tarnwick-labs.test"
ORDER = ["legal_name", "hq_city", "ceo", "founded_year", "headcount_range", "funding_total"]


def run(coro):
    return asyncio.run(asyncio.wait_for(coro, 120))


async def browser_ctx(p, width=1280, height=900):
    b = await p.chromium.launch(args=["--no-sandbox"])
    ctx = await b.new_context(viewport={"width": width, "height": height}, base_url=SVC)
    ctx.set_default_timeout(15000)
    return b, ctx


async def ui_login(page, email="ada@example.com", pw="correct horse"):
    await page.goto("/login")
    await page.get_by_test_id("login-email").fill(email)
    await page.get_by_test_id("login-password").fill(pw)
    await page.get_by_test_id("login-submit").click()
    await page.get_by_test_id("current-user").wait_for(state="visible")


def domain_searches(d):
    return [c for c in mock_log() if c["method"] == "search" and c.get("status") == 200 and c.get("query") == d]


async def wait_text(loc, want, timeout=20):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if (await loc.inner_text(timeout=1000)).strip() == want:
                return
        except Exception:
            pass
        await asyncio.sleep(0.2)
    raise AssertionError(f"text never became {want!r}; last {await loc.inner_text()!r}")


def test_signup_login_logout_and_auth_error(fresh):
    # Screens: /signup, /login; data-testid signup-*, login-*, auth-error ("Present only when there is one"),
    # current-user ("Visible on every screen when signed in. Text contains the display name"), logout-button.
    async def go():
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await page.goto("/signup")
            assert await page.get_by_test_id("auth-error").count() == 0
            await page.get_by_test_id("signup-email").fill("ui-new@example.com")
            await page.get_by_test_id("signup-password").fill("correct horse")
            await page.get_by_test_id("signup-display-name").fill("Una Interface")
            await page.get_by_test_id("signup-submit").click()
            cu = page.get_by_test_id("current-user")
            await cu.wait_for(state="visible")
            assert "Una Interface" in await cu.inner_text()
            for route in ("/", f"/dossiers/{D}", f"/dossiers/{D}/evidence", "/contested"):
                await page.goto(route)
                await page.get_by_test_id("current-user").wait_for(state="visible")
            await page.get_by_test_id("logout-button").click()
            await page.wait_for_timeout(800)
            assert await page.get_by_test_id("current-user").count() == 0 or \
                not await page.get_by_test_id("current-user").is_visible()
            await page.goto("/login")
            assert await page.get_by_test_id("auth-error").count() == 0
            await page.get_by_test_id("login-email").fill("ada@example.com")
            await page.get_by_test_id("login-password").fill("wrong password")
            await page.get_by_test_id("login-submit").click()
            await page.get_by_test_id("auth-error").wait_for(state="visible")
            await page.goto("/signup")
            await page.get_by_test_id("signup-email").fill("ada@example.com")
            await page.get_by_test_id("signup-password").fill("correct horse")
            await page.get_by_test_id("signup-display-name").fill("Dup")
            await page.get_by_test_id("signup-submit").click()
            await page.get_by_test_id("auth-error").wait_for(state="visible")
            await b.close()
    run(go())


def test_html_and_json_share_dossier_route(fresh):
    # "The browser and the API share /dossiers/{domain}. Return the UI for Accept: text/html; API requests
    # without that header receive JSON."
    t = fresh["ada"]
    assert create(t, D).status_code == 202
    wait_done(t, D)
    r = httpx.get(SVC + f"/dossiers/{D}", headers={"Accept": "text/html", "Authorization": f"Bearer {t}"}, timeout=5)
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/html"), r.headers
    r2 = httpx.get(SVC + f"/dossiers/{D}", headers={"Authorization": f"Bearer {t}"}, timeout=5)
    assert r2.headers["content-type"].startswith("application/json") and r2.json()["domain"] == D
    for route in ("/", f"/dossiers/{D}/evidence", "/contested", "/signup", "/login"):
        r = httpx.get(SVC + route, headers={"Accept": "text/html"}, timeout=5)
        assert r.status_code == 200 and "text/html" in r.headers["content-type"], route


def test_research_flow_polls_until_ready_and_renders_fields(fresh):
    # / research form; "A research request that succeeds, with 202 or 200, opens /dossiers/{domain} for the
    # normalised domain." "While the dossier's state is building, the screen reads the dossier again at least
    # every 2 seconds until the state is ready or failed, and then shows the new fields without a manual reload."
    async def go():
        mock_reset(0)
        for prov, m in (("nimble", ["search", "extract", "research"]), ("tavily", ["search", "extract"])):
            mock_fault(prov, m, "delay", seconds=2)
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await ui_login(page)
            await page.goto("/")
            await page.get_by_test_id("research-domain").fill("  WWW.Tarnwick-Labs.TEST. ")
            reads = []
            page.on("request", lambda r: reads.append(time.time()) if r.method == "GET" and
                    re.search(r"/dossiers/tarnwick-labs\.test(\?|$)", r.url) else None)
            await page.get_by_test_id("research-submit").click()
            await page.wait_for_url(re.compile(r"/dossiers/tarnwick-labs\.test$"))
            await wait_text(page.get_by_test_id("dossier-domain"), D)
            st = page.get_by_test_id("dossier-state")
            await wait_text(st, "building", timeout=5)
            t_build = time.time()
            await wait_text(st, "ready", timeout=40)
            t_ready = time.time()
            in_build = [x for x in reads if t_build - 0.1 <= x <= t_ready]
            span = t_ready - t_build
            if span > 4.5:
                assert len(in_build) >= int(span / 2.0) - 1, (len(in_build), span)
            api = j(get(login("ada@example.com"), D))
            # fields, in table order, with status, values, citations
            ids = await page.locator("[data-testid^='field-']").evaluate_all(
                "els => els.map(e => e.getAttribute('data-testid'))")
            order = [x[len("field-"):] for x in ids if x[len("field-"):] in ORDER]
            assert order == ORDER, ids
            for f in ORDER:
                fe = page.get_by_test_id(f"field-{f}")
                assert await fe.get_attribute("data-status") == api["fields"][f]["status"]
                v = api["fields"][f]["value"]
                fv = page.get_by_test_id(f"field-value-{f}")
                if v is None:
                    assert await fv.count() == 0
                else:
                    assert await fv.get_attribute("data-value") == str(v)
                for n, c in enumerate(api["fields"][f]["citations"], 1):
                    ce = page.get_by_test_id(f"citation-{f}-{n}")
                    assert oracle_ws(c["excerpt"]) in oracle_ws(await ce.inner_text())
                    assert await ce.get_attribute("data-provider") == c["provider"]
                    hrefs = await ce.locator("a").evaluate_all("els => els.map(e => e.href)")
                    assert c["url"] in hrefs or c["url"].rstrip("/") in [h.rstrip("/") for h in hrefs], hrefs
                assert await page.get_by_test_id(f"citation-{f}-{len(api['fields'][f]['citations']) + 1}").count() == 0
                contested = page.get_by_test_id(f"field-contested-{f}")
                assert (await contested.count() > 0) == (api["fields"][f]["status"] == "contested")
            sp = page.get_by_test_id("dossier-spent")
            assert await sp.get_attribute("data-units") == str(api["spent_units"])
            assert await page.get_by_test_id("dossier-researched-at").count() == 1
            href = await page.get_by_test_id("dossier-evidence-link").get_attribute("href")
            assert href.rstrip("/").endswith(f"/dossiers/{D}/evidence")
            await b.close()
    run(go())


def oracle_ws(s):
    return re.sub(r"\s+", " ", s).strip()


def test_research_invalid_domain_shows_error(fresh):
    # research-error "when the request is refused — including an invalid domain"
    async def go():
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await ui_login(page)
            await page.goto("/")
            assert await page.get_by_test_id("research-error").count() == 0
            await page.get_by_test_id("research-domain").fill("https://not a domain/")
            await page.get_by_test_id("research-submit").click()
            await page.get_by_test_id("research-error").wait_for(state="visible")
            assert await page.get_by_test_id("research-uncertain").count() == 0 or \
                not await page.get_by_test_id("research-uncertain").is_visible()
            await b.close()
    run(go())


def test_existing_domain_opens_dossier_without_build(fresh):
    # "A domain that already has a dossier, including one created by another client after this browser read
    # the list, opens that dossier and starts no build."
    async def go():
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await ui_login(page)
            await page.goto("/")
            await page.get_by_test_id("empty-dossiers").wait_for(state="visible")
            mock_reset(0)
            await asyncio.to_thread(lambda: create(fresh["bob"], D))
            await asyncio.to_thread(lambda: wait_done(fresh["bob"], D))
            await page.get_by_test_id("research-domain").fill(D)
            await page.get_by_test_id("research-submit").click()
            await page.wait_for_url(re.compile(r"/dossiers/tarnwick-labs\.test$"))
            await wait_text(page.get_by_test_id("dossier-state"), "ready")
            await asyncio.sleep(1)
            assert len(domain_searches(D)) == 1
            await b.close()
    run(go())


def test_list_order_states_search_and_empty(fresh):
    # / : dossier-list "Children ordered by domain ascending"; dossier-item-{domain} data-state, text has domain
    # and legal name when known, links to /dossiers/{domain}; dossier-search filters as q; empty-dossiers.
    t = fresh["ada"]
    doms = ["tarnwick-labs.test", "quillon-dynamics.test", "nullmark-systems.test"]
    for d in doms:
        create(t, d)
    for d in doms:
        wait_done(t, d, timeout=40)

    async def go():
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await ui_login(page)
            await page.goto("/")
            lst = page.get_by_test_id("dossier-list")
            await lst.wait_for(state="visible")
            ids = await lst.locator("[data-testid^='dossier-item-']").evaluate_all(
                "els => els.map(e => e.getAttribute('data-testid'))")
            assert ids == [f"dossier-item-{d}" for d in sorted(doms)], ids
            for d in doms:
                it = page.get_by_test_id(f"dossier-item-{d}")
                assert await it.get_attribute("data-state") == "ready"
                txt = await it.inner_text()
                assert d in txt
                ln = j(get(t, d))["fields"]["legal_name"]["value"]
                if ln:
                    assert ln in txt
                hrefs = await it.evaluate("e => [e.href, ...Array.from(e.querySelectorAll('a')).map(a => a.href)]")
                assert any(h and h.rstrip('/').endswith(f"/dossiers/{d}") for h in hrefs), hrefs
            await page.get_by_test_id("dossier-search").fill("S.A.S")
            await page.wait_for_timeout(1500)
            vis = await page.locator("[data-testid^='dossier-item-']").evaluate_all(
                "els => els.filter(e => e.offsetParent !== null).map(e => e.getAttribute('data-testid'))")
            assert vis == ["dossier-item-tarnwick-labs.test"], vis
            await page.get_by_test_id("dossier-search").fill("zzz-nothing")
            await page.get_by_test_id("empty-dossiers").wait_for(state="visible")
            await b.close()
    run(go())


def test_dossier_not_found_and_normalised_browser_route(fresh):
    # dossier-not-found "Shown instead of the fields when no dossier exists"; "The domain in a browser route
    # is normalised as in §4."
    t = fresh["ada"]
    create(t, D)
    wait_done(t, D)

    async def go():
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await ui_login(page)
            await page.goto("/dossiers/nobody-home.test")
            await page.get_by_test_id("dossier-not-found").wait_for(state="visible")
            assert await page.locator("[data-testid='field-ceo']").count() == 0
            await page.goto("/dossiers/WWW.Tarnwick-Labs.TEST")
            await wait_text(page.get_by_test_id("dossier-domain"), D)
            await page.goto("/dossiers/WWW.Tarnwick-Labs.TEST/evidence")
            await page.get_by_test_id("evidence-ceo").wait_for(state="attached")
            await b.close()
    run(go())


def test_evidence_screen_matches_candidates(fresh):
    # /dossiers/{domain}/evidence: evidence-{field} children in API candidates order; candidate-{field}-{n}
    # attributes; evidence-empty-{field} when none.
    t = fresh["ada"]
    for d in ("rankford-tools.test",):
        mock_reset(0)
        create(t, d)
        wait_done(t, d, timeout=40)
    api = j(get(t, "rankford-tools.test"))

    async def go():
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await ui_login(page)
            await page.goto("/dossiers/rankford-tools.test/evidence")
            for f in FIELDS:
                await page.get_by_test_id(f"evidence-{f}").wait_for(state="attached")
                cands = api["fields"][f]["candidates"]
                if not cands:
                    await page.get_by_test_id(f"evidence-empty-{f}").wait_for(state="visible")
                    continue
                for n, c in enumerate(cands, 1):
                    el = page.get_by_test_id(f"candidate-{f}-{n}")
                    assert await el.get_attribute("data-value") == str(c["value"])
                    assert await el.get_attribute("data-provider") == c["provider"]
                    assert await el.get_attribute("data-kind") == (c["kind"] or "")
                    assert await el.get_attribute("data-url") == c["url"]
                    dp = await el.get_attribute("data-published-at")
                    if c["published_at"] is None:
                        assert dp == ""
                    else:
                        from conftest import parse_ts
                        assert parse_ts(dp) == parse_ts(c["published_at"])
                    assert await el.get_attribute("data-selected") == ("true" if c["selected"] else "false")
                    assert oracle_ws(c["excerpt"]) in oracle_ws(await el.inner_text())
                assert await page.get_by_test_id(f"candidate-{f}-{len(cands) + 1}").count() == 0
            await b.close()
    run(go())


def test_contested_screen(fresh):
    # /contested: contested-list ordered by domain then field order; contested-item-{domain}-{field} with
    # data-value of the selected value, text with domain, field and every distinct candidate value, link to
    # the evidence screen; empty-contested when none.
    t = fresh["ada"]

    async def go():
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await ui_login(page)
            await page.goto("/contested")
            await page.get_by_test_id("empty-contested").wait_for(state="visible")
            for d in ("rankford-tools.test", "halvorsen-robotics.test", "tarnwick-labs.test"):
                mock_reset(0)
                await asyncio.to_thread(lambda: create(t, d))
                await asyncio.to_thread(lambda: wait_done(t, d, timeout=40))
            api = {d: j(get(t, d)) for d in ("halvorsen-robotics.test", "rankford-tools.test", "tarnwick-labs.test")}
            want = [(d, f) for d in sorted(api) for f in ORDER if api[d]["fields"][f]["status"] == "contested"]
            await page.goto("/contested")
            lst = page.get_by_test_id("contested-list")
            await lst.wait_for(state="visible")
            ids = await lst.locator("[data-testid^='contested-item-']").evaluate_all(
                "els => els.map(e => e.getAttribute('data-testid'))")
            assert ids == [f"contested-item-{d}-{f}" for d, f in want], (ids, want)
            for d, f in want:
                el = page.get_by_test_id(f"contested-item-{d}-{f}")
                assert await el.get_attribute("data-value") == str(api[d]["fields"][f]["value"])
                txt = await el.inner_text()
                assert d in txt
                assert f in txt or f.replace("_", " ") in txt.lower(), txt
                for v in {str(c["value"]) for c in api[d]["fields"][f]["candidates"]}:
                    assert v in txt, (v, txt)
                hrefs = await el.evaluate("e => [e.href, ...Array.from(e.querySelectorAll('a')).map(a => a.href)]")
                assert any(h and h.rstrip('/').endswith(f"/dossiers/{d}/evidence") for h in hrefs), hrefs
            await b.close()
    run(go())


def test_refresh_button_and_competing_client(fresh):
    # dossier-refresh "Sends POST /dossiers/{domain}/refresh"; "A refresh from this browser while that build
    # runs is answered 202 like any other and the screen follows the running build to its end."
    t = fresh["ada"]
    create(t, D)
    wait_done(t, D)

    async def go():
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await ui_login(page)
            await page.goto(f"/dossiers/{D}")
            await wait_text(page.get_by_test_id("dossier-state"), "ready")
            mock_reset(0)
            for prov, m in (("nimble", ["search", "extract", "research"]), ("tavily", ["search", "extract"])):
                mock_fault(prov, m, "delay", seconds=2)
            await asyncio.to_thread(lambda: refresh(fresh["bob"], D))
            posts = []
            page.on("response", lambda r: posts.append(r.status) if r.request.method == "POST" and
                    "/refresh" in r.url else None)
            await page.get_by_test_id("dossier-refresh").click()
            await wait_text(page.get_by_test_id("dossier-state"), "building", timeout=6)
            await wait_text(page.get_by_test_id("dossier-state"), "ready", timeout=40)
            assert posts and posts[0] == 202, posts
            await asyncio.sleep(1)
            assert len(domain_searches(D)) == 1
            assert await page.get_by_test_id("refresh-error").count() == 0
            await b.close()
    run(go())


def test_refresh_refused_shows_error(fresh):
    # refresh-error "Error message, when a refresh is refused"
    t = fresh["ada"]
    create(t, D)
    wait_done(t, D)

    async def go():
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await ui_login(page)
            await page.goto(f"/dossiers/{D}")
            await wait_text(page.get_by_test_id("dossier-state"), "ready")

            async def refuse(route):
                await route.fulfill(status=404, content_type="application/json; charset=utf-8",
                                    body=json.dumps({"error": {"code": "not_found", "message": "gone"}}))
            await page.route(re.compile(r".*/dossiers/[^/]+/refresh$"), refuse)
            await page.get_by_test_id("dossier-refresh").click()
            await page.get_by_test_id("refresh-error").wait_for(state="visible")
            assert await page.get_by_test_id("refresh-uncertain").count() == 0 or \
                not await page.get_by_test_id("refresh-uncertain").is_visible()
            await b.close()
    run(go())


def _lost_after_commit(kind):
    async def handler(route):
        if route.request.method == "POST":
            await route.fetch()          # the request reaches the service and commits
            await route.abort("connectionreset")  # ... and its response is lost
        else:
            await route.continue_()
    return handler


def test_lost_research_response_uncertain_then_retry(fresh):
    # "If a research or refresh response is lost, including after the request commits, show research-uncertain
    # ..., not research-error. Keep the request retryable with the same key and body. A successful retry
    # removes both the error and the uncertainty elements, shows the dossier, and starts at most one build."
    async def go():
        mock_reset(0)
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await ui_login(page)
            await page.goto("/")
            keys = []
            page.on("request", lambda r: keys.append(r.headers.get("idempotency-key")) if r.method == "POST"
                    and r.url.rstrip("/").endswith("/dossiers") else None)
            await page.route(re.compile(r".*/dossiers/?$"), _lost_after_commit("research"))
            await page.get_by_test_id("research-domain").fill(D)
            await page.get_by_test_id("research-submit").click()
            un = page.get_by_test_id("research-uncertain")
            await un.wait_for(state="visible")
            assert (await un.inner_text()).strip()
            assert await page.get_by_test_id("research-error").count() == 0 or \
                not await page.get_by_test_id("research-error").is_visible()
            await page.unroute(re.compile(r".*/dossiers/?$"))
            if not (await page.get_by_test_id("research-domain").input_value()).strip():
                await page.get_by_test_id("research-domain").fill(D)
            await page.get_by_test_id("research-submit").click()
            await page.wait_for_url(re.compile(r"/dossiers/tarnwick-labs\.test$"))
            await wait_text(page.get_by_test_id("dossier-state"), "ready", timeout=40)
            assert await page.get_by_test_id("research-uncertain").count() == 0
            assert await page.get_by_test_id("research-error").count() == 0
            assert len(keys) >= 2 and keys[0] and keys[0] == keys[1], keys
            await asyncio.sleep(1)
            assert len(domain_searches(D)) == 1
            await b.close()
    run(go())


def test_lost_refresh_response_uncertain_then_retry(fresh):
    t = fresh["ada"]
    create(t, D)
    wait_done(t, D)

    async def go():
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await ui_login(page)
            await page.goto(f"/dossiers/{D}")
            await wait_text(page.get_by_test_id("dossier-state"), "ready")
            mock_reset(0)
            keys = []
            page.on("request", lambda r: keys.append(r.headers.get("idempotency-key")) if r.method == "POST"
                    and "/refresh" in r.url else None)
            pat = re.compile(r".*/dossiers/[^/]+/refresh$")
            await page.route(pat, _lost_after_commit("refresh"))
            await page.get_by_test_id("dossier-refresh").click()
            un = page.get_by_test_id("refresh-uncertain")
            await un.wait_for(state="visible")
            assert (await un.inner_text()).strip()
            assert await page.get_by_test_id("refresh-error").count() == 0 or \
                not await page.get_by_test_id("refresh-error").is_visible()
            await page.unroute(pat)
            await asyncio.to_thread(lambda: wait_done(t, D, timeout=40))
            await page.get_by_test_id("dossier-refresh").click()
            await page.wait_for_timeout(1500)
            assert await page.get_by_test_id("refresh-uncertain").count() == 0
            assert await page.get_by_test_id("refresh-error").count() == 0
            await wait_text(page.get_by_test_id("dossier-state"), "ready", timeout=40)
            assert len(keys) >= 2 and keys[0] and keys[0] == keys[1], keys
            await asyncio.sleep(1)
            assert len(domain_searches(D)) == 1, "retry started a second build"
            await b.close()
    run(go())


def test_reload_latest_read_wins(fresh):
    # "dossier-reload reads the dossier again. Latest read wins: a delayed earlier read must not overwrite a
    # later one, including when responses arrive out of order."
    t = fresh["ada"]
    mock_reset(0)
    create(t, D)
    wait_done(t, D)

    async def go():
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await ui_login(page)
            await page.goto(f"/dossiers/{D}")
            await wait_text(page.get_by_test_id("dossier-state"), "ready")
            v = page.get_by_test_id("field-value-ceo")
            assert await v.get_attribute("data-value") == "Mira Solberg"
            gate = asyncio.Event()
            state = {"n": 0}
            pat = re.compile(r".*/dossiers/tarnwick-labs\.test(\?.*)?$")

            async def hold_first(route):
                if route.request.method != "GET":
                    return await route.continue_()
                state["n"] += 1
                if state["n"] == 1:
                    resp = await route.fetch()      # the earlier read: old data
                    body = await resp.body()
                    await gate.wait()
                    try:
                        await route.fulfill(response=resp, body=body)
                    except Exception:
                        pass
                else:
                    await route.continue_()
            await page.route(pat, hold_first)
            await page.get_by_test_id("dossier-reload").click()
            for _ in range(50):
                if state["n"] >= 1:
                    break
                await asyncio.sleep(0.1)
            mock_epoch(1)
            await asyncio.to_thread(lambda: refresh(t, D))
            await asyncio.to_thread(lambda: wait_done(t, D, timeout=40))
            await page.get_by_test_id("dossier-reload").click()
            for _ in range(100):
                if (await v.count()) and await v.get_attribute("data-value") == "Jonas Erikson Vale":
                    break
                await asyncio.sleep(0.2)
            assert await v.get_attribute("data-value") == "Jonas Erikson Vale"
            gate.set()
            await asyncio.sleep(2)
            assert await page.get_by_test_id("field-value-ceo").get_attribute("data-value") == "Jonas Erikson Vale"
            await b.close()
    run(go())


@pytest.mark.parametrize("width", [375, 1280])
def test_no_horizontal_scroll_and_labels(fresh, width):
    # "The required flows must remain clear and usable at a 375 CSS-pixel viewport and at conventional desktop
    # widths, without horizontal page scrolling. Inputs need visible labels"
    t = fresh["ada"]
    for d in ("rankford-tools.test", "ironvale-pottery.test"):
        mock_reset(0)
        create(t, d)
        wait_done(t, d, timeout=40)

    async def go():
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p, width=width, height=800)
            page = await ctx.new_page()
            for route in ("/signup", "/login"):
                await page.goto(route)
                await page.wait_for_load_state("networkidle")
                await _no_hscroll(page, route)
                await _labels(page)
            await ui_login(page)
            for route in ("/", "/dossiers/rankford-tools.test", "/dossiers/ironvale-pottery.test",
                          "/dossiers/rankford-tools.test/evidence", "/contested", "/dossiers/nobody-home.test"):
                await page.goto(route)
                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(500)
                await _no_hscroll(page, route)
                await _labels(page)
            await b.close()
    run(go())


async def _no_hscroll(page, route):
    sw, cw = await page.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]")
    assert sw <= cw + 1, (route, sw, cw)


async def _labels(page):
    bad = await page.evaluate("""() => Array.from(document.querySelectorAll('input:not([type=hidden]),select,textarea'))
      .filter(e => e.offsetParent !== null)
      .filter(e => !((e.labels && Array.from(e.labels).some(l => l.innerText.trim())) ||
                     (e.getAttribute('aria-labelledby') && document.getElementById(e.getAttribute('aria-labelledby'))
                        && document.getElementById(e.getAttribute('aria-labelledby')).innerText.trim())))
      .map(e => e.getAttribute('data-testid') || e.name || e.id)""")
    assert not bad, f"inputs without a visible label: {bad}"


def test_html_shells_without_bearer_and_json_unchanged(fresh):
    # RULING R2-2: any request whose Accept includes text/html gets the UI with 200, signed in or not; without
    # text/html in Accept the stage-1 JSON behaviour is unchanged (401 unauthenticated when unauthenticated).
    acc = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    for route in ("/", f"/dossiers/{D}", "/dossiers/nobody-home.test", f"/dossiers/{D}/evidence", "/contested",
                  "/signup", "/login"):
        r = httpx.get(SVC + route, headers={"Accept": acc}, timeout=5)
        assert r.status_code == 200 and "text/html" in r.headers.get("content-type", ""), (route, r.status_code)
    r = httpx.get(SVC + f"/dossiers/{D}", timeout=5)
    assert r.status_code == 401 and r.json()["error"]["code"] == "unauthenticated"
    r = httpx.get(SVC + f"/dossiers/{D}", headers={"Accept": "application/json"}, timeout=5)
    assert r.status_code == 401


def test_signed_out_screen_goes_to_login_and_back(fresh):
    # RULING R2-2 "A signed-out browser on a protected screen is taken to /login (redirect or in-page), and goes
    # back to the screen it came from after login. It is never shown a raw JSON error."
    t = fresh["ada"]
    create(t, D)
    wait_done(t, D)

    async def go():
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await page.goto(f"/dossiers/{D}")
            await page.get_by_test_id("login-email").wait_for(state="visible")
            body = await page.inner_text("body")
            assert '"error"' not in body and "unauthenticated" not in body.lower().replace(" ", ""), body[:300]
            await page.get_by_test_id("login-email").fill("ada@example.com")
            await page.get_by_test_id("login-password").fill("correct horse")
            await page.get_by_test_id("login-submit").click()
            await wait_text(page.get_by_test_id("dossier-domain"), D)
            assert page.url.rstrip("/").endswith(f"/dossiers/{D}")
            await b.close()
    run(go())


def test_researched_at_people_first_and_exact(fresh):
    # RULING R2-3: dossier-researched-at shows a people-first format and also contains the exact API string,
    # with datetime or data-value carrying that string (on the element or inside it).
    t = fresh["ada"]
    from conftest import reset as _reset
    create(t, D)
    wait_done(t, D)
    api = j(get(t, D))

    async def go():
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await ui_login(page)
            await page.goto(f"/dossiers/{D}")
            el = page.get_by_test_id("dossier-researched-at")
            await el.wait_for(state="visible")
            txt = await el.inner_text()
            assert api["researched_at"] in txt, (txt, api["researched_at"])
            assert re.search(r"[A-Za-z]{3}", txt.replace(api["researched_at"], "")), txt
            attrs = await el.evaluate("""e => [e.getAttribute('datetime'), e.getAttribute('data-value'),
                ...Array.from(e.querySelectorAll('[datetime],[data-value]')).flatMap(x => [x.getAttribute('datetime'), x.getAttribute('data-value')])]""")
            assert api["researched_at"] in attrs, attrs
            await b.close()
    run(go())


def test_post_seal_poll_gap_at_most_2s(fresh):
    # POST-SEAL ADDITION (fault survivor). "While the dossier's state is building, the screen reads the dossier
    # again at least every 2 seconds" — the largest gap between reads while building stays within 2 s
    # (+0.6 s scheduling slack).
    async def go():
        mock_reset(0)
        for prov, m in (("nimble", ["search", "extract", "research"]), ("tavily", ["search", "extract"])):
            mock_fault(prov, m, "delay", seconds=3)
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await ui_login(page)
            await page.goto("/")
            reads = []
            page.on("request", lambda r: reads.append(time.time()) if r.method == "GET" and
                    re.search(r"/dossiers/tarnwick-labs\.test(\?|$)", r.url) else None)
            await page.get_by_test_id("research-domain").fill(D)
            await page.get_by_test_id("research-submit").click()
            st = page.get_by_test_id("dossier-state")
            await wait_text(st, "building", timeout=8)
            t0 = time.time()
            await wait_text(st, "ready", timeout=60)
            t1 = time.time()
            rs = [x for x in reads if t0 - 2.5 <= x <= t1]
            assert len(rs) >= 2, rs
            gaps = [b_ - a_ for a_, b_ in zip(rs, rs[1:])]
            assert max(gaps) <= 2.6, (gaps, t1 - t0)
            await b.close()
    run(go())


def test_post_seal_reload_out_of_order_stale_response(fresh):
    # POST-SEAL ADDITION (fault survivor). "Latest read wins: a delayed earlier read must not overwrite a later
    # one, including when responses arrive out of order." The earlier read is held about 3 s (well inside any
    # client timeout) and answered with the older dossier after the later read has been shown.
    t = fresh["ada"]
    mock_reset(0)
    create(t, D)
    wait_done(t, D)
    old = get(t, D)
    old_body, old_ct = old.content, old.headers["content-type"]
    mock_epoch(1)
    refresh(t, D)
    wait_done(t, D, timeout=40)

    async def go():
        async with pw_api.async_playwright() as p:
            b, ctx = await browser_ctx(p)
            page = await ctx.new_page()
            await ui_login(page)
            await page.goto(f"/dossiers/{D}")
            v = page.get_by_test_id("field-value-ceo")
            await v.wait_for(state="visible")
            assert await v.get_attribute("data-value") == "Jonas Erikson Vale"
            state = {"n": 0}
            pat = re.compile(r".*/dossiers/tarnwick-labs\.test(\?.*)?$")

            async def stale_first(route):
                if route.request.method != "GET":
                    return await route.continue_()
                state["n"] += 1
                if state["n"] == 1:
                    await asyncio.sleep(3)
                    try:
                        await route.fulfill(status=200, body=old_body, headers={"content-type": old_ct})
                    except Exception:
                        pass
                else:
                    await route.continue_()
            await page.route(pat, stale_first)
            await page.get_by_test_id("dossier-reload").click()
            await asyncio.sleep(0.3)
            await page.get_by_test_id("dossier-reload").click()
            await asyncio.sleep(4.5)
            assert state["n"] >= 2, state
            assert await page.get_by_test_id("field-value-ceo").get_attribute("data-value") == "Jonas Erikson Vale"
            await b.close()
    run(go())
