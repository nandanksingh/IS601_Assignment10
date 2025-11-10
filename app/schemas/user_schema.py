# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment-10: Secure User Model (Pydantic Validation + JWT + Database Testing)
# File: app/schemas/user_schema.py
# ----------------------------------------------------------
# Description:
# Defines Pydantic schemas for user data exchange between
# API endpoints, database models, and JWT authentication.
# ----------------------------------------------------------

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ----------------------------------------------------------
# Shared Base Schema
# ----------------------------------------------------------
class UserBase(BaseModel):
    """Base schema shared by all user representations."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        examples=["nandan123"],
        description="Unique username or handle of the user"
    )
    email: EmailStr = Field(
        ...,
        examples=["nandan@example.com"],
        description="User's unique email address"
    )
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)  # Enables ORM ↔ Pydantic conversion


# ----------------------------------------------------------
# Schema: User Creation (Registration)
# ----------------------------------------------------------
class UserCreate(UserBase):
    """Schema for creating a new user (includes raw password)."""
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        examples=["StrongPass123"],
        description="User's plain-text password (will be hashed before saving)"
    )


# ----------------------------------------------------------
# Schema: User Login
# ----------------------------------------------------------
class UserLogin(BaseModel):
    """Schema for login credentials."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        examples=["nandan123", "nandan@example.com"],
        description="Username or email used to log in"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        examples=["StrongPass123"],
        description="Plain-text password for login"
    )


# ----------------------------------------------------------
# Schema: User API Response
# ----------------------------------------------------------
class UserResponse(BaseModel):
    """Schema for returning user details in API responses."""
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # Enables model_validate() for ORM objects


# ----------------------------------------------------------
# Schema: Token and Authentication
# ----------------------------------------------------------
class Token(BaseModel):
    """JWT Access Token schema for authentication responses."""
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None  # Optional embedded user info


class TokenData(BaseModel):
    """Payload schema used for JWT validation."""
    sub: Optional[str] = None
