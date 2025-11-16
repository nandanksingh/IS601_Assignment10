# Author: Nandan Kumar
# Date: 11/05/2025
# Assignment 10: Secure User Model, Pydantic Validation, and Docker Testing
# File: app/operations/__init__.py
# ----------------------------------------------------------
# Description:
# Core arithmetic logic module for the FastAPI Calculator.
# Contains reusable mathematical functions: add, subtract,
# multiply, and divide. Each function includes input validation
# and structured logging. This module is imported directly
# in main.py and serves as a stateless logic layer for the API.
# Compatible with containerized execution under Docker Compose.
# ----------------------------------------------------------

import logging
from typing import Union

# ----------------------------------------------------------
# Type Alias and Logger Configuration
# ----------------------------------------------------------
Number = Union[int, float]
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ----------------------------------------------------------
# Helper Function: Validate Numeric Input
# ----------------------------------------------------------
def validate_number(value: Number) -> Number:
    """
    Ensure that the provided input is a numeric value.
    Raises a ValueError if the input is not int or float.
    """
    if not isinstance(value, (int, float)):
        logger.error(f"Invalid input type: {type(value)} - must be numeric.")
        raise ValueError("Input must be numeric (int or float).")
    return value


# ----------------------------------------------------------
# Arithmetic Operations
# ----------------------------------------------------------
def add(a: Number, b: Number) -> float:
    """Perform addition of two numbers."""
    a, b = validate_number(a), validate_number(b)
    result = a + b
    logger.info(f"Add operation: {a} + {b} = {result}")
    return float(result)


def subtract(a: Number, b: Number) -> float:
    """Perform subtraction of two numbers."""
    a, b = validate_number(a), validate_number(b)
    result = a - b
    logger.info(f"Subtract operation: {a} - {b} = {result}")
    return float(result)


def multiply(a: Number, b: Number) -> float:
    """Perform multiplication of two numbers."""
    a, b = validate_number(a), validate_number(b)
    result = a * b
    logger.info(f"Multiply operation: {a} * {b} = {result}")
    return float(result)


def divide(a: Number, b: Number) -> float:
    """
    Perform division of two numbers with zero-division protection.
    Raises a ValueError if b is zero.
    """
    a, b = validate_number(a), validate_number(b)
    if b == 0:
        logger.warning(f"Division by zero attempt: a={a}, b={b}")
        raise ValueError("Division by zero is not allowed.")
    result = a / b
    logger.info(f"Divide operation: {a} / {b} = {result}")
    return float(result)


# ----------------------------------------------------------
# Public API
# ----------------------------------------------------------
__all__ = ["add", "subtract", "multiply", "divide"]
