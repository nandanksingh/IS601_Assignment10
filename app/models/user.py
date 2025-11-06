# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/05/2025
# Assignment-10: Secure User Model (Pydantic Validation + Database Testing)
# File: app/models/user.py
# ----------------------------------------------------------
# Description:
# This module defines the SQLAlchemy User model used for secure
# authentication in the FastAPI application. It integrates:
#   • Password hashing and verification
#   • Pydantic-based validation (schema ↔ model conversion)
#   • JWT token generation and verification
#
# The model is designed for maintainability, testing, and
# containerized (Docker) deployment as part of Assignment-10.
# ----------------------------------------------------------

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from app.database import Base
from app.security import hash_password, verify_password
from app.schemas.user import UserCreate, UserRead


# ----------------------------------------------------------
# JWT Configuration (to be moved to .env or config module)
# ----------------------------------------------------------
SECRET_KEY = "super_secret_key_123"           # Example key for local use
ALGORITHM = "HS256"                           # Signing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30              # Token validity (minutes)


# ----------------------------------------------------------
# SQLAlchemy ORM Model
# ----------------------------------------------------------
class User(Base):
    """
    Represents an application user in the database.

    Attributes:
        id (int): Primary key identifier.
        username (str): Unique username for login.
        email (str): Unique email address.
        password_hash (str): Securely hashed user password.
        is_active (bool): Indicates if the account is active.
        created_at (datetime): Record creation timestamp.
        updated_at (datetime): Auto-updated modification timestamp.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ------------------------------------------------------
    # Password Management
    # ------------------------------------------------------
    def set_password(self, plain_password: str) -> None:
        """
        Hashes a plain-text password and stores it in the model.

        Args:
            plain_password (str): Raw user password from input.
        """
        self.password_hash = hash_password(plain_password)

    def check_password(self, plain_password: str) -> bool:
        """
        Compares a plain-text password with the stored hash.

        Returns:
            bool: True if password matches, False otherwise.
        """
        return verify_password(plain_password, self.password_hash)

    # ------------------------------------------------------
    # Pydantic Schema Integration
    # ------------------------------------------------------
    @classmethod
    def from_schema(cls, schema: UserCreate) -> "User":
        """
        Creates a new User ORM instance from validated Pydantic input.

        Args:
            schema (UserCreate): Pydantic model containing validated user data.

        Returns:
            User: SQLAlchemy ORM instance ready to be added to the DB session.
        """
        user = cls(
            username=schema.username,
            email=schema.email,
            is_active=True
        )
        user.set_password(schema.password)
        return user

    def to_schema(self) -> UserRead:
        """
        Converts this ORM instance into a Pydantic response schema.

        Returns:
            UserRead: Pydantic object representing safe public data.
        """
        return UserRead.model_validate(self)

    # ------------------------------------------------------
    # JWT Token Management
    # ------------------------------------------------------
    @staticmethod
    def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
        """
        Generates a signed JWT access token for a given user ID.

        Args:
            user_id (int): The user’s unique identifier.
            expires_delta (timedelta, optional): Custom expiration time.

        Returns:
            str: Encoded JWT token string.
        """
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode = {"sub": str(user_id), "exp": expire}
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[int]:
        """
        Validates a JWT token and extracts the embedded user ID.

        Args:
            token (str): Encoded JWT token from the client.

        Returns:
            Optional[int]: User ID if the token is valid, otherwise None.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return int(payload.get("sub")) if payload.get("sub") else None
        except JWTError:
            return None

    # ------------------------------------------------------
    # Representation Helper
    # ------------------------------------------------------
    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return (
            f"<User(username='{self.username}', "
            f"email='{self.email}', active={self.is_active})>"
        )
