"""
Main FastAPI application for the decision tree API - LongBow Core + VM Builder Only
"""

import logging
import os

from fastapi import FastAPI

from api.db.migrate import apply_migrations
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
def on_startup():
    """Run startup tasks: migrations, logging, and observability."""
    apply_migrations(get_db_path())

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
                "auth_enabled": AuthMiddleware.is_enabled(),
                "otel_enabled": otel_enabled,
                "json_logging": json_logging,
            }
        },
    )

    # Track startup in metrics
    increment_counter("app.startup")


@app.on_event("shutdown")
def on_shutdown():
    """Run shutdown tasks: flush observability data."""
    logger.info("Shutting down Lorien API")
    shutdown_opentelemetry()
    increment_counter("app.shutdown")


# ============================================================================
# MIDDLEWARE - Order matters! Applied in reverse order (last added = first run)
# ============================================================================

# 1. Authentication middleware (runs last, after deprecation redirects)
#    Enforces Bearer token auth for all write operations
app.add_middleware(AuthMiddleware)

# 2. Deprecation middleware
#    Redirects legacy routes to /api/v1 with Sunset headers
app.add_middleware(DeprecationMiddleware)

# 3. Observability middleware (runs first)
#    Adds request/trace IDs, structured logging, and OpenTelemetry
enable_otel = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") is not None
app.add_middleware(ObservabilityMiddleware, enable_otel=enable_otel)


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
