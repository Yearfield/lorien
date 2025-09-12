"""
Performance optimization utilities for the decision tree application.

This module provides database indexes, caching, and streaming utilities
to ensure optimal performance as the dataset grows.
"""

import sqlite3
import logging
from typing import Dict, Any, List, Optional, Generator
from functools import lru_cache
import time
import csv
import io
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Handles database performance optimizations."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
    
    def create_performance_indexes(self) -> Dict[str, str]:
        """
        Create performance-optimized indexes for common queries.
        
        Returns:
            Dictionary of created indexes with their SQL
        """
        indexes = {
            # Depth-based queries (for tree traversal)
            'idx_nodes_depth': 'CREATE INDEX IF NOT EXISTS idx_nodes_depth ON nodes(depth)',
            
            # Slot-based queries (for children retrieval)
            'idx_nodes_slot': 'CREATE INDEX IF NOT EXISTS idx_nodes_slot ON nodes(slot)',
            
            # Parent-slot composite index (for efficient children queries)
            'idx_nodes_parent_slot': 'CREATE INDEX IF NOT EXISTS idx_nodes_parent_slot ON nodes(parent_id, slot)',
            
            # Leaf node queries (for outcomes)
            'idx_nodes_leaf': 'CREATE INDEX IF NOT EXISTS idx_nodes_leaf ON nodes(is_leaf) WHERE is_leaf = 1',
            
            # Label-based searches (for dictionary/conflict resolution)
            'idx_nodes_label': 'CREATE INDEX IF NOT EXISTS idx_nodes_label ON nodes(label)',
            
            # Depth-label composite (for duplicate detection)
            'idx_nodes_depth_label': 'CREATE INDEX IF NOT EXISTS idx_nodes_depth_label ON nodes(depth, label)',
            
            # Parent-depth composite (for tree structure queries)
            'idx_nodes_parent_depth': 'CREATE INDEX IF NOT EXISTS idx_nodes_parent_depth ON nodes(parent_id, depth)',
        }
        
        created_indexes = {}
        cursor = self.conn.cursor()
        
        for name, sql in indexes.items():
            try:
                cursor.execute(sql)
                created_indexes[name] = sql
                logger.info(f"Created index: {name}")
            except sqlite3.Error as e:
                logger.warning(f"Failed to create index {name}: {e}")
        
        self.conn.commit()
        return created_indexes
    
    def analyze_query_performance(self, query: str, params: tuple = ()) -> Dict[str, Any]:
        """
        Analyze query performance using EXPLAIN QUERY PLAN.
        
        Args:
            query: SQL query to analyze
            params: Query parameters
            
        Returns:
            Performance analysis results
        """
        cursor = self.conn.cursor()
        
        # Get query plan
        explain_query = f"EXPLAIN QUERY PLAN {query}"
        cursor.execute(explain_query, params)
        plan = cursor.fetchall()
        
        # Get query timing
        start_time = time.time()
        cursor.execute(query, params)
        results = cursor.fetchall()
        end_time = time.time()
        
        return {
            'query_plan': plan,
            'execution_time': end_time - start_time,
            'result_count': len(results),
            'query': query,
            'params': params
        }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive database statistics for performance monitoring.
        
        Returns:
            Database statistics dictionary
        """
        cursor = self.conn.cursor()
        
        # Table sizes
        cursor.execute("SELECT COUNT(*) FROM nodes")
        total_nodes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM nodes WHERE parent_id IS NULL")
        root_nodes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM nodes WHERE is_leaf = 1")
        leaf_nodes = cursor.fetchone()[0]
        
        # Depth distribution
        cursor.execute("SELECT depth, COUNT(*) FROM nodes GROUP BY depth ORDER BY depth")
        depth_distribution = dict(cursor.fetchall())
        
        # Slot distribution
        cursor.execute("SELECT slot, COUNT(*) FROM nodes WHERE slot IS NOT NULL GROUP BY slot ORDER BY slot")
        slot_distribution = dict(cursor.fetchall())
        
        # Index usage (SQLite doesn't provide this directly, but we can check if indexes exist)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='nodes'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        # Database file size (approximate)
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        db_size_bytes = page_count * page_size
        
        return {
            'total_nodes': total_nodes,
            'root_nodes': root_nodes,
            'leaf_nodes': leaf_nodes,
            'depth_distribution': depth_distribution,
            'slot_distribution': slot_distribution,
            'indexes': indexes,
            'database_size_bytes': db_size_bytes,
            'database_size_mb': round(db_size_bytes / (1024 * 1024), 2)
        }


class StreamingCSVExporter:
    """Handles streaming CSV export for large datasets."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
    
    def export_tree_streaming(self, batch_size: int = 1000) -> Generator[str, None, None]:
        """
        Stream tree data as CSV in batches to avoid memory issues.
        
        Args:
            batch_size: Number of rows to process per batch
            
        Yields:
            CSV data chunks
        """
        cursor = self.conn.cursor()
        
        # Get total count for progress tracking
        cursor.execute("SELECT COUNT(*) FROM nodes")
        total_count = cursor.fetchone()[0]
        
        # Create CSV header
        header = "id,parent_id,label,depth,slot,is_leaf\n"
        yield header
        
        # Stream data in batches
        offset = 0
        while offset < total_count:
            cursor.execute("""
                SELECT id, parent_id, label, depth, slot, is_leaf
                FROM nodes
                ORDER BY id
                LIMIT ? OFFSET ?
            """, (batch_size, offset))
            
            batch = cursor.fetchall()
            if not batch:
                break
            
            # Convert batch to CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerows(batch)
            yield output.getvalue()
            
            offset += len(batch)
            logger.info(f"Exported {offset}/{total_count} nodes")
    
    def export_children_streaming(self, parent_id: int, batch_size: int = 100) -> Generator[str, None, None]:
        """
        Stream children data for a specific parent.
        
        Args:
            parent_id: Parent node ID
            batch_size: Number of rows to process per batch
            
        Yields:
            CSV data chunks
        """
        cursor = self.conn.cursor()
        
        # Get total count for this parent
        cursor.execute("SELECT COUNT(*) FROM nodes WHERE parent_id = ?", (parent_id,))
        total_count = cursor.fetchone()[0]
        
        if total_count == 0:
            return
        
        # Create CSV header
        header = "id,parent_id,label,depth,slot,is_leaf\n"
        yield header
        
        # Stream data in batches
        offset = 0
        while offset < total_count:
            cursor.execute("""
                SELECT id, parent_id, label, depth, slot, is_leaf
                FROM nodes
                WHERE parent_id = ?
                ORDER BY slot
                LIMIT ? OFFSET ?
            """, (parent_id, batch_size, offset))
            
            batch = cursor.fetchall()
            if not batch:
                break
            
            # Convert batch to CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerows(batch)
            yield output.getvalue()
            
            offset += len(batch)


