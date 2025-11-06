# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/05/2025
# Assignment-10: Secure User Model (Pydantic Validation + Database Testing)
# File: tests/conftest.py
# ----------------------------------------------------------
# Description:
# Provides shared pytest fixtures for Assignment-10 covering:
#   - Database session lifecycle management (SQLAlchemy)
#   - Fake user data creation using Faker
#   - FastAPI server startup for E2E testing
#   - Playwright browser setup for UI automation
# ----------------------------------------------------------

import subprocess
import time
import pytest
import requests
from faker import Faker
from contextlib import contextmanager
from playwright.sync_api import sync_playwright
from sqlalchemy.exc import SQLAlchemyError
from app.database import Base, engine, SessionLocal
from app.models.user import User

# Initialize Faker
fake = Faker()
Faker.seed(12345)


# ----------------------------------------------------------
# Database Fixtures
# ----------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Initialize clean database schema for the test session."""
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
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()


@pytest.fixture
def fake_user_data():
    """Return fake user data for testing."""
    return {
        "username": fake.unique.user_name(),
        "email": fake.unique.email(),
        "password_hash": "TestPass123",
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
            "password_hash": "TempPass123",
        }
        user = User(**data)
        users.append(user)
        db_session.add(user)
    db_session.commit()
    return users


# ----------------------------------------------------------
# FastAPI Server Fixture (for E2E tests)
# ----------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def fastapi_server():
    """Start FastAPI server before E2E tests and stop it after tests."""
    print("\nStarting FastAPI server for E2E tests...")
    server = subprocess.Popen(["python", "main.py"])
    url = "http://127.0.0.1:8000/health"
    started = False

    for _ in range(30):
        try:
            if requests.get(url).status_code == 200:
                print("FastAPI server is running.")
                started = True
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)

    if not started:
        server.terminate()
        raise RuntimeError("FastAPI server did not start in time.")

    yield  # Run tests

    print("Stopping FastAPI server...")
    server.terminate()
    try:
        server.wait(timeout=5)
        print("FastAPI server stopped successfully.")
    except Exception:
        print("Server did not terminate cleanly; killing process.")
        server.kill()


# ----------------------------------------------------------
# Playwright Fixtures
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
