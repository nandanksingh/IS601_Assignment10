# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment-10: Secure User Model (Pydantic Validation + JWT + Database Testing)
# File: app/models/user_model.py
# ----------------------------------------------------------
# Description:
# Defines the SQLAlchemy User ORM model for FastAPI.
# Integrates:
#   • Password hashing and verification
#   • JWT token creation and decoding
#   • Conversion to Pydantic response schema
#   • Database timestamp management
# ----------------------------------------------------------

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from sqlalchemy import Column, Integer, String, DateTime, Boolean, func

from app.database.dbase import Base
from app.auth.security import hash_password, verify_password
from app.schemas.base import UserCreate
from app.schemas.user_schema import UserResponse 

# ----------------------------------------------------------
# JWT Configuration (temporary local setup)
# ----------------------------------------------------------
SECRET_KEY = "super_secret_key_123"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30


class User(Base):
    """SQLAlchemy User model with password hashing and token methods."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ------------------------------------------------------
    # Password Management
    # ------------------------------------------------------
    def set_password(self, password: str):
        """Hashes and stores the user password."""
        self.password_hash = hash_password(password)

    def verify_password(self, password: str) -> bool:
        """Verifies the provided password against stored hash."""
        return verify_password(password, self.password_hash)

    # ------------------------------------------------------
    # JWT Token Methods
    # ------------------------------------------------------
    @staticmethod
    def create_token(user_id: int) -> str:
        """Generate JWT token for user authentication."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(user_id), "exp": expire}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[int]:
        """Decode token and return user_id if valid."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return int(payload.get("sub"))
        except (JWTError, ValueError):
            return None

    # ------------------------------------------------------
    # Representation and Serialization
    # ------------------------------------------------------
    def to_read_schema(self) -> UserResponse:
        """Convert SQLAlchemy model to Pydantic read schema."""
        return UserResponse(
            id=self.id,
            username=self.username,
            email=self.email,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __repr__(self):
        """Readable string representation for debugging."""
        return f"<User username='{self.username}', email='{self.email}'>"
