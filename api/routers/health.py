"""
Health check router for the decision tree API.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import os

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository
from core.version import __version__
from ..models import HealthResponse, DBInfo

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check(repo: SQLiteRepository = Depends(get_repository)):
    """
    Comprehensive health check endpoint.

    Returns:
        200 with health status, version, database info, and feature flags
    """
    # Check database status
    db_info = await _check_database_health(repo)

    # Check feature flags
    features = await _check_features()

    # Build response
    response_data = {
        "ok": True,
        "version": __version__,
        "db": db_info,
        "features": features
    }

    # Add metrics if analytics is enabled (default false)
    analytics_enabled = os.getenv("ANALYTICS_ENABLED", "false").lower() == "true"
    if analytics_enabled:
        metrics_data = await _get_runtime_metrics()
        if metrics_data:
            response_data["metrics"] = metrics_data

    return response_data


@router.get("/health/metrics")
async def health_metrics():
    """
    Minimal telemetry endpoint returning non-PHI counters.

    Only available when ANALYTICS_ENABLED=true.
    Returns 404 when analytics is disabled.
    """
    analytics_enabled = os.getenv("ANALYTICS_ENABLED", "false").lower() == "true"
    if not analytics_enabled:
        raise HTTPException(status_code=404, detail="Analytics disabled")

    metrics_data = await _get_runtime_metrics()
    return metrics_data

async def _check_database_health(repo: SQLiteRepository) -> Dict[str, Any]:
    """Check database configuration and health."""
    try:
        with repo._get_connection() as conn:
            # Get database configuration
            cursor = conn.cursor()
            
            # Check WAL mode
            cursor.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]
            
            # Check foreign keys
            cursor.execute("PRAGMA foreign_keys")
            foreign_keys = cursor.fetchone()[0]
            
            # Check page size
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
            # Get database path from repository (resolved path)
            db_path = repo.get_resolved_db_path()
            
            return {
                "wal": journal_mode == "wal",
                "foreign_keys": bool(foreign_keys),
                "page_size": page_size,
                "path": db_path
            }
    except Exception as e:
        return {
            "wal": False,
            "foreign_keys": False,
            "page_size": 0,
            "path": None,
            "error": str(e)
        }

async def _check_features() -> Dict[str, bool]:
    """Check feature availability."""
    # Check if LLM is enabled via environment variable
    llm_enabled = os.getenv("LLM_ENABLED", "false").lower() == "true"
    
    # Check if LLM model file exists (if enabled)
    if llm_enabled:
        model_path = os.getenv("LLM_MODEL_PATH", "llm/models/model.gguf")
        llm_enabled = os.path.exists(model_path)
    
    return {
        "llm": llm_enabled
    }

async def _get_runtime_metrics() -> Dict[str, Any]:
    """Get runtime metrics (non-PHI counters only)."""
    try:
        # Import here to avoid circular dependencies
        from ..metrics import snapshot

        telemetry = snapshot()

        # Count rows in the primary table using a fresh repository connection
        repo = SQLiteRepository()
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM nodes")
            node_count = cursor.fetchone()[0]

        return {
            "telemetry": telemetry,
            "table_counts": {"nodes": node_count},
        }
    except Exception as e:
        return {
            "error": str(e),
            "telemetry": {},
            "table_counts": {},
        }
