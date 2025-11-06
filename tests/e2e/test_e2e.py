# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/05/2025
# Assignment-10: Secure User Model (Pydantic Validation + Database Testing)
# File: tests/e2e/test_e2e.py
# ----------------------------------------------------------
# Description:
# End-to-End (E2E) test suite for the FastAPI application.
# Uses Playwright to simulate user actions and verify that
# the web interface, backend API, and PostgreSQL database
# operate correctly together in the Docker environment.
#
# Covers:
#   • Homepage and health route accessibility
#   • Calculator arithmetic functionality
#   • Error handling for invalid inputs
#   • Backend stability while DB and API layers run together
# ----------------------------------------------------------

import pytest
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

BASE_URL = "http://localhost:8000"


# ----------------------------------------------------------
# Fixture: Launch Browser Once per Module
# ----------------------------------------------------------
@pytest.fixture(scope="module")
def browser():
    """Launch a headless Chromium instance for all E2E tests."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    """Provide a fresh browser page for each test."""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


# ----------------------------------------------------------
# Test: Application Root Endpoint
# ----------------------------------------------------------
@pytest.mark.e2e
def test_homepage_loads(page):
    """Verify homepage renders and FastAPI app responds correctly."""
    page.goto(BASE_URL)
    title_text = page.text_content("h1")
    assert title_text and "FastAPI" in title_text, "Homepage failed to load or incorrect title."


# ----------------------------------------------------------
# Calculator Functional Tests
# ----------------------------------------------------------
@pytest.mark.e2e
def test_addition(page):
    """Verify adding two numbers returns correct result."""
    page.goto(BASE_URL)
    page.fill("#a", "5")
    page.fill("#b", "7")
    page.click("text=Add")
    page.wait_for_selector("#result")
    assert "Result: 12" in page.text_content("#result")


@pytest.mark.e2e
def test_subtraction(page):
    """Verify subtraction displays correct result."""
    page.goto(BASE_URL)
    page.fill("#a", "15")
    page.fill("#b", "4")
    page.click("text=Subtract")
    page.wait_for_selector("#result")
    assert "Result: 11" in page.text_content("#result")


@pytest.mark.e2e
def test_multiplication(page):
    """Verify multiplication displays correct result."""
    page.goto(BASE_URL)
    page.fill("#a", "6")
    page.fill("#b", "3")
    page.click("text=Multiply")
    page.wait_for_selector("#result")
    assert "Result: 18" in page.text_content("#result")


@pytest.mark.e2e
def test_division(page):
    """Verify division displays correct result."""
    page.goto(BASE_URL)
    page.fill("#a", "20")
    page.fill("#b", "5")
    page.click("text=Divide")
    page.wait_for_selector("#result")
    assert "Result: 4" in page.text_content("#result")


# ----------------------------------------------------------
# Negative & Error Case Tests
# ----------------------------------------------------------
@pytest.mark.e2e
def test_divide_by_zero(page):
    """Verify dividing by zero displays an error message."""
    page.goto(BASE_URL)
    page.fill("#a", "10")
    page.fill("#b", "0")
    page.click("text=Divide")
    try:
        page.wait_for_selector("#result", timeout=3000)
    except PlaywrightTimeoutError:
        pytest.fail("Result element not found after division by zero.")
    assert "Cannot divide by zero" in page.text_content("#result")


@pytest.mark.e2e
def test_invalid_input(page):
    """Verify non-numeric input triggers an error message."""
    page.goto(BASE_URL)
    page.fill("#a", "abc")
    page.fill("#b", "3")
    page.click("text=Add")
    page.wait_for_selector("#result")
    assert "Error" in page.text_content("#result")


@pytest.mark.e2e
def test_missing_input(page):
    """Verify empty inputs trigger a validation error message."""
    page.goto(BASE_URL)
    page.fill("#a", "")
    page.fill("#b", "")
    page.click("text=Add")
    page.wait_for_selector("#result")
    assert "Error" in page.text_content("#result")



