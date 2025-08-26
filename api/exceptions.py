"""
Custom exception handlers for the API layer.
"""

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request
import sqlite3


class DecisionTreeAPIException(HTTPException):
    """Base exception for API errors."""
    
    def __init__(self, status_code: int, detail: str, code: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code


class ValidationError(DecisionTreeAPIException):
    """Raised when request validation fails."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            code="VALIDATION_ERROR"
        )


class ConflictError(DecisionTreeAPIException):
    """Raised when there's a conflict (e.g., duplicate slot)."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            code="CONFLICT_ERROR"
        )


class TooManyChildrenError(DecisionTreeAPIException):
    """Raised when trying to add more than 5 children."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            code="TOO_MANY_CHILDREN"
        )


def handle_value_error(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ValueError exceptions from domain logic."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation Error",
            "detail": str(exc),
            "code": "VALIDATION_ERROR"
        }
    )


def handle_integrity_error(request: Request, exc: sqlite3.IntegrityError) -> JSONResponse:
    """Handle SQLite IntegrityError exceptions."""
    error_detail = str(exc)
    
    # Map specific integrity errors to appropriate status codes
    if "UNIQUE constraint failed" in error_detail:
        status_code = status.HTTP_409_CONFLICT
        error_code = "DUPLICATE_ENTRY"
    elif "FOREIGN KEY constraint failed" in error_detail:
        status_code = status.HTTP_400_BAD_REQUEST
        error_code = "FOREIGN_KEY_VIOLATION"
    elif "CHECK constraint failed" in error_detail:
        status_code = status.HTTP_400_BAD_REQUEST
        error_code = "CONSTRAINT_VIOLATION"
    else:
        status_code = status.HTTP_409_CONFLICT
        error_code = "INTEGRITY_ERROR"
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": "Database Integrity Error",
            "detail": error_detail,
            "code": error_code
        }
    )


def handle_decision_tree_api_exception(request: Request, exc: DecisionTreeAPIException) -> JSONResponse:
    """Handle custom API exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "code": exc.code
        }
    )
