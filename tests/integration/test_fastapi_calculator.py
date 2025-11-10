# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment-10: Secure User Model (Pydantic Validation + JWT Auth + Database Testing)
# File: tests/integration/test_fastapi_calculator.py
# ----------------------------------------------------------
# Description:
# Integration tests for Assignment 10.
# Covers:
#   • Arithmetic API endpoints (core calculator)
#   • Health check endpoint
#   • Placeholders for JWT-based auth routes (xfail for now)
# ----------------------------------------------------------

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from app.auth import dependencies

# Initialize test client
client = TestClient(app)


# ----------------------------------------------------------
#  Calculator Endpoint Tests
# ----------------------------------------------------------
@pytest.mark.parametrize(
    "endpoint, payload, expected",
    [
        ("/add", {"a": 4, "b": 6}, {"result": 10}),
        ("/subtract", {"a": 15, "b": 5}, {"result": 10}),
        ("/multiply", {"a": 3, "b": 4}, {"result": 12}),
        ("/divide", {"a": 20, "b": 4}, {"result": 5.0}),
    ],
)
def test_calculator_routes(endpoint, payload, expected):
    """Ensure arithmetic routes return correct results."""
    response = client.post(endpoint, json=payload)
    assert response.status_code == 200
    assert response.json() == expected


def test_divide_by_zero():
    """Verify division by zero returns proper error."""
    response = client.post("/divide", json={"a": 10, "b": 0})
    assert response.status_code in (400, 422)
    assert "error" in response.text.lower()


# ----------------------------------------------------------
#  Placeholder Auth & Secure User Tests (to be implemented later)
# ----------------------------------------------------------

@pytest.mark.xfail(reason="User registration endpoint not implemented yet")
def test_register_user_placeholder():
    """Expected fail until /register route is implemented."""
    response = client.post(
        "/register",
        json={"username": "nandan", "email": "nandan@example.com", "password": "StrongPass1"},
    )
    assert response.status_code in (200, 201)
    assert "username" in response.json()


@pytest.mark.xfail(reason="User login endpoint not implemented yet")
def test_login_user_placeholder():
    """Expected fail until /login route is implemented."""
    response = client.post(
        "/login",
        data={"username": "nandan", "password": "StrongPass1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.xfail(reason="Protected user endpoint not implemented yet")
def test_users_me_placeholder():
    """Expected fail until /users/me route is implemented."""
    token = dependencies.create_access_token({"sub": "1"})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert "username" in response.json()


# ----------------------------------------------------------
#  Health Endpoint Test
# ----------------------------------------------------------
def test_health_check():
    """Ensure /health endpoint responds successfully."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "healthy" in data["status"].lower()
