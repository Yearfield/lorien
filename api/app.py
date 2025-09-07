"""
Main FastAPI application for the decision tree API.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sqlite3
import logging

from .routes import router as api_router
from .routers.health import router as health_router
from .routers.flags_audit import router as flags_audit_router
from .routers.red_flags import router as red_flags_router
from .routers.import_jobs import router as import_jobs_router
from .routers.import_router import router as import_router
from .routers.tree_stats_router import router as tree_stats_router
from .routers.tree_export_router import router as tree_export_router
from .routers.admin_router import router as admin_router
from .routers.tree_edit_router import router as tree_edit_router
from .routers.tree_list_router import router as tree_list_router
from .routers.flags import router as flags_router
from .routers.outcomes import router as outcomes_router
from .routers.dictionary import router as dictionary_router
from .routers.tree import router as tree_router
from .routers.edit_tree import router as edit_tree_router
from .routers.tree_parents import router as tree_parents_router
from .routers.tree_children import router as tree_children_router
from .routers.tree_slots import router as tree_slots_router
from .routers.tree_materialize import router as tree_materialize_router
from .routers.tree_conflicts import router as tree_conflicts_router
from .routers.tree_vm_builder import router as tree_vm_builder_router
from .routers.tree_navigate_router import router as tree_navigate_router
from .routers.tree_admin_router import router as tree_admin_router
from .routers.tree_stats_lists_router import router as tree_stats_lists_router
from .routers.tree_label_router import router as tree_label_router
from .routers.admin_sanitize_router import router as admin_sanitize_router
from .routers.tree_builder_router import router as tree_builder_router
from .routers.admin_root_audit_router import router as admin_root_audit_router
from .additional_routes import router as additional_router
from .exceptions import (
    DecisionTreeAPIException, handle_value_error, handle_integrity_error,
    handle_decision_tree_api_exception
)
from core.version import __version__
import os

# Create FastAPI app
app = FastAPI(
    title="Decision Tree API",
    description="API for managing decision tree structures with strict 5-children rule",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration with environment toggle
allow_all = os.getenv("CORS_ALLOW_ALL", "false").lower() == "true"
if allow_all:
    origins = ["*"]
else:
    origins = [
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://0.0.0.0",
        "http://10.0.2.2"  # Android emulator
    ]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(ValueError, handle_value_error)
app.add_exception_handler(sqlite3.IntegrityError, handle_integrity_error)
app.add_exception_handler(DecisionTreeAPIException, handle_decision_tree_api_exception)

# Add global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle any unhandled exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred",
            "code": "INTERNAL_ERROR"
        }
    )

# Mount all under versioned prefix
API_PREFIX = "/api/v1"
app.include_router(api_router, prefix=API_PREFIX)
app.include_router(health_router, prefix=API_PREFIX)
app.include_router(flags_audit_router, prefix=API_PREFIX)
app.include_router(red_flags_router, prefix=API_PREFIX)
app.include_router(import_jobs_router, prefix=API_PREFIX)
app.include_router(import_router, prefix=API_PREFIX)
app.include_router(tree_stats_router, prefix=API_PREFIX)
app.include_router(tree_export_router, prefix=API_PREFIX)
app.include_router(admin_router, prefix=API_PREFIX)
app.include_router(tree_edit_router, prefix=API_PREFIX)
app.include_router(tree_list_router, prefix=API_PREFIX)
app.include_router(flags_router, prefix=API_PREFIX)
app.include_router(tree_router, prefix=API_PREFIX)
app.include_router(edit_tree_router, prefix=API_PREFIX)
app.include_router(tree_parents_router, prefix=API_PREFIX)
app.include_router(tree_children_router, prefix=API_PREFIX)
app.include_router(tree_slots_router, prefix=API_PREFIX)
app.include_router(tree_materialize_router, prefix=API_PREFIX)
app.include_router(tree_conflicts_router, prefix=API_PREFIX)
app.include_router(tree_vm_builder_router, prefix=API_PREFIX)
app.include_router(tree_navigate_router, prefix=API_PREFIX)
app.include_router(tree_admin_router, prefix=API_PREFIX)
app.include_router(tree_stats_lists_router, prefix=API_PREFIX)
app.include_router(tree_label_router, prefix=API_PREFIX)
app.include_router(admin_sanitize_router, prefix=API_PREFIX)
app.include_router(tree_builder_router, prefix=API_PREFIX)
app.include_router(admin_root_audit_router, prefix=API_PREFIX)
app.include_router(outcomes_router, prefix=API_PREFIX)
app.include_router(dictionary_router, prefix=API_PREFIX)
app.include_router(additional_router, prefix=API_PREFIX)

# Also mount at root for dual-mount requirement
app.include_router(api_router)
app.include_router(health_router)
app.include_router(flags_audit_router)
app.include_router(red_flags_router)
app.include_router(import_jobs_router)
app.include_router(import_router)
app.include_router(tree_stats_router)
app.include_router(tree_export_router)
app.include_router(admin_router)
app.include_router(tree_edit_router)
app.include_router(tree_list_router)
app.include_router(flags_router)
app.include_router(tree_router)
app.include_router(edit_tree_router)
app.include_router(tree_parents_router)
app.include_router(tree_children_router)
app.include_router(tree_slots_router)
app.include_router(tree_materialize_router)
app.include_router(tree_conflicts_router)
app.include_router(tree_vm_builder_router)
app.include_router(tree_navigate_router)
app.include_router(tree_admin_router)
app.include_router(tree_stats_lists_router)
app.include_router(tree_label_router)
app.include_router(admin_sanitize_router)
app.include_router(tree_builder_router)
app.include_router(admin_root_audit_router)
app.include_router(outcomes_router)
app.include_router(dictionary_router)
app.include_router(additional_router)

# Always include LLM router for health endpoint, but functionality controlled by LLM_ENABLED
try:
    from .routers.llm import router as llm_router
    app.include_router(llm_router, prefix=API_PREFIX)
    app.include_router(llm_router)  # Also mount at root for dual-mount
except ImportError:
    # LLM dependencies not available, skip silently
    pass

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with pointers to docs and versioned health."""
    return {
        "message": "Lorien API",
        "version": __version__,
        "docs": "/docs",
        "health": f"{API_PREFIX}/health"
    }

# Startup logging
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def _log_mount_prefix():
    logger.info("API mounted at %s", API_PREFIX)
