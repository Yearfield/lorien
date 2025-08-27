"""
Main FastAPI application for the decision tree API.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sqlite3

from .routes import router
from .routers.health import router as health_router
from .exceptions import (
    DecisionTreeAPIException, handle_value_error, handle_integrity_error,
    handle_decision_tree_api_exception
)
import os

# Create FastAPI app
app = FastAPI(
    title="Decision Tree API",
    description="API for managing decision tree structures with strict 5-children rule",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for Flutter development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Flutter web dev server
        "http://localhost:8080",  # Alternative Flutter port
        "http://localhost:*",     # Any localhost port for development
    ],
    allow_credentials=True,
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

# Include routes
app.include_router(router, prefix="")
app.include_router(health_router, prefix="")

# Conditionally include LLM router if enabled
if os.getenv("LLM_ENABLED", "false").lower() == "true":
    try:
        from .routers.llm import router as llm_router
        app.include_router(llm_router, prefix="")
    except ImportError:
        # LLM dependencies not available, skip silently
        pass

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Decision Tree API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Health check at root level
@app.get("/health")
async def root_health():
    """Root-level health check."""
    return {"status": "healthy", "service": "decision-tree-api"}
