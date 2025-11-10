# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment-10: Secure User Model (Pydantic Validation + Database Testing)
# File: tests/conftest.py
# ----------------------------------------------------------
# Description:
# Provides shared pytest fixtures for Assignment-10 covering:
#   - Database session lifecycle (SQLAlchemy)
#   - Fake user data creation (Faker)
#   - Optional FastAPI server for E2E tests
#   - Optional Playwright browser automation
# ----------------------------------------------------------

import subprocess
import time
import pytest
import requests
from faker import Faker
from contextlib import contextmanager
from playwright.sync_api import sync_playwright
from sqlalchemy.exc import SQLAlchemyError

from app.database.dbase import Base, engine, SessionLocal
from app.models.user_model import User
from app.auth.security import hash_password

# ----------------------------------------------------------
# Faker Initialization
# ----------------------------------------------------------
fake = Faker()
Faker.seed(12345)


# ----------------------------------------------------------
# Database Fixtures
# ----------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Initialize a clean database schema for the test session."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide an isolated SQLAlchemy session for each test."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@contextmanager
def managed_db_session():
    """Context manager for manual session handling with rollback."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture
def fake_user_data():
    """Return fake user data with hashed password for testing."""
    profile = fake.simple_profile()
    return {
        "username": profile["username"],
        "email": profile["mail"],
        "password_hash": hash_password("TestPass123"),
    }


@pytest.fixture
def test_user(db_session, fake_user_data):
    """Create and return a single test user."""
    user = User(**fake_user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def seed_users(db_session):
    """Create multiple users for integration tests."""
    users = []
    for _ in range(5):
        data = {
            "username": fake.unique.user_name(),
            "email": fake.unique.email(),
            "password_hash": hash_password("TempPass123"),
        }
        user = User(**data)
        users.append(user)
        db_session.add(user)
    db_session.commit()
    return users


# ----------------------------------------------------------
# Optional FastAPI Server Fixture (for E2E tests)
# ----------------------------------------------------------
@pytest.fixture(scope="session")
def fastapi_server():
    """Start FastAPI server before E2E tests (manual use only)."""
    print("\n[SETUP] Starting FastAPI server for E2E tests...")
    server = subprocess.Popen(["python", "main.py"])
    url = "http://127.0.0.1:8000/health"

    for _ in range(30):
        try:
            if requests.get(url).status_code == 200:
                print("[READY] FastAPI server is running.")
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    else:
        server.terminate()
        raise RuntimeError("FastAPI server did not start in time.")

    yield
    print("[TEARDOWN] Stopping FastAPI server...")
    server.terminate()
    try:
        server.wait(timeout=5)
        print("[OK] Server stopped successfully.")
    except Exception:
        server.kill()
        print("[FORCE] Server killed.")


# ----------------------------------------------------------
# Optional Playwright Fixtures
# ----------------------------------------------------------
@pytest.fixture(scope="session")
def playwright_instance():
    """Manage Playwright instance lifecycle."""
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance):
    """Launch a headless Chromium browser for test session."""
    browser = playwright_instance.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page(browser):
    """Provide a clean browser page for each test."""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
