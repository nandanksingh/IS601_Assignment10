# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment-10: Secure User Model + OAuth2 + JWT Integration
# File: app/auth/dependencies.py
# ----------------------------------------------------------
# Description:
# Authentication utilities and dependencies for FastAPI.
# Includes:
#   • JWT token creation and validation
#   • OAuth2 Bearer token authentication
#   • Current user dependency for protected routes
#   • Database session management for request scope
# ----------------------------------------------------------

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database.dbase import SessionLocal
from app.models.user_model import User
from app.auth.security import hash_password, verify_password
from app.config import settings
from app.schemas.user_schema import UserResponse

# ----------------------------------------------------------
# OAuth2 and JWT Configuration
# ----------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


# ----------------------------------------------------------
# Database Session Dependency
# ----------------------------------------------------------
def get_db():  # pragma: no cover
    """Provide a SQLAlchemy session for request scope."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------------------------------------
# JWT Token Utilities
# ----------------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT access token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ----------------------------------------------------------
# User Authentication
# ----------------------------------------------------------
def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by username/email and password.
    Returns the User ORM object if credentials are valid.
    """
    user = db.query(User).filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()

    if not user or not verify_password(password, user.password_hash):
        return None

    return user


# ----------------------------------------------------------
# Get Current Authenticated User
# ----------------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Extract and return the current user from a valid JWT token."""
    payload = verify_access_token(token)
    user_id: Optional[str] = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return UserResponse.model_validate(user)
