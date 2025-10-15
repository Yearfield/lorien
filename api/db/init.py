"""
Database initialization and connection pool setup.

This module provides:
- Database connection pool initialization
- Performance monitoring setup
- Query cache initialization
- Database health checks
- Graceful shutdown handling
"""

import asyncio
import logging
import os
import sqlite3
from pathlib import Path
from typing import Optional

from api.db.connection_pool import initialize_connection_pool, close_connection_pool
from api.db.monitoring import initialize_database_monitor
from api.db.cache import initialize_query_cache, CacheStrategy
from api.settings import get_db_path

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database manager for initialization and lifecycle management.
    
    Handles:
    - Connection pool initialization
    - Performance monitoring setup
    - Query cache configuration
    - Database health monitoring
    - Graceful shutdown
    """
    
    def __init__(
        self,
        db_path: Optional[str] = None,
        enable_pooling: bool = True,
        enable_monitoring: bool = True,
        enable_caching: bool = True,
        pool_min_connections: int = 2,
        pool_max_connections: int = 10,
        pool_connection_timeout: float = 30.0,
        slow_query_threshold_ms: float = 100.0,
        cache_max_size_mb: int = 100,
        cache_default_ttl_seconds: int = 300
    ):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
            enable_pooling: Whether to enable connection pooling
            enable_monitoring: Whether to enable performance monitoring
            enable_caching: Whether to enable query caching
            pool_min_connections: Minimum connections in pool
            pool_max_connections: Maximum connections in pool
            pool_connection_timeout: Connection timeout in seconds
            slow_query_threshold_ms: Slow query threshold in milliseconds
            cache_max_size_mb: Maximum cache size in megabytes
            cache_default_ttl_seconds: Default cache TTL in seconds
        """
        self.db_path = db_path or get_db_path()
        self.enable_pooling = enable_pooling
        self.enable_monitoring = enable_monitoring
        self.enable_caching = enable_caching
        
        # Pool configuration
        self.pool_min_connections = pool_min_connections
        self.pool_max_connections = pool_max_connections
        self.pool_connection_timeout = pool_connection_timeout
        
        # Monitoring configuration
        self.slow_query_threshold_ms = slow_query_threshold_ms
        
        # Cache configuration
        self.cache_max_size_bytes = cache_max_size_mb * 1024 * 1024
        self.cache_default_ttl_seconds = cache_default_ttl_seconds
        
        self._initialized = False
        self._shutdown_handlers = []
        
        logger.info(f"Database manager initialized: {self.db_path}")
    
    async def initialize(self) -> bool:
        """
        Initialize database components.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Ensure database directory exists
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize connection pool if enabled
            if self.enable_pooling:
                logger.info("Initializing connection pool...")
                await initialize_connection_pool(
                    db_path=self.db_path,
                    min_connections=self.pool_min_connections,
                    max_connections=self.pool_max_connections,
                    connection_timeout=self.pool_connection_timeout,
                    slow_query_threshold_ms=self.slow_query_threshold_ms
                )
                logger.info("Connection pool initialized")
            
            # Initialize monitoring if enabled
            if self.enable_monitoring:
                logger.info("Initializing database monitoring...")
                initialize_database_monitor(
                    slow_query_threshold_ms=self.slow_query_threshold_ms,
                    critical_query_threshold_ms=self.slow_query_threshold_ms * 10,
                    health_check_interval=60.0
                )
                logger.info("Database monitoring initialized")
            
            # Initialize query cache if enabled
            if self.enable_caching:
                logger.info("Initializing query cache...")
                initialize_query_cache(
                    max_size_bytes=self.cache_max_size_bytes,
                    default_ttl_seconds=self.cache_default_ttl_seconds,
                    max_entries=10000,
                    strategy=CacheStrategy.SMART
                )
                logger.info("Query cache initialized")
            
            # Run initial database health check
            await self._perform_health_check()
            
            # Setup shutdown handlers
            self._setup_shutdown_handlers()
            
            self._initialized = True
            logger.info("Database manager initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database manager initialization failed: {e}")
            return False
    
    async def _perform_health_check(self):
        """Perform initial database health check."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Check database integrity
            cursor = conn.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()
            
            if integrity_result[0] != "ok":
                logger.warning(f"Database integrity check failed: {integrity_result[0]}")
            else:
                logger.info("Database integrity check passed")
            
            # Check if tables exist
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['nodes', 'triage', 'red_flags', 'tree_parent_version']
            missing_tables = [t for t in expected_tables if t not in tables]
            
            if missing_tables:
                logger.warning(f"Missing tables: {missing_tables}")
            else:
                logger.info("All required tables present")
            
            # Check WAL mode
            cursor = conn.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]
            logger.info(f"Journal mode: {journal_mode}")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
    
    def _setup_shutdown_handlers(self):
        """Setup graceful shutdown handlers."""
        import atexit
        
        def shutdown_handler():
            """Handle application shutdown."""
            try:
                # Run shutdown in event loop if available
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Schedule shutdown for next iteration
                        asyncio.create_task(self._shutdown())
                    else:
                        loop.run_until_complete(self._shutdown())
                except RuntimeError:
                    # No event loop, run synchronously
                    asyncio.run(self._shutdown())
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
        
        atexit.register(shutdown_handler)
        self._shutdown_handlers.append(shutdown_handler)
    
    async def _shutdown(self):
        """Perform graceful shutdown of database components."""
        logger.info("Starting database manager shutdown...")
        
        try:
            # Close connection pool
            if self.enable_pooling:
                logger.info("Closing connection pool...")
                await close_connection_pool()
                logger.info("Connection pool closed")
            
            # Clear query cache
            if self.enable_caching:
                logger.info("Clearing query cache...")
                from api.db.cache import get_query_cache
                cache = get_query_cache()
                await cache.clear()
                logger.info("Query cache cleared")
            
            # Stop monitoring
            if self.enable_monitoring:
                logger.info("Stopping database monitoring...")
                from api.db.monitoring import get_database_monitor
                monitor = get_database_monitor()
                monitor.stop_monitoring()
                logger.info("Database monitoring stopped")
            
            logger.info("Database manager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during database shutdown: {e}")
    
    def is_initialized(self) -> bool:
        """Check if database manager is initialized."""
        return self._initialized
    
    async def get_database_info(self) -> dict:
        """Get comprehensive database information."""
        info = {
            "initialized": self._initialized,
            "db_path": self.db_path,
            "components": {
                "pooling": self.enable_pooling,
                "monitoring": self.enable_monitoring,
                "caching": self.enable_caching
            }
        }
        
        try:
            # Get connection pool stats
            if self.enable_pooling:
                from api.db.connection_pool import get_connection_pool
                pool = get_connection_pool()
                info["connection_pool"] = pool.get_stats().__dict__
            
            # Get cache stats
            if self.enable_caching:
                from api.db.cache import get_query_cache
                cache = get_query_cache()
                info["cache"] = await cache.get_cache_info()
            
            # Get monitoring stats
            if self.enable_monitoring:
                from api.db.monitoring import get_database_monitor
                monitor = get_database_monitor()
                info["monitoring"] = monitor.get_performance_summary()
            
            # Get database file info
            if os.path.exists(self.db_path):
                stat = os.stat(self.db_path)
                info["database_file"] = {
                    "size_bytes": stat.st_size,
                    "size_mb": stat.st_size / (1024 * 1024),
                    "modified": stat.st_mtime
                }
            
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            info["error"] = str(e)
        
        return info


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        raise RuntimeError("Database manager not initialized")
    return _db_manager


