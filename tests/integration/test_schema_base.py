# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/05/2025
# Assignment-10: Secure User Model (Pydantic Validation + Database Testing)
# File: tests/integration/test_schema_base.py
# ----------------------------------------------------------
# Description:
# Integration tests for `app/schemas/base.py`.
# Validates field constraints and password strength rules
# for UserBase, PasswordMixin, UserCreate, and UserLogin
# Pydantic schemas defined in Assignment-10.
# ----------------------------------------------------------

import pytest
from pydantic import ValidationError
from app.schemas.base import UserBase, PasswordMixin, UserCreate, UserLogin


# ----------------------------------------------------------
#  UserBase Schema Tests
# ----------------------------------------------------------
def test_user_base_valid():
    """Ensure valid data initializes UserBase correctly."""
    data = {
        "first_name": "Nandan",
        "last_name": "Kumar",
        "username": "nandan123",
        "email": "nandan@example.com",
    }
    user = UserBase(**data)
    assert user.first_name == "Nandan"
    assert user.email == "nandan@example.com"


def test_user_base_invalid_email():
    """Reject invalid email format."""
    invalid_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "email": "invalid-email",
    }
    with pytest.raises(ValidationError):
        UserBase(**invalid_data)


def test_user_base_missing_field():
    """Ensure missing required field raises ValidationError."""
    incomplete_data = {"first_name": "OnlyName"}
    with pytest.raises(ValidationError):
        UserBase(**incomplete_data)


# ----------------------------------------------------------
#  PasswordMixin Schema Tests
# ----------------------------------------------------------
@pytest.mark.parametrize("password", [
    "SecurePass123",     # valid
    "AnotherGood1",      # valid variant
])
def test_password_mixin_valid(password):
    """Accept strong passwords that meet all rules."""
    schema = PasswordMixin(password=password)
    assert schema.password == password


@pytest.mark.parametrize("password, expected_msg", [
    ("short", "Password must be at least 6 characters"),
    ("lowercase1", "uppercase"),
    ("UPPERCASE1", "lowercase"),
    ("NoDigitsHere", "digit"),
])
def test_password_mixin_invalid(password, expected_msg):
    """Reject weak passwords missing uppercase/lowercase/digit/length."""
    with pytest.raises(ValidationError) as exc_info:
        PasswordMixin(password=password)
    assert expected_msg.lower() in str(exc_info.value).lower()


# ----------------------------------------------------------
#  UserCreate Schema Tests
# ----------------------------------------------------------
def test_user_create_valid():
    """Validate a full user creation payload."""
    data = {
        "first_name": "Nandan",
        "last_name": "Kumar",
        "username": "nandan123",
        "email": "nandan@example.com",
        "password": "SecurePass123",
    }
    schema = UserCreate(**data)
    assert schema.username == "nandan123"
    assert schema.password == "SecurePass123"


def test_user_create_invalid_password():
    """Ensure weak password in registration raises ValidationError."""
    bad_data = {
        "first_name": "Nandan",
        "last_name": "Kumar",
        "username": "nandan123",
        "email": "nandan@example.com",
        "password": "weak",
    }
    with pytest.raises(ValidationError):
        UserCreate(**bad_data)


# ----------------------------------------------------------
#  UserLogin Schema Tests
# ----------------------------------------------------------
def test_user_login_valid():
    """Accept proper username/email with strong password."""
    data = {"username": "nandan@example.com", "password": "SecurePass123"}
    schema = UserLogin(**data)
    assert schema.username == "nandan@example.com"


@pytest.mark.parametrize("username", ["ab", "", None])
def test_user_login_invalid_username(username):
    """Reject too-short or missing username field."""
    data = {"username": username, "password": "SecurePass123"}
    with pytest.raises(ValidationError):
        UserLogin(**data)


def test_user_login_invalid_password():
    """Reject password that violates policy in login schema."""
    data = {"username": "nandan@example.com", "password": "short"}
    with pytest.raises(ValidationError):
        UserLogin(**data)
