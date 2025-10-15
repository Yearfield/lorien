"""
Database performance monitoring and alerting system.

This module provides:
- Query performance tracking and analysis
- Database health monitoring
- Performance alerts and notifications
- Query optimization recommendations
- Database metrics collection and reporting
"""

import logging
import sqlite3
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from anyio import to_thread

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class QueryAlert:
    """Database query performance alert."""

    level: AlertLevel
    message: str
    query: str
    execution_time_ms: float
    timestamp: datetime
    threshold_ms: float
    recommendations: list[str] = field(default_factory=list)


@dataclass
class DatabaseHealth:
    """Database health status."""

    status: str  # "healthy", "degraded", "critical"
    integrity_check: bool
    table_count: int
    index_count: int
    database_size_mb: float
    last_vacuum: Optional[datetime]
    wal_size_mb: float
    cache_hit_ratio: float
    lock_wait_time_ms: float
    connection_count: int
    active_transactions: int
    slow_queries_count: int
    alerts: list[QueryAlert] = field(default_factory=list)


@dataclass
class QueryMetrics:
    """Detailed query performance metrics."""

    query_hash: str
    query_text: str
    execution_count: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    last_executed: datetime
    slow_executions: int
    error_count: int
    last_error: Optional[str] = None


class DatabaseMonitor:
    """
    Database performance monitoring and alerting system.

    Features:
    - Real-time query performance tracking
    - Database health monitoring
    - Performance alerts and notifications
    - Query optimization recommendations
    - Historical performance analysis
    """

    def __init__(
        self,
        slow_query_threshold_ms: float = 100.0,
        critical_query_threshold_ms: float = 1000.0,
        health_check_interval: float = 60.0,
        metrics_retention_hours: int = 24,
        max_queries_tracked: int = 1000,
    ):
        """
        Initialize database monitor.

        Args:
            slow_query_threshold_ms: Threshold for slow query alerts
            critical_query_threshold_ms: Threshold for critical query alerts
            health_check_interval: Interval for health checks (seconds)
            metrics_retention_hours: How long to retain metrics data
            max_queries_tracked: Maximum number of unique queries to track
        """
        self.slow_query_threshold_ms = slow_query_threshold_ms
        self.critical_query_threshold_ms = critical_query_threshold_ms
        self.health_check_interval = health_check_interval
        self.metrics_retention_hours = metrics_retention_hours
        self.max_queries_tracked = max_queries_tracked

        # Query performance tracking
        self._query_metrics: dict[str, QueryMetrics] = {}
        self._query_history: deque = deque(maxlen=10000)
        self._alerts: deque = deque(maxlen=1000)

        # Health monitoring
        self._last_health_check: Optional[datetime] = None
        self._health_status: Optional[DatabaseHealth] = None
        self._monitoring_active = False

        # Performance thresholds
        self._thresholds = {
            "slow_query_ms": slow_query_threshold_ms,
            "critical_query_ms": critical_query_threshold_ms,
            "cache_hit_ratio_min": 0.95,
            "lock_wait_time_ms_max": 100.0,
            "connection_count_max": 50,
            "active_transactions_max": 20,
        }

        logger.info(f"Database monitor initialized with thresholds: {self._thresholds}")

    def start_monitoring(self):
        """Start the database monitoring system."""
        if self._monitoring_active:
            logger.warning("Database monitoring already active")
            return

        self._monitoring_active = True
        logger.info("Database monitoring started")

    def stop_monitoring(self):
        """Stop the database monitoring system."""
        self._monitoring_active = False
        logger.info("Database monitoring stopped")

    def record_query_execution(
        self, query: str, execution_time_ms: float, error: Optional[str] = None
    ):
        """
        Record a query execution for performance tracking.

        Args:
            query: SQL query that was executed
            execution_time_ms: Query execution time in milliseconds
            error: Error message if query failed
        """
        if not self._monitoring_active:
            return

        query_hash = self._hash_query(query)
        now = datetime.now()

        # Update query metrics
        if query_hash in self._query_metrics:
            metrics = self._query_metrics[query_hash]
            metrics.execution_count += 1
            metrics.total_time_ms += execution_time_ms
            metrics.avg_time_ms = metrics.total_time_ms / metrics.execution_count
            metrics.min_time_ms = min(metrics.min_time_ms, execution_time_ms)
            metrics.max_time_ms = max(metrics.max_time_ms, execution_time_ms)
            metrics.last_executed = now

            if execution_time_ms > self.slow_query_threshold_ms:
                metrics.slow_executions += 1

            if error:
                metrics.error_count += 1
                metrics.last_error = error
        else:
            # Create new query metrics
            self._query_metrics[query_hash] = QueryMetrics(
                query_hash=query_hash,
                query_text=query[:200] + "..." if len(query) > 200 else query,
                execution_count=1,
                total_time_ms=execution_time_ms,
                avg_time_ms=execution_time_ms,
                min_time_ms=execution_time_ms,
                max_time_ms=execution_time_ms,
                last_executed=now,
                slow_executions=1 if execution_time_ms > self.slow_query_threshold_ms else 0,
                error_count=1 if error else 0,
                last_error=error,
            )

        # Add to history
        self._query_history.append(
            {
                "query_hash": query_hash,
                "query": query,
                "execution_time_ms": execution_time_ms,
                "timestamp": now,
                "error": error,
            }
        )

        # Check for alerts
        self._check_query_alerts(query, execution_time_ms, error)

        # Cleanup old metrics if needed
        if len(self._query_metrics) > self.max_queries_tracked:
            self._cleanup_old_metrics()

    def _hash_query(self, query: str) -> str:
        """Create a hash for query identification."""
        # Normalize query by removing whitespace and parameter values
        normalized = " ".join(query.split())
        # Replace parameter placeholders with ?
        import re

        normalized = re.sub(r"\$\d+", "?", normalized)
        normalized = re.sub(r":\w+", "?", normalized)
        return str(hash(normalized))

    def _check_query_alerts(self, query: str, execution_time_ms: float, error: Optional[str]):
        """Check for query performance alerts."""
        if error:
            alert = QueryAlert(
                level=AlertLevel.ERROR,
                message=f"Query failed: {error}",
                query=query[:100] + "..." if len(query) > 100 else query,
                execution_time_ms=execution_time_ms,
                timestamp=datetime.now(),
                threshold_ms=0.0,
                recommendations=["Check query syntax and parameters", "Verify database schema"],
            )
            self._alerts.append(alert)
            return

        if execution_time_ms > self.critical_query_threshold_ms:
            alert = QueryAlert(
                level=AlertLevel.CRITICAL,
                message=f"Critical query performance: {execution_time_ms:.2f}ms",
                query=query[:100] + "..." if len(query) > 100 else query,
                execution_time_ms=execution_time_ms,
                timestamp=datetime.now(),
                threshold_ms=self.critical_query_threshold_ms,
                recommendations=[
                    "Consider adding database indexes",
                    "Optimize query structure",
                    "Check for missing WHERE clauses",
                    "Consider query result caching",
                ],
            )
            self._alerts.append(alert)
        elif execution_time_ms > self.slow_query_threshold_ms:
            alert = QueryAlert(
                level=AlertLevel.WARNING,
                message=f"Slow query detected: {execution_time_ms:.2f}ms",
                query=query[:100] + "..." if len(query) > 100 else query,
                execution_time_ms=execution_time_ms,
                timestamp=datetime.now(),
                threshold_ms=self.slow_query_threshold_ms,
                recommendations=[
                    "Consider adding database indexes",
                    "Review query execution plan",
                    "Check for table scans",
                ],
            )
            self._alerts.append(alert)

    def _cleanup_old_metrics(self):
        """Clean up old metrics to prevent memory growth."""
        cutoff_time = datetime.now() - timedelta(hours=self.metrics_retention_hours)

        # Remove old query metrics
        to_remove = []
        for query_hash, metrics in self._query_metrics.items():
            if metrics.last_executed < cutoff_time:
                to_remove.append(query_hash)

        for query_hash in to_remove:
            del self._query_metrics[query_hash]

        # Clean up query history
        while self._query_history and self._query_history[0]["timestamp"] < cutoff_time:
            self._query_history.popleft()

        # Clean up old alerts
        while self._alerts and self._alerts[0].timestamp < cutoff_time:
            self._alerts.popleft()

        logger.debug(f"Cleaned up {len(to_remove)} old query metrics")

    async def check_database_health(self, conn: sqlite3.Connection) -> DatabaseHealth:
        """
        Perform comprehensive database health check.

        Args:
            conn: Database connection

        Returns:
            DatabaseHealth object with current status
        """
        try:
            # Basic database info
            cursor = await to_thread.run_sync(conn.execute, "PRAGMA database_list")
            db_info = await to_thread.run_sync(cursor.fetchall)
            db_size_mb = 0.0
            for db_row in db_info:
                if db_row[1] == "main":  # Main database
                    db_path = db_row[2]
                    try:
                        import os

                        db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
                    except OSError:
                        pass

            # Integrity check
            cursor = await to_thread.run_sync(conn.execute, "PRAGMA integrity_check")
            integrity_result = await to_thread.run_sync(cursor.fetchone)
            integrity_ok = integrity_result[0] == "ok"

            # Table and index counts
            cursor = await to_thread.run_sync(
                conn.execute, "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
            )
            table_count = (await to_thread.run_sync(cursor.fetchone))[0]

            cursor = await to_thread.run_sync(
                conn.execute, "SELECT COUNT(*) FROM sqlite_master WHERE type='index'"
            )
            index_count = (await to_thread.run_sync(cursor.fetchone))[0]

            # WAL file size
            cursor = await to_thread.run_sync(conn.execute, "PRAGMA journal_mode")
            journal_mode = (await to_thread.run_sync(cursor.fetchone))[0]
            wal_size_mb = 0.0
            if journal_mode == "wal":
                try:
                    wal_path = db_path + "-wal"
                    import os

                    if os.path.exists(wal_path):
                        wal_size_mb = os.path.getsize(wal_path) / (1024 * 1024)
                except:
                    pass

            # Cache hit ratio
            cursor = await to_thread.run_sync(conn.execute, "PRAGMA cache_size")
            cache_size = (await to_thread.run_sync(cursor.fetchone))[0]
            # Note: SQLite doesn't provide direct cache hit ratio, this is a placeholder
            cache_hit_ratio = 0.95  # Would need custom implementation for real metrics

            # Connection and transaction info (approximations)
            connection_count = 1  # Current connection
            active_transactions = 1  # Current transaction

            # Determine overall health status
            status = "healthy"
            if not integrity_ok:
                status = "critical"
            elif wal_size_mb > 100:  # Large WAL file
                status = "degraded"
            elif (
                len([a for a in self._alerts if a.level in [AlertLevel.ERROR, AlertLevel.CRITICAL]])
                > 5
            ):
                status = "degraded"

            health = DatabaseHealth(
                status=status,
                integrity_check=integrity_ok,
                table_count=table_count,
                index_count=index_count,
                database_size_mb=db_size_mb,
                last_vacuum=None,  # Would need custom tracking
                wal_size_mb=wal_size_mb,
                cache_hit_ratio=cache_hit_ratio,
                lock_wait_time_ms=0.0,  # Would need custom implementation
                connection_count=connection_count,
                active_transactions=active_transactions,
                slow_queries_count=len([a for a in self._alerts if a.level == AlertLevel.WARNING]),
                alerts=list(self._alerts)[-10:],  # Last 10 alerts
            )

            self._health_status = health
            self._last_health_check = datetime.now()

            return health

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return DatabaseHealth(
                status="critical",
                integrity_check=False,
                table_count=0,
                index_count=0,
                database_size_mb=0.0,
                last_vacuum=None,
                wal_size_mb=0.0,
                cache_hit_ratio=0.0,
                lock_wait_time_ms=0.0,
                connection_count=0,
                active_transactions=0,
                slow_queries_count=0,
                alerts=[],
            )

    def get_query_metrics(self, limit: int = 50) -> list[QueryMetrics]:
        """Get query performance metrics."""
        # Sort by total execution time and return top queries
        sorted_metrics = sorted(
            self._query_metrics.values(), key=lambda x: x.total_time_ms, reverse=True
        )
        return sorted_metrics[:limit]

    def get_recent_alerts(self, limit: int = 20) -> list[QueryAlert]:
        """Get recent performance alerts."""
        return list(self._alerts)[-limit:]

    def get_performance_summary(self) -> dict[str, Any]:
        """Get overall performance summary."""
        total_queries = sum(m.execution_count for m in self._query_metrics.values())
        total_time = sum(m.total_time_ms for m in self._query_metrics.values())
        avg_query_time = total_time / total_queries if total_queries > 0 else 0

        return {
            "total_queries": total_queries,
            "unique_queries": len(self._query_metrics),
            "total_execution_time_ms": total_time,
            "avg_query_time_ms": avg_query_time,
            "slow_queries": len([a for a in self._alerts if a.level == AlertLevel.WARNING]),
            "critical_queries": len([a for a in self._alerts if a.level == AlertLevel.CRITICAL]),
            "error_queries": len([a for a in self._alerts if a.level == AlertLevel.ERROR]),
            "health_status": self._health_status.status if self._health_status else "unknown",
            "last_health_check": self._last_health_check.isoformat()
            if self._last_health_check
            else None,
        }

    def get_optimization_recommendations(self) -> list[str]:
        """Get database optimization recommendations."""
        recommendations = []

        if not self._query_metrics:
            return recommendations

        # Analyze slow queries
        slow_queries = [
            m for m in self._query_metrics.values() if m.avg_time_ms > self.slow_query_threshold_ms
        ]

        if slow_queries:
            recommendations.append(
                f"Found {len(slow_queries)} slow queries. Consider adding indexes or optimizing query structure."
            )

        # Analyze query patterns
        select_queries = [
            m
            for m in self._query_metrics.values()
            if m.query_text.strip().upper().startswith("SELECT")
        ]

        if select_queries:
            avg_select_time = sum(m.avg_time_ms for m in select_queries) / len(select_queries)
            if avg_select_time > 50:
                recommendations.append(
                    "SELECT queries are averaging high execution times. "
                    "Consider adding database indexes on frequently queried columns."
                )

        # Analyze error patterns
        error_queries = [m for m in self._query_metrics.values() if m.error_count > 0]
        if error_queries:
            recommendations.append(
                f"Found {len(error_queries)} queries with errors. "
                "Review query syntax and parameter validation."
            )

        return recommendations


# Global monitor instance
_monitor: Optional[DatabaseMonitor] = None


def get_database_monitor() -> DatabaseMonitor:
    """Get the global database monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = DatabaseMonitor()
        _monitor.start_monitoring()
    return _monitor


def initialize_database_monitor(
    slow_query_threshold_ms: float = 100.0,
    critical_query_threshold_ms: float = 1000.0,
    health_check_interval: float = 60.0,
) -> DatabaseMonitor:
    """
    Initialize the global database monitor.

    Args:
        slow_query_threshold_ms: Threshold for slow query alerts
        critical_query_threshold_ms: Threshold for critical query alerts
        health_check_interval: Interval for health checks (seconds)

    Returns:
        Initialized DatabaseMonitor instance
    """
    global _monitor

    if _monitor is not None:
        logger.warning("Database monitor already initialized")
        return _monitor

    _monitor = DatabaseMonitor(
        slow_query_threshold_ms=slow_query_threshold_ms,
        critical_query_threshold_ms=critical_query_threshold_ms,
        health_check_interval=health_check_interval,
    )
    _monitor.start_monitoring()

    logger.info("Global database monitor initialized")
    return _monitor
