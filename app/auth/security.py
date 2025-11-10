# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment-10: Secure User Model (Password Hashing + Verification)
# File: app/auth/security.py
# ----------------------------------------------------------
# Description:
# Provides secure password hashing and verification utilities
# for the FastAPI authentication system.
# Built using passlib’s CryptContext with bcrypt.
# ----------------------------------------------------------

from passlib.context import CryptContext

# ----------------------------------------------------------
# Cryptographic Context
# ----------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ----------------------------------------------------------
# Password Utilities
# ----------------------------------------------------------
def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its stored hash."""
    return pwd_context.verify(plain_password, hashed_password)
