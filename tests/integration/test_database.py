# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/09/2025
# Assignment-10: Secure User Model (Integration Database Tests)
# File: tests/integration/test_database.py
# ----------------------------------------------------------
# Description:
# Comprehensive integration tests for database configuration.
# Validates PostgreSQL + SQLite fallback logic, engine creation,
# environment reloads, and coverage execution paths.
# Ensures the database layer remains robust under CI/CD and
# local development environments.
# ----------------------------------------------------------

import os
import sys
import pytest
import importlib
import socket
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

DATABASE_MODULE = "app.database.dbase"
CONFIG_MODULE = "app.config"

# ----------------------------------------------------------
# Fixture: Mock DATABASE_URL
# ----------------------------------------------------------
@pytest.fixture
def mock_settings(monkeypatch):
    """Mock DATABASE_URL and reload database modules."""
    mock_url = "postgresql://user:password@localhost:5432/test_db"
    monkeypatch.setenv("DATABASE_URL", mock_url)
    for mod in [CONFIG_MODULE, DATABASE_MODULE]:
        if mod in sys.modules:
            del sys.modules[mod]
    import app.config as config
    import app.database.dbase as dbase
    importlib.reload(config)
    importlib.reload(dbase)
    return mock_url

# ----------------------------------------------------------
# Helper: Reload database module
# ----------------------------------------------------------
def reload_database_module():
    """Reload app.database.dbase dynamically for isolation."""
    if DATABASE_MODULE in sys.modules:
        del sys.modules[DATABASE_MODULE]
    return importlib.import_module(DATABASE_MODULE)

# ----------------------------------------------------------
# Core Engine Tests
# ----------------------------------------------------------
def test_get_engine_success(mock_settings):
    db = reload_database_module()
    engine = db.get_engine()
    assert isinstance(engine, Engine)
    assert str(engine.url).startswith("postgresql://")

def test_get_engine_failure_with_sqlite(monkeypatch):
    """Force simulated engine creation failure to ensure full coverage."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy::test")

    for mod in ["app.database.__init__", "app.database.dbase"]:
        if mod in sys.modules:
            del sys.modules[mod]

    import app.database.dbase as dbase

    with patch("app.database.dbase.create_engine", side_effect=SQLAlchemyError("Simulated failure")):
        with pytest.raises(SQLAlchemyError, match="Engine creation failed"):
            dbase.get_engine()

@pytest.mark.skip(reason="Using PostgreSQL for integration tests per assignment specification")
def test_get_engine_sqlite_connect_args(monkeypatch):
    """(Skipped) SQLite engine check — not required for PostgreSQL CI/CD."""
    pass


# ----------------------------------------------------------
# Session and Metadata Tests
# ----------------------------------------------------------
def test_session_factory(mock_settings):
    db = reload_database_module()
    session = db.SessionLocal()
    assert isinstance(session, Session)
    session.close()

def test_base_declaration(mock_settings):
    db = reload_database_module()
    Base = db.Base
    new_base = db.declarative_base()
    assert isinstance(Base, new_base.__class__)

def test_init_and_drop_db(monkeypatch, mock_settings):
    db = reload_database_module()
    with patch("app.models.user_model.Base.metadata.create_all") as mock_create, \
         patch("app.models.user_model.Base.metadata.drop_all") as mock_drop:
        db.init_db()
        mock_create.assert_called_once()
        db.drop_db()
        mock_drop.assert_called_once()

# ----------------------------------------------------------
# Config Reload Tests
# ----------------------------------------------------------
from app.config import settings

def test_env_flags(monkeypatch):
    """Verify that environment flags map correctly to ENV values."""
    monkeypatch.setenv("ENV", "development")
    settings.reload()
    assert settings.is_dev and not settings.is_prod

    monkeypatch.setenv("ENV", "production")
    settings.reload()
    assert settings.is_prod and not settings.is_dev

    monkeypatch.setenv("ENV", "testing")
    settings.reload()
    assert settings.is_test and not settings.is_dev

def test_reload_updates_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/test_db")
    settings.reload()
    assert settings.DATABASE_URL == "postgresql://user:pass@localhost:5432/test_db"

# ----------------------------------------------------------
# Fallback Logic Tests
# ----------------------------------------------------------
import app.database as db_init

def test_is_test_env_detected(monkeypatch):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy::test")
    importlib.reload(db_init)
    assert db_init.IS_TEST_ENV is True

def test_postgres_unavailable_true():
    with patch("socket.create_connection", side_effect=OSError("Connection refused")):
        assert db_init._postgres_unavailable() is True

def test_postgres_unavailable_false():
    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None
    with patch("socket.create_connection", return_value=mock_conn):
        assert db_init._postgres_unavailable() is False

def test_ensure_sqlite_fallback(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/test_db")
    with patch("app.database._postgres_unavailable", return_value=True):
        db_init._ensure_sqlite_fallback()
        assert os.getenv("DATABASE_URL") == "sqlite:///./test.db"

def test_trigger_fallback_executes(monkeypatch):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy::test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/test_db")
    with patch("app.database._postgres_unavailable", return_value=True):
        db_init._trigger_fallback_if_test_env()
        assert os.getenv("DATABASE_URL") == "sqlite:///./test.db"

def test_trigger_fallback_error(monkeypatch):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy::test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/test_db")
    with patch("app.database._ensure_sqlite_fallback", side_effect=Exception("Simulated failure")):
        with pytest.raises(RuntimeError, match="Fallback logic failed"):
            db_init._trigger_fallback_if_test_env()

# ----------------------------------------------------------
# Coverage Trigger Tests
# ----------------------------------------------------------
def test_run_session_lifecycle_for_coverage(monkeypatch):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy::test")
    import app.database.dbase as dbase
    dbase._run_session_lifecycle_for_coverage()

def test_run_session_lifecycle_error(monkeypatch):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy::test")
    import app.database.dbase as dbase
    with patch("app.database.dbase.get_session", side_effect=Exception("Simulated session error")):
        with pytest.raises(RuntimeError, match="Session lifecycle failed"):
            dbase._run_session_lifecycle_for_coverage()
