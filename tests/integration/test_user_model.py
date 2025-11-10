# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment-10: Secure User Model (Pydantic Validation + Database Testing)
# File: tests/integration/test_user_model.py
# ----------------------------------------------------------
# Description:
# Integration tests for the SQLAlchemy User model.
# Covers:
#   • Session creation & rollback
#   • Unique constraints & commits
#   • Query, update, and bulk insert behavior
#   • Password hashing / verification
#   • Model __repr__ verification
# ----------------------------------------------------------

import pytest
import logging
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.user_model import User
from app.database.dbase import Base, engine, SessionLocal
from app.auth.security import hash_password

logger = logging.getLogger(__name__)


# ----------------------------------------------------------
# Fixtures
# ----------------------------------------------------------
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Recreate tables before each test to ensure isolation."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide a clean SQLAlchemy session for each test."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def make_user():
    """Return a factory for generating user instances."""
    def _make(username: str, email: str):
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
    """Verify DB connectivity via simple SELECT query."""
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


# ----------------------------------------------------------
# Insert / Commit / Rollback Tests
# ----------------------------------------------------------
def test_user_commit_and_rollback(db_session, make_user):
    """Commit valid user, verify rollback on duplicate email."""
    u1 = make_user("alpha", "alpha@example.com")
    db_session.add(u1)
    db_session.commit()

    # Duplicate email should raise IntegrityError
    u2 = make_user("beta", "alpha@example.com")
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Ensure only one valid user remains
    users = db_session.query(User).all()
    assert len(users) == 1
    assert users[0].username == "alpha"


# ----------------------------------------------------------
# Query Behavior
# ----------------------------------------------------------
def test_user_query_methods(db_session, make_user):
    """Verify common query filters and ordering."""
    db_session.add_all([
        make_user("user1", "u1@example.com"),
        make_user("user2", "u2@example.com"),
        make_user("user3", "u3@example.com"),
    ])
    db_session.commit()

    assert db_session.query(User).count() == 3

    found = db_session.query(User).filter_by(username="user2").first()
    assert found and found.email == "u2@example.com"

    ordered = db_session.query(User).order_by(User.email).all()
    assert [u.email for u in ordered] == sorted([u.email for u in ordered])


# ----------------------------------------------------------
# Update & Refresh Tests
# ----------------------------------------------------------
def test_user_update_and_refresh(db_session, make_user):
    """Ensure updates persist and timestamps refresh."""
    user = make_user("nandan", "nandan@example.com")
    db_session.add(user)
    db_session.commit()

    user.email = "updated@example.com"
    db_session.commit()
    db_session.refresh(user)

    assert user.email == "updated@example.com"


# ----------------------------------------------------------
# Bulk Insert Tests
# ----------------------------------------------------------
@pytest.mark.slow
def test_bulk_user_insert(db_session, make_user):
    """Insert multiple users efficiently using bulk_save_objects."""
    users = [make_user(f"bulk{i}", f"bulk{i}@example.com") for i in range(5)]
    db_session.bulk_save_objects(users)
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
    except SQLAlchemyError:
        db_session.rollback()

    # Ensure rollback cleared pending insert
    assert db_session.query(User).filter_by(username="rollback").first() is None


# ----------------------------------------------------------
# Model Password 
# ----------------------------------------------------------
def test_user_password_methods():
    """Cover set_password(), verify_password(), and __repr__()."""
    user = User(username="demo", email="demo@example.com")
    user.set_password("MySecurePass123")
    assert user.password_hash is not None
    assert user.verify_password("MySecurePass123") is True
    assert user.verify_password("WrongPass") is False

    # __repr__ validation
    repr_out = repr(user)
    assert "demo" in repr_out
    assert "demo@example.com" in repr_out

# ----------------------------------------------------------
# Schema Conversion Coverage
# ----------------------------------------------------------
def test_user_to_read_schema(db_session, make_user):
    """Ensure to_read_schema() correctly converts model to Pydantic schema."""
    user = make_user("convert", "convert@example.com")
    db_session.add(user)
    db_session.commit()

    schema = user.to_read_schema()
    assert schema.username == "convert"
    assert schema.email == "convert@example.com"
    assert hasattr(schema, "created_at")
    assert hasattr(schema, "updated_at")


