# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/16/2025
# Assignment-10: Secure User Model (Security & JWT Utilities)
# File: app/auth/security.py
# ----------------------------------------------------------


import logging
from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from app.config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ----------------------------------------------------------
# PASSWORD HASHING
# ----------------------------------------------------------
def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    if not isinstance(password, str) or not password:
        logger.error("Invalid password input for hashing.")
        raise ValueError("Password must be a non-empty string.")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Safely verify passwords without raising."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        logger.warning("Password verification failed due to empty input.")
        return False


# ----------------------------------------------------------
# JWT CREATION
# ----------------------------------------------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT token. Tests require failing branch → RuntimeError('JWT creation failed')."""
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ))
        to_encode.update({"exp": expire})

        token = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        logger.info("JWT access token created successfully.")
        return token

    except Exception as e:
        logger.error(f"Token creation failed: {e}")
        raise RuntimeError("JWT creation failed") from e
        # ^ EXACT string test expects


# ----------------------------------------------------------
# JWT DECODING
# ----------------------------------------------------------
def decode_access_token(token: str) -> dict:
    """
    Decode JWT token.

    Tests expect:
      • expired token → RuntimeError("Invalid or expired token")
      • invalid token → RuntimeError("Invalid or expired token")
      • unexpected decode error → RuntimeError("Token decode failure")
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload

    except ExpiredSignatureError as e:
        logger.warning(f"Invalid or expired token: {e}")
        raise RuntimeError("Invalid or expired token") from e

    except JWTError as e:
        logger.warning(f"Invalid or expired token: {e}")
        raise RuntimeError("Invalid or expired token") from e

    except Exception as e:
        logger.error(f"Unexpected token decode error: {e}")
        raise RuntimeError("Token decode failure") from e
        # ^ EXACT message test expects
