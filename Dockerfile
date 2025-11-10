# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment-10: Secure User Model, Pydantic Validation, and Docker Testing
# File: Dockerfile
# ----------------------------------------------------------
# Description:
# Production-ready Dockerfile for FastAPI + PostgreSQL (or SQLite fallback).
# Supports multi-environment builds (local, CI, or Docker Compose).
# Features:
#   • Non-root user
#   • Layer caching optimization
#   • Health check for container monitoring
#   • Uvicorn worker configuration for concurrency
# ----------------------------------------------------------

# ----------------------------------------------------------
# 1. Base Image
# ----------------------------------------------------------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
   PYTHONUNBUFFERED=1 \
   PIP_NO_CACHE_DIR=1 \
   PATH="/home/appuser/.local/bin:$PATH"

WORKDIR /app

# ----------------------------------------------------------
# 2. System Dependencies
# ----------------------------------------------------------
RUN apt-get update && \
   apt-get install -y --no-install-recommends \
   build-essential \
   libpq-dev \
   curl && \
   rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------
# 3. Create Secure Non-root User
# ----------------------------------------------------------
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# ----------------------------------------------------------
# 4. Install Python Dependencies
# ----------------------------------------------------------
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel && \
   pip install --no-cache-dir -r requirements.txt

# ----------------------------------------------------------
# 5. Copy Application Source Code
# ----------------------------------------------------------
COPY . .

# ----------------------------------------------------------
# 6. Set Permissions
# ----------------------------------------------------------
RUN chown -R appuser:appgroup /app
USER appuser

# ----------------------------------------------------------
# 7. Expose Port & Healthcheck
# ----------------------------------------------------------
EXPOSE 8000

# Healthcheck uses "/health" endpoint
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
   CMD curl -f http://localhost:8000/health || exit 1

# ----------------------------------------------------------
# 8. Default Command
# ----------------------------------------------------------
# main.py is in project root, and app entry = main:app
# ----------------------------------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
