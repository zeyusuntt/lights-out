"""Browser flows against a running service and mock web (DOSSIER_URL, MOCK_URL)."""

import time

import httpx

from conftest import BASE, sign_in

from playwright.sync_api import expect


def no_horizontal_scroll(page):
    assert page.evaluate("document.documentElement.scrollWidth") <= page.viewport_size["width"]


def test_signed_out_screen_goes_to_login_and_back(page):
    page.goto(f"{BASE}/contested")
    page.wait_for_url("**/login?next=*")
    page.fill("[data-testid=login-email]", "ada@example.com")
    page.fill("[data-testid=login-password]", "wrong horse")
    page.click("[data-testid=login-submit]")
    expect(page.get_by_test_id("auth-error")).to_be_visible()
    page.fill("[data-testid=login-password]", "correct horse")
    page.click("[data-testid=login-submit]")
    page.wait_for_url("**/contested")
    expect(page.get_by_test_id("current-user")).to_contain_text("Ada")
    expect(page.get_by_test_id("empty-contested")).to_be_visible()


def test_signup_then_logout(page):
    page.goto(f"{BASE}/signup")
    page.fill("[data-testid=signup-email]", "zoe@example.com")
    page.fill("[data-testid=signup-password]", "12345678")
    page.fill("[data-testid=signup-display-name]", "Zoë")
    page.click("[data-testid=signup-submit]")
    expect(page.get_by_test_id("current-user")).to_contain_text("Zoë")
    expect(page.get_by_test_id("empty-dossiers")).to_be_visible()
    page.click("[data-testid=logout-button]")
    page.wait_for_url("**/login")
    expect(page.get_by_test_id("current-user")).to_have_count(0)


def test_research_invalid_then_valid_and_dossier_follows_build(page, mock):
    sign_in(page)
    page.fill("[data-testid=research-domain]", "https://nope")
    page.click("[data-testid=research-submit]")
    expect(page.get_by_test_id("research-error")).to_be_visible()
    page.fill("[data-testid=research-domain]", " WWW.Corvid-Security.test ")
    page.click("[data-testid=research-submit]")
    page.wait_for_url("**/dossiers/corvid-security.test")
    expect(page.get_by_test_id("dossier-domain")).to_have_text("corvid-security.test")
    expect(page.get_by_test_id("dossier-state")).to_have_text("ready", timeout=15000)
    expect(page.locator("[data-testid^=field-]").filter(has=page.locator("xpath=self::*[@data-status]"))).to_have_count(6)
    expect(page.get_by_test_id("field-ceo")).to_have_attribute("data-status", "known")
    expect(page.get_by_test_id("field-value-ceo")).to_have_attribute("data-value", "Marcus Dalton")
    expect(page.get_by_test_id("citation-ceo-1")).to_have_attribute("data-provider", "nimble")
    expect(page.get_by_test_id("field-contested-legal_name")).to_be_visible()
    expect(page.get_by_test_id("dossier-researched-at")).to_contain_text("2026-03-01T09:00:00+00:00")
    no_horizontal_scroll(page)
    page.click("[data-testid=dossier-evidence-link]")
    expect(page.get_by_test_id("candidate-legal_name-1")).to_have_attribute("data-selected", "true")
    expect(page.get_by_test_id("candidate-legal_name-2")).to_have_attribute("data-kind", "aggregator")
    no_horizontal_scroll(page)
    page.goto(f"{BASE}/contested")
    expect(page.get_by_test_id("contested-item-corvid-security.test-legal_name")).to_contain_text("Corvid Security Holdings Inc.")
    page.goto(f"{BASE}/")
    expect(page.get_by_test_id("dossier-item-corvid-security.test")).to_have_attribute("data-state", "ready")
    page.fill("[data-testid=dossier-search]", "zzz")
    expect(page.get_by_test_id("empty-dossiers")).to_be_visible()


def test_lost_research_response_is_uncertain_and_retry_builds_once(page, mock):
    sign_in(page)
    lost = {"done": False}

    def lose_after_commit(route):
        if route.request.method == "POST" and not lost["done"]:
            route.fetch()
            lost["done"] = True
            route.abort()
        else:
            route.continue_()

    page.route("**/dossiers", lose_after_commit)
    page.fill("[data-testid=research-domain]", "quillmate.test")
    page.click("[data-testid=research-submit]")
    expect(page.get_by_test_id("research-uncertain")).not_to_be_empty()
    expect(page.get_by_test_id("research-error")).to_have_count(0)
    page.click("[data-testid=research-submit]")
    page.wait_for_url("**/dossiers/quillmate.test")
    expect(page.get_by_test_id("dossier-state")).to_have_text("ready", timeout=15000)
    assert sum(c["method"] == "research" for c in mock.calls()) == 1


