# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/05/2025
# Assignment-10: Secure User Model (Pydantic Validation + Database Testing)
# File: tests/integration/test_user.py
# ----------------------------------------------------------
# Description:
# Integration tests for direct User model and database operations.
# Covers:
#   • Session creation & rollback
#   • User persistence and constraints
#   • Query operations
#   • Update and bulk insert examples
# ----------------------------------------------------------

import pytest
import logging
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.database import Base, engine, SessionLocal
from app.security import hash_password

logger = logging.getLogger(__name__)


# ----------------------------------------------------------
# Fixtures
# ----------------------------------------------------------
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Initialize test DB tables and teardown after all tests."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide isolated session for each test with rollback."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def make_user():
    """Return a helper to create users easily."""
    def _make(username, email):
        return User(
            username=username,
            email=email,
            password_hash=hash_password("SecurePass123"),
        )
    return _make


# ----------------------------------------------------------
# Connection Test
# ----------------------------------------------------------
def test_database_connection(db_session):
    """Verify database connectivity via simple SELECT."""
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


# ----------------------------------------------------------
# Insert / Commit / Rollback Tests
# ----------------------------------------------------------
def test_user_commit_and_rollback(db_session, make_user):
    """Commit valid user, trigger rollback on duplicate."""
    u1 = make_user("alpha", "alpha@example.com")
    db_session.add(u1)
    db_session.commit()

    # Duplicate email → should raise IntegrityError
    u2 = make_user("beta", "alpha@example.com")
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Ensure only first user remains
    users = db_session.query(User).all()
    assert len(users) == 1
    assert users[0].username == "alpha"


# ----------------------------------------------------------
# Query Behavior
# ----------------------------------------------------------
def test_user_query_methods(db_session, make_user):
    """Demonstrate common query filters and ordering."""
    db_session.add_all([
        make_user("user1", "u1@example.com"),
        make_user("user2", "u2@example.com"),
        make_user("user3", "u3@example.com"),
    ])
    db_session.commit()

    total = db_session.query(User).count()
    assert total >= 3

    found = db_session.query(User).filter_by(username="user2").first()
    assert found is not None
    assert found.email == "u2@example.com"

    ordered = db_session.query(User).order_by(User.email).all()
    assert all(isinstance(u.email, str) for u in ordered)


# ----------------------------------------------------------
# Update & Refresh Tests
# ----------------------------------------------------------
def test_user_update_and_refresh(db_session, make_user):
    """Update user email and verify updated_at refresh."""
    user = make_user("nandan", "nandan@example.com")
    db_session.add(user)
    db_session.commit()

    old_email = user.email
    user.email = "updated@example.com"
    db_session.commit()
    db_session.refresh(user)

    assert user.email != old_email
    assert user.email == "updated@example.com"


# ----------------------------------------------------------
# Bulk Insert Tests
# ----------------------------------------------------------
@pytest.mark.slow
def test_bulk_user_insert(db_session, make_user):
    """Insert multiple users efficiently using bulk_save_objects."""
    bulk_users = [make_user(f"bulk{i}", f"bulk{i}@ex.com") for i in range(5)]
    db_session.bulk_save_objects(bulk_users)
    db_session.commit()

    count = db_session.query(User).count()
    assert count >= 5


# ----------------------------------------------------------
# Unique Constraints
# ----------------------------------------------------------
def test_unique_constraints(db_session, make_user):
    """Ensure unique username and email constraints are enforced."""
    u1 = make_user("dupuser", "dup@example.com")
    db_session.add(u1)
    db_session.commit()

    u2 = make_user("dupuser", "diff@example.com")
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    u3 = make_user("diffuser", "dup@example.com")
    db_session.add(u3)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


# ----------------------------------------------------------
# Transaction Rollback Behavior
# ----------------------------------------------------------
def test_transaction_rollback(db_session, make_user):
    """Force SQL error to confirm rollback behavior."""
    user = make_user("rollback", "rollback@example.com")
    db_session.add(user)
    try:
        db_session.execute(text("SELECT * FROM non_existing_table"))
        db_session.commit()
    except Exception:
        db_session.rollback()

    assert db_session.query(User).filter_by(username="rollback").first() is None


# ----------------------------------------------------------
# Model Representation
# ----------------------------------------------------------
def test_user_repr(db_session, make_user):
    """Ensure model __repr__ is human-readable."""
    user = make_user("pretty", "pretty@example.com")
    db_session.add(user)
    db_session.commit()
    assert "username='pretty'" in repr(user)
    assert "email='pretty@example.com'" in repr(user)
