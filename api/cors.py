"""
CORS (Cross-Origin Resource Sharing) configuration for Lorien API.

Provides secure CORS configuration with environment-based settings.
"""

import logging

from fastapi.middleware.cors import CORSMiddleware

from .security import get_security_config

logger = logging.getLogger(__name__)


def setup_cors(app):
    """
    Configure CORS middleware with security-conscious settings.

    Args:
        app: FastAPI application instance
    """
    security_config = get_security_config()

    # Determine allowed origins based on environment
    if "*" in security_config.cors_origins:
        # Development mode - allow all origins
        allowed_origins = ["*"]
        logger.warning("⚠ CORS: Allowing all origins (*) - not recommended for production")
    else:
        # Production mode - specific origins only
        allowed_origins = list(security_config.cors_origins)
        logger.info(f"✓ CORS: Restricting to specific origins: {allowed_origins}")

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=security_config.cors_allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Forwarded-For",
            "X-Real-IP",
        ],
        expose_headers=[
            "Content-Range",
            "X-Content-Range",
            "X-Total-Count",
        ],
        max_age=3600,  # Cache preflight requests for 1 hour
    )

    logger.info("✓ CORS middleware configured")


def get_cors_origins() -> list[str]:
    """
    Get the configured CORS origins.

    Returns:
        List of allowed CORS origins
    """
    security_config = get_security_config()
    return list(security_config.cors_origins)


def is_cors_enabled() -> bool:
    """
    Check if CORS is properly configured.

    Returns:
        True if CORS origins are configured, False otherwise
    """
    security_config = get_security_config()
    return len(security_config.cors_origins) > 0
