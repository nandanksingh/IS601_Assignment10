# Author: Nandan Kumar
# Date: 11/09/2025
# Assignment 10: Secure User Model (Pydantic Validation)
# File: app/schemas/base.py
# ----------------------------------------------------------
# Description:
# This module defines reusable Pydantic schemas and validation
# logic for user creation and authentication. It provides a
# foundation for all user-related models and ensures data integrity
# through password strength and email validation.
# ----------------------------------------------------------

from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator


# ----------------------------------------------------------
# User Base Schema
# ----------------------------------------------------------
class UserBase(BaseModel):
    """
    Represents common fields for a user profile.
    Used as a base for both creation and response schemas.
    """

    first_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="User's first name"
    )
    last_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="User's last name"
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username for login"
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address of the user"
    )

    # Enables ORM model to Pydantic model conversion
    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------
# Password Validation Mixin
# ----------------------------------------------------------
class PasswordMixin(BaseModel):
    """
    Adds password validation rules to enforce strong credentials.
    """

    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Password must contain uppercase, lowercase, and digits"
    )

    @model_validator(mode="before")
    @classmethod
    def validate_password_strength(cls, values: dict) -> dict:
        """
        Validates password complexity before model creation.
        Ensures the password is at least six characters long and
        contains uppercase letters, lowercase letters, and numbers.
        """
        password = values.get("password")

        if not password:
            raise ValueError("Password is required.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in password):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one numeric digit.")

        return values


# ----------------------------------------------------------
# Composite Schemas
# ----------------------------------------------------------
class UserCreate(UserBase, PasswordMixin):
    """
    Used when registering a new user.
    Inherits all basic profile fields and password validation rules.
    """
    pass


class UserLogin(PasswordMixin):
    """
    Used for user authentication during login.
    Accepts username or email and password for verification.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username or email used for login"
    )
