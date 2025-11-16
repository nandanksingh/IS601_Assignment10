# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/13/2025
# Assignment-10: Configuration Module Tests
# File: tests/integration/test_config.py
# ----------------------------------------------------------

import os
import builtins
import pytest
from app.config import Settings, reload_settings, get_environment_mode


# ----------------------------------------------------------
# Test: Environment Flag Logic
# ----------------------------------------------------------
def test_environment_flags(monkeypatch):
    """Validate is_dev, is_prod, is_test helper properties."""

    # Development
    monkeypatch.setenv("ENV", "development")
    s = Settings()
    assert s.is_dev is True
    assert s.is_prod is False
    assert s.is_test is False

    # Production
    monkeypatch.setenv("ENV", "production")
    s = Settings()
    assert s.is_prod is True
    assert s.is_dev is False
    assert s.is_test is False

    # Testing
    monkeypatch.setenv("ENV", "testing")
    s = Settings()
    assert s.is_test is True
    assert s.is_dev is False
    assert s.is_prod is False


# ----------------------------------------------------------
# Test: reload_settings()
# ----------------------------------------------------------
def test_reload_updates_values(monkeypatch):
    """reload_settings() must refresh values from updated environment."""

    monkeypatch.setenv("DATABASE_URL", "sqlite:///./changed.db")
    monkeypatch.setenv("SECRET_KEY", "newkey123")
    monkeypatch.setenv("ENV", "testing")

    # Call reload()
    updated = reload_settings()

    assert updated.DATABASE_URL == "sqlite:///./changed.db"
    assert updated.SECRET_KEY == "newkey123"
    assert updated.is_test is True


# ----------------------------------------------------------
# Test: get_environment_mode()
# ----------------------------------------------------------
@pytest.mark.parametrize(
    "env_value, expected",
    [
        ("development", "development mode"),
        ("production", "production mode"),
        ("testing", "testing mode"),
        ("something_else", "Unknown environment"),
    ],
)
def test_print_environment_modes(env_value, expected, monkeypatch):
    """Validate mode → readable text conversion."""
    assert expected.lower() in get_environment_mode(env_value).lower()
