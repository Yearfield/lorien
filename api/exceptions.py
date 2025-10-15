"""
Centralized error handling system for the API layer.

Provides:
- Consistent error codes and messages
- Production-safe error responses
- Structured error logging with correlation IDs
- Error tracking and metrics
- Security-conscious error details
"""

import os
import sqlite3
from typing import Any, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from .observability.context import get_context_dict, get_request_id, get_trace_id
from .observability.logging import get_logger
from .observability.metrics import increment_counter


# Error codes registry - centralized and consistent
class ErrorCodes:
    """Centralized registry of all error codes used in the API."""

    # Validation errors (400)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"

    # Authentication errors (401)
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"

    # Authorization errors (403)
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    FORBIDDEN_OPERATION = "FORBIDDEN_OPERATION"

    # Not found errors (404)
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    ENDPOINT_NOT_FOUND = "ENDPOINT_NOT_FOUND"

    # Conflict errors (409)
    CONFLICT_ERROR = "CONFLICT_ERROR"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"
    RESOURCE_EXISTS = "RESOURCE_EXISTS"

    # Business logic errors (422)
    TOO_MANY_CHILDREN = "TOO_MANY_CHILDREN"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    INVALID_STATE_TRANSITION = "INVALID_STATE_TRANSITION"

    # Database errors (409/400)
    DATABASE_ERROR = "DATABASE_ERROR"
    INTEGRITY_ERROR = "INTEGRITY_ERROR"
    FOREIGN_KEY_VIOLATION = "FOREIGN_KEY_VIOLATION"
    CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"

    # Rate limiting (429)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Internal server errors (500)
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"


# Production-safe error messages
class ErrorMessages:
    """Production-safe error messages that don't expose internal details."""

    @staticmethod
    def get_safe_message(code: str, detail: Optional[str] = None) -> str:
        """Get a production-safe error message for the given error code."""
        safe_messages = {
            ErrorCodes.VALIDATION_ERROR: "The request data is invalid",
            ErrorCodes.INVALID_INPUT: "The provided input is not valid",
            ErrorCodes.MISSING_REQUIRED_FIELD: "A required field is missing",
            ErrorCodes.INVALID_FORMAT: "The data format is not supported",
            ErrorCodes.AUTHENTICATION_REQUIRED: "Authentication is required",
            ErrorCodes.INVALID_TOKEN: "The authentication token is invalid",
            ErrorCodes.TOKEN_EXPIRED: "The authentication token has expired",
            ErrorCodes.INSUFFICIENT_PERMISSIONS: "You don't have permission to perform this action",
            ErrorCodes.FORBIDDEN_OPERATION: "This operation is not allowed",
            ErrorCodes.RESOURCE_NOT_FOUND: "The requested resource was not found",
            ErrorCodes.ENDPOINT_NOT_FOUND: "The requested endpoint was not found",
            ErrorCodes.CONFLICT_ERROR: "There was a conflict with the current state",
            ErrorCodes.DUPLICATE_ENTRY: "A resource with this identifier already exists",
            ErrorCodes.RESOURCE_EXISTS: "The resource already exists",
            ErrorCodes.TOO_MANY_CHILDREN: "Cannot add more children to this node",
            ErrorCodes.BUSINESS_RULE_VIOLATION: "The operation violates a business rule",
            ErrorCodes.INVALID_STATE_TRANSITION: "Invalid state transition",
            ErrorCodes.DATABASE_ERROR: "A database error occurred",
            ErrorCodes.INTEGRITY_ERROR: "Database integrity constraint violated",
            ErrorCodes.FOREIGN_KEY_VIOLATION: "Referenced resource does not exist",
            ErrorCodes.CONSTRAINT_VIOLATION: "Data constraint violation",
            ErrorCodes.RATE_LIMIT_EXCEEDED: "Too many requests. Please try again later",
            ErrorCodes.INTERNAL_SERVER_ERROR: "An internal server error occurred",
            ErrorCodes.DATABASE_CONNECTION_ERROR: "Unable to connect to the database",
            ErrorCodes.EXTERNAL_SERVICE_ERROR: "External service is currently unavailable",
        }

        message = safe_messages.get(code, "An error occurred")

        # In development, append the original detail if provided
        if os.getenv("ENVIRONMENT", "development") == "development" and detail:
            message = f"{message}: {detail}"

        return message


