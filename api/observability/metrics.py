"""
Metrics collection and aggregation.

Provides in-memory metrics storage and export for monitoring.
All metrics are non-PHI and safe for observability platforms.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Optional


@dataclass
class MetricValue:
    """A single metric value with timestamp."""

    value: float
    timestamp: float = field(default_factory=time.time)
    tags: dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Thread-safe metrics collector.

    Stores counters, gauges, and histograms in memory.
    """

    def __init__(self):
        """Initialize the metrics collector."""
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._timers: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

        # Track when metrics were last reset
        self._start_time = time.time()

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

    def set_gauge(self, name: str, value: float, tags: Optional[dict[str, str]] = None):
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

    def record_histogram(self, name: str, value: float, tags: Optional[dict[str, str]] = None):
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

    def record_timer(self, name: str, duration_ms: float, tags: Optional[dict[str, str]] = None):
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
            }

    def reset(self):
        """Reset all metrics (useful for testing)."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._timers.clear()
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


def increment_counter(name: str, value: float = 1.0, tags: Optional[dict[str, str]] = None):
    """Increment a counter metric."""
    _metrics_collector.increment_counter(name, value, tags)


def set_gauge(name: str, value: float, tags: Optional[dict[str, str]] = None):
    """Set a gauge metric."""
    _metrics_collector.set_gauge(name, value, tags)


def record_histogram(name: str, value: float, tags: Optional[dict[str, str]] = None):
    """Record a histogram value."""
    _metrics_collector.record_histogram(name, value, tags)


def record_timer(name: str, duration_ms: float, tags: Optional[dict[str, str]] = None):
    """Record a timer value."""
    _metrics_collector.record_timer(name, duration_ms, tags)


def get_metrics_snapshot() -> dict[str, Any]:
    """Get a snapshot of all metrics."""
    return _metrics_collector.get_snapshot()


def reset_metrics():
    """Reset all metrics (for testing)."""
    _metrics_collector.reset()
