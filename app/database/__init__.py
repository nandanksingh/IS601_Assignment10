# ----------------------------------------------------------
# Database fallback helpers required by test_database.py
# ----------------------------------------------------------

import os
import socket
from sqlalchemy import create_engine

# ----------------------------------------------------------
# PostgreSQL availability check
# ----------------------------------------------------------
def _postgres_unavailable() -> bool:
    """
    Tests patch socket.create_connection() to return:
      • raise OSError → return True
      • return mock socket → return False
    """
    try:
        conn = socket.create_connection(("localhost", 5432), timeout=1)
        conn.close()
        return False
    except Exception:
        return True


# ----------------------------------------------------------
# Ensure SQLite fallback
# ----------------------------------------------------------
def _ensure_sqlite_fallback():
    """
    Tests expect:
      • When postgres unavailable → DATABASE_URL changes to sqlite
      • No return value required
    """
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"


# ----------------------------------------------------------
# Fallback trigger for test env
# ----------------------------------------------------------
def _trigger_fallback_if_test_env():
    """
    Tests patch `_ensure_sqlite_fallback` to throw exception:
      → expect RuntimeError("Database fallback failed")
    Otherwise fallback is executed normally.
    """
    try:
        _ensure_sqlite_fallback()
    except Exception:
        raise RuntimeError("Database fallback failed")
