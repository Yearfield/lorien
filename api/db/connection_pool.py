"""
SQLite connection pool implementation for improved performance and scalability.

This module provides a connection pool that:
- Limits concurrent connections to prevent resource exhaustion
- Reuses connections to reduce overhead
- Provides connection monitoring and metrics
- Supports graceful shutdown and cleanup
"""

import asyncio
import logging
import sqlite3
import threading
import time
from collections import deque
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Optional
from weakref import WeakSet

from anyio import to_thread

logger = logging.getLogger(__name__)


@dataclass
class ConnectionPoolStats:
    """Statistics for the connection pool."""

    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    max_connections: int = 0
    connection_waits: int = 0
    connection_timeouts: int = 0
    total_queries: int = 0
    avg_query_time_ms: float = 0.0
    slow_queries: int = 0
    last_reset: float = field(default_factory=time.time)


@dataclass
class QueryMetrics:
    """Metrics for individual query performance."""

    query_count: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float("inf")
    max_time_ms: float = 0.0
    slow_query_threshold_ms: float = 100.0  # Queries slower than 100ms


class SQLiteConnectionPool:
    """
    SQLite connection pool with monitoring and performance tracking.

    Features:
    - Connection reuse and pooling
    - Connection limits and timeouts
    - Query performance monitoring
    - Graceful shutdown
    - Thread-safe operations
    """

    def __init__(
        self,
        db_path: str,
        min_connections: int = 2,
        max_connections: int = 10,
        connection_timeout: float = 30.0,
        slow_query_threshold_ms: float = 100.0,
        **sqlite_kwargs,
    ):
        """
        Initialize the connection pool.

        Args:
            db_path: Path to SQLite database file
            min_connections: Minimum number of connections to maintain
            max_connections: Maximum number of concurrent connections
            connection_timeout: Timeout for acquiring connections (seconds)
            slow_query_threshold_ms: Threshold for slow query detection
            **sqlite_kwargs: Additional SQLite connection parameters
        """
        self.db_path = db_path
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.slow_query_threshold_ms = slow_query_threshold_ms

        # Connection management
        self._pool: deque[sqlite3.Connection] = deque()
        self._active_connections: WeakSet[sqlite3.Connection] = WeakSet()
        self._lock = asyncio.Lock()
        self._closed = False

        # Statistics and monitoring
        self._stats = ConnectionPoolStats(max_connections=max_connections)
        self._query_metrics = QueryMetrics(slow_query_threshold_ms=slow_query_threshold_ms)
        self._stats_lock = threading.Lock()

        # SQLite connection parameters
        self._sqlite_kwargs = {
            "detect_types": sqlite3.PARSE_DECLTYPES,
            "isolation_level": None,  # autocommit-style
            "check_same_thread": False,
            **sqlite_kwargs,
        }

        logger.info(
            f"Initialized SQLite connection pool: {db_path}, "
            f"min={min_connections}, max={max_connections}"
        )

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new SQLite connection with proper configuration."""
        conn = sqlite3.connect(self.db_path, **self._sqlite_kwargs)
        conn.row_factory = sqlite3.Row

        # Apply pragmas for optimal performance
        pragmas = [
            "PRAGMA foreign_keys = ON;",
            "PRAGMA journal_mode = WAL;",
            "PRAGMA synchronous = NORMAL;",
            "PRAGMA cache_size = -64000;",  # 64MB cache
            "PRAGMA temp_store = MEMORY;",
            "PRAGMA mmap_size = 268435456;",  # 256MB memory mapping
            "PRAGMA optimize;",  # Optimize database periodically
        ]

        for pragma in pragmas:
            try:
                conn.execute(pragma)
            except sqlite3.Error as e:
                logger.warning(f"Failed to apply pragma '{pragma}': {e}")

        return conn

    async def _initialize_pool(self):
        """Initialize the connection pool with minimum connections."""
        async with self._lock:
            for _ in range(self.min_connections):
                conn = await to_thread.run_sync(self._create_connection)
                self._pool.append(conn)
                self._stats.total_connections += 1
                self._stats.idle_connections += 1

        logger.info(f"Initialized pool with {self.min_connections} connections")

    @asynccontextmanager
    async def get_connection(self) -> AsyncIterator[sqlite3.Connection]:
        """
        Get a connection from the pool with automatic cleanup.

        Yields:
            sqlite3.Connection: Database connection

        Raises:
            TimeoutError: If connection cannot be acquired within timeout
            RuntimeError: If pool is closed
        """
        if self._closed:
            raise RuntimeError("Connection pool is closed")

        conn = None
        acquired_time = time.time()

        try:
            # Try to acquire connection with timeout
            conn = await asyncio.wait_for(
                self._acquire_connection(), timeout=self.connection_timeout
            )

            async with self._lock:
                self._active_connections.add(conn)
                with self._stats_lock:
                    self._stats.active_connections += 1
                    self._stats.idle_connections -= 1

            # Start transaction
            await to_thread.run_sync(conn.execute, "BEGIN;")

            yield conn

            # Commit transaction
            await to_thread.run_sync(conn.execute, "COMMIT;")

        except asyncio.TimeoutError:
            with self._stats_lock:
                self._stats.connection_timeouts += 1
            raise TimeoutError(f"Failed to acquire connection within {self.connection_timeout}s")

        except Exception:
            if conn:
                try:
                    await to_thread.run_sync(conn.execute, "ROLLBACK;")
                except sqlite3.Error:
                    pass  # Ignore rollback errors
            raise

        finally:
            if conn:
                await self._release_connection(conn)

    async def _acquire_connection(self) -> sqlite3.Connection:
        """Acquire a connection from the pool, creating new ones if needed."""
        async with self._lock:
            if self._pool:
                # Reuse existing connection
                conn = self._pool.popleft()
                with self._stats_lock:
                    self._stats.idle_connections -= 1
                return conn

            # Check if we can create a new connection
            current_total = len(self._active_connections) + len(self._pool)
            if current_total < self.max_connections:
                # Create new connection
                conn = await to_thread.run_sync(self._create_connection)
                with self._stats_lock:
                    self._stats.total_connections += 1
                return conn

            # Wait for a connection to become available
            with self._stats_lock:
                self._stats.connection_waits += 1

        # Wait for connection to be released
        while True:
            await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
            async with self._lock:
                if self._pool:
                    conn = self._pool.popleft()
                    with self._stats_lock:
                        self._stats.idle_connections -= 1
                    return conn
                if self._closed:
                    raise RuntimeError("Connection pool is closed")

    async def _release_connection(self, conn: sqlite3.Connection):
        """Release a connection back to the pool."""
        try:
            # Reset connection state
            await to_thread.run_sync(conn.execute, "ROLLBACK;")
        except sqlite3.Error:
            pass  # Ignore rollback errors

        async with self._lock:
            if self._closed:
                conn.close()
                return

            # Check if connection is still valid
            try:
                await to_thread.run_sync(conn.execute, "SELECT 1;")
                self._pool.append(conn)
                with self._stats_lock:
                    self._stats.active_connections -= 1
                    self._stats.idle_connections += 1
            except sqlite3.Error:
                # Connection is invalid, close it
                conn.close()
                with self._stats_lock:
                    self._stats.active_connections -= 1
                    self._stats.total_connections -= 1

    async def execute_with_metrics(
        self, query: str, params: tuple = (), fetch: str = "none"
    ) -> Any:
        """
        Execute a query with performance monitoring.

        Args:
            query: SQL query to execute
            params: Query parameters
            fetch: How to fetch results ("one", "all", "none")

        Returns:
            Query results based on fetch parameter
        """
        start_time = time.time()

        async with self.get_connection() as conn:
            try:
                if fetch == "one":
                    result = await to_thread.run_sync(
                        lambda: conn.execute(query, params).fetchone()
                    )
                elif fetch == "all":
                    result = await to_thread.run_sync(
                        lambda: conn.execute(query, params).fetchall()
                    )
                else:
                    result = await to_thread.run_sync(lambda: conn.execute(query, params))

                # Record metrics
                query_time_ms = (time.time() - start_time) * 1000
                self._record_query_metrics(query_time_ms)

                return result

            except sqlite3.Error:
                query_time_ms = (time.time() - start_time) * 1000
                self._record_query_metrics(query_time_ms)
                logger.error(f"Query failed after {query_time_ms:.2f}ms: {query}")
                raise

    def _record_query_metrics(self, query_time_ms: float):
        """Record query performance metrics."""
        with self._stats_lock:
            self._stats.total_queries += 1

            # Update query metrics
            self._query_metrics.query_count += 1
            self._query_metrics.total_time_ms += query_time_ms
            self._query_metrics.min_time_ms = min(self._query_metrics.min_time_ms, query_time_ms)
            self._query_metrics.max_time_ms = max(self._query_metrics.max_time_ms, query_time_ms)

            # Update average query time
            if self._query_metrics.query_count > 0:
                self._stats.avg_query_time_ms = (
                    self._query_metrics.total_time_ms / self._query_metrics.query_count
                )

            # Track slow queries
            if query_time_ms > self._query_metrics.slow_query_threshold_ms:
                self._stats.slow_queries += 1

    def get_stats(self) -> ConnectionPoolStats:
        """Get current connection pool statistics."""
        with self._stats_lock:
            # Update current stats
            self._stats.active_connections = len(self._active_connections)
            self._stats.idle_connections = len(self._pool)
            return ConnectionPoolStats(
                total_connections=self._stats.total_connections,
                active_connections=self._stats.active_connections,
                idle_connections=self._stats.idle_connections,
                max_connections=self._stats.max_connections,
                connection_waits=self._stats.connection_waits,
                connection_timeouts=self._stats.connection_timeouts,
                total_queries=self._stats.total_queries,
                avg_query_time_ms=self._stats.avg_query_time_ms,
                slow_queries=self._stats.slow_queries,
                last_reset=self._stats.last_reset,
            )

    def reset_stats(self):
        """Reset connection pool statistics."""
        with self._stats_lock:
            self._stats.connection_waits = 0
            self._stats.connection_timeouts = 0
            self._stats.total_queries = 0
            self._stats.avg_query_time_ms = 0.0
            self._stats.slow_queries = 0
            self._stats.last_reset = time.time()

            # Reset query metrics
            self._query_metrics.query_count = 0
            self._query_metrics.total_time_ms = 0.0
            self._query_metrics.min_time_ms = float("inf")
            self._query_metrics.max_time_ms = 0.0

    async def close(self):
        """Close the connection pool and all connections."""
        async with self._lock:
            self._closed = True

            # Close all idle connections
            while self._pool:
                conn = self._pool.popleft()
                conn.close()

            # Wait for active connections to finish
            while self._active_connections:
                await asyncio.sleep(0.1)

            self._stats.idle_connections = 0
            logger.info("Connection pool closed")


# Global connection pool instance
_connection_pool: Optional[SQLiteConnectionPool] = None


def get_connection_pool() -> SQLiteConnectionPool:
    """Get the global connection pool instance."""
    global _connection_pool
    if _connection_pool is None:
        raise RuntimeError("Connection pool not initialized")
    return _connection_pool


async def initialize_connection_pool(
    db_path: str,
    min_connections: int = 2,
    max_connections: int = 10,
    connection_timeout: float = 30.0,
    slow_query_threshold_ms: float = 100.0,
    **sqlite_kwargs,
) -> SQLiteConnectionPool:
    """
    Initialize the global connection pool.

    Args:
        db_path: Path to SQLite database file
        min_connections: Minimum number of connections to maintain
        max_connections: Maximum number of concurrent connections
        connection_timeout: Timeout for acquiring connections (seconds)
        slow_query_threshold_ms: Threshold for slow query detection
        **sqlite_kwargs: Additional SQLite connection parameters

    Returns:
        Initialized SQLiteConnectionPool instance
    """
    global _connection_pool

    if _connection_pool is not None:
        logger.warning("Connection pool already initialized")
        return _connection_pool

    _connection_pool = SQLiteConnectionPool(
        db_path=db_path,
        min_connections=min_connections,
        max_connections=max_connections,
        connection_timeout=connection_timeout,
        slow_query_threshold_ms=slow_query_threshold_ms,
        **sqlite_kwargs,
    )

    await _connection_pool._initialize_pool()
    logger.info("Global connection pool initialized")

    return _connection_pool


async def close_connection_pool():
    """Close the global connection pool."""
    global _connection_pool

    if _connection_pool is not None:
        await _connection_pool.close()
        _connection_pool = None
        logger.info("Global connection pool closed")
