# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/05/2025
# Assignment-10: Secure User Model (Pydantic Validation + JWT Auth + Database Testing)
# File: tests/integration/test_fastapi_calculator.py
# ----------------------------------------------------------
# Description:
# Integration tests for Assignment 10.
# Extends previous FastAPI Calculator tests to include:
#   • Secure user registration
#   • JWT-based login and authorization
#   • Protected endpoint validation
#   • Backward compatibility for calculator routes
# ----------------------------------------------------------

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from app.auth import dependencies
from app.models.user import User

client = TestClient(app)


# ----------------------------------------------------------
#  Calculator Endpoint Tests (Backwards Compatibility)
# ----------------------------------------------------------
@pytest.mark.parametrize("endpoint, payload, expected", [
    ("/add", {"a": 4, "b": 6}, {"result": 10}),
    ("/subtract", {"a": 15, "b": 5}, {"result": 10}),
    ("/multiply", {"a": 3, "b": 4}, {"result": 12}),
    ("/divide", {"a": 20, "b": 4}, {"result": 5.0}),
])
def test_calculator_routes(client, endpoint, payload, expected):
    """Ensure arithmetic routes still work correctly."""
    res = client.post(endpoint, json=payload)
    assert res.status_code == 200
    assert res.json() == expected


def test_divide_by_zero(client):
    """Check division by zero returns a proper error message."""
    res = client.post("/divide", json={"a": 10, "b": 0})
    assert res.status_code in (400, 422)
    assert "error" in res.text.lower()


# ----------------------------------------------------------
#  Secure User Model & JWT Authentication Tests
# ----------------------------------------------------------
@patch("app.crud.create_user")
def test_register_user(mock_create_user):
    """Simulate successful user registration."""
    fake_user = User(
        id=1,
        username="nandan",
        email="nandan@example.com",
        password_hash="hashedpass",
        is_active=True,
    )
    mock_create_user.return_value = fake_user

    response = client.post(
        "/register",
        json={"username": "nandan", "email": "nandan@example.com", "password": "StrongPass1"}
    )

    assert response.status_code in (200, 201)
    body = response.json()
    assert body["username"] == "nandan"
    assert "email" in body


@patch("app.auth.dependencies.authenticate_user")
def test_login_user(mock_auth_user):
    """Verify JWT token is issued on successful login."""
    mock_auth_user.return_value = MagicMock(id=1, username="nandan")
    response = client.post(
        "/login",
        data={"username": "nandan", "password": "StrongPass1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@patch("app.auth.dependencies.authenticate_user", side_effect=Exception("Invalid credentials"))
def test_login_user_invalid(mock_auth_user):
    """Ensure invalid credentials return HTTP 401."""
    response = client.post(
        "/login",
        data={"username": "wrong", "password": "bad"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401


@patch("app.auth.dependencies.get_current_user")
def test_protected_me_valid_token(mock_current_user):
    """Access /users/me with a valid JWT token."""
    mock_current_user.return_value = MagicMock(username="nandan", email="nandan@example.com")
    token = dependencies.create_access_token({"sub": "1"})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "nandan"
    assert "email" in data


def test_protected_me_invalid_token():
    """Access /users/me with invalid JWT should return 401."""
    bad_token = "invalid.token"
    response = client.get("/users/me", headers={"Authorization": f"Bearer {bad_token}"})
    assert response.status_code == 401
    assert "invalid" in response.text.lower()


# ----------------------------------------------------------
#  Health Endpoint (Container + DB Check)
# ----------------------------------------------------------
def test_health_check(client):
    """Ensure /health endpoint responds in Docker environment."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "ok" in data["status"].lower() or "healthy" in data["status"].lower()
