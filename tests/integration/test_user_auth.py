# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/05/2025
# Assignment-10: Secure User Model (Pydantic Validation + Database Testing)
# File: tests/integration/test_user_auth.py
# ----------------------------------------------------------
# Description:
# Integration tests for the User model and authentication logic.
# Covers:
#   • Password hashing & verification
#   • Unique email/username constraints
#   • JWT creation and verification
#   • SQLAlchemy ORM persistence
# ----------------------------------------------------------

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.security import hash_password, verify_password
from app.database import Base, engine, SessionLocal


# ----------------------------------------------------------
# Fixtures
# ----------------------------------------------------------
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Create test tables before running tests and drop after."""
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


@pytest.fixture
def user_data():
    """Return reusable fake user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": hash_password("SecurePass123"),
    }


# ----------------------------------------------------------
#  Password Hashing and Verification
# ----------------------------------------------------------
def test_password_hashing_and_verification():
    """Verify bcrypt hashing and validation functions."""
    raw_password = "SecurePass123"
    hashed = hash_password(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed)
    assert not verify_password("WrongPass", hashed)


# ----------------------------------------------------------
#  User ORM Behavior
# ----------------------------------------------------------
def test_user_creation_and_persistence(db_session, user_data):
    """Create and persist a new user in the database."""
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()

    fetched = db_session.query(User).filter_by(username="testuser").first()
    assert fetched is not None
    assert fetched.username == "testuser"
    assert fetched.email == "test@example.com"
    assert verify_password("SecurePass123", fetched.password_hash)


def test_unique_username_email_constraint(db_session, user_data):
    """Enforce unique username and email constraints."""
    user1 = User(**user_data)
    db_session.add(user1)
    db_session.commit()

    duplicate = User(**user_data)
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


# ----------------------------------------------------------
#  JWT Token Handling
# ----------------------------------------------------------
def test_jwt_token_creation_and_verification():
    """Ensure JWT token correctly encodes and decodes user ID."""
    token = User.create_token(user_id=42)
    decoded_user_id = User.verify_token(token)
    assert decoded_user_id == 42


def test_invalid_token_rejected():
    """Return None when verifying invalid token string."""
    invalid = "abc.def.ghi"
    result = User.verify_token(invalid)
    assert result is None


# ----------------------------------------------------------
#  Model Representation
# ----------------------------------------------------------
def test_user_model_repr(db_session, user_data):
    """Check __repr__ returns readable format."""
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    repr_str = repr(user)
    assert "username='testuser'" in repr_str
    assert "email='test@example.com'" in repr_str
