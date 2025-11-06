# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/05/2025
# Assignment-10: Secure User Model + OAuth2 + JWT Integration
# File: app/auth/dependencies.py
# ----------------------------------------------------------
# Description:
# Implements authentication dependencies for FastAPI routes
# using OAuth2PasswordBearer and JWT. Built on top of secure
# password hashing (bcrypt) and SQLAlchemy ORM models.
# Tokens are generated via python-jose and validated using
# the OAuth2 bearer token scheme.
# ----------------------------------------------------------

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database.dbase import SessionLocal
from app.models.user import User
from app import schemas
from app.config import settings


# ----------------------------------------------------------
# OAuth2 Configuration
# ----------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ----------------------------------------------------------
# Database Dependency
# ----------------------------------------------------------
def get_db():
    """Provide a SQLAlchemy session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------------------------------------
# Token Generation & Verification
# ----------------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT token with an expiration time."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_access_token(token: str) -> dict:
    """Verify and decode a JWT access token."""
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
# Authenticate User (for login)
# ----------------------------------------------------------
def authenticate_user(db: Session, username_or_email: str, password: str):
    """Placeholder authentication logic."""
    # TODO: Replace with actual user verification using bcrypt + SQLAlchemy
    raise NotImplementedError("User authentication not implemented yet")


# ----------------------------------------------------------
# Get Current User (via OAuth2 Bearer Token)
# ----------------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> schemas.UserRead:
    """Extract user information from a valid JWT token."""
    payload = verify_access_token(token)
    user_id: Optional[str] = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return schemas.UserRead.model_validate(user)
