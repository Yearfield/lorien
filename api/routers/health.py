"""
Health check router for the decision tree API.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
import os

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository
from core.version import __version__
from ..models import HealthResponse, DBInfo

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthResponse)
async def health_check(repo: SQLiteRepository = Depends(get_repository)) -> HealthResponse:
    """
    Comprehensive health check endpoint.
    
    Returns:
        HealthResponse with health status, version, database info, and feature flags
    """
    # Check database status
    db_info = await _check_database_health(repo)
    
    # Check feature flags
    features = await _check_features()
    
    # Build response
    response_data = {
        "ok": True,
        "version": __version__,
        "db": DBInfo(**db_info),
        "features": features
    }
    
    # Add metrics if analytics is enabled
    # Check environment variable at request time, not import time
    analytics_enabled = os.getenv("ANALYTICS_ENABLED", "false").lower() == "true"
    if analytics_enabled:
        metrics_data = await _get_runtime_metrics()
        if metrics_data:
            response_data["metrics"] = metrics_data
    
    # Create response with or without metrics
    if "metrics" in response_data:
        return HealthResponse(**response_data)
    else:
        # Create response without metrics field
        return HealthResponse(
            ok=response_data["ok"],
            version=response_data["version"],
            db=response_data["db"],
            features=response_data["features"]
        )


@router.get("/health/metrics")
async def health_metrics():
    """
    Minimal telemetry endpoint returning non-PHI counters.

    Only available when ANALYTICS_ENABLED=true.
    Returns 404 when analytics is disabled.
    """
    analytics_enabled = os.getenv("ANALYTICS_ENABLED", "false").lower() == "true"
    if not analytics_enabled:
        from fastapi import HTTPException
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
        
        # Get telemetry snapshot
        telemetry = snapshot()
        
        # Import here to avoid circular dependencies
        from storage.sqlite import SQLiteRepository
        repo = SQLiteRepository()
        
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            # Count records in main tables (non-PHI)
            cursor.execute("SELECT COUNT(*) FROM nodes")
            node_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM red_flags")
            flag_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM red_flag_audit")
            audit_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM triage")
            triage_count = cursor.fetchone()[0]
            
            # Get audit retention status
            try:
                cursor.execute("SELECT retention_status FROM audit_retention_status LIMIT 1")
                retention_status = cursor.fetchone()
                retention_status = retention_status[0] if retention_status else "UNKNOWN"
            except:
                retention_status = "VIEW_NOT_AVAILABLE"
            
            return {
                "telemetry": telemetry,
                "table_counts": {
                    "nodes": node_count,
                    "red_flags": flag_count,
                    "red_flag_audit": audit_count,
                    "triage": triage_count
                },
                "audit_retention": {
                    "status": retention_status,
                    "total_audit_rows": audit_count
                },
                "cache": {
                    "enabled": True,
                    "ttl_seconds": 300  # 5 minutes default
                }
            }
    except Exception as e:
        return {
            "error": str(e),
            "telemetry": {},
            "table_counts": {},
            "audit_retention": {"status": "ERROR"},
            "cache": {"enabled": False}
        }
