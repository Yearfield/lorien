"""
Enhanced metrics collection and aggregation system.

Provides:
- In-memory metrics storage and export
- Performance monitoring and profiling
- Business metrics tracking
- Health and availability metrics
- Integration with external monitoring systems
- Non-PHI safe for observability platforms
"""

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Optional


@dataclass
class MetricValue:
    """A single metric value with timestamp and metadata."""

    value: float
    timestamp: float = field(default_factory=time.time)
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceProfile:
    """Performance profiling data for operations."""

    operation_name: str
    start_time: float
    end_time: float
    duration_ms: float
    tags: dict[str, str]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds."""
        return self.duration_ms / 1000.0


class BusinessMetrics:
    """Business-specific metrics for decision tree operations."""

    def __init__(self):
        self._metrics_collector = MetricsCollector()

    def track_tree_operation(
        self, operation: str, success: bool, duration_ms: float, **tags
    ) -> None:
        """Track tree-related operations."""
        self._metrics_collector.increment_counter(
            "business.tree_operations",
            tags={**tags, "operation": operation, "success": str(success)},
        )
        self._metrics_collector.record_timer(
            "business.tree_operation_duration", duration_ms, tags={**tags, "operation": operation}
        )

    def track_node_operations(self, operation: str, node_count: int, **tags) -> None:
        """Track node-related operations."""
        self._metrics_collector.increment_counter(
            "business.node_operations", value=node_count, tags={**tags, "operation": operation}
        )

    def track_export_operations(self, format_type: str, record_count: int, **tags) -> None:
        """Track export operations."""
        self._metrics_collector.increment_counter(
            "business.exports", tags={**tags, "format": format_type}
        )
        self._metrics_collector.record_histogram(
            "business.export_record_count", record_count, tags={**tags, "format": format_type}
        )

    def track_import_operations(
        self, format_type: str, record_count: int, success: bool, **tags
    ) -> None:
        """Track import operations."""
        self._metrics_collector.increment_counter(
            "business.imports", tags={**tags, "format": format_type, "success": str(success)}
        )
        if success:
            self._metrics_collector.record_histogram(
                "business.import_record_count", record_count, tags={**tags, "format": format_type}
            )


class MetricsCollector:
    """
    Enhanced thread-safe metrics collector.

    Stores counters, gauges, histograms, and performance profiles in memory.
    Provides comprehensive monitoring capabilities.
    """

    def __init__(self):
        """Initialize the metrics collector."""
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._timers: dict[str, list[float]] = defaultdict(list)
        self._performance_profiles: list[PerformanceProfile] = []
        self._lock = Lock()

        # Track when metrics were last reset
        self._start_time = time.time()

        # Performance tracking limits
        self._max_profiles = 1000  # Keep last 1000 performance profiles

    def increment_counter(
        self, name: str, value: float = 1.0, tags: Optional[dict[str, str]] = None
    ):
        """
        Increment a counter metric.

        Args:
            name: Metric name
            value: Amount to increment by
            tags: Optional tags for grouping
        """
        with self._lock:
            key = self._make_key(name, tags)
            self._counters[key] += value

    def set_gauge(self, name: str, value: float, tags: Optional[dict[str, str]] = None) -> None:
        """
        Set a gauge metric (current value).

        Args:
            name: Metric name
            value: Current value
            tags: Optional tags for grouping
        """
        with self._lock:
            key = self._make_key(name, tags)
            self._gauges[key] = value

    def record_histogram(
        self, name: str, value: float, tags: Optional[dict[str, str]] = None
    ) -> None:
        """
        Record a value in a histogram.

        Args:
            name: Metric name
            value: Value to record
            tags: Optional tags for grouping
        """
        with self._lock:
            key = self._make_key(name, tags)
            self._histograms[key].append(value)

            # Limit histogram size to prevent memory growth
            if len(self._histograms[key]) > 1000:
                self._histograms[key] = self._histograms[key][-1000:]

    def record_timer(
        self, name: str, duration_ms: float, tags: Optional[dict[str, str]] = None
    ) -> None:
        """
        Record a timing measurement.

        Args:
            name: Metric name
            duration_ms: Duration in milliseconds
            tags: Optional tags for grouping
        """
        self.record_histogram(name, duration_ms, tags)
        with self._lock:
            key = self._make_key(name, tags)
            self._timers[key].append(duration_ms)

            # Limit timer size
            if len(self._timers[key]) > 1000:
                self._timers[key] = self._timers[key][-1000:]

    def record_performance_profile(self, profile: PerformanceProfile) -> None:
        """
        Record a performance profile.

        Args:
            profile: Performance profile data
        """
        with self._lock:
            self._performance_profiles.append(profile)

            # Limit profile count
            if len(self._performance_profiles) > self._max_profiles:
                self._performance_profiles = self._performance_profiles[-self._max_profiles :]

    def start_performance_timer(self, operation_name: str, **tags) -> "PerformanceTimer":
        """
        Start a performance timer for an operation.

        Args:
            operation_name: Name of the operation being timed
            **tags: Additional tags for the operation

        Returns:
            PerformanceTimer context manager
        """
        return PerformanceTimer(self, operation_name, tags)

    def get_snapshot(self) -> dict[str, Any]:
        """
        Get a snapshot of all metrics.

        Returns:
            Dictionary with all current metrics
        """
        with self._lock:
            return {
                "timestamp": time.time(),
                "uptime_seconds": time.time() - self._start_time,
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    key: self._calculate_histogram_stats(values)
                    for key, values in self._histograms.items()
                },
                "timers": {
                    key: self._calculate_histogram_stats(values)
                    for key, values in self._timers.items()
                },
                "performance_profiles": {
                    "count": len(self._performance_profiles),
                    "recent_operations": [
                        {
                            "operation": profile.operation_name,
                            "duration_ms": profile.duration_ms,
                            "tags": profile.tags,
                            "timestamp": profile.start_time,
                        }
                        for profile in self._performance_profiles[-10:]  # Last 10 operations
                    ],
                },
            }

    def reset(self) -> None:
        """Reset all metrics (useful for testing)."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._timers.clear()
            self._performance_profiles.clear()
            self._start_time = time.time()

    def _make_key(self, name: str, tags: Optional[dict[str, str]]) -> str:
        """Create a unique key from metric name and tags."""
        if not tags:
            return name

        # Sort tags for consistent keys
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}{{{tag_str}}}"

    def _calculate_histogram_stats(self, values: list[float]) -> dict[str, float]:
        """Calculate statistics for a histogram."""
        if not values:
            return {
                "count": 0,
                "sum": 0,
                "min": 0,
                "max": 0,
                "mean": 0,
                "p50": 0,
                "p95": 0,
                "p99": 0,
            }

        sorted_values = sorted(values)
        count = len(sorted_values)
        total = sum(sorted_values)

        return {
            "count": count,
            "sum": total,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "mean": total / count,
            "p50": self._percentile(sorted_values, 0.50),
            "p95": self._percentile(sorted_values, 0.95),
            "p99": self._percentile(sorted_values, 0.99),
        }

    def _percentile(self, sorted_values: list[float], percentile: float) -> float:
        """Calculate a percentile from sorted values."""
        if not sorted_values:
            return 0.0

        index = int(len(sorted_values) * percentile)
        index = min(index, len(sorted_values) - 1)
        return sorted_values[index]


