"""
Unified authentication middleware - AUTHORITATIVE version.

Provides comprehensive token-based authentication for all protected endpoints.
This is the single source of truth for authentication in the Lorien API.

Authentication is controlled via the AUTH_TOKEN environment variable:
- If AUTH_TOKEN is not set: authentication is disabled (dev mode)
- If AUTH_TOKEN is set: all write operations require Bearer token authentication
- Read operations (GET, HEAD, OPTIONS) are always public
- Health and readiness probes are always public
"""

import logging
import os

from fastapi import Request
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

# Security scheme for OpenAPI docs
security = HTTPBearer(auto_error=False)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authoritative authentication middleware for the Lorien API.

    This middleware enforces token-based authentication for all write operations
    across the entire API surface. It is the single source of truth for auth.
    """

    # Public endpoints that never require authentication
    PUBLIC_ENDPOINTS: set[str] = {
        "/health",
        "/live",
        "/ready",
        "/api/v1/health",
        "/api/v1/live",
        "/api/v1/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
    }

    # Read-only HTTP methods that don't require authentication
    READ_METHODS: set[str] = {"GET", "HEAD", "OPTIONS"}

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self._log_startup_status()

    def _log_startup_status(self):
        """Log authentication status at startup."""
        if self.is_enabled():
            logger.info("✓ Authentication enabled - write operations require valid Bearer token")
        else:
            logger.warning(
                "⚠ Authentication DISABLED - set AUTH_TOKEN environment variable to enable"
            )

    @staticmethod
    def is_enabled() -> bool:
        """Check if authentication is enabled via AUTH_TOKEN environment variable."""
        return os.getenv("AUTH_TOKEN") is not None

    @staticmethod
    def get_token() -> str | None:
        """Get the current auth token from environment."""
        return os.getenv("AUTH_TOKEN")

    def _is_public_endpoint(self, path: str) -> bool:
        """Check if the endpoint is public (never requires auth)."""
        return any(path.startswith(endpoint) for endpoint in self.PUBLIC_ENDPOINTS)

    def _requires_authentication(self, request: Request) -> bool:
        """Determine if a request requires authentication."""
        # Public endpoints are always accessible
        if self._is_public_endpoint(request.url.path):
            return False

        # Read-only methods are always accessible
        if request.method in self.READ_METHODS:
            return False

        # All write operations require authentication when enabled
        return True

    async def dispatch(self, request: Request, call_next):
        """
        Process request and enforce authentication for protected endpoints.

        Flow:
        1. Check if auth is enabled (via AUTH_TOKEN env var)
        2. If disabled, allow all requests
        3. If enabled, check if request requires auth
        4. If required, validate Bearer token
        5. If valid, proceed; otherwise return 401
        """
        # If auth is not enabled, allow all requests
        if not self.is_enabled():
            return await call_next(request)

        # Check if this request requires authentication
        if not self._requires_authentication(request):
            return await call_next(request)

        # Extract and validate token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.warning(
                f"Authentication required but missing: {request.method} {request.url.path}"
            )
            return JSONResponse(
                status_code=401,
                content={
                    "detail": {
                        "error": "authentication_required",
                        "message": "Authorization header required for write operations",
                        "hint": "Include 'Authorization: Bearer <token>' header",
                    }
                },
            )

        if not auth_header.startswith("Bearer "):
            logger.warning(f"Invalid auth format: {request.method} {request.url.path}")
            return JSONResponse(
                status_code=401,
                content={
                    "detail": {
                        "error": "invalid_auth_format",
                        "message": "Authorization header must use Bearer token format",
                        "expected_format": "Bearer <token>",
                    }
                },
            )

        token = auth_header[7:]  # Remove "Bearer " prefix
        expected_token = self.get_token()

        if token != expected_token:
            logger.warning(f"Invalid token attempt: {request.method} {request.url.path}")
            return JSONResponse(
                status_code=401,
                content={
                    "detail": {
                        "error": "invalid_token",
                        "message": "Invalid authentication token",
                    }
                },
            )

        # Log successful authentication (at debug level to avoid noise)
        logger.debug(f"✓ Authenticated: {request.method} {request.url.path}")

        return await call_next(request)


def get_auth_token() -> str | None:
    """
    Get the current auth token from environment.

    Returns:
        Current AUTH_TOKEN value or None if not set
    """
    return AuthMiddleware.get_token()


def is_auth_enabled() -> bool:
    """
    Check if authentication is enabled.

    Returns:
        True if AUTH_TOKEN is set, False otherwise
    """
    return AuthMiddleware.is_enabled()
