"""
Database query caching system for improved performance.

This module provides:
- Intelligent query result caching
- Cache invalidation strategies
- Cache performance monitoring
- TTL-based cache expiration
- Cache statistics and metrics
"""

import asyncio
import hashlib
import json
import logging
import pickle
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Set

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache invalidation strategies."""

    TTL = "ttl"  # Time-based expiration
    LRU = "lru"  # Least recently used
    MANUAL = "manual"  # Manual invalidation only
    SMART = "smart"  # Combination of TTL and pattern-based invalidation


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: Optional[int] = None
    tags: set[str] = field(default_factory=set)
    size_bytes: int = 0


@dataclass
class CacheStats:
    """Cache performance statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    invalidations: int = 0
    total_entries: int = 0
    total_size_bytes: int = 0
    hit_ratio: float = 0.0
    avg_access_time_ms: float = 0.0
    last_reset: datetime = field(default_factory=datetime.now)


class QueryCache:
    """
    Intelligent database query result cache.

    Features:
    - TTL-based expiration
    - LRU eviction
    - Pattern-based invalidation
    - Cache statistics
    - Memory usage tracking
    - Thread-safe operations
    """

    def __init__(
        self,
        max_size_bytes: int = 100 * 1024 * 1024,  # 100MB default
        default_ttl_seconds: int = 300,  # 5 minutes default
        max_entries: int = 10000,
        strategy: CacheStrategy = CacheStrategy.SMART,
        enable_compression: bool = True,
    ):
        """
        Initialize query cache.

        Args:
            max_size_bytes: Maximum cache size in bytes
            default_ttl_seconds: Default TTL for cache entries
            max_entries: Maximum number of cache entries
            strategy: Cache invalidation strategy
            enable_compression: Whether to compress cache values
        """
        self.max_size_bytes = max_size_bytes
        self.default_ttl_seconds = default_ttl_seconds
        self.max_entries = max_entries
        self.strategy = strategy
        self.enable_compression = enable_compression

        # Cache storage (OrderedDict for LRU behavior)
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = asyncio.Lock()

        # Statistics
        self._stats = CacheStats()
        self._stats_lock = asyncio.Lock()

        # Invalidation patterns
        self._invalidation_patterns: dict[str, set[str]] = {}

        logger.info(
            f"Query cache initialized: max_size={max_size_bytes/1024/1024:.1f}MB, "
            f"max_entries={max_entries}, strategy={strategy.value}"
        )

    def _generate_cache_key(self, query: str, params: tuple = (), **kwargs) -> str:
        """
        Generate a cache key for a query and parameters.

        Args:
            query: SQL query
            params: Query parameters
            **kwargs: Additional cache key components

        Returns:
            Cache key string
        """
        # Normalize query
        normalized_query = " ".join(query.strip().split())

        # Create hash of query + params + kwargs
        key_data = {"query": normalized_query, "params": params, **kwargs}

        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def _serialize_value(self, value: Any) -> bytes:
        """Serialize cache value for storage."""
        try:
            if self.enable_compression:
                import gzip

                serialized = pickle.dumps(value)
                compressed = gzip.compress(serialized)
                return compressed
            else:
                return pickle.dumps(value)
        except Exception as e:
            logger.warning(f"Failed to serialize cache value: {e}")
            return pickle.dumps(value)

    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize cache value from storage."""
        try:
            if self.enable_compression:
                import gzip

                decompressed = gzip.decompress(data)
                return pickle.loads(decompressed)
            else:
                return pickle.loads(data)
        except Exception as e:
            logger.warning(f"Failed to deserialize cache value: {e}")
            return pickle.loads(data)

    def _calculate_size(self, entry: CacheEntry) -> int:
        """Calculate the size of a cache entry."""
        try:
            serialized = self._serialize_value(entry.value)
            return len(serialized) + len(entry.key.encode()) + 200  # Overhead estimate
        except Exception:
            return 1000  # Fallback size estimate

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if a cache entry has expired."""
        if entry.ttl_seconds is None:
            return False

        age = (datetime.now() - entry.created_at).total_seconds()
        return age > entry.ttl_seconds

    async def get(
        self, query: str, params: tuple = (), tags: Optional[set[str]] = None, **kwargs
    ) -> Optional[Any]:
        """
        Get a cached query result.

        Args:
            query: SQL query
            params: Query parameters
            tags: Cache tags for invalidation
            **kwargs: Additional cache key components

        Returns:
            Cached result or None if not found/expired
        """
        cache_key = self._generate_cache_key(query, params, **kwargs)
        start_time = time.time()

        async with self._lock:
            if cache_key not in self._cache:
                async with self._stats_lock:
                    self._stats.misses += 1
                return None

            entry = self._cache[cache_key]

            # Check if expired
            if self._is_expired(entry):
                del self._cache[cache_key]
                async with self._stats_lock:
                    self._stats.misses += 1
                return None

            # Update access information
            entry.last_accessed = datetime.now()
            entry.access_count += 1

            # Move to end (LRU behavior)
            self._cache.move_to_end(cache_key)

            async with self._stats_lock:
                self._stats.hits += 1

            access_time = (time.time() - start_time) * 1000
            async with self._stats_lock:
                # Update average access time
                total_requests = self._stats.hits + self._stats.misses
                if total_requests > 0:
                    self._stats.avg_access_time_ms = (
                        self._stats.avg_access_time_ms * (total_requests - 1) + access_time
                    ) / total_requests

            return entry.value

    async def set(
        self,
        query: str,
        value: Any,
        params: tuple = (),
        ttl_seconds: Optional[int] = None,
        tags: Optional[set[str]] = None,
        **kwargs,
    ) -> bool:
        """
        Cache a query result.

        Args:
            query: SQL query
            value: Result to cache
            params: Query parameters
            ttl_seconds: Time-to-live in seconds
            tags: Cache tags for invalidation
            **kwargs: Additional cache key components

        Returns:
            True if successfully cached, False otherwise
        """
        if value is None:
            return False

        cache_key = self._generate_cache_key(query, params, **kwargs)
        now = datetime.now()

        # Create cache entry
        entry = CacheEntry(
            key=cache_key,
            value=value,
            created_at=now,
            last_accessed=now,
            access_count=1,
            ttl_seconds=ttl_seconds or self.default_ttl_seconds,
            tags=tags or set(),
        )

        # Calculate size
        entry.size_bytes = self._calculate_size(entry)

        async with self._lock:
            # Check if we need to make space
            await self._make_space(entry.size_bytes)

            # Store entry
            self._cache[cache_key] = entry
            self._cache.move_to_end(cache_key)

            # Update invalidation patterns
            if tags:
                for tag in tags:
                    if tag not in self._invalidation_patterns:
                        self._invalidation_patterns[tag] = set()
                    self._invalidation_patterns[tag].add(cache_key)

            async with self._stats_lock:
                self._stats.total_entries = len(self._cache)
                self._stats.total_size_bytes = sum(e.size_bytes for e in self._cache.values())

        logger.debug(f"Cached query result: {cache_key[:16]}... (size: {entry.size_bytes} bytes)")
        return True

    async def _make_space(self, required_bytes: int):
        """Make space in cache by evicting entries."""
        current_size = sum(e.size_bytes for e in self._cache.values())

        # Check if we need to evict entries
        while (
            len(self._cache) >= self.max_entries
            or current_size + required_bytes > self.max_size_bytes
        ):
            if not self._cache:
                break

            # Evict least recently used entry
            oldest_key, oldest_entry = self._cache.popitem(last=False)
            current_size -= oldest_entry.size_bytes

            # Remove from invalidation patterns
            for tag in oldest_entry.tags:
                if tag in self._invalidation_patterns:
                    self._invalidation_patterns[tag].discard(oldest_key)
                    if not self._invalidation_patterns[tag]:
                        del self._invalidation_patterns[tag]

            async with self._stats_lock:
                self._stats.evictions += 1

            logger.debug(f"Evicted cache entry: {oldest_key[:16]}...")

    async def invalidate(self, pattern: str = None, tags: Optional[Set[str]] = None):
        """
        Invalidate cache entries.

        Args:
            pattern: Invalidation pattern (SQL query pattern)
            tags: Tags to invalidate
        """
        async with self._lock:
            invalidated_count = 0

            if tags:
                # Invalidate by tags
                for tag in tags:
                    if tag in self._invalidation_patterns:
                        for cache_key in list(self._invalidation_patterns[tag]):
                            if cache_key in self._cache:
                                del self._cache[cache_key]
                                invalidated_count += 1
                        del self._invalidation_patterns[tag]

            if pattern:
                # Invalidate by query pattern
                pattern_lower = pattern.lower()
                keys_to_remove = []

                for cache_key, entry in self._cache.items():
                    if pattern_lower in entry.value.get("query", "").lower():
                        keys_to_remove.append(cache_key)

                for key in keys_to_remove:
                    del self._cache[key]
                    invalidated_count += 1

            async with self._stats_lock:
                self._stats.invalidations += invalidated_count
                self._stats.total_entries = len(self._cache)
                self._stats.total_size_bytes = sum(e.size_bytes for e in self._cache.values())

            logger.info(f"Invalidated {invalidated_count} cache entries")

    async def clear(self):
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            self._invalidation_patterns.clear()

            async with self._stats_lock:
                self._stats.total_entries = 0
                self._stats.total_size_bytes = 0

            logger.info("Cache cleared")

    async def cleanup_expired(self):
        """Remove expired entries from cache."""
        async with self._lock:
            expired_keys = []

            for cache_key, entry in self._cache.items():
                if self._is_expired(entry):
                    expired_keys.append(cache_key)

            for key in expired_keys:
                del self._cache[key]

            async with self._stats_lock:
                self._stats.total_entries = len(self._cache)
                self._stats.total_size_bytes = sum(e.size_bytes for e in self._cache.values())

            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

    def get_stats(self) -> CacheStats:
        """Get cache performance statistics."""
        with asyncio.Lock():
            # Update hit ratio
            total_requests = self._stats.hits + self._stats.misses
            self._stats.hit_ratio = self._stats.hits / total_requests if total_requests > 0 else 0.0

            return CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                evictions=self._stats.evictions,
                invalidations=self._stats.invalidations,
                total_entries=len(self._cache),
                total_size_bytes=sum(e.size_bytes for e in self._cache.values()),
                hit_ratio=self._stats.hit_ratio,
                avg_access_time_ms=self._stats.avg_access_time_ms,
                last_reset=self._stats.last_reset,
            )

    def reset_stats(self):
        """Reset cache statistics."""
        with asyncio.Lock():
            self._stats = CacheStats()

    async def get_cache_info(self) -> dict[str, Any]:
        """Get detailed cache information."""
        async with self._lock:
            return {
                "cache_size_bytes": sum(e.size_bytes for e in self._cache.values()),
                "cache_entries": len(self._cache),
                "max_size_bytes": self.max_size_bytes,
                "max_entries": self.max_entries,
                "strategy": self.strategy.value,
                "compression_enabled": self.enable_compression,
                "invalidation_patterns": len(self._invalidation_patterns),
                "stats": self.get_stats().__dict__,
            }


