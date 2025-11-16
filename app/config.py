# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/13/2025
# Assignment-10: Application Configuration Module
# File: app/config.py
# ----------------------------------------------------------
# Description:
# Centralized configuration system for database URLs, JWT
# authentication settings, and environment-mode detection.
# Provides explicit helper utilities for testability:
#   • reload_settings() – recreate global settings after env change
#   • get_environment_mode() – return readable environment text
# These utilities ensure full coverage without side effects.
# ----------------------------------------------------------

import os
from pydantic_settings import BaseSettings


# ----------------------------------------------------------
# Settings Class
# ----------------------------------------------------------
class Settings(BaseSettings):
    """Main configuration class used across the FastAPI app."""

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    # JWT / Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_key_123")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    )

    # Application Environment
    ENV: str = os.getenv("ENV", "development")

    # ----------------------------
    # Environment Helper Properties
    # ----------------------------
    @property
    def is_dev(self) -> bool:
        return self.ENV.lower() == "development"

    @property
    def is_prod(self) -> bool:
        return self.ENV.lower() == "production"

    @property
    def is_test(self) -> bool:
        return self.ENV.lower() == "testing"

    # ----------------------------
    # Pydantic v2 config
    # ----------------------------
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# ----------------------------------------------------------
# Global settings instance
# ----------------------------------------------------------
settings = Settings()


# ----------------------------------------------------------
# TEST HOOK: Reload settings instance
# ----------------------------------------------------------
def reload_settings() -> Settings:
    """
    Recreate the global settings instance after environment
    variables change. Required by test_reload_updates_values().
    """
    global settings
    settings = Settings()
    return settings


# ----------------------------------------------------------
# TEST HOOK: Convert ENV → readable mode label
# ----------------------------------------------------------
def get_environment_mode(env: str) -> str:
    """
    Convert environment name into a readable text label.

    Expected:
      development  → "development mode"
      production   → "production mode"
      testing      → "testing mode"
      anything else → "Unknown environment"
    """
    env = (env or "").lower()

    if env == "development":
        return "development mode"
    elif env == "production":
        return "production mode"
    elif env == "testing":
        return "testing mode"
    else:
        return "Unknown environment"
