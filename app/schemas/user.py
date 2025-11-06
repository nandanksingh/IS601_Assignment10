# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/05/2025
# Assignment-10: Secure User Model (Pydantic Validation + Database Testing)
# File: app/schemas/user.py
# ----------------------------------------------------------
# Description:
# Defines user-related Pydantic schemas for validation,
# API serialization, and JWT token exchange.
# Now upgraded to use UUIDs for unique user identification.
# ----------------------------------------------------------

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.schemas.base import UserBase, UserCreate, UserLogin


# ----------------------------------------------------------
# Schema: UserRead (API-Safe Response)
# ----------------------------------------------------------
class UserRead(UserBase):
    """
    Represents user data returned in API responses.
    Uses UUID for unique, non-sequential identification.
    Excludes password and other sensitive information.
    """
    id: UUID
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "first_name": "Nandan",
                "last_name": "Kumar",
                "username": "nandan123",
                "email": "nandan@example.com",
                "is_active": True,
                "created_at": "2025-11-05T10:00:00Z",
                "updated_at": "2025-11-05T11:00:00Z",
            }
        }
    )


# ----------------------------------------------------------
# Schema: Token (JWT Response)
# ----------------------------------------------------------
class Token(BaseModel):
    """
    Returned after successful authentication.
    Contains a JWT access token and associated user data.
    """
    access_token: str
    token_type: str = "bearer"
    user: UserRead

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "nandan123",
                    "email": "nandan@example.com",
                    "is_active": True,
                },
            }
        }
    )


# ----------------------------------------------------------
# Schema: TokenData (Decoded JWT Payload)
# ----------------------------------------------------------
class TokenData(BaseModel):
    """
    Represents data extracted from a decoded JWT token.
    Used internally to identify the authenticated user.
    """
    user_id: Optional[UUID] = None
