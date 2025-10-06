"""Health and readiness endpoints for the decision tree API."""

import asyncio
from contextlib import closing
import logging
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_db_connection
from ..settings import get_db_path
from core.version import __version__

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

@router.get("/health")
def health_check(conn: sqlite3.Connection = Depends(get_db_connection)):
    """
    Comprehensive health check endpoint.

    Returns:
        200 with health status, version, database info, and feature flags
    """
    try:
        db_stats = _check_database_health(conn)
        feature_flags = _check_features()
        llm_enabled = feature_flags["llm"]
        status_value = "ok" if db_stats.get("integrity", "ok").lower() == "ok" else "degraded"
        if status_value == "ok" and feature_flags.get("llm_requested") and not llm_enabled:
            status_value = "degraded"

        return {
            "ok": status_value == "ok",
            "status": status_value,
            "version": __version__,
            "db": {
                "path": db_stats["path"],
                "exists": db_stats["exists"],
                "journal_mode": db_stats["journal_mode"],
                "tables": db_stats["tables"],
                "nodes": db_stats["nodes"],
                "integrity": db_stats["integrity"],
                "objects": db_stats.get("objects", 0),
            },
            "features": feature_flags,
        }
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Health check failed")
        return {
            "ok": False,
            "status": "error",
            "version": __version__,
            "db": {"path": None, "exists": False, "journal_mode": None, "tables": 0, "nodes": 0, "objects": 0},
            "features": {"llm": False, "llm_requested": False, "analytics": False},
            "error": str(exc),
        }


@router.get("/health/metrics")
async def health_metrics():
    """
    Minimal telemetry endpoint returning non-PHI counters.

    Only available when ANALYTICS_ENABLED=true.
    Returns 404 when analytics is disabled.
    """
    analytics_enabled = _env_flag_enabled("ANALYTICS_ENABLED")
    if not analytics_enabled:
        raise HTTPException(status_code=404, detail="Analytics disabled")

    metrics_data = await asyncio.to_thread(_collect_runtime_metrics)
    return metrics_data

def _check_database_health(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Check database configuration and health."""
    try:
        with closing(conn.execute("PRAGMA journal_mode")) as cursor:
            journal_row = cursor.fetchone()
        journal_mode = (journal_row[0] if journal_row else "").lower()

        table_names = _fetch_names(conn, "table")
        object_names = _fetch_names(conn, "table", "view", "trigger")

        node_count = _safe_count_nodes(conn) if "nodes" in table_names else 0

        with closing(conn.execute("PRAGMA integrity_check")) as cursor:
            integrity_row = cursor.fetchone()
        integrity = integrity_row[0] if integrity_row else "unknown"

        db_path = Path(get_db_path())

        return {
            "path": str(db_path),
            "exists": db_path.exists(),
            "journal_mode": journal_mode,
            "tables": len([name for name in table_names if name]),
            "nodes": node_count,
            "integrity": integrity,
            "objects": len([name for name in object_names if name]),
        }
    except Exception as exc:
        raise RuntimeError(f"database check failed: {exc}") from exc


def _check_features() -> Dict[str, bool]:
    """Check feature availability."""
    llm_gate_enabled = _env_flag_enabled("LLM_ENABLED")
    if llm_gate_enabled:
        model_path = Path(os.getenv("LLM_MODEL_PATH", "llm/models/model.gguf"))
        llm_active = model_path.is_file()
        if not llm_active:
            logger.warning("LLM feature flagged on but model missing at %s", model_path)
    else:
        llm_active = False

    analytics_enabled = _env_flag_enabled("ANALYTICS_ENABLED")

    return {
        "llm": llm_active,
        "llm_requested": llm_gate_enabled,
        "analytics": analytics_enabled,
    }


def _collect_runtime_metrics() -> Dict[str, Any]:
    """Get runtime metrics (non-PHI counters only)."""
    try:
        with closing(sqlite3.connect(get_db_path())) as conn:
            with closing(conn.cursor()) as cursor:
                if _table_exists(cursor, "nodes"):
                    cursor.execute("SELECT COUNT(*) FROM nodes")
                    row = cursor.fetchone()
                    node_count = row[0] if row else 0
                else:
                    node_count = 0

        return {
            "telemetry": {},  # No metrics module available
            "table_counts": {"nodes": node_count},
        }
    except Exception as exc:
        logger.warning("Runtime metrics unavailable: %s", exc)
        return {
            "error": str(exc),
            "telemetry": {},
            "table_counts": {"nodes": 0},
        }


def _fetch_names(conn: sqlite3.Connection, *object_types: str) -> List[str]:
    """Return names of SQLite objects for the given types."""
    placeholders = ",".join("?" for _ in object_types)
    query = (
        "SELECT name FROM sqlite_master WHERE type IN (" + placeholders + ")"
    )
    with closing(conn.execute(query, object_types)) as cursor:
        return [row[0] for row in cursor.fetchall()]


def _safe_count_nodes(conn: sqlite3.Connection) -> int:
    """Count nodes table entries with defensive error handling."""
    try:
        with closing(conn.execute("SELECT COUNT(*) FROM nodes")) as cursor:
            row = cursor.fetchone()
        return row[0] if row else 0
    except sqlite3.OperationalError as exc:
        logger.warning("Failed to count nodes: %s", exc)
        return 0


def _table_exists(cursor: sqlite3.Cursor, table_name: str) -> bool:
    """Check if a table exists using the provided cursor."""
    cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    return cursor.fetchone() is not None


def _env_flag_enabled(name: str, default: bool = False) -> bool:
    """Return True when the environment toggle is set to a truthy value."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}

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
