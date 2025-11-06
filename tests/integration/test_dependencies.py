# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/05/2025
# Assignment-10: Secure User Model + OAuth2 + JWT Integration
# File: tests/integration/test_dependencies.py
# ----------------------------------------------------------
# Description:
# Integration tests for authentication dependencies.
# Validates JWT token creation, decoding, and user
# authentication flows using mocked database sessions.
# ----------------------------------------------------------

import pytest
from unittest.mock import MagicMock, patch
from jose import jwt
from fastapi import HTTPException, status
from datetime import timedelta

from app.auth import dependencies
from app.security import hash_password


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
        password_hash=hash_password("secure123"),
        is_active=True,
    )


# ----------------------------------------------------------
# Test: JWT Creation & Verification
# ----------------------------------------------------------
def test_create_and_verify_token():
    """Ensure that JWT tokens are created and verified correctly."""
    data = {"sub": "1", "username": "testuser"}
    token = dependencies.create_access_token(data, timedelta(minutes=1))

    # Decode using jose directly
    decoded = jwt.decode(
        token,
        dependencies.SECRET_KEY,
        algorithms=[dependencies.ALGORITHM],
    )

    assert decoded.get("sub") == "1"
    assert "exp" in decoded

    # Verify using helper
    payload = dependencies.verify_access_token(token)
    assert payload["sub"] == "1"


def test_verify_access_token_invalid():
    """Ensure that invalid tokens raise HTTP 401."""
    with pytest.raises(HTTPException) as exc_info:
        dependencies.verify_access_token("invalid.token.value")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in exc_info.value.detail.lower()


# ----------------------------------------------------------
# Test: Authenticate User
# ----------------------------------------------------------
def test_authenticate_user_valid(mock_db, fake_user):
    """Verify authenticate_user() succeeds with correct credentials."""
    # Mock DB lookup
    with patch("app.crud.get_user_by_username", return_value=fake_user), \
         patch("app.crud.get_user_by_email", return_value=None):

        user = dependencies.authenticate_user(mock_db, "testuser", "secure123")
        assert user.username == "testuser"
        assert user.email == "test@example.com"


def test_authenticate_user_invalid_password(mock_db, fake_user):
    """Verify authenticate_user() raises HTTP 401 for wrong password."""
    with patch("app.crud.get_user_by_username", return_value=fake_user), \
         patch("app.crud.get_user_by_email", return_value=None):

        with pytest.raises(HTTPException) as exc_info:
            dependencies.authenticate_user(mock_db, "testuser", "wrongpass")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid username or password" in exc_info.value.detail.lower()


def test_authenticate_user_not_found(mock_db):
    """Verify authenticate_user() raises HTTP 401 when user not found."""
    with patch("app.crud.get_user_by_username", return_value=None), \
         patch("app.crud.get_user_by_email", return_value=None):

        with pytest.raises(HTTPException) as exc_info:
            dependencies.authenticate_user(mock_db, "ghost", "nopass")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


# ----------------------------------------------------------
# Test: get_current_user()
# ----------------------------------------------------------
def test_get_current_user_valid_token(mock_db, fake_user):
    """Verify get_current_user() retrieves user from valid token."""
    token = dependencies.create_access_token({"sub": str(fake_user.id)})

    # Mock DB query
    mock_query = MagicMock()
    mock_query.filter_by.return_value.first.return_value = fake_user
    mock_db.query.return_value = mock_query

    result = dependencies.get_current_user(token=token, db=mock_db)
    assert result.username == fake_user.username
    assert result.email == fake_user.email


def test_get_current_user_missing_user_id(mock_db):
    """Verify token without 'sub' raises HTTP 401."""
    token = dependencies.create_access_token({})
    payload = jwt.decode(token, dependencies.SECRET_KEY, algorithms=[dependencies.ALGORITHM])
    del payload["exp"]  # simulate tampering

    fake_token = jwt.encode(payload, dependencies.SECRET_KEY, algorithm=dependencies.ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        dependencies.get_current_user(token=fake_token, db=mock_db)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "missing user id" in exc_info.value.detail.lower()


def test_get_current_user_user_not_found(mock_db):
    """Verify get_current_user() raises HTTP 401 if user does not exist."""
    token = dependencies.create_access_token({"sub": "999"})
    mock_db.query.return_value.filter_by.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        dependencies.get_current_user(token=token, db=mock_db)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "not found" in exc_info.value.detail.lower()
