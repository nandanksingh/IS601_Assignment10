# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/05/2025
# Assignment-10: Secure User Model, Pydantic Validation, and Docker Testing
# File: main.py
# ----------------------------------------------------------
# Description:
# FastAPI entry point for the Calculator API.
# Implements arithmetic endpoints (Add, Subtract, Multiply, Divide)
# with full Pydantic validation, structured logging, and custom
# exception handling for API and validation errors.
#
# Serves the modern HTML front-end via Jinja2 templates.
# Designed for containerized execution with Docker Compose.
# ----------------------------------------------------------

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator
from app.operations import add, subtract, multiply, divide  # ← Updated import path
import uvicorn
import logging

# ----------------------------------------------------------
# Application & Logging Configuration
# ----------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="FastAPI Calculator", version="1.0")

# Directory for HTML templates
templates = Jinja2Templates(directory="templates")


# ----------------------------------------------------------
# Pydantic Models for Request & Response Validation
# ----------------------------------------------------------
class OperationRequest(BaseModel):
    """Schema for arithmetic operation requests."""
    a: float = Field(..., description="The first number to operate on")
    b: float = Field(..., description="The second number to operate on")

    @field_validator("a", "b")
    def validate_numbers(cls, value):
        """Ensure both operands are valid numeric types."""
        if not isinstance(value, (int, float)):
            raise ValueError("Both a and b must be numbers.")
        return value


class OperationResponse(BaseModel):
    """Schema for successful operation responses."""
    result: float = Field(..., description="The computed result of the operation")


class ErrorResponse(BaseModel):
    """Schema for standardized error responses."""
    error: str = Field(..., description="Description of the error encountered")


# ----------------------------------------------------------
# Exception Handlers
# ----------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPException and return JSON-formatted error."""
    logger.error(f"HTTPException at {request.url.path}: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle input validation errors and return detailed messages."""
    errors = "; ".join(f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors())
    logger.warning(f"ValidationError on {request.url.path}: {errors}")
    return JSONResponse(status_code=400, content={"error": f"Invalid or missing numeric input: {errors}"})


# ----------------------------------------------------------
# Route: Home Page
# ----------------------------------------------------------
@app.get("/")
async def read_root(request: Request):
    """Render the calculator web UI (index.html)."""
    return templates.TemplateResponse("index.html", {"request": request})


# ----------------------------------------------------------
# Routes: Arithmetic Operations
# ----------------------------------------------------------
@app.post("/add", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def add_route(operation: OperationRequest):
    """Perform addition."""
    try:
        result = add(operation.a, operation.b)
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Addition failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/subtract", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def subtract_route(operation: OperationRequest):
    """Perform subtraction."""
    try:
        result = subtract(operation.a, operation.b)
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Subtraction failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/multiply", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def multiply_route(operation: OperationRequest):
    """Perform multiplication."""
    try:
        result = multiply(operation.a, operation.b)
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Multiplication failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/divide", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def divide_route(operation: OperationRequest):
    """Perform division, handling division-by-zero gracefully."""
    try:
        result = divide(operation.a, operation.b)
        return OperationResponse(result=result)
    except ValueError as e:
        logger.warning(f"Division error (user input): {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected division error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ----------------------------------------------------------
# Health check endpoint
# ----------------------------------------------------------
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker."""
    return {"status": "healthy"}


# ----------------------------------------------------------
# Application Entry Point
# ----------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
