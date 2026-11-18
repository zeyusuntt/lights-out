import importlib.util
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

_spec = importlib.util.spec_from_file_location(
    "api_conftest", Path(__file__).resolve().parents[1] / "api" / "conftest.py")
shared = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(shared)
api, ada, mock, BASE = shared.api, shared.ada, shared.mock, shared.BASE


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def page(browser, api):
    context = browser.new_context(viewport={"width": 375, "height": 800})
    pg = context.new_page()
    pg.set_default_timeout(15000)
    yield pg
    context.close()


def sign_in(page, email="ada@example.com"):
    page.goto(f"{BASE}/login")
    page.fill("[data-testid=login-email]", email)
    page.fill("[data-testid=login-password]", "correct horse")
    page.click("[data-testid=login-submit]")
    page.wait_for_selector("[data-testid=current-user]")
