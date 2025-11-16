# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/17/2025
# Assignment-10: Secure User Model (Database Layer Testing)
# File: tests/integration/test_dbase.py
# ----------------------------------------------------------
# Description:
# Full coverage test suite for app/database/dbase.py.
#
# Covers ALL branches:
#   • get_engine() error paths (SQLAlchemyError + unexpected exception)
#   • get_session() failure branch
#   • init_db() failure branch
#   • drop_db() failure branch
#   • _postgres_unavailable() both True & False paths
#   • _trigger_fallback_if_test_env() failure branch
#   • _run_session_lifecycle_for_coverage() commit & rollback flows
#
# Goal:
#   Achieve 100% line coverage for dbase.py.
# ----------------------------------------------------------

import os
import pytest
from unittest.mock import patch

import app.database.dbase as dbase
from sqlalchemy.exc import SQLAlchemyError


# ----------------------------------------------------------
# 1. get_engine() — SQLAlchemyError branch (lines 62–64)
# ----------------------------------------------------------
def test_get_engine_sqlalchemy_error(monkeypatch):
    """Force create_engine to raise SQLAlchemyError → triggers expected error path."""

    def raise_sqlalchemy(*args, **kwargs):
        raise SQLAlchemyError("engine-failure")

    monkeypatch.setattr(dbase, "create_engine", raise_sqlalchemy)
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "1")

    with pytest.raises(SQLAlchemyError):
        dbase.get_engine()


# ----------------------------------------------------------
# 2. get_engine() — unexpected generic Exception (lines 82–84)
# ----------------------------------------------------------
def test_get_engine_unexpected_error(monkeypatch):
    """Force create_engine to raise ValueError → wrapped into SQLAlchemyError."""

    def raise_unexpected(*args, **kwargs):
        raise ValueError("boom")

    monkeypatch.setattr(dbase, "create_engine", raise_unexpected)
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "1")

    with pytest.raises(SQLAlchemyError) as exc:
        dbase.get_engine()

    assert "unexpected failure" in str(exc.value)


# ----------------------------------------------------------
# 3. get_session() — exception branch (lines 94–95)
# ----------------------------------------------------------
def test_get_session_failure(monkeypatch):
    """Force SessionLocal to throw an exception → hit 'Session creation failed' path."""

    def bad_session():
        raise RuntimeError("session broken")

    monkeypatch.setattr(dbase, "SessionLocal", bad_session)

    with pytest.raises(RuntimeError) as exc:
        dbase.get_session()

    assert "Session creation failed" in str(exc.value)


# ----------------------------------------------------------
# 4. init_db() — failure branch (lines 102–103)
# ----------------------------------------------------------
def test_init_db_failure(monkeypatch):
    """Force metadata.create_all() to fail → triggers RuntimeError("init_db failed")."""

    def fail_create_all(*args, **kwargs):
        raise Exception("x")

    monkeypatch.setattr(dbase.Base.metadata, "create_all", fail_create_all)

    with pytest.raises(RuntimeError) as exc:
        dbase.init_db()

    assert "init_db failed" in str(exc.value)


# ----------------------------------------------------------
# 5. drop_db() — failure branch (lines 113–114)
# ----------------------------------------------------------
def test_drop_db_failure(monkeypatch):
    """Force metadata.drop_all() to fail → triggers RuntimeError("drop_db failed")."""

    def fail_drop_all(*args, **kwargs):
        raise Exception("x")

    monkeypatch.setattr(dbase.Base.metadata, "drop_all", fail_drop_all)

    with pytest.raises(RuntimeError) as exc:
        dbase.drop_db()

    assert "drop_db failed" in str(exc.value)


# ----------------------------------------------------------
# 6. _postgres_unavailable() — True branch already covered
# ----------------------------------------------------------
def test_postgres_unavailable_true(monkeypatch):
    """Force socket.create_connection to fail → function returns True."""

    def fail_connect(*args, **kwargs):
        raise Exception("cannot connect")

    monkeypatch.setattr(dbase.socket, "create_connection", fail_connect)

    assert dbase._postgres_unavailable() is True


# ----------------------------------------------------------
# 7. _postgres_unavailable() — False branch (line 121)
# ----------------------------------------------------------
def test_postgres_unavailable_false(monkeypatch):
    """Force create_connection to succeed → hit return False branch."""

    class FakeConn:
        def close(self): pass

    def good_connect(*args, **kwargs):
        return FakeConn()

    monkeypatch.setattr(dbase.socket, "create_connection", good_connect)

    assert dbase._postgres_unavailable() is False


# ----------------------------------------------------------
# 8. _trigger_fallback_if_test_env() — failure branch (126–129)
# ----------------------------------------------------------
def test_trigger_fallback_failure(monkeypatch):
    """Force _ensure_sqlite_fallback() to fail → RuntimeError('fallback failed')."""

    def fail_fallback():
        raise Exception("bad fallback")

    monkeypatch.setattr(dbase, "_ensure_sqlite_fallback", fail_fallback)

    with pytest.raises(RuntimeError) as exc:
        dbase._trigger_fallback_if_test_env()

    assert "fallback failed" in str(exc.value)


# ----------------------------------------------------------
# 9. _run_session_lifecycle_for_coverage() — commit path
# ----------------------------------------------------------
def test_session_lifecycle_commit(monkeypatch):
    """Simulate a successful commit → return True."""

    class FakeSession:
        closed = False
        is_active = True

        def commit(self): pass
        def close(self): pass

    monkeypatch.setattr(dbase, "get_session", lambda: FakeSession())

    assert dbase._run_session_lifecycle_for_coverage() is True


# ----------------------------------------------------------
# 10. _run_session_lifecycle_for_coverage() — rollback path
# ----------------------------------------------------------
def test_session_lifecycle_rollback(monkeypatch):
    """Simulate commit failure → force rollback → raise RuntimeError."""

    class FakeSession:
        closed = False
        is_active = True

        def commit(self):
            raise Exception("fail")

        def rollback(self): pass
        def close(self): pass

    monkeypatch.setattr(dbase, "get_session", lambda: FakeSession())

    with pytest.raises(RuntimeError):
        dbase._run_session_lifecycle_for_coverage()
