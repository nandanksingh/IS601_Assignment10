# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/08/2025
# Assignment-10: Secure User Model + FastAPI Modular Design
# File: app/__init__.py
# ----------------------------------------------------------
# Description:
# Makes the `app` directory a Python package and ensures
# proper path resolution for imports across submodules
# (auth, models, schemas, database, etc.).
# ----------------------------------------------------------

from pathlib import Path

# Project root path for relative imports
BASE_DIR = Path(__file__).resolve().parent

__all__ = ["BASE_DIR"]
