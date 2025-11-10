# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment-10: Secure User Model (Pydantic Validation + JWT + Database Testing)
# File: app/schemas/__init__.py
# ----------------------------------------------------------
# Description:
# Initializes schema package imports for easy access across the app.
# Aggregates all shared and user-related schemas into a single namespace.
# ----------------------------------------------------------

from .base import UserBase, PasswordMixin, UserCreate, UserLogin
from .user_schema import UserResponse, Token, TokenData

__all__ = [
    "UserBase",
    "PasswordMixin",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenData",
]

