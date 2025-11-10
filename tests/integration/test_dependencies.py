# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment-10: Secure User Model + OAuth2 + JWT Integration
# File: tests/integration/test_dependencies.py
# ----------------------------------------------------------
# Description:
# Integration tests for authentication dependencies.
# Validates JWT token creation, decoding, and user
# authentication flows using mocked database sessions.
# ----------------------------------------------------------

import pytest
from unittest.mock import MagicMock
from jose import jwt
from fastapi import HTTPException, status
from datetime import timedelta

from app.auth import dependencies
from app.auth.security import hash_password, verify_password


# ----------------------------------------------------------
# Fixtures
# ----------------------------------------------------------
@pytest.fixture
def mock_db():
    """Provide a mocked SQLAlchemy DB session."""
    return MagicMock()


@pytest.fixture
def fake_user():
    """Provide a fake user object for authentication tests."""
    return MagicMock(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("SecurePass123"),
        is_active=True,
    )


# ----------------------------------------------------------
# Test: JWT Creation & Verification
# ----------------------------------------------------------
def test_create_and_verify_token():
    """Ensure that JWT tokens are created and verified correctly."""
    data = {"sub": "1", "username": "testuser"}
    token = dependencies.create_access_token(data, timedelta(minutes=1))

    # Decode using same secret and algorithm
    decoded = jwt.decode(
        token,
        dependencies.SECRET_KEY,
        algorithms=[dependencies.ALGORITHM],
    )

    assert decoded.get("sub") == "1"
    assert "exp" in decoded

    payload = dependencies.verify_access_token(token)
    assert payload["sub"] == "1"


def test_verify_access_token_invalid():
    """Ensure that invalid tokens raise HTTP 401."""
    with pytest.raises(HTTPException) as exc_info:
        dependencies.verify_access_token("invalid.token.value")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in exc_info.value.detail.lower()


# ----------------------------------------------------------
# Test: authenticate_user()
# ----------------------------------------------------------
def test_authenticate_user_valid(mock_db, fake_user):
    """Ensure authenticate_user() returns a valid user for correct credentials."""
    # Mock DB query chain
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = fake_user
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    result = dependencies.authenticate_user(mock_db, fake_user.username, "SecurePass123")
    assert result is not None
    assert result.username == fake_user.username
    assert verify_password("SecurePass123", result.password_hash)  # type: ignore[arg-type]


def test_authenticate_user_invalid_password(mock_db, fake_user):
    """Ensure authenticate_user() returns None for invalid password."""
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = fake_user
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    result = dependencies.authenticate_user(mock_db, fake_user.username, "WrongPass")
    assert result is None


def test_authenticate_user_not_found(mock_db):
    """Ensure authenticate_user() returns None for nonexistent users."""
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    result = dependencies.authenticate_user(mock_db, "ghostuser", "password123")
    assert result is None


# ----------------------------------------------------------
# Test: get_current_user()
# ----------------------------------------------------------
def test_get_current_user_valid_token(mock_db, fake_user):
    """Verify get_current_user() retrieves user from valid token."""
    token = dependencies.create_access_token({"sub": str(fake_user.id)})

    # Mock DB query chain
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = fake_user
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    result = dependencies.get_current_user(token=token, db=mock_db)
    assert result.username == fake_user.username
    assert result.email == fake_user.email


def test_get_current_user_missing_user_id(mock_db):
    """Verify token without 'sub' raises HTTP 401."""
    token = dependencies.create_access_token({})  # no 'sub' claim

    with pytest.raises(HTTPException) as exc_info:
        dependencies.get_current_user(token=token, db=mock_db)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "user id" in exc_info.value.detail.lower()


def test_get_current_user_user_not_found(mock_db):
    """Verify get_current_user() raises HTTP 401 if user does not exist."""
    token = dependencies.create_access_token({"sub": "999"})

    # Mock DB returning None
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    with pytest.raises(HTTPException) as exc_info:
        dependencies.get_current_user(token=token, db=mock_db)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "not found" in exc_info.value.detail.lower()
