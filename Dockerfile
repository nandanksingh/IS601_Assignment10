# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/05/2025
# Assignment-10: Secure User Model, Pydantic Validation, and Docker Testing
# File: Dockerfile
# ----------------------------------------------------------
# Description:
# Production-grade Dockerfile for FastAPI + PostgreSQL + pgAdmin setup.
# Includes security best practices, non-root user execution,
# and integrated health checks for CI/CD and Docker Compose testing.
# ----------------------------------------------------------

# ----------------------------------------------------------
# Base Image
# ----------------------------------------------------------
FROM python:3.12-slim

# ----------------------------------------------------------
# Environment Variables
# ----------------------------------------------------------
# - PYTHONDONTWRITEBYTECODE: Prevents creation of .pyc files
# - PYTHONUNBUFFERED: Ensures real-time log output (no buffering)
# - PATH: Adds local bin path for installed packages
# ----------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
   PYTHONUNBUFFERED=1 \
   PATH="/home/appuser/.local/bin:$PATH"

WORKDIR /app

# ----------------------------------------------------------
# System Dependencies
# ----------------------------------------------------------
# - build-essential, libpq-dev: required for psycopg2 / SQLAlchemy
# - curl: used for health checks
# ----------------------------------------------------------
RUN apt-get update && \
   apt-get install -y --no-install-recommends \
   build-essential \
   libpq-dev \
   curl && \
   rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------
# Create Secure Non-root User
# ----------------------------------------------------------
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# ----------------------------------------------------------
# Install Python Dependencies
# ----------------------------------------------------------
# Copy requirements first for caching efficiency (Docker layer optimization)
# ----------------------------------------------------------
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
   pip install --no-cache-dir -r requirements.txt

# ----------------------------------------------------------
# Copy Application Code
# ----------------------------------------------------------
COPY . .

# ----------------------------------------------------------
# Set Permissions and Switch User
# ----------------------------------------------------------
RUN chown -R appuser:appgroup /app
USER appuser

# ----------------------------------------------------------
# Expose Port & Healthcheck
# ----------------------------------------------------------
# Expose the default FastAPI port and verify app availability via curl
# ----------------------------------------------------------
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
   CMD curl -f http://localhost:8000/health || exit 1

# ----------------------------------------------------------
# Default Command
# ----------------------------------------------------------
# Run FastAPI using Uvicorn with optimal concurrency for Docker
# ----------------------------------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
