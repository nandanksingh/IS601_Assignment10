# Author: Nandan Kumar
# Date: 11/09/2025
# Assignment 10: Secure User Model (OAuth2 + JWT Integration)
# File: app/auth/dependencies.py
# ----------------------------------------------------------
# Description:
# This module provides authentication dependencies and utilities
# for the FastAPI application. It handles the creation and validation
# of JSON Web Tokens (JWT), manages database sessions per request,
# and defines dependencies for retrieving the current authenticated user.
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
from app.schemas.user_schema import UserResponse

# ----------------------------------------------------------
# JWT Configuration
# ----------------------------------------------------------
SECRET_KEY = "super_secret_key_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 password flow for FastAPI authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ----------------------------------------------------------
# Database Session Dependency
# Database dependency used by FastAPI routes
# ----------------------------------------------------------
from app.database.dbase import get_session

def get_db():
    db = get_session()

    # Add attribute so tests can check it
    db.closed = False

    try:
        yield db
    finally:
        db.close()
        db.closed = True


# ----------------------------------------------------------
# JWT Token Utilities
# ----------------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token with an expiration time.

    Args:
        data (dict): The data payload to include in the token.
        expires_delta (timedelta, optional): Custom expiration duration.

    Returns:
        str: A signed JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Args:
        token (str): The JWT token to be verified.

    Returns:
        dict: The decoded payload if the token is valid.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
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
    Authenticate a user using their username or email and password.

    Args:
        db (Session): The active SQLAlchemy session.
        username_or_email (str): The username or email of the user.
        password (str): The plain-text password.

    Returns:
        Optional[User]: The user object if authentication is successful, otherwise None.
    """
    user = db.query(User).filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()

    if not user or not verify_password(password, user.password_hash):
        return None

    return user


# ----------------------------------------------------------
# Retrieve Current Authenticated User
# ----------------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Extract and return the current user from a valid JWT token.

    Args:
        token (str): The bearer token from the Authorization header.
        db (Session): The database session.

    Returns:
        UserResponse: A Pydantic schema representing the authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.
    """
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
