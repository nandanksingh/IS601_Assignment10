# ----------------------------------------------------------
# Author: Nandan Kumar
# Date: 11/09/2025
# Assignment-10: Secure User Model, Pydantic Validation, and Docker Testing
# File: main.py
# ----------------------------------------------------------
# Description:
# Entry point for the FastAPI Calculator application.
# Implements secure arithmetic endpoints (Add, Subtract, Multiply, Divide)
# with full Pydantic validation, structured logging, and robust
# exception handling for validation and runtime errors.
#
# Includes /health endpoint for Docker and GitHub Actions testing.
# Serves HTML front-end via Jinja2 templates.
# ----------------------------------------------------------

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator
from app.operations import add, subtract, multiply, divide
import uvicorn
import logging
import os

# ----------------------------------------------------------
# Logging Configuration
# ----------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("calculator")

# ----------------------------------------------------------
# FastAPI Application Setup
# ----------------------------------------------------------
app = FastAPI(
    title="FastAPI Calculator",
    version="1.0.0",
    description="Secure, container-ready FastAPI calculator with Pydantic validation.",
)

templates = Jinja2Templates(directory="templates")

# ----------------------------------------------------------
# Pydantic Schemas
# ----------------------------------------------------------
class OperationRequest(BaseModel):
    """Validate arithmetic input payloads."""
    a: float = Field(..., description="First number")
    b: float = Field(..., description="Second number")

    @field_validator("a", "b")
    @classmethod
    def validate_numbers(cls, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Both a and b must be numbers.")
        return value


class OperationResponse(BaseModel):
    """Response schema for valid arithmetic results."""
    result: float = Field(..., description="Computed result")


class ErrorResponse(BaseModel):
    """Response schema for API error messages."""
    error: str = Field(..., description="Error details")

# ----------------------------------------------------------
# Global Exception Handlers
# ----------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"[HTTP ERROR] {request.url.path}: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = "; ".join(f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors())
    logger.warning(f"[VALIDATION ERROR] {request.url.path}: {errors}")
    return JSONResponse(status_code=400, content={"error": f"Invalid input: {errors}"})

# ----------------------------------------------------------
# Routes
# ----------------------------------------------------------
@app.get("/", tags=["UI"])
async def read_root(request: Request):
    """Serve the calculator web UI."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/add", response_model=OperationResponse, responses={400: {"model": ErrorResponse}}, tags=["Arithmetic"])
async def add_route(operation: OperationRequest):
    """Add two numbers."""
    try:
        result = add(operation.a, operation.b)
        logger.info(f"Add operation: {operation.a} + {operation.b} = {result}")
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Addition failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/subtract", response_model=OperationResponse, responses={400: {"model": ErrorResponse}}, tags=["Arithmetic"])
async def subtract_route(operation: OperationRequest):
    """Subtract two numbers."""
    try:
        result = subtract(operation.a, operation.b)
        logger.info(f"Subtract operation: {operation.a} - {operation.b} = {result}")
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Subtraction failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/multiply", response_model=OperationResponse, responses={400: {"model": ErrorResponse}}, tags=["Arithmetic"])
async def multiply_route(operation: OperationRequest):
    """Multiply two numbers."""
    try:
        result = multiply(operation.a, operation.b)
        logger.info(f"Multiply operation: {operation.a} * {operation.b} = {result}")
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Multiplication failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/divide", response_model=OperationResponse, responses={400: {"model": ErrorResponse}}, tags=["Arithmetic"])
async def divide_route(operation: OperationRequest):
    """Divide two numbers with zero-division handling."""
    try:
        result = divide(operation.a, operation.b)
        logger.info(f"Divide operation: {operation.a} / {operation.b} = {result}")
        return OperationResponse(result=result)
    except ValueError as e:
        logger.warning(f"Division error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected division error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/health", response_model=dict, tags=["System"])
async def health_check():
    """Health endpoint used for Docker and CI/CD monitoring."""
    logger.info("Health check endpoint hit — returning healthy status.")
    return {"status": "healthy"}

# ----------------------------------------------------------
# Entrypoint
# ----------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
