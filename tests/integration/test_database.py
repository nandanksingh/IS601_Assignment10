# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/05/2025
# Assignment-10: Secure User Model (Pydantic Validation + Database Testing)
# File: tests/integration/test_database.py
# ----------------------------------------------------------
# Description:
# Integration-level tests for the database layer.
# These tests validate SQLAlchemy engine creation, session
# lifecycle, and table initialization using mock settings.
# The goal is to ensure that database connectivity and ORM
# setup work reliably across local and Docker environments.
# ----------------------------------------------------------

import pytest
import sys
import importlib
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

DATABASE_MODULE = "app.database"


# ----------------------------------------------------------
# Fixture: Mock settings.DATABASE_URL before import
# ----------------------------------------------------------
@pytest.fixture
def mock_settings(monkeypatch):
    """
    Mocks DATABASE_URL from app.config.settings before app.database loads.
    Prevents accidental connection to a real database during tests.
    """
    mock_url = "postgresql://user:password@localhost:5432/test_db"
    mock_settings = MagicMock()
    mock_settings.DATABASE_URL = mock_url

    # Ensure fresh import of app.database
    if DATABASE_MODULE in sys.modules:
        del sys.modules[DATABASE_MODULE]

    monkeypatch.setattr(f"{DATABASE_MODULE}.settings", mock_settings)
    return mock_settings


# ----------------------------------------------------------
# Helper: Reload database module
# ----------------------------------------------------------
def reload_database_module():
    """Re-imports app.database to apply patched environment."""
    if DATABASE_MODULE in sys.modules:
        del sys.modules[DATABASE_MODULE]
    return importlib.import_module(DATABASE_MODULE)


# ----------------------------------------------------------
# Test: Engine Creation Success
# ----------------------------------------------------------
def test_get_engine_success(mock_settings):
    """Ensure that get_engine() creates a valid SQLAlchemy Engine."""
    db = reload_database_module()
    engine = db.get_engine()
    assert isinstance(engine, Engine)
    assert str(engine.url).startswith("postgresql://"), "Engine URL should match mocked DATABASE_URL."


# ----------------------------------------------------------
# Test: Engine Creation Failure
# ----------------------------------------------------------
def test_get_engine_failure(mock_settings):
    """Ensure get_engine() raises SQLAlchemyError on invalid engine creation."""
    db = reload_database_module()
    with patch("app.database.create_engine", side_effect=SQLAlchemyError("Engine creation failed")):
        with pytest.raises(SQLAlchemyError, match="Engine creation failed"):
            db.get_engine()


# ----------------------------------------------------------
# Test: Session Factory and Lifecycle
# ----------------------------------------------------------
def test_session_factory(mock_settings):
    """Ensure SessionLocal provides working session objects."""
    db = reload_database_module()
    session = db.SessionLocal()
    assert isinstance(session, Session)
    session.close()


# ----------------------------------------------------------
# Test: Base Declaration Type
# ----------------------------------------------------------
def test_base_declaration(mock_settings):
    """Ensure Base is a valid SQLAlchemy declarative base."""
    db = reload_database_module()
    Base = db.Base
    new_base = db.declarative_base()
    assert isinstance(Base, new_base.__class__)


# ----------------------------------------------------------
# Test: init_db() and drop_db() invocation
# ----------------------------------------------------------
def test_init_and_drop_db(monkeypatch, mock_settings):
    """
    Validate that init_db() and drop_db() trigger table creation
    and deletion via SQLAlchemy metadata methods.
    """
    db = reload_database_module()

    with patch("app.models.user.Base.metadata.create_all") as mock_create, \
         patch("app.models.user.Base.metadata.drop_all") as mock_drop:

        db.init_db()
        mock_create.assert_called_once()

        db.drop_db()
        mock_drop.assert_called_once()