# Global metrics collector instance
_metrics_collector = MetricsCollector()


# Convenience functions


def increment_counter(name: str, value: float = 1.0, tags: Optional[dict[str, str]] = None) -> None:
    """Increment a counter metric."""
    _metrics_collector.increment_counter(name, value, tags)


def set_gauge(name: str, value: float, tags: Optional[dict[str, str]] = None) -> None:
    """Set a gauge metric."""
    _metrics_collector.set_gauge(name, value, tags)


def record_histogram(name: str, value: float, tags: Optional[dict[str, str]] = None) -> None:
    """Record a histogram value."""
    _metrics_collector.record_histogram(name, value, tags)


def record_timer(name: str, duration_ms: float, tags: Optional[dict[str, str]] = None) -> None:
    """Record a timer value."""
    _metrics_collector.record_timer(name, duration_ms, tags)


def get_metrics_snapshot() -> dict[str, Any]:
    """Get a snapshot of all metrics."""
    return _metrics_collector.get_snapshot()


def reset_metrics() -> None:
    """Reset all metrics (for testing)."""
    _metrics_collector.reset()


# Performance timer context manager
class PerformanceTimer:
    """Context manager for timing operations."""

    def __init__(self, collector: MetricsCollector, operation_name: str, tags: dict[str, str]):
        self.collector = collector
        self.operation_name = operation_name
        self.tags = tags
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            end_time = time.time()
            duration_ms = (end_time - self.start_time) * 1000

            # Create performance profile
            profile = PerformanceProfile(
                operation_name=self.operation_name,
                start_time=self.start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                tags=self.tags,
                metadata={
                    "exception": exc_type.__name__ if exc_type else None,
                    "success": exc_type is None,
                },
            )

            # Record the profile
            self.collector.record_performance_profile(profile)

            # Also record as timer
            self.collector.record_timer(
                f"performance.{self.operation_name}",
                duration_ms,
                self.tags,
            )


# Global business metrics instance
_business_metrics: Optional[BusinessMetrics] = None


def get_business_metrics() -> BusinessMetrics:
    """Get the global business metrics instance."""
    global _business_metrics
    if _business_metrics is None:
        _business_metrics = BusinessMetrics()
    return _business_metrics


# Performance timing decorator
def time_operation(operation_name: str, **tags) -> Any:
    """Decorator to time function execution."""

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            async def async_wrapper(*args, **kwargs):
                with _metrics_collector.start_performance_timer(operation_name, **tags):
                    return await func(*args, **kwargs)

            return async_wrapper
        else:

            def sync_wrapper(*args, **kwargs):
                with _metrics_collector.start_performance_timer(operation_name, **tags):
                    return func(*args, **kwargs)

            return sync_wrapper

    return decorator
