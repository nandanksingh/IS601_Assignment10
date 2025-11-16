# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment 10: Secure User Model + FastAPI Modular Design
# File: app/__init__.py
# ----------------------------------------------------------
# Description:
# Marks the "app" directory as a Python package and ensures
# consistent path resolution for imports across all submodules
# (auth, models, schemas, database, operations, etc.).
# ----------------------------------------------------------

from pathlib import Path

# Define base directory path for use across the project
BASE_DIR = Path(__file__).resolve().parent

__all__ = ["BASE_DIR"]
