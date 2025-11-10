# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment-10: Secure User Model (Pydantic Validation + Docker Testing)
# File: app/config.py
# ----------------------------------------------------------
# Description:
# Centralized configuration management for the FastAPI application.
# Loads environment variables (database URL, JWT secrets, etc.)
# using Pydantic’s BaseSettings for secure, validated settings.
# Supports multi-environment setups (development, production, testing)
# and integrates seamlessly with Docker and CI/CD pipelines.
# ----------------------------------------------------------

from pydantic_settings import BaseSettings


# ----------------------------------------------------------
# Application Settings
# ----------------------------------------------------------
class Settings(BaseSettings):
    """
    Global configuration class for the FastAPI app.
    Reads variables from environment or .env file and provides
    convenient access for database, JWT, and environment settings.
    """

    # ------------------------------------------------------
    # Database Configuration
    # ------------------------------------------------------
    DATABASE_URL: str = "sqlite:///./test.db"  
    # Example for Docker/Postgres:
    # DATABASE_URL="postgresql://postgres:postgres@db:5432/fastapi_db"

    # ------------------------------------------------------
    # JWT / Security Configuration
    # ------------------------------------------------------
    SECRET_KEY: str = "super_secret_key_123"   # override via .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ------------------------------------------------------
    # Environment Configuration
    # ------------------------------------------------------
    ENV: str = "development"  # options: development, production, testing

    # ------------------------------------------------------
    # Utility Properties
    # ------------------------------------------------------
    @property
    def is_dev(self) -> bool:
        """True if running in development mode."""
        return self.ENV.lower() == "development"

    @property
    def is_prod(self) -> bool:
        """True if running in production mode."""
        return self.ENV.lower() == "production"

    @property
    def is_test(self) -> bool:
        """True if running in testing mode."""
        return self.ENV.lower() == "testing"

        # ------------------------------------------------------
    # Utility: Reload settings dynamically (for tests)
    # ------------------------------------------------------
    def reload(self):
        """Reload settings from current environment (for pytest monkeypatch)."""
        updated = self.__class__()  # rebuild from env
        for field, value in updated.__dict__.items():
            setattr(self, field, value)


    # ------------------------------------------------------
    # Pydantic Configuration (v2.x compatible)
    # ------------------------------------------------------
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# ----------------------------------------------------------
# Instantiate Global Settings Object
# ----------------------------------------------------------
settings = Settings()