class NavigationCache:
    """In-memory cache for frequently accessed navigation data."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache = {}
        self._access_times = {}
        self._hit_count = 0
        self._miss_count = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self._cache:
            self._access_times[key] = time.time()
            self._hit_count += 1
            return self._cache[key]
        
        self._miss_count += 1
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache with LRU eviction."""
        if len(self._cache) >= self.max_size:
            self._evict_lru()
        
        self._cache[key] = value
        self._access_times[key] = time.time()
    
    def _evict_lru(self) -> None:
        """Evict least recently used item."""
        if not self._access_times:
            return
        
        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        del self._cache[lru_key]
        del self._access_times[lru_key]
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._access_times.clear()
        self._hit_count = 0
        self._miss_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._hit_count + self._miss_count
        hit_rate = (self._hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hit_count': self._hit_count,
            'miss_count': self._miss_count,
            'hit_rate_percent': round(hit_rate, 2),
            'total_requests': total_requests
        }


# Global navigation cache instance
navigation_cache = NavigationCache(max_size=1000)

@lru_cache(maxsize=100)
def get_cached_children(parent_id: int, conn_str: str) -> List[Dict[str, Any]]:
    """
    Get children for a parent with caching.
    
    Args:
        parent_id: Parent node ID
        conn_str: Connection string for cache key
        
    Returns:
        List of child nodes
    """
    # This would be called from the actual repository methods
    # The caching is handled at the repository level
    pass

def clear_navigation_cache() -> None:
    """Clear the navigation cache."""
    navigation_cache.clear()

def get_cache_stats() -> Dict[str, Any]:
    """Get navigation cache statistics."""
    return navigation_cache.get_stats()

