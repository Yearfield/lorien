"""Health and readiness endpoints for the decision tree API."""

import asyncio
import logging
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

import anyio
from fastapi import APIRouter, Depends, HTTPException, Request

from core.version import __version__

from ..dependencies import get_db_connection
from ..middleware.auth import AuthMiddleware
from ..observability import get_health_status, get_metrics_snapshot, get_error_tracker
from ..settings import get_db_path
from ..db.init import get_database_manager
from ..db.monitoring import get_database_monitor
from ..db.cache import get_query_cache

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(conn: sqlite3.Connection = Depends(get_db_connection)) -> dict[str, Any]:
    """
    Comprehensive health check endpoint.

    Returns:
        200 with health status, version, database info, and feature flags
    """
    try:
        db_stats = await _check_database_health(conn)
        feature_flags = _check_features()
        llm_enabled = feature_flags["llm"]
        status_value = "ok" if db_stats.get("integrity", "ok").lower() == "ok" else "degraded"
        if status_value == "ok" and feature_flags.get("llm_requested") and not llm_enabled:
            status_value = "degraded"

        # Get observability metrics
        error_health = get_health_status()
        metrics_snapshot = get_metrics_snapshot()
        
        # Get enhanced database information
        enhanced_db_info = await _get_enhanced_database_info(conn)
        
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
                **enhanced_db_info
            },
            "features": feature_flags,
            "observability": {
                "error_tracking": {
                    "status": error_health["status"],
                    "recent_errors": error_health["recent_errors"]["total"],
                    "error_severity": error_health["recent_errors"]["by_severity"],
                },
                "metrics": {
                    "uptime_seconds": metrics_snapshot["uptime_seconds"],
                    "total_requests": metrics_snapshot.get("counters", {}).get("http.requests", 0),
                    "total_errors": metrics_snapshot.get("counters", {}).get("api.errors", 0),
                    "performance_profiles": metrics_snapshot.get("performance_profiles", {}).get("count", 0),
                },
            },
        }
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Health check failed")
        return {
            "ok": False,
            "status": "error",
            "version": __version__,
            "db": {
                "path": None,
                "exists": False,
                "journal_mode": None,
                "tables": 0,
                "nodes": 0,
                "objects": 0,
            },
            "features": {"llm": False, "llm_requested": False, "analytics": False},
            "error": str(exc),
        }


@router.get("/health/metrics")
async def health_metrics(request: Request) -> dict[str, Any]:
    """
    Observability metrics endpoint with authentication.

    Returns comprehensive metrics including:
    - Request/response statistics
    - Performance timings
    - Error rates
    - Database statistics

    Authentication:
    - Requires Bearer token when AUTH_TOKEN is set
    - Always requires authentication (even for GET requests)

    Returns:
        200 with metrics data when authenticated
        401 when authentication fails
        404 when analytics is disabled
    """
    # Require authentication for metrics endpoint
    if AuthMiddleware.is_enabled():
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "authentication_required",
                    "message": "Metrics endpoint requires Bearer token authentication",
                    "hint": "Include 'Authorization: Bearer <token>' header",
                },
            )

        token = auth_header[7:]  # Remove "Bearer " prefix
        expected_token = AuthMiddleware.get_token()

        if token != expected_token:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "invalid_token",
                    "message": "Invalid authentication token",
                },
            )

    # Check if analytics/metrics are enabled
    analytics_enabled = _env_flag_enabled("ANALYTICS_ENABLED")
    if not analytics_enabled:
        raise HTTPException(status_code=404, detail="Metrics collection disabled")

    # Collect metrics from observability system
    try:
        from ..observability.metrics import get_metrics_snapshot

        observability_metrics = get_metrics_snapshot()
    except ImportError:
        observability_metrics = {}

    # Collect legacy metrics
    legacy_metrics = await asyncio.to_thread(_collect_runtime_metrics)

    # Combine metrics
    return {
        "timestamp": observability_metrics.get("timestamp", asyncio.get_event_loop().time()),
        "uptime_seconds": observability_metrics.get("uptime_seconds", 0),
        "observability": observability_metrics,
        "database": legacy_metrics,
    }


