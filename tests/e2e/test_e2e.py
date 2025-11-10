# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment-10: Secure User Model (Pydantic Validation + Docker E2E)
# File: tests/e2e/test_e2e.py
# ----------------------------------------------------------
# Description:
# End-to-End (E2E) test suite for the FastAPI Calculator app.
# Uses Playwright to simulate user actions and verify that
# frontend, backend API, and database work correctly together.
# ----------------------------------------------------------

import os
import time
import pytest
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ----------------------------------------------------------
# Base URL (Local or Docker)
# ----------------------------------------------------------
BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000")


# ----------------------------------------------------------
# Helper: Wait until FastAPI server is ready
# ----------------------------------------------------------
def wait_for_app_ready(url=f"{BASE_URL}/health", timeout=30):
    """Wait up to 30s for FastAPI /health to return 200."""
    for _ in range(timeout):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(" FastAPI server is ready.")
                return
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    pytest.fail(f"FastAPI not responding at {url}")


# ----------------------------------------------------------
# Fixtures
# ----------------------------------------------------------
@pytest.fixture(scope="module")
def browser():
    """Launch headless Chromium once per test module."""
    wait_for_app_ready()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    """Provide a new clean page per test."""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


# ----------------------------------------------------------
# Homepage / Health Tests
# ----------------------------------------------------------
@pytest.mark.e2e
def test_homepage_loads(page):
    """Ensure homepage and FastAPI root route render."""
    page.goto(BASE_URL, wait_until="domcontentloaded")
    title_text = page.text_content("h1") or ""
    assert "FastAPI" in title_text or "Calculator" in title_text


@pytest.mark.e2e
def test_health_endpoint_direct():
    """Check /health route returns JSON healthy."""
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200
    body = res.json()
    assert "status" in body
    assert body["status"].lower() in ["ok", "healthy", "running"]


# ----------------------------------------------------------
# Calculator Functionality
# ----------------------------------------------------------
@pytest.mark.e2e
@pytest.mark.parametrize(
    "op, a, b, expected",
    [
        ("Add", "5", "7", "12"),
        ("Subtract", "15", "4", "11"),
        ("Multiply", "6", "3", "18"),
        ("Divide", "20", "5", "4"),
    ],
)
def test_calculator_operations(page, op, a, b, expected):
    """Verify arithmetic operations work end-to-end."""
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.fill("#a", a)
    page.fill("#b", b)
    page.click(f"text={op}")
    try:
        page.wait_for_selector("#result", timeout=7000)
        result_text = page.text_content("#result") or ""
        assert expected in result_text
    except PlaywrightTimeoutError:
        pytest.fail(f"Timeout waiting for result in {op} operation")


# ----------------------------------------------------------
# Negative / Error Handling
# ----------------------------------------------------------
@pytest.mark.e2e
def test_divide_by_zero(page):
    """Ensure division by zero returns proper error message."""
    page.goto(BASE_URL)
    page.fill("#a", "10")
    page.fill("#b", "0")
    page.click("text=Divide")
    try:
        page.wait_for_selector("#result", timeout=5000)
        msg = page.text_content("#result") or ""
        assert "Cannot divide by zero" in msg or "error" in msg.lower()
    except PlaywrightTimeoutError:
        pytest.fail("Result element not found after division by zero.")


@pytest.mark.e2e
def test_invalid_input(page):
    """Ensure non-numeric input triggers an error message."""
    page.goto(BASE_URL)
    page.fill("#a", "abc")
    page.fill("#b", "3")
    page.click("text=Add")
    page.wait_for_selector("#result", timeout=5000)
    msg = page.text_content("#result") or ""
    assert "error" in msg.lower()


@pytest.mark.e2e
def test_missing_input(page):
    """Ensure empty inputs display validation error."""
    page.goto(BASE_URL)
    page.fill("#a", "")
    page.fill("#b", "")
    page.click("text=Add")
    page.wait_for_selector("#result", timeout=5000)
    msg = page.text_content("#result") or ""
    assert "error" in msg.lower() or "invalid" in msg.lower()
