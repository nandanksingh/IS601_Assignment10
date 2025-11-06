# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/05/2025
# Assignment-10: Secure User Model (Pydantic Validation + Database Testing)
# File: app/database/dbase.py
# ----------------------------------------------------------
# Description:
# Centralized database configuration and management module
# for the FastAPI application. Handles:
#   • SQLAlchemy engine and session setup
#   • Declarative Base for ORM models
#   • Database initialization and teardown
#   • FastAPI dependency for DB sessions
#
# This design ensures clean integration with Docker,
# Pydantic configuration (from app.config), and CI/CD tests.
# ----------------------------------------------------------

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from app.config import settings


# ----------------------------------------------------------
# Engine Factory
# ----------------------------------------------------------
def get_engine(database_url: str = settings.DATABASE_URL):
    """
    Create and return a SQLAlchemy Engine bound to the configured database.
    Echo is enabled for transparency during development and testing.
    """
    try:
        engine = create_engine(database_url, echo=True, future=True)
        return engine
    except SQLAlchemyError as e:
        print(f"[DB ERROR] Unable to create engine: {e}")
        raise


# ----------------------------------------------------------
# Global Engine, Session Factory, and Base Declaration
# ----------------------------------------------------------
engine = get_engine()
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base = declarative_base()


# ----------------------------------------------------------
# Dependency: Provide Database Session
# ----------------------------------------------------------
def get_db():
    """
    Dependency function for FastAPI routes.
    Yields a transactional SQLAlchemy session and ensures closure after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------------------------------------
# Utility Functions: Initialize and Drop Tables
# ----------------------------------------------------------
def init_db():
    """
    Create all database tables defined in SQLAlchemy models.
    Should be called at app startup or before running integration tests.
    """
    from app.models.user import Base  # lazy import to avoid circular dependency
    Base.metadata.create_all(bind=engine)
    print("[DB INIT] Database tables created successfully.")


def drop_db():
    """
    Drop all database tables.
    Use carefully — typically only for test cleanup or reinitialization.
    """
    from app.models.user import Base
    Base.metadata.drop_all(bind=engine)
    print("[DB DROP] Database tables dropped successfully.")


# ----------------------------------------------------------
# CLI Execution
# ----------------------------------------------------------
if __name__ == "__main__":
    init_db()  # pragma: no cover
