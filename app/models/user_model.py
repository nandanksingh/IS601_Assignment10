# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/09/2025
# Assignment-10: Secure User Model (SQLAlchemy + Schema Integration)
# File: app/models/user_model.py
# ----------------------------------------------------------
# Description:
# Defines the SQLAlchemy User model used in the FastAPI app.
# Provides methods for password hashing, verification, schema
# conversion, and readable model representation.
# ----------------------------------------------------------

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, func, UniqueConstraint
from app.schemas.user_schema import UserResponse
from app.auth.security import hash_password, verify_password
from app.database.dbase import Base


# ----------------------------------------------------------
# User Model Definition
# ----------------------------------------------------------
class User(Base):
    """Represents a user record in the database."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("username", name="uq_user_username"),
        UniqueConstraint("email", name="uq_user_email"),
    )

    # ------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------
    def set_password(self, password: str):
        """Hashes and sets the user's password securely."""
        self.password_hash = hash_password(password)

    def verify_password(self, password: str) -> bool:
        """Verifies that a plain-text password matches the stored hash."""
        return verify_password(password, self.password_hash)

    def to_read_schema(self) -> UserResponse:
        """Converts model instance to a Pydantic response schema."""
        return UserResponse(
            id=self.id,
            username=self.username,
            email=self.email,
            is_active=True,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __repr__(self) -> str:
        """Readable representation for debugging and logging."""
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"
