# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/09/2025
# Assignment-10: Secure User Authentication Tests
# File: tests/integration/test_user_auth.py
# ----------------------------------------------------------
# Description:
# Validates password hashing, verification, and JWT token
# generation/decoding. Also covers SQLAlchemy ORM user model
# persistence, schema conversion, and exception handling.
# Ensures complete coverage of app/auth/security.py and
# app/models/user_model.py logic.
# ----------------------------------------------------------

import pytest
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError

from app.models.user_model import User
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


# ----------------------------------------------------------
# Password Hashing Tests
# ----------------------------------------------------------
def test_password_hashing_and_verification():
    """Verify that hashing and password checks work correctly."""
    raw_password = "SecurePass123"
    hashed = hash_password(raw_password)
    assert verify_password(raw_password, hashed)
    assert not verify_password("WrongPass", hashed)


def test_password_verification_with_invalid_hash():
    """Ensure verify_password handles invalid or corrupted hashes gracefully."""
    result = verify_password("AnyPass", "$2b$12$invalidhashstring")
    assert result is False


def test_hash_password_rejects_invalid_input():
    """Ensure hash_password raises error for invalid inputs."""
    with pytest.raises(ValueError, match="Password must be a non-empty string."):
        hash_password("")


# ----------------------------------------------------------
# User Model Tests
# ----------------------------------------------------------
@pytest.fixture
def user_data():
    """Provide reusable fake user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password_hash": hash_password("TestPass123"),
    }


def test_user_creation_and_persistence(db_session, user_data):
    """Confirm that user records persist in the database."""
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()

    stored = db_session.query(User).filter_by(username="testuser").first()
    assert stored.email == "test@example.com"


def test_unique_username_email_constraint(db_session, user_data):
    """Ensure uniqueness constraints are enforced correctly."""
    user1 = User(**user_data)
    db_session.add(user1)
    db_session.commit()

    user2 = User(**user_data)
    db_session.add(user2)
    with pytest.raises(SQLAlchemyError):
        db_session.commit()


def test_rollback_after_integrity_error(db_session, user_data):
    """Ensure rollback executes properly after failed commit."""
    user1 = User(**user_data)
    db_session.add(user1)
    db_session.commit()

    user2 = User(**user_data)
    db_session.add(user2)
    with pytest.raises(SQLAlchemyError):
        db_session.commit()
    db_session.rollback()
    assert db_session.query(User).count() == 1


def test_user_model_repr(db_session, user_data):
    """Validate string representation of User model."""
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    output = repr(user)
    assert "username='testuser'" in output


def test_to_read_schema_conversion(db_session, user_data):
    """Ensure User ORM instance converts to Pydantic schema correctly."""
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    schema = user.to_read_schema()
    assert schema.username == "testuser"
    assert schema.email == "test@example.com"


def test_database_commit_failure(monkeypatch, db_session, user_data):
    """Simulate SQLAlchemy commit failure for coverage."""
    user = User(**user_data)
    db_session.add(user)
    with patch.object(db_session, "commit", side_effect=SQLAlchemyError("commit fail")):
        with pytest.raises(SQLAlchemyError, match="commit fail"):
            db_session.commit()


# ----------------------------------------------------------
# JWT Token Tests
# ----------------------------------------------------------
def test_jwt_token_creation_and_verification():
    """Validate token creation and successful decoding."""
    token = create_access_token({"sub": "testuser"})
    decoded = decode_access_token(token)
    assert decoded.get("sub") == "testuser"


def test_invalid_token_rejected():
    """Ensure decode_access_token rejects invalid token strings."""
    with pytest.raises(RuntimeError, match="Invalid or expired token"):
        decode_access_token("invalid.token.signature")


def test_tampered_jwt_signature():
    """Reject tampered JWT signatures gracefully."""
    token = create_access_token({"sub": "user"})
    tampered = token + "tamper"
    with pytest.raises(RuntimeError, match="Invalid or expired token"):
        decode_access_token(tampered)


def test_expired_token_behavior(monkeypatch):
    """Ensure expired tokens are properly rejected."""
    from datetime import datetime, timedelta
    from jose import jwt
    from app.config import settings

    expired_token = jwt.encode(
        {"sub": "user", "exp": datetime.utcnow() - timedelta(seconds=1)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    with pytest.raises(RuntimeError, match="Invalid or expired token"):
        decode_access_token(expired_token)

# ----------------------------------------------------------
# Additional Coverage Tests for security.py
# ----------------------------------------------------------

def test_verify_password_invalid_type():
    """Covers branch where password types are invalid."""
    from app.auth.security import verify_password
    assert verify_password(123, "notahash") is False


def test_verify_password_empty_strings():
    """Covers branch where inputs are empty."""
    from app.auth.security import verify_password
    assert verify_password("", "") is False


def test_create_access_token_failure(monkeypatch):
    """Force jwt.encode to fail to cover exception branch."""
    import app.auth.security as sec

    def bad_encode(*args, **kwargs):
        raise Exception("encode failed")

    monkeypatch.setattr("jose.jwt.encode", bad_encode)

    with pytest.raises(RuntimeError, match="JWT creation failed"):
        sec.create_access_token({"sub": "1"})


def test_decode_access_token_unexpected_error(monkeypatch):
    """Force unexpected exception in decode to cover fallback branch."""
    import app.auth.security as sec

    def bad_decode(*args, **kwargs):
        raise ValueError("unexpected decode error")

    monkeypatch.setattr("jose.jwt.decode", bad_decode)

    with pytest.raises(RuntimeError, match="Token decode failure"):
        sec.decode_access_token("dummy")
