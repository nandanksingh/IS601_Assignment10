# Author: Nandan Kumar
# Date: 11/09/2025
# Assignment 10: Secure User Model (Schema Initialization)
# File: app/schemas/__init__.py
# ----------------------------------------------------------
# Description:
# This module initializes the schema package and provides
# a single access point for all user-related Pydantic models.
# Importing from this module ensures consistency across the
# application and simplifies schema management for routes,
# authentication, and testing.
# ----------------------------------------------------------

from .base import UserBase, PasswordMixin, UserCreate, UserLogin
from .user_schema import UserResponse, Token, TokenData

# ----------------------------------------------------------
# Exposed Schema Objects
# ----------------------------------------------------------
# These are made available for other modules such as routes,
# authentication utilities, and testing scripts.
# They cover user creation, authentication, and response models.
# ----------------------------------------------------------
__all__ = [
    "UserBase",
    "PasswordMixin",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenData",
]