def test_lost_refresh_response_is_uncertain_and_retry_refreshes_once(page, mock):
    sign_in(page)
    page.fill("[data-testid=research-domain]", "corvid-security.test")
    page.click("[data-testid=research-submit]")
    expect(page.get_by_test_id("dossier-state")).to_have_text("ready", timeout=15000)
    lost = {"done": False}

    def lose_after_commit(route):
        if not lost["done"]:
            route.fetch()
            lost["done"] = True
            route.abort()
        else:
            route.continue_()

    page.route("**/refresh", lose_after_commit)
    page.click("[data-testid=dossier-refresh]")
    expect(page.get_by_test_id("refresh-uncertain")).not_to_be_empty()
    page.click("[data-testid=dossier-refresh]")
    expect(page.get_by_test_id("refresh-uncertain")).to_have_count(0)
    expect(page.get_by_test_id("dossier-state")).to_have_text("ready", timeout=15000)
    assert sum(c["method"] == "research" for c in mock.calls()) == 2


def test_latest_read_wins_over_a_delayed_earlier_read(page, mock, api, ada):
    sign_in(page)
    page.fill("[data-testid=research-domain]", "corvid-security.test")
    page.click("[data-testid=research-submit]")
    expect(page.get_by_test_id("dossier-state")).to_have_text("ready", timeout=15000)
    held = {"count": 0}

    def hold_first(route):
        if route.request.method == "GET" and held["count"] == 0:
            held["count"] += 1
            stale = route.fetch()
            time.sleep(1.5)
            route.fulfill(response=stale)
        else:
            route.continue_()

    page.route("**/dossiers/corvid-security.test", hold_first)
    page.click("[data-testid=dossier-reload]")
    httpx.post(f"{BASE}/_test/clock", json={"now": "2026-03-02T00:00:00+00:00"})
    api.post("/dossiers/corvid-security.test/refresh", headers={**ada, "Idempotency-Key": "other-client"})
    time.sleep(0.2)
    page.click("[data-testid=dossier-reload]")
    expect(page.get_by_test_id("dossier-researched-at")).to_contain_text("2026-03-02", timeout=15000)
    time.sleep(2)
    expect(page.get_by_test_id("dossier-researched-at")).to_contain_text("2026-03-02")


def test_unknown_dossier_and_html_negotiation(page):
    sign_in(page)
    page.goto(f"{BASE}/dossiers/WWW.Absent.test")
    expect(page.get_by_test_id("dossier-not-found")).to_be_visible()
    expect(page.get_by_test_id("dossier-domain")).to_have_text("absent.test")
    page.goto(f"{BASE}/dossiers/absent.test/evidence")
    expect(page.get_by_test_id("dossier-not-found")).to_be_visible()
    assert httpx.get(f"{BASE}/dossiers/absent.test").status_code == 401
    html = httpx.get(f"{BASE}/dossiers/absent.test", headers={"Accept": "text/html"})
    assert html.status_code == 200 and html.headers["content-type"].startswith("text/html")


def test_people_first_auth_error_and_hidden_nav_when_signed_out(page):
    page.goto(f"{BASE}/login")
    expect(page.locator("nav.nav")).to_be_hidden()
    page.fill("[data-testid=login-email]", "ada@example.com")
    page.fill("[data-testid=login-password]", "wrong horse")
    page.click("[data-testid=login-submit]")
    expect(page.get_by_test_id("auth-error")).to_have_text("Email or password is incorrect.")


def test_first_build_fields_read_as_in_progress(page, mock):
    mock.fault(["research"], "delay", seconds=3)
    sign_in(page)
    page.fill("[data-testid=research-domain]", "corvid-security.test")
    page.click("[data-testid=research-submit]")
    expect(page.get_by_test_id("dossier-state")).to_have_text("building")
    expect(page.get_by_test_id("field-ceo")).to_contain_text("Research in progress")
    expect(page.get_by_test_id("field-ceo")).to_have_attribute("data-status", "unknown")
    expect(page.get_by_test_id("dossier-state")).to_have_text("ready", timeout=20000)