async def initialize_database(
    db_path: Optional[str] = None,
    enable_pooling: bool = True,
    enable_monitoring: bool = True,
    enable_caching: bool = True,
    **kwargs
) -> bool:
    """
    Initialize the global database manager.
    
    Args:
        db_path: Path to SQLite database file
        enable_pooling: Whether to enable connection pooling
        enable_monitoring: Whether to enable performance monitoring
        enable_caching: Whether to enable query caching
        **kwargs: Additional configuration options
        
    Returns:
        True if initialization successful, False otherwise
    """
    global _db_manager
    
    if _db_manager is not None:
        logger.warning("Database manager already initialized")
        return True
    
    # Set default configuration from environment
    config = {
        "db_path": db_path,
        "enable_pooling": enable_pooling,
        "enable_monitoring": enable_monitoring,
        "enable_caching": enable_caching,
        "pool_min_connections": int(os.getenv("LORIEN_POOL_MIN_CONNECTIONS", "2")),
        "pool_max_connections": int(os.getenv("LORIEN_POOL_MAX_CONNECTIONS", "10")),
        "pool_connection_timeout": float(os.getenv("LORIEN_POOL_TIMEOUT", "30.0")),
        "slow_query_threshold_ms": float(os.getenv("LORIEN_SLOW_QUERY_THRESHOLD", "100.0")),
        "cache_max_size_mb": int(os.getenv("LORIEN_CACHE_SIZE_MB", "100")),
        "cache_default_ttl_seconds": int(os.getenv("LORIEN_CACHE_TTL_SECONDS", "300")),
        **kwargs
    }
    
    _db_manager = DatabaseManager(**config)
    
    success = await _db_manager.initialize()
    
    if success:
        logger.info("Global database manager initialized successfully")
    else:
        logger.error("Failed to initialize global database manager")
        _db_manager = None
    
    return success


async def shutdown_database():
    """Shutdown the global database manager."""
    global _db_manager
    
    if _db_manager is not None:
        await _db_manager._shutdown()
        _db_manager = None
        logger.info("Global database manager shutdown completed")