# Global cache instance
_cache: Optional[QueryCache] = None


def get_query_cache() -> QueryCache:
    """Get the global query cache instance."""
    global _cache
    if _cache is None:
        _cache = QueryCache()
    return _cache


def initialize_query_cache(
    max_size_bytes: int = 100 * 1024 * 1024,
    default_ttl_seconds: int = 300,
    max_entries: int = 10000,
    strategy: CacheStrategy = CacheStrategy.SMART,
) -> QueryCache:
    """
    Initialize the global query cache.

    Args:
        max_size_bytes: Maximum cache size in bytes
        default_ttl_seconds: Default TTL for cache entries
        max_entries: Maximum number of cache entries
        strategy: Cache invalidation strategy

    Returns:
        Initialized QueryCache instance
    """
    global _cache

    if _cache is not None:
        logger.warning("Query cache already initialized")
        return _cache

    _cache = QueryCache(
        max_size_bytes=max_size_bytes,
        default_ttl_seconds=default_ttl_seconds,
        max_entries=max_entries,
        strategy=strategy,
    )

    logger.info("Global query cache initialized")
    return _cache


# Cache decorator for easy use
def cached_query(
    ttl_seconds: int = 300,
    tags: Optional[set[str]] = None,
    cache_condition: Optional[callable] = None,
):
    """
    Decorator for caching database query results.

    Args:
        ttl_seconds: Cache TTL in seconds
        tags: Cache tags for invalidation
        cache_condition: Function to determine if result should be cached

    Example:
        @cached_query(ttl_seconds=600, tags={'nodes', 'tree'})
        async def get_nodes(parent_id: int):
            # Database query implementation
            pass
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache = get_query_cache()

            # Generate cache key from function name and arguments
            cache_key_data = {"function": func.__name__, "args": args, "kwargs": kwargs}
            cache_key = json.dumps(cache_key_data, sort_keys=True, default=str)

            # Try to get from cache
            cached_result = await cache.get(query=cache_key, tags=tags)

            if cached_result is not None:
                return cached_result

            # Execute function
            result = await func(*args, **kwargs)

            # Check if we should cache the result
            should_cache = True
            if cache_condition:
                should_cache = cache_condition(result)

            if should_cache and result is not None:
                await cache.set(query=cache_key, value=result, ttl_seconds=ttl_seconds, tags=tags)

            return result

        return wrapper

    return decorator
