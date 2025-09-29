"""
Health check router for the decision tree API.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import os
import sqlite3

from ..dependencies import get_db_connection
from ..settings import get_db_path
from core.version import __version__

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check(conn: sqlite3.Connection = Depends(get_db_connection)):
    """
    Comprehensive health check endpoint.

    Returns:
        200 with health status, version, database info, and feature flags
    """
    # Open a short-lived connection for introspection
    from ..dependencies import get_db_connection
    conn = await get_db_connection()
    try:
        db_path = get_db_path()
        wal = conn.execute("PRAGMA journal_mode").fetchone()[0]
        # migration marker (exists if migrations applied)
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        nodes = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] if "nodes" in tables else 0
        # Check LLM feature flag
        llm_enabled = os.getenv("LLM_ENABLED", "false").lower() == "true"
        
        return {
            "version": __version__,
            "db": {"path": db_path, "journal_mode": wal, "tables": len(tables), "nodes": nodes},
            "llm": llm_enabled,
            "status": "ok"
        }
    finally:
        try:
            conn.close()
        except Exception:
            pass


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

async def _check_database_health(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Check database configuration and health."""
    try:
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
        
        # Check integrity
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]
        
        # Count database objects (tables, views, triggers)
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type IN ('table', 'view', 'trigger')")
        object_count = cursor.fetchone()[0]
        
        # Report the actual DB path in use
        db_path = get_db_path()
        
        return {
            "wal": journal_mode == "wal",
            "foreign_keys": bool(foreign_keys),
            "page_size": page_size,
            "integrity": integrity,
            "objects": object_count,
            "path": db_path
        }
    except Exception as e:
        return {
            "wal": False,
            "foreign_keys": False,
            "page_size": 0,
            "integrity": "error",
            "objects": 0,
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
        # Count rows in the primary table using a fresh connection
        from ..settings import get_db_path
        conn = sqlite3.connect(get_db_path())
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM nodes")
            node_count = cursor.fetchone()[0]
        finally:
            conn.close()

        return {
            "telemetry": {},  # No metrics module available
            "table_counts": {"nodes": node_count},
        }
    except Exception as e:
        return {
            "error": str(e),
            "telemetry": {},
            "table_counts": {},
        }

@router.get("/live")
def live() -> Dict[str, Any]:
    """Liveness probe: process is up."""
    return {"status": "live"}

@router.get("/ready")
def ready(conn: sqlite3.Connection = Depends(get_db_connection)) -> Dict[str, Any]:
    """Readiness probe: DB reachable and schema present."""
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'")
    ok = cur.fetchone() is not None
    return {"status": "ready" if ok else "not_ready", "db": {"has_nodes_table": ok}}
