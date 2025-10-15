"""
Main FastAPI application for the decision tree API - LongBow Core + VM Builder Only
"""

import logging
import os
import sqlite3

from fastapi import FastAPI, HTTPException

from api.cors import setup_cors
from api.db.migrate import apply_migrations
from api.exceptions import (
    DecisionTreeAPIException,
    handle_decision_tree_api_exception,
    handle_generic_exception,
    handle_http_exception,
    handle_integrity_error,
    handle_value_error,
)
from api.middleware.auth import AuthMiddleware
from api.middleware.deprecation import DeprecationMiddleware
from api.observability import ObservabilityMiddleware, setup_logging
from api.observability.metrics import increment_counter
from api.observability.telemetry import setup_opentelemetry, shutdown_opentelemetry
from api.routers.conflicts import router as conflicts_router
from api.routers.dictionary import router as dictionary_router
from api.routers.health import router as health_router
from api.routers.import_router import router as import_router
from api.routers.tree_basic import router as tree_basic_router
from api.routers.tree_delete_restore import router as tree_delete_restore_router
from api.routers.tree_export_router import router as export_router
from api.security import (
    InputValidationMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    get_security_config,
)
from api.settings import get_db_path
from core.version import __version__

# Set up structured logging early
log_level = os.getenv("LOG_LEVEL", "INFO")
json_logging = os.getenv("JSON_LOGGING", "true").lower() == "true"
setup_logging(level=log_level, json_output=json_logging)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Lorien - VM Builder",
    description="Minimal decision tree API for VM Builder with LongBow import/export",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
def on_startup() -> None:
    """Run startup tasks: migrations, logging, observability, and security."""
    apply_migrations(get_db_path())

    # Initialize security configuration
    security_config = get_security_config()

    # Validate security configuration
    if security_config.is_production and not security_config.auth_token:
        logger.error("❌ CRITICAL: Production deployment requires AUTH_TOKEN")
        raise RuntimeError("Production deployment requires AUTH_TOKEN environment variable")

    # Initialize OpenTelemetry if enabled
    otel_enabled = setup_opentelemetry(
        service_name="lorien-api",
        service_version=__version__,
    )

    logger.info(
        "✓ Lorien API started",
        extra={
            "extra_fields": {
                "version": __version__,
                "environment": security_config.environment,
                "auth_required": security_config.auth_required,
                "rate_limiting": security_config.rate_limit_enabled,
                "security_headers": security_config.security_headers_enabled,
                "otel_enabled": otel_enabled,
                "json_logging": json_logging,
            }
        },
    )

    # Track startup in metrics
    increment_counter("app.startup")


@app.on_event("shutdown")
def on_shutdown() -> None:
    """Run shutdown tasks: flush observability data."""
    logger.info("Shutting down Lorien API")
    shutdown_opentelemetry()
    increment_counter("app.shutdown")


# ============================================================================
# MIDDLEWARE - Order matters! Applied in reverse order (last added = first run)
# ============================================================================

# 1. Security Headers middleware (runs last, adds headers to all responses)
#    Adds security headers like HSTS, CSP, X-Frame-Options, etc.
app.add_middleware(SecurityHeadersMiddleware)

# 2. Input Validation middleware
#    Validates and sanitizes request inputs
app.add_middleware(InputValidationMiddleware)

# 3. Rate Limiting middleware
#    Prevents abuse with rate limiting
app.add_middleware(RateLimitMiddleware)

# 4. Authentication middleware
#    Enforces Bearer token auth for all write operations
app.add_middleware(AuthMiddleware)

# 5. Deprecation middleware
#    Redirects legacy routes to /api/v1 with Sunset headers
app.add_middleware(DeprecationMiddleware)

# 6. Observability middleware (runs first)
#    Adds request/trace IDs, structured logging, and OpenTelemetry
enable_otel = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") is not None
app.add_middleware(ObservabilityMiddleware, enable_otel=enable_otel)

# 7. CORS middleware (configured separately)
#    Handles cross-origin requests with security-conscious settings
setup_cors(app)


# ============================================================================
# EXCEPTION HANDLERS - Order matters! More specific handlers first
# ============================================================================

# Register centralized exception handlers
app.add_exception_handler(DecisionTreeAPIException, handle_decision_tree_api_exception)
app.add_exception_handler(ValueError, handle_value_error)
app.add_exception_handler(sqlite3.IntegrityError, handle_integrity_error)
app.add_exception_handler(HTTPException, handle_http_exception)
app.add_exception_handler(Exception, handle_generic_exception)


# ============================================================================
# CANONICAL ROUTES - All under /api/v1
# ============================================================================

app.include_router(health_router, prefix="/api/v1")
app.include_router(import_router, prefix="/api/v1")
app.include_router(export_router, prefix="/api/v1")
app.include_router(conflicts_router, prefix="/api/v1")
app.include_router(dictionary_router)

# Note: tree_basic_router already has prefix="/api/v1/tree" internally
# Note: tree_delete_restore_router already has prefix="/api/v1/tree" internally
app.include_router(tree_basic_router)
app.include_router(tree_delete_restore_router)


# ============================================================================
# DEPRECATED ROUTES - Kept for backward compatibility
# These routes are automatically redirected by DeprecationMiddleware
# ============================================================================

# Legacy root-level routes (no /api/v1 prefix) are still accessible but will:
# - Return 301 Permanent Redirect to /api/v1 versions
# - Include Sunset and Deprecation headers
# - Be removed in a future version

# To access these routes without redirect, use /api/v1 versions directly