async def _get_enhanced_database_info(conn: sqlite3.Connection) -> dict[str, Any]:
    """Get enhanced database information including performance metrics."""
    enhanced_info = {}
    
    try:
        # Get database manager info
        try:
            db_manager = get_database_manager()
            enhanced_info["manager"] = await db_manager.get_database_info()
        except RuntimeError:
            enhanced_info["manager"] = {"error": "Database manager not initialized"}
        
        # Get connection pool stats
        try:
            from api.db.connection_pool import get_connection_pool
            pool = get_connection_pool()
            enhanced_info["connection_pool"] = pool.get_stats().__dict__
        except RuntimeError:
            enhanced_info["connection_pool"] = {"error": "Connection pool not initialized"}
        
        # Get cache stats
        try:
            cache = get_query_cache()
            enhanced_info["cache"] = await cache.get_cache_info()
        except RuntimeError:
            enhanced_info["cache"] = {"error": "Query cache not initialized"}
        
        # Get monitoring stats
        try:
            monitor = get_database_monitor()
            enhanced_info["monitoring"] = monitor.get_performance_summary()
            enhanced_info["optimization_recommendations"] = monitor.get_optimization_recommendations()
        except RuntimeError:
            enhanced_info["monitoring"] = {"error": "Database monitor not initialized"}
        
        # Get database health check
        try:
            monitor = get_database_monitor()
            health = await monitor.check_database_health(conn)
            enhanced_info["health"] = {
                "status": health.status,
                "integrity_check": health.integrity_check,
                "table_count": health.table_count,
                "index_count": health.index_count,
                "database_size_mb": health.database_size_mb,
                "wal_size_mb": health.wal_size_mb,
                "cache_hit_ratio": health.cache_hit_ratio,
                "slow_queries_count": health.slow_queries_count,
                "alerts_count": len(health.alerts)
            }
        except RuntimeError:
            enhanced_info["health"] = {"error": "Database monitor not initialized"}
        
    except Exception as e:
        logger.error(f"Error getting enhanced database info: {e}")
        enhanced_info["error"] = str(e)
    
    return enhanced_info


async def _check_database_health(conn: sqlite3.Connection) -> dict[str, Any]:
    """Check database configuration and health."""
    try:
        cursor = await anyio.to_thread.run_sync(conn.execute, "PRAGMA journal_mode")
        journal_row = await anyio.to_thread.run_sync(cursor.fetchone)
        journal_mode = (journal_row[0] if journal_row else "").lower()

        table_names = await _fetch_names(conn, "table")
        object_names = await _fetch_names(conn, "table", "view", "trigger")

        node_count = await _safe_count_nodes(conn) if "nodes" in table_names else 0

        cursor = await anyio.to_thread.run_sync(conn.execute, "PRAGMA integrity_check")
        integrity_row = await anyio.to_thread.run_sync(cursor.fetchone)
        integrity = integrity_row[0] if integrity_row else "unknown"

        db_path = Path(get_db_path())

        # Get schema version information
        schema_info = await _get_schema_version_info(conn)

        return {
            "path": str(db_path),
            "exists": db_path.exists(),
            "journal_mode": journal_mode,
            "tables": len([name for name in table_names if name]),
            "nodes": node_count,
            "integrity": integrity,
            "objects": len([name for name in object_names if name]),
            "schema_version": schema_info["applied"],
            "schema_target": schema_info["target"],
            "schema_status": schema_info["status"],
        }
    except Exception as exc:
        raise RuntimeError(f"database check failed: {exc}") from exc


def _check_features() -> dict[str, bool]:
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


def _collect_runtime_metrics() -> dict[str, Any]:
    """Get runtime metrics (non-PHI counters only)."""
    try:
        with (
            closing(sqlite3.connect(get_db_path())) as conn,
            closing(conn.cursor()) as cursor,
        ):
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


