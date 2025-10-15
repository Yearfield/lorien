"""
Enhanced tree repository with caching, monitoring, and performance optimizations.

This repository extends the base TreeRepository with:
- Query result caching
- Performance monitoring
- Connection pooling
- Query optimization
- Error tracking and recovery
"""

import asyncio
import logging
import sqlite3
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from contextlib import asynccontextmanager

from api.db.connection_pool import get_connection_pool
from api.db.cache import get_query_cache, cached_query
from api.db.monitoring import get_database_monitor
from api.repositories.tree_repo import TreeRepository

logger = logging.getLogger(__name__)


class EnhancedTreeRepository:
    """
    Enhanced tree repository with performance optimizations.
    
    Features:
    - Connection pooling
    - Query result caching
    - Performance monitoring
    - Automatic query optimization
    - Error tracking and recovery
    """
    
    def __init__(self, use_cache: bool = True, use_monitoring: bool = True):
        """
        Initialize enhanced repository.
        
        Args:
            use_cache: Whether to enable query caching
            use_monitoring: Whether to enable performance monitoring
        """
        self.use_cache = use_cache
        self.use_monitoring = use_monitoring
        
        # Get service instances
        self._cache = get_query_cache() if use_cache else None
        self._monitor = get_database_monitor() if use_monitoring else None
        
        # Cache tags for different data types
        self._cache_tags = {
            'nodes': {'tree', 'nodes'},
            'parents': {'tree', 'parents'},
            'children': {'tree', 'children'},
            'triage': {'tree', 'triage'},
            'red_flags': {'tree', 'red_flags'},
            'stats': {'tree', 'stats'}
        }
        
        logger.info(f"Enhanced repository initialized: cache={use_cache}, monitoring={use_monitoring}")
    
    @asynccontextmanager
    async def _get_connection(self):
        """Get database connection with monitoring."""
        start_time = time.time()
        
        try:
            pool = get_connection_pool()
            async with pool.get_connection() as conn:
                yield conn
        except Exception as e:
            if self._monitor:
                self._monitor.record_query_execution(
                    query="connection_error",
                    execution_time_ms=(time.time() - start_time) * 1000,
                    error=str(e)
                )
            raise
    
    async def _execute_query(
        self,
        query: str,
        params: Tuple = (),
        fetch: str = "all",
        cache_key: Optional[str] = None,
        cache_tags: Optional[Set[str]] = None,
        cache_ttl: int = 300
    ) -> Any:
        """
        Execute a query with caching and monitoring.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            fetch: How to fetch results ("one", "all", "none")
            cache_key: Optional cache key override
            cache_tags: Cache tags for invalidation
            cache_ttl: Cache TTL in seconds
            
        Returns:
            Query results
        """
        start_time = time.time()
        
        # Try cache first
        if self.use_cache and self._cache and cache_key:
            cached_result = await self._cache.get(
                query=cache_key,
                params=params,
                tags=cache_tags
            )
            if cached_result is not None:
                logger.debug(f"Cache hit for query: {query[:50]}...")
                return cached_result
        
        # Execute query
        result = None
        error = None
        
        try:
            async with self._get_connection() as conn:
                if fetch == "one":
                    result = await asyncio.to_thread(
                        lambda: conn.execute(query, params).fetchone()
                    )
                elif fetch == "all":
                    result = await asyncio.to_thread(
                        lambda: conn.execute(query, params).fetchall()
                    )
                else:
                    result = await asyncio.to_thread(
                        lambda: conn.execute(query, params)
                    )
        
        except Exception as e:
            error = str(e)
            logger.error(f"Query execution failed: {e}")
            raise
        
        finally:
            # Record metrics
            execution_time_ms = (time.time() - start_time) * 1000
            
            if self._monitor:
                self._monitor.record_query_execution(
                    query=query,
                    execution_time_ms=execution_time_ms,
                    error=error
                )
        
        # Cache result
        if self.use_cache and self._cache and cache_key and result is not None:
            await self._cache.set(
                query=cache_key,
                value=result,
                params=params,
                ttl_seconds=cache_ttl,
                tags=cache_tags
            )
            logger.debug(f"Cached query result: {query[:50]}...")
        
        return result
    
    # Optimized query methods with caching
    
    async def get_node_by_id(self, node_id: int) -> Optional[Dict[str, Any]]:
        """Get a node by ID with caching."""
        query = "SELECT * FROM nodes WHERE id = ?"
        cache_key = f"node_by_id_{node_id}"
        
        result = await self._execute_query(
            query=query,
            params=(node_id,),
            fetch="one",
            cache_key=cache_key,
            cache_tags=self._cache_tags['nodes'],
            cache_ttl=600  # 10 minutes for individual nodes
        )
        
        return dict(result) if result else None
    
    async def get_children_by_parent_id(self, parent_id: int) -> List[Dict[str, Any]]:
        """Get children of a parent with caching."""
        query = """
            SELECT * FROM nodes 
            WHERE parent_id = ? 
            ORDER BY slot ASC
        """
        cache_key = f"children_by_parent_{parent_id}"
        
        results = await self._execute_query(
            query=query,
            params=(parent_id,),
            fetch="all",
            cache_key=cache_key,
            cache_tags=self._cache_tags['children'],
            cache_ttl=300  # 5 minutes for children lists
        )
        
        return [dict(row) for row in results]
    
    async def get_parents_by_depth(self, depth: int) -> List[Dict[str, Any]]:
        """Get all parents at a specific depth with caching."""
        query = """
            SELECT * FROM nodes 
            WHERE depth = ? AND parent_id IS NOT NULL
            ORDER BY id ASC
        """
        cache_key = f"parents_by_depth_{depth}"
        
        results = await self._execute_query(
            query=query,
            params=(depth,),
            fetch="all",
            cache_key=cache_key,
            cache_tags=self._cache_tags['parents'],
            cache_ttl=180  # 3 minutes for parent lists
        )
        
        return [dict(row) for row in results]
    
    async def get_next_incomplete_parent(self) -> Optional[Dict[str, Any]]:
        """Get next incomplete parent with caching."""
        query = """
            SELECT n.* FROM nodes n
            WHERE n.depth < 5 AND n.parent_id IS NOT NULL
            AND (
                SELECT COUNT(*) FROM nodes c 
                WHERE c.parent_id = n.id
            ) < 5
            ORDER BY n.id ASC
            LIMIT 1
        """
        cache_key = "next_incomplete_parent"
        
        result = await self._execute_query(
            query=query,
            fetch="one",
            cache_key=cache_key,
            cache_tags=self._cache_tags['parents'],
            cache_ttl=60  # 1 minute for dynamic queries
        )
        
        return dict(result) if result else None
    
    async def get_tree_statistics(self) -> Dict[str, Any]:
        """Get tree statistics with caching."""
        queries = {
            'total_nodes': "SELECT COUNT(*) as count FROM nodes",
            'nodes_by_depth': """
                SELECT depth, COUNT(*) as count 
                FROM nodes 
                GROUP BY depth 
                ORDER BY depth
            """,
            'leaf_nodes': "SELECT COUNT(*) as count FROM nodes WHERE is_leaf = 1",
            'triage_count': "SELECT COUNT(*) as count FROM triage",
            'red_flags_count': "SELECT COUNT(*) as count FROM red_flags"
        }
        
        stats = {}
        
        for stat_name, query in queries.items():
            cache_key = f"tree_stats_{stat_name}"
            
            if stat_name == 'nodes_by_depth':
                result = await self._execute_query(
                    query=query,
                    fetch="all",
                    cache_key=cache_key,
                    cache_tags=self._cache_tags['stats'],
                    cache_ttl=300
                )
                stats[stat_name] = [dict(row) for row in result]
            else:
                result = await self._execute_query(
                    query=query,
                    fetch="one",
                    cache_key=cache_key,
                    cache_tags=self._cache_tags['stats'],
                    cache_ttl=300
                )
                stats[stat_name] = dict(result)['count'] if result else 0
        
        return stats
    
    async def search_nodes(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search nodes with caching."""
        query = """
            SELECT * FROM nodes 
            WHERE label LIKE ? 
            ORDER BY label ASC 
            LIMIT ?
        """
        cache_key = f"search_nodes_{hash(search_term)}_{limit}"
        
        results = await self._execute_query(
            query=query,
            params=(f"%{search_term}%", limit),
            fetch="all",
            cache_key=cache_key,
            cache_tags=self._cache_tags['nodes'],
            cache_ttl=180  # 3 minutes for search results
        )
        
        return [dict(row) for row in results]
    
    async def get_triage_by_node_id(self, node_id: int) -> Optional[Dict[str, Any]]:
        """Get triage information for a node with caching."""
        query = "SELECT * FROM triage WHERE node_id = ?"
        cache_key = f"triage_by_node_{node_id}"
        
        result = await self._execute_query(
            query=query,
            params=(node_id,),
            fetch="one",
            cache_key=cache_key,
            cache_tags=self._cache_tags['triage'],
            cache_ttl=600  # 10 minutes for triage data
        )
        
        return dict(result) if result else None
    
    async def get_red_flags(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get red flags with caching."""
        query = "SELECT * FROM red_flags ORDER BY name ASC LIMIT ?"
        cache_key = f"red_flags_{limit}"
        
        results = await self._execute_query(
            query=query,
            params=(limit,),
            fetch="all",
            cache_key=cache_key,
            cache_tags=self._cache_tags['red_flags'],
            cache_ttl=600  # 10 minutes for red flags
        )
        
        return [dict(row) for row in results]
    
    # Write operations with cache invalidation
    
    async def create_node(self, label: str, parent_id: Optional[int] = None, 
                         depth: int = 0, slot: Optional[int] = None) -> int:
        """Create a new node and invalidate relevant caches."""
        async with self._get_connection() as conn:
            # Create node
            cursor = await asyncio.to_thread(
                lambda: conn.execute(
                    "INSERT INTO nodes (label, parent_id, depth, slot, is_leaf) VALUES (?, ?, ?, ?, ?)",
                    (label, parent_id, depth, slot, 1 if depth >= 5 else 0)
                )
            )
            node_id = cursor.lastrowid
            
            # Invalidate caches
            if self.use_cache and self._cache:
                await self._cache.invalidate(tags={'tree'})  # Invalidate all tree caches
                if parent_id:
                    await self._cache.invalidate(tags={'children'})
            
            logger.info(f"Created node {node_id}: {label}")
            return node_id
    
    async def update_node(self, node_id: int, **updates) -> bool:
        """Update a node and invalidate relevant caches."""
        if not updates:
            return False
        
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        params = list(updates.values()) + [node_id]
        
        async with self._get_connection() as conn:
            cursor = await asyncio.to_thread(
                lambda: conn.execute(
                    f"UPDATE nodes SET {set_clause}, updated_at = ? WHERE id = ?",
                    params + [time.strftime('%Y-%m-%dT%H:%M:%fZ'), node_id]
                )
            )
            
            if cursor.rowcount > 0:
                # Invalidate caches
                if self.use_cache and self._cache:
                    await self._cache.invalidate(tags={'tree'})
                    await self._cache.invalidate(tags={'nodes'})
                
                logger.info(f"Updated node {node_id}")
                return True
            
            return False
    
    async def delete_node(self, node_id: int) -> bool:
        """Delete a node and invalidate relevant caches."""
        async with self._get_connection() as conn:
            # Get parent_id before deletion for cache invalidation
            cursor = await asyncio.to_thread(
                lambda: conn.execute("SELECT parent_id FROM nodes WHERE id = ?", (node_id,))
            )
            result = await asyncio.to_thread(cursor.fetchone)
            parent_id = result[0] if result else None
            
            # Delete node (cascade will handle children and triage)
            cursor = await asyncio.to_thread(
                lambda: conn.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
            )
            
            if cursor.rowcount > 0:
                # Invalidate caches
                if self.use_cache and self._cache:
                    await self._cache.invalidate(tags={'tree'})
                    if parent_id:
                        await self._cache.invalidate(tags={'children'})
                
                logger.info(f"Deleted node {node_id}")
                return True
            
            return False
    
    async def update_triage(self, node_id: int, diagnostic_triage: str = None, 
                           actions: str = None) -> bool:
        """Update triage information and invalidate caches."""
        updates = {}
        if diagnostic_triage is not None:
            updates['diagnostic_triage'] = diagnostic_triage
        if actions is not None:
            updates['actions'] = actions
        
        if not updates:
            return False
        
        updates['updated_at'] = time.strftime('%Y-%m-%dT%H:%M:%fZ')
        
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        params = list(updates.values()) + [node_id]
        
        async with self._get_connection() as conn:
            cursor = await asyncio.to_thread(
                lambda: conn.execute(
                    f"UPDATE triage SET {set_clause} WHERE node_id = ?",
                    params
                )
            )
            
            if cursor.rowcount > 0:
                # Invalidate caches
                if self.use_cache and self._cache:
                    await self._cache.invalidate(tags={'triage'})
                
                logger.info(f"Updated triage for node {node_id}")
                return True
            
            return False
    
    # Cache management methods
    
    async def invalidate_cache(self, tags: Optional[Set[str]] = None, 
                              pattern: Optional[str] = None):
        """Invalidate cache entries."""
        if self.use_cache and self._cache:
            await self._cache.invalidate(tags=tags, pattern=pattern)
            logger.info(f"Invalidated cache: tags={tags}, pattern={pattern}")
    
    async def clear_cache(self):
        """Clear all cache entries."""
        if self.use_cache and self._cache:
            await self._cache.clear()
            logger.info("Cleared all cache entries")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        if self.use_cache and self._cache:
            return await self._cache.get_cache_info()
        return {}
    
    async def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get database monitoring statistics."""
        if self.use_monitoring and self._monitor:
            return self._monitor.get_performance_summary()
        return {}
    
    async def get_optimization_recommendations(self) -> List[str]:
        """Get database optimization recommendations."""
        if self.use_monitoring and self._monitor:
            return self._monitor.get_optimization_recommendations()
        return []