class DecisionTreeAPIException(HTTPException):
    """Enhanced base exception for API errors with tracking and logging."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        code: str,
        safe_message: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code
        self.safe_message = safe_message or ErrorMessages.get_safe_message(code, detail)
        self.context = context or {}

        # Log the error with structured data
        self._log_error()

    def _log_error(self):
        """Log the error with structured data and correlation IDs."""
        logger = get_logger(__name__)

        extra_fields = {
            "error": {
                "code": self.code,
                "status_code": self.status_code,
                "detail": self.detail,
                "safe_message": self.safe_message,
                "context": self.context,
            }
        }

        # Include correlation IDs if available
        context_dict = get_context_dict()
        if context_dict.get("request_id"):
            extra_fields["request_id"] = context_dict["request_id"]
        if context_dict.get("trace_id"):
            extra_fields["trace_id"] = context_dict["trace_id"]

        logger.error(
            f"API Error: {self.code} - {self.detail}",
            extra_fields=extra_fields,
        )

        # Track error metrics
        increment_counter(
            "api.errors",
            tags={
                "error_code": self.code,
                "status_code": str(self.status_code),
                "error_type": "api_exception",
            },
        )


# Specific exception classes for common scenarios
class ValidationError(DecisionTreeAPIException):
    """Raised when request validation fails."""

    def __init__(self, detail: str, field: Optional[str] = None):
        context = {"field": field} if field else {}
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            code=ErrorCodes.VALIDATION_ERROR,
            context=context,
        )


class AuthenticationError(DecisionTreeAPIException):
    """Raised when authentication fails."""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code=ErrorCodes.AUTHENTICATION_REQUIRED,
        )


class AuthorizationError(DecisionTreeAPIException):
    """Raised when authorization fails."""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            code=ErrorCodes.INSUFFICIENT_PERMISSIONS,
        )


class NotFoundError(DecisionTreeAPIException):
    """Raised when a resource is not found."""

    def __init__(self, resource_type: str = "resource", resource_id: Optional[str] = None):
        detail = f"{resource_type} not found"
        if resource_id:
            detail = f"{resource_type} with id '{resource_id}' not found"

        context = {"resource_type": resource_type, "resource_id": resource_id}
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            code=ErrorCodes.RESOURCE_NOT_FOUND,
            context=context,
        )


class ConflictError(DecisionTreeAPIException):
    """Raised when there's a conflict (e.g., duplicate slot)."""

    def __init__(self, detail: str, conflict_type: Optional[str] = None):
        context = {"conflict_type": conflict_type} if conflict_type else {}
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            code=ErrorCodes.CONFLICT_ERROR,
            context=context,
        )


class TooManyChildrenError(DecisionTreeAPIException):
    """Raised when trying to add more than 5 children."""

    def __init__(self, detail: str = "Cannot add more than 5 children to a node"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            code=ErrorCodes.TOO_MANY_CHILDREN,
        )


class RateLimitError(DecisionTreeAPIException):
    """Raised when rate limit is exceeded."""

    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            code=ErrorCodes.RATE_LIMIT_EXCEEDED,
        )


# ============================================================================
# CENTRALIZED ERROR HANDLERS
# ============================================================================


def create_error_response(
    request: Request,
    status_code: int,
    error_code: str,
    detail: str,
    safe_message: Optional[str] = None,
    context: Optional[dict[str, Any]] = None,
) -> JSONResponse:
    """
    Create a standardized error response with logging and metrics.

    Args:
        request: The FastAPI request object
        status_code: HTTP status code
        error_code: Internal error code
        detail: Detailed error message (for logging)
        safe_message: Safe message for client (sanitized for production)
        context: Additional context for logging

    Returns:
        JSONResponse with standardized error format
    """
    logger = get_logger(__name__)

    # Get safe message or generate one
    if not safe_message:
        safe_message = ErrorMessages.get_safe_message(error_code, detail)

    # Get correlation IDs
    request_id = get_request_id()
    trace_id = get_trace_id()

    # Build error response
    error_response = {
        "error": {
            "code": error_code,
            "message": safe_message,
            "request_id": request_id,
            "trace_id": trace_id,
        }
    }

    # Add additional context in development mode
    if os.getenv("ENVIRONMENT", "development") == "development":
        error_response["error"]["detail"] = detail
        if context:
            error_response["error"]["context"] = context

    # Log the error with full context
    extra_fields = {
        "error": {
            "code": error_code,
            "status_code": status_code,
            "detail": detail,
            "safe_message": safe_message,
            "context": context or {},
            "request_path": request.url.path,
            "request_method": request.method,
        }
    }

    if request_id:
        extra_fields["request_id"] = request_id
    if trace_id:
        extra_fields["trace_id"] = trace_id

    logger.error(
        f"HTTP Error {status_code}: {error_code} - {detail}",
        extra_fields=extra_fields,
    )

    # Track error metrics
    increment_counter(
        "api.errors",
        tags={
            "error_code": error_code,
            "status_code": str(status_code),
            "error_type": "http_error",
            "method": request.method,
            "path": request.url.path,
        },
    )

    # Track error for alerting and analysis
    severity = _get_severity_from_status_code(status_code)
    try:
        import asyncio

        # Run error tracking in background if event loop is running
        try:
            loop = asyncio.get_running_loop()
            # Lazy import to avoid circular dependency
            from .observability.error_tracking import track_error

            loop.create_task(
                track_error(
                    error_code=error_code,
                    status_code=status_code,
                    message=detail,
                    severity=severity,
                    context=dict(
                        request_path=request.url.path,
                        request_method=request.method,
                        safe_message=safe_message,
                        **(context or {}),
                    ),
                )
            )
        except RuntimeError:
            # No event loop running, skip async tracking
            pass
    except Exception:
        # Don't let error tracking failures affect the main response
        pass

    return JSONResponse(status_code=status_code, content=error_response)


