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
    try:
        db_stats = _check_database_health(conn)
        llm_enabled = (await _check_features())["llm"]
        status_value = "ok" if db_stats.get("integrity", "ok").lower() == "ok" else "degraded"

        return {
            "ok": status_value == "ok",
            "status": status_value,
            "version": __version__,
            "db": {
                "path": db_stats["path"],
                "journal_mode": db_stats["journal_mode"],
                "tables": db_stats["tables"],
                "nodes": db_stats["nodes"],
                "integrity": db_stats["integrity"],
                "objects": db_stats.get("objects", 0),
            },
            "features": {"llm": llm_enabled},
        }
    except Exception as e:
        return {
            "ok": False,
            "status": "error",
            "version": __version__,
            "db": {"path": None, "journal_mode": None, "tables": 0, "nodes": 0},
            "features": {"llm": False},
            "error": str(e)
        }


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

def _check_database_health(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Check database configuration and health."""
    try:
        # Get database configuration
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]

        table_names = [row[0] for row in cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]
        object_names = [row[0] for row in cursor.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view','trigger')"
        ).fetchall()]

        node_count = 0
        if "nodes" in table_names:
            node_count = cursor.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]

        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]

        return {
            "path": get_db_path(),
            "journal_mode": (journal_mode or "").lower(),
            "tables": sum(1 for name in table_names if name),
            "nodes": node_count,
            "integrity": integrity,
            "objects": sum(1 for name in object_names if name),
        }
    except Exception as e:
        raise RuntimeError(f"database check failed: {e}") from e

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
