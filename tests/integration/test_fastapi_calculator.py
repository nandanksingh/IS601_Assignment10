# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment 10: Secure User Model (FastAPI Calculator Tests)
# File: tests/integration/test_fastapi_calculator.py
# ----------------------------------------------------------
# Description:
# Extended integration tests to achieve full coverage.
# Adds negative tests for validation and JSON errors.
# ----------------------------------------------------------

import pytest
from fastapi.testclient import TestClient
from main import app
from app.operations import add, subtract, multiply, divide

client = TestClient(app)


# ----------------------------------------------------------
# Arithmetic Tests
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
def test_arithmetic_operations(endpoint, payload, expected):
    response = client.post(endpoint, json=payload)
    assert response.status_code == 200
    assert response.json() == expected


def test_invalid_json_request():
    """Invalid payload triggers validation error."""
    response = client.post("/add", json={"a": "text", "b": 5})
    assert response.status_code in (400, 422)


def test_divide_by_zero_error():
    """Division by zero returns handled error."""
    response = client.post("/divide", json={"a": 10, "b": 0})
    assert response.status_code in (400, 422)
    assert "error" in response.text.lower()


def test_health_endpoint_ok():
    """Ensure /health returns success."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "healthy" in response.json()["status"].lower()


def test_operation_logic_directly():
    """Test imported functions directly for coverage."""
    assert add(1, 2) == 3
    assert subtract(5, 3) == 2
    assert multiply(2, 5) == 10
    assert divide(9, 3) == 3.0


def test_divide_invalid_input():
    """Trigger invalid type branch from validate_number."""
    with pytest.raises(ValueError):
        divide("text", 5)
