# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/09/2025
# Assignment 10: Secure User Model (Pydantic Validation + JWT)
# File: app/schemas/user_schema.py
# ----------------------------------------------------------
# Description:
# This module defines Pydantic schemas used for validating
# and serializing user-related data within the FastAPI app.
# It includes user creation, login, response, and token models.
# Each schema ensures secure and structured communication
# between the API, database, and authentication system.
# ----------------------------------------------------------

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ----------------------------------------------------------
# Shared Base Schema
# ----------------------------------------------------------
class UserBase(BaseModel):
    """
    Defines the base attributes common to all user schemas.
    Provides ORM compatibility and reusable validation logic.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username for the user"
    )
    email: EmailStr = Field(
        ...,
        description="User's valid email address"
    )
    is_active: bool = True

    # Enables ORM mode for SQLAlchemy integration
    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------
# Schema: User Creation
# ----------------------------------------------------------
class UserCreate(UserBase):
    """
    Used when creating a new user account.
    Includes a plain-text password that will be hashed before saving.
    """

    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Plain-text password (will be securely hashed)"
    )


# ----------------------------------------------------------
# Schema: User Login
# ----------------------------------------------------------
class UserLogin(BaseModel):
    """
    Used when authenticating an existing user.
    Accepts either a username or an email, along with the password.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username or email used for login"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Plain-text password used for authentication"
    )


# ----------------------------------------------------------
# Schema: User Read (for ORM model serialization)
# ----------------------------------------------------------
class UserRead(UserBase):
    """
    Returned after creating or fetching a user from the database.
    This schema includes the user's ID and timestamps.
    """

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# ----------------------------------------------------------
# Schema: User Response
# ----------------------------------------------------------
class UserResponse(BaseModel):
    """
    Schema for safely returning user information in API responses.
    Excludes password or other sensitive details.
    """

    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------------
# Schema: JWT Token
# ----------------------------------------------------------
class Token(BaseModel):
    """
    Represents the structure of a JWT access token.
    Includes token type and optionally user details.
    """

    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None


# ----------------------------------------------------------
# Schema: Token Payload
# ----------------------------------------------------------
class TokenData(BaseModel):
    """
    Represents the payload extracted from a decoded JWT.
    Contains only the user ID or subject field.
    """

    sub: Optional[str] = None