def _get_severity_from_status_code(status_code: int):
    """Map HTTP status code to error severity."""
    # Lazy import to avoid circular dependency
    from .observability.error_tracking import ErrorSeverity

    if 400 <= status_code < 500:
        if status_code == 401:
            return ErrorSeverity.MEDIUM  # Auth issues are medium severity
        elif status_code == 403:
            return ErrorSeverity.MEDIUM  # Permission issues are medium severity
        elif status_code == 404:
            return ErrorSeverity.LOW  # Not found is usually low severity
        elif status_code == 429:
            return ErrorSeverity.MEDIUM  # Rate limiting is medium severity
        else:
            return ErrorSeverity.MEDIUM  # Other 4xx errors
    elif 500 <= status_code < 600:
        return ErrorSeverity.HIGH  # Server errors are high severity
    else:
        return ErrorSeverity.LOW  # Unknown status codes


def handle_value_error(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ValueError exceptions from domain logic."""
    return create_error_response(
        request=request,
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code=ErrorCodes.VALIDATION_ERROR,
        detail=str(exc),
    )


def handle_integrity_error(request: Request, exc: sqlite3.IntegrityError) -> JSONResponse:
    """Handle SQLite IntegrityError exceptions with enhanced mapping."""
    error_detail = str(exc)

    # Map specific integrity errors to appropriate status codes and error codes
    if "UNIQUE constraint failed" in error_detail:
        status_code = status.HTTP_409_CONFLICT
        error_code = ErrorCodes.DUPLICATE_ENTRY
        safe_message = ErrorMessages.get_safe_message(error_code)
    elif "FOREIGN KEY constraint failed" in error_detail:
        status_code = status.HTTP_400_BAD_REQUEST
        error_code = ErrorCodes.FOREIGN_KEY_VIOLATION
        safe_message = ErrorMessages.get_safe_message(error_code)
    elif "CHECK constraint failed" in error_detail:
        status_code = status.HTTP_400_BAD_REQUEST
        error_code = ErrorCodes.CONSTRAINT_VIOLATION
        safe_message = ErrorMessages.get_safe_message(error_code)
    else:
        status_code = status.HTTP_409_CONFLICT
        error_code = ErrorCodes.INTEGRITY_ERROR
        safe_message = ErrorMessages.get_safe_message(error_code)

    return create_error_response(
        request=request,
        status_code=status_code,
        error_code=error_code,
        detail=error_detail,
        safe_message=safe_message,
        context={"sqlite_error": True},
    )


def handle_decision_tree_api_exception(
    request: Request, exc: DecisionTreeAPIException
) -> JSONResponse:
    """Handle custom API exceptions."""
    return create_error_response(
        request=request,
        status_code=exc.status_code,
        error_code=exc.code,
        detail=exc.detail,
        safe_message=exc.safe_message,
        context=exc.context,
    )


def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTPException with enhanced logging."""
    # Map common HTTP exceptions to our error codes
    error_code_mapping = {
        status.HTTP_400_BAD_REQUEST: ErrorCodes.VALIDATION_ERROR,
        status.HTTP_401_UNAUTHORIZED: ErrorCodes.AUTHENTICATION_REQUIRED,
        status.HTTP_403_FORBIDDEN: ErrorCodes.INSUFFICIENT_PERMISSIONS,
        status.HTTP_404_NOT_FOUND: ErrorCodes.RESOURCE_NOT_FOUND,
        status.HTTP_409_CONFLICT: ErrorCodes.CONFLICT_ERROR,
        status.HTTP_422_UNPROCESSABLE_ENTITY: ErrorCodes.VALIDATION_ERROR,
        status.HTTP_429_TOO_MANY_REQUESTS: ErrorCodes.RATE_LIMIT_EXCEEDED,
        status.HTTP_500_INTERNAL_SERVER_ERROR: ErrorCodes.INTERNAL_SERVER_ERROR,
    }

    error_code = error_code_mapping.get(exc.status_code, ErrorCodes.INTERNAL_SERVER_ERROR)

    return create_error_response(
        request=request,
        status_code=exc.status_code,
        error_code=error_code,
        detail=exc.detail,
        context={"http_exception": True},
    )


def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions with comprehensive logging."""
    logger = get_logger(__name__)

    # Log the full exception with traceback
    logger.exception(
        f"Unexpected exception: {type(exc).__name__}: {str(exc)}",
        extra_fields={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "request_path": request.url.path,
            "request_method": request.method,
        },
    )

    # Track unexpected errors
    increment_counter(
        "api.errors",
        tags={
            "error_code": ErrorCodes.INTERNAL_SERVER_ERROR,
            "status_code": "500",
            "error_type": "unexpected_exception",
            "exception_type": type(exc).__name__,
        },
    )

    return create_error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
        detail=f"Unexpected error: {type(exc).__name__}: {str(exc)}",
        context={
            "exception_type": type(exc).__name__,
            "unexpected": True,
        },
    )
