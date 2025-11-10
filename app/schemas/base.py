# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment-10: Secure User Model (Pydantic Validation + Database Testing)
# File: app/schemas/base.py
# ----------------------------------------------------------
# Description:
# Shared foundational Pydantic schemas and mixins used by
# all user-related models. Handles common profile fields
# and centralized password-strength validation.
# ----------------------------------------------------------

from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator


# ----------------------------------------------------------
# Common User Fields
# ----------------------------------------------------------
class UserBase(BaseModel):
    """Basic user profile fields shared across schemas."""
    first_name: str = Field(..., min_length=2, max_length=50, examples=["Nandan"])
    last_name: str = Field(..., min_length=2, max_length=50, examples=["Kumar"])
    username: str = Field(..., min_length=3, max_length=50, examples=["nandan123"])
    email: EmailStr = Field(..., examples=["nandan@example.com"])

    # Enables ORM model ↔ Pydantic model conversion
    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------
# Password Validation Mixin
# ----------------------------------------------------------
class PasswordMixin(BaseModel):
    """Adds strong password policy validation."""
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        examples=["SecurePass123"],
        description="Password must contain uppercase, lowercase, and digits."
    )

    @model_validator(mode="before")
    @classmethod
    def validate_password_strength(cls, values: dict) -> dict:
        """Validate password complexity before model creation."""
        pwd = values.get("password")
        if not pwd:
            raise ValueError("Password is required.")
        if len(pwd) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        if not any(c.isupper() for c in pwd):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in pwd):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in pwd):
            raise ValueError("Password must contain at least one numeric digit.")
        return values


# ----------------------------------------------------------
# Composite Schemas
# ----------------------------------------------------------
class UserCreate(UserBase, PasswordMixin):
    """Used for user registration (inherits password validation rules)."""
    pass


class UserLogin(PasswordMixin):
    """Used for authentication; accepts username or email."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username or email used for login.",
        examples=["nandan@example.com"]
    )
