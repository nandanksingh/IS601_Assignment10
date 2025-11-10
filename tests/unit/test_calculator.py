# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment-10: Secure User Model, Pydantic Validation, and Docker Testing
# File: tests/unit/test_calculator.py
# ----------------------------------------------------------
# Description:
# Unit tests for arithmetic functions implemented in app/operations.
# Verifies mathematical accuracy, type validation, and error handling
# across Add, Subtract, Multiply, and Divide functions.
# ----------------------------------------------------------

"""
These tests validate the calculator logic layer (app/operations).
Executed automatically in CI/CD under Docker and GitHub Actions.
"""

import pytest
from app.operations import add, subtract, multiply, divide


# ----------------------------------------------------------
#  add()
# ----------------------------------------------------------
@pytest.mark.parametrize("a, b, expected", [
    (3, 5, 8),
    (-2, 6, 4),
    (2.5, 1.5, 4.0),
    (0, 0, 0),
])
def test_add(a, b, expected):
    """Verify add() correctly adds integers, floats, and negatives."""
    assert add(a, b) == expected


# ----------------------------------------------------------
#  subtract()
# ----------------------------------------------------------
@pytest.mark.parametrize("a, b, expected", [
    (10, 4, 6),
    (4, 10, -6),
    (-3, -2, -1),
    (7.5, 2.5, 5.0),
])
def test_subtract(a, b, expected):
    """Verify subtract() returns accurate results across data types."""
    assert subtract(a, b) == expected


# ----------------------------------------------------------
#  multiply()
# ----------------------------------------------------------
@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 6),
    (-2, 3, -6),
    (1.5, 2.0, 3.0),
    (0, 7, 0),
])
def test_multiply(a, b, expected):
    """Ensure multiply() handles integers, floats, and sign variations."""
    assert multiply(a, b) == expected


# ----------------------------------------------------------
#  divide()
# ----------------------------------------------------------
@pytest.mark.parametrize("a, b, expected", [
    (8, 2, 4.0),
    (-9, 3, -3.0),
    (7.5, 2.5, 3.0),
    (0, 5, 0.0),
])
def test_divide(a, b, expected):
    """Verify divide() returns precise float results for valid inputs."""
    assert divide(a, b) == expected


# ----------------------------------------------------------
#  divide() → Division by Zero
# ----------------------------------------------------------
def test_divide_by_zero():
    """Ensure divide() raises ValueError when dividing by zero."""
    with pytest.raises(ValueError, match="Division by zero is not allowed"):
        divide(10, 0)


# ----------------------------------------------------------
#  Invalid Type Handling
# ----------------------------------------------------------
@pytest.mark.parametrize("func, a, b", [
    (add, "abc", 5),
    (subtract, 3, None),
    (multiply, [1, 2], 4),
    (divide, 5, "xyz"),
])
def test_invalid_type_inputs(func, a, b):
    """Ensure all arithmetic functions raise ValueError for invalid types."""
    with pytest.raises(ValueError, match="Input must be numeric"):
        func(a, b)
