# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/05/2025
# Assignment-10: Secure User Model (Pydantic Validation + Database Testing)
# File: app/config.py
# ----------------------------------------------------------
# Description:
# Centralized configuration management for the FastAPI application.
# Loads environment variables (database URL, JWT secrets, etc.)
# using Pydantic’s BaseSettings for secure and validated settings.
# This allows consistent access across all modules (models, auth, db).
# ----------------------------------------------------------

from pydantic_settings import BaseSettings


# ----------------------------------------------------------
# Application Settings
# ----------------------------------------------------------
class Settings(BaseSettings):
    """
    Application-wide configuration class.
    Reads values from environment variables or a `.env` file.
    Ensures consistent and secure access to environment-level data.
    """

    # ------------------------------------------------------
    # Database Configuration
    # ------------------------------------------------------
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/fastapi_db"

    # ------------------------------------------------------
    # JWT / Security Configuration
    # ------------------------------------------------------
    SECRET_KEY: str = "super_secret_key_123"       # to be overridden in .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30          # default = 30 mins

    # ------------------------------------------------------
    # Environment Configuration
    # ------------------------------------------------------
    ENV: str = "development"                       # or "production", "testing"

    class Config:
        env_file = ".env"                          # auto-load environment variables


# ----------------------------------------------------------
# Instantiate Global Settings Object
# ----------------------------------------------------------
settings = Settings()