async def _fetch_names(conn: sqlite3.Connection, *object_types: str) -> list[str]:
    """Return names of SQLite objects for the given types."""
    placeholders = ",".join("?" for _ in object_types)
    query = "SELECT name FROM sqlite_master WHERE type IN (" + placeholders + ")"
    cursor = await anyio.to_thread.run_sync(conn.execute, query, object_types)
    rows = await anyio.to_thread.run_sync(cursor.fetchall)
    return [row[0] for row in rows]


async def _safe_count_nodes(conn: sqlite3.Connection) -> int:
    """Count nodes table entries with defensive error handling."""
    try:
        cursor = await anyio.to_thread.run_sync(conn.execute, "SELECT COUNT(*) FROM nodes")
        row = await anyio.to_thread.run_sync(cursor.fetchone)
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


async def _get_schema_version_info(conn: sqlite3.Connection) -> dict[str, Any]:
    """Get current schema version and migration status."""
    from api.db.migrate import get_schema_version

    try:
        # Check if migrations table exists
        cursor = await anyio.to_thread.run_sync(
            conn.execute,
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'",
        )
        table_exists = await anyio.to_thread.run_sync(cursor.fetchone) is not None

        if not table_exists:
            return {
                "applied": 0,
                "target": get_schema_version(),
                "status": "pending_initial_migration",
            }

        # Count applied migrations
        cursor = await anyio.to_thread.run_sync(
            conn.execute, "SELECT COUNT(*) FROM schema_migrations"
        )
        row = await anyio.to_thread.run_sync(cursor.fetchone)
        applied = row[0] if row else 0

        target = get_schema_version()

        if applied < target:
            status = "pending_upgrade"
        elif applied == target:
            status = "current"
        else:
            status = "unknown"  # More migrations applied than expected

        return {"applied": applied, "target": target, "status": status}
    except Exception as exc:
        logger.warning(f"Failed to get schema version: {exc}")
        return {"applied": 0, "target": get_schema_version(), "status": "error"}


@router.get("/live")
def live() -> dict[str, Any]:
    """Liveness probe: process is up."""
    return {"status": "live"}


@router.get("/ready")
async def ready(conn: sqlite3.Connection = Depends(get_db_connection)) -> dict[str, Any]:
    """Readiness probe: DB reachable and schema present."""
    cur = await anyio.to_thread.run_sync(
        conn.execute, "SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'"
    )
    ok = await anyio.to_thread.run_sync(cur.fetchone) is not None
    return {"status": "ready" if ok else "not_ready", "db": {"has_nodes_table": ok}}


@router.get("/metrics")
async def get_metrics() -> dict[str, Any]:
    """
    Get detailed metrics and performance data.
    
    Returns:
        200 with comprehensive metrics snapshot
    """
    try:
        metrics = get_metrics_snapshot()
        return {
            "timestamp": metrics["timestamp"],
            "uptime_seconds": metrics["uptime_seconds"],
            "metrics": metrics,
        }
    except Exception as exc:
        logger.exception("Failed to get metrics")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


@router.get("/errors")
async def get_error_status() -> dict[str, Any]:
    """
    Get error tracking and health status.
    
    Returns:
        200 with error tracking data
    """
    try:
        error_health = get_health_status()
        error_patterns = get_error_tracker().get_error_patterns(limit=50)
        
        return {
            "health": error_health,
            "recent_patterns": error_patterns,
        }
    except Exception as exc:
        logger.exception("Failed to get error status")
        raise HTTPException(status_code=500, detail="Failed to retrieve error status")


@router.get("/observability")
async def get_observability_status() -> dict[str, Any]:
    """
    Get comprehensive observability status.
    
    Returns:
        200 with full observability data
    """
    try:
        return {
            "health": get_health_status(),
            "metrics": get_metrics_snapshot(),
            "error_patterns": get_error_tracker().get_error_patterns(limit=100),
        }
    except Exception as exc:
        logger.exception("Failed to get observability status")
        raise HTTPException(status_code=500, detail="Failed to retrieve observability status")
