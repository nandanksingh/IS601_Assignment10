# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/13/2025
# Assignment-10: Secure User Model & Global Test Fixtures
# File: tests/conftest.py
# ----------------------------------------------------------
# Description:
# Centralized pytest fixture module.
#
# Provides:
#   • Fully isolated SQLite test database for all tests
#   • Clean table resets before each test (no stale state)
#   • Safe SQLAlchemy session fixture (auto commit/rollback)
#   • Faker-based unique test users 
#   • Optional E2E FastAPI server launcher
#   • Optional Playwright browser automation support
#
# Goals:
#   • Prevent uniqueness collisions
#   • Avoid PendingRollbackError
#   • Provide consistent database behavior across all tests
#   • Maximize test reliability and coverage
# ----------------------------------------------------------

import os
import time
import subprocess
from contextlib import contextmanager

import pytest
import requests
from faker import Faker
from playwright.sync_api import sync_playwright

# -------------------------------------------------------------------
# Force SQLite test DB BEFORE importing any app modules
# -------------------------------------------------------------------
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["ENV"] = "testing"

from app.database.dbase import Base, engine, SessionLocal  # noqa: E402
from app.models.user_model import User                    # noqa: E402
from app.auth.security import hash_password               # noqa: E402


# ----------------------------------------------------------
# Faker Setup — seeded for deterministic unique test values
# ----------------------------------------------------------
fake = Faker()
Faker.seed(12345)


# ----------------------------------------------------------
# GLOBAL DATABASE SETUP (run ONCE per test session)
# ----------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Create a clean database schema at the start of the test session.
    Drops everything again at the end of the session.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ----------------------------------------------------------
# PER-TEST DATABASE RESET (full table reset)
# ----------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_db():
    """
    Ensures every test runs with a completely fresh database state.
    Avoids uniqueness conflicts and leftover test data.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ----------------------------------------------------------
# SAFE SQLALCHEMY SESSION FIXTURE
# ----------------------------------------------------------
@pytest.fixture
def db_session():
    """
    Provides a function-scoped SQLAlchemy session.
    Automatically commits on success or rolls back on errors.
    Fully closes session after use.
    """
    session = SessionLocal()
    try:
        yield session

        if session.is_active:
            try:
                session.commit()
            except Exception:
                session.rollback()

    finally:
        session.close()


# ----------------------------------------------------------
# OPTIONAL CONTEXT MANAGER FOR ADVANCED TESTS
# ----------------------------------------------------------
@contextmanager
def managed_db_session():
    """
    Manual session manager used only by specialized tests.
    Mirrors db_session behavior but works with `with` blocks.
    """
    session = SessionLocal()
    try:
        yield session
        if session.is_active:
            try:
                session.commit()
            except Exception:
                session.rollback()
    finally:
        session.close()


# ----------------------------------------------------------
# FIXTURES — Fake User Data & Seed Users
# ----------------------------------------------------------
@pytest.fixture
def fake_user_data():
    """Provide a unique, valid user record for tests."""
    return {
        "username": fake.unique.user_name(),
        "email": fake.unique.email(),
        "password_hash": hash_password("TestPass123"),
    }


@pytest.fixture
def test_user(db_session, fake_user_data):
    """Insert and return a single persisted User instance."""
    user = User(**fake_user_data)
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)
    return user


@pytest.fixture
def seed_users(db_session):
    """Insert 5 unique users and return them as a list."""
    users = []
    for _ in range(5):
        data = {
            "username": fake.unique.user_name(),
            "email": fake.unique.email(),
            "password_hash": hash_password("TempPass123"),
        }
        user = User(**data)
        db_session.add(user)
        users.append(user)
    return users


# ----------------------------------------------------------
# OPTIONAL FASTAPI SERVER (E2E-level integration tests)
# ----------------------------------------------------------
@pytest.fixture(scope="session")
def fastapi_server():
    """
    Launch the FastAPI app in a subprocess.
    Used by E2E tests that perform real HTTP calls.

    Automatically waits for /health to return 200 OK.
    """
    server = subprocess.Popen(["python", "main.py"])
    health_url = "http://127.0.0.1:8000/health"

    # Wait up to 30 seconds for server to start
    for _ in range(30):
        try:
            r = requests.get(health_url)
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(1)
    else:
        server.terminate()
        raise RuntimeError("FastAPI server did not start in time.")

    yield server

    # Teardown
    server.terminate()
    try:
        server.wait(timeout=5)
    except Exception:
        server.kill()


# ----------------------------------------------------------
# PLAYWRIGHT FIXTURES (for browser-based E2E tests)
# ----------------------------------------------------------
@pytest.fixture(scope="session")
def playwright_instance():
    """
    Provides a Playwright instance for browser automation.
    Returns None if Playwright is unavailable.
    """
    try:
        with sync_playwright() as playwright:
            yield playwright
    except Exception:
        yield None


@pytest.fixture(scope="session")
def browser(playwright_instance):
    """
    Launch a Chromium browser (headless).
    Skips browser tests automatically if unavailable.
    """
    if playwright_instance is None:
        pytest.skip("Playwright is not available on this system.")

    browser = playwright_instance.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page(browser):
    """
    Provide a fresh browser page for each E2E test.
    Ensures isolation so tests do not leak cookies or state.
    """
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
