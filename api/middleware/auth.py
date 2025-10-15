"""
Enhanced authentication middleware with comprehensive security features.

Provides secure token-based authentication for all protected endpoints.
This is the single source of truth for authentication in the Lorien API.

Features:
- Environment-based authentication requirements
- Production-mandatory authentication
- Rate limiting and brute force protection
- Security event logging
- Timing attack protection
- Comprehensive error handling
"""

import logging
import time

from fastapi import Request
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from ..security import get_security_config

logger = logging.getLogger(__name__)

# Security scheme for OpenAPI docs
security = HTTPBearer(auto_error=False)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Enhanced authentication middleware with comprehensive security features.

    This middleware enforces secure token-based authentication with:
    - Environment-based authentication requirements
    - Production-mandatory authentication
    - Rate limiting and brute force protection
    - Security event logging
    - Timing attack protection
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.security_config = get_security_config()
        self.failed_attempts: dict[str, list[float]] = {}
        self._log_startup_status()

    def _log_startup_status(self):
        """Log authentication status at startup."""
        if self.security_config.is_production and not self.security_config.auth_token:
            logger.error("❌ CRITICAL: Production environment requires AUTH_TOKEN to be set")
            raise RuntimeError("Production deployment requires AUTH_TOKEN environment variable")

        if self.security_config.auth_required:
            logger.info(
                "✓ Authentication REQUIRED - all write operations require valid Bearer token"
            )
        else:
            logger.warning(
                "⚠ Authentication OPTIONAL - set AUTH_TOKEN and AUTH_REQUIRED=true to enable"
            )

    def is_enabled(self) -> bool:
        """Check if authentication is required based on security configuration."""
        return self.security_config.auth_required

    def get_token(self) -> str | None:
        """Get the current auth token from security configuration."""
        return self.security_config.auth_token

    def _is_public_endpoint(self, path: str) -> bool:
        """Check if the endpoint is public (never requires auth)."""
        return self.security_config.is_endpoint_public(path)

    def _requires_authentication(self, request: Request) -> bool:
        """Determine if a request requires authentication."""
        # Public endpoints are always accessible
        if self._is_public_endpoint(request.url.path):
            return False

        # Read-only methods are accessible if auth is not required
        read_methods = {"GET", "HEAD", "OPTIONS"}
        if request.method in read_methods and not self.security_config.auth_required:
            return False

        # All write operations require authentication when enabled
        return self.security_config.auth_required

    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client is rate limited due to failed auth attempts."""
        if client_ip not in self.failed_attempts:
            return False

        current_time = time.time()
        # Clean old attempts (older than 1 hour)
        self.failed_attempts[client_ip] = [
            attempt_time
            for attempt_time in self.failed_attempts[client_ip]
            if current_time - attempt_time < 3600
        ]

        # Check if too many failed attempts (more than 5 in 1 hour)
        return len(self.failed_attempts[client_ip]) >= 5

    def _record_failed_attempt(self, client_ip: str):
        """Record a failed authentication attempt."""
        current_time = time.time()
        if client_ip not in self.failed_attempts:
            self.failed_attempts[client_ip] = []
        self.failed_attempts[client_ip].append(current_time)

    async def dispatch(self, request: Request, call_next):
        """
        Process request and enforce authentication for protected endpoints.

        Enhanced security flow:
        1. Check if auth is required based on environment and configuration
        2. If not required, allow all requests
        3. If required, check rate limiting for failed attempts
        4. Validate Bearer token with timing attack protection
        5. Log security events and track failed attempts
        6. Return appropriate error responses
        """
        client_ip = self.security_config._get_client_ip(request)

        # Check if this request requires authentication
        if not self._requires_authentication(request):
            return await call_next(request)

        # Check rate limiting for failed auth attempts
        if self._is_rate_limited(client_ip):
            self.security_config.log_security_event(
                "auth_rate_limited",
                request,
                {
                    "client_ip": client_ip,
                    "failed_attempts": len(self.failed_attempts.get(client_ip, [])),
                },
            )

            return JSONResponse(
                status_code=429,
                content={
                    "detail": {
                        "error": "rate_limited",
                        "message": "Too many failed authentication attempts. Please try again later.",
                        "retry_after": "3600",  # 1 hour
                    }
                },
            )

        # Extract and validate token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            self.security_config.log_security_event(
                "missing_auth_header", request, {"client_ip": client_ip}
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
            self.security_config.log_security_event(
                "invalid_auth_format",
                request,
                {
                    "client_ip": client_ip,
                    "auth_header": auth_header[:20] + "..."
                    if len(auth_header) > 20
                    else auth_header,
                },
            )

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

        # Use timing-safe comparison
        if not self.security_config.validate_auth_token(token):
            self._record_failed_attempt(client_ip)
            self.security_config.log_security_event(
                "invalid_auth_token", request, {"client_ip": client_ip, "token_length": len(token)}
            )

            return JSONResponse(
                status_code=401,
                content={
                    "detail": {
                        "error": "invalid_token",
                        "message": "Invalid authentication token",
                    }
                },
            )

        # Clear failed attempts on successful authentication
        if client_ip in self.failed_attempts:
            del self.failed_attempts[client_ip]

        # Log successful authentication (at debug level to avoid noise)
        logger.debug(f"✓ Authenticated: {request.method} {request.url.path} from {client_ip}")

        return await call_next(request)


def get_auth_token() -> str | None:
    """
    Get the current auth token from security configuration.

    Returns:
        Current AUTH_TOKEN value or None if not set
    """
    security_config = get_security_config()
    return security_config.auth_token


def is_auth_enabled() -> bool:
    """
    Check if authentication is required.

    Returns:
        True if authentication is required, False otherwise
    """
    security_config = get_security_config()
    return security_config.auth_required


# Removed duplicate function definition - using the one from security.py
