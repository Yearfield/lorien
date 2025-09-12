"""
Observability and metrics collection for Lorien.

Provides lightweight metrics collection for monitoring system health and performance.
"""

import time
import logging
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from datetime import datetime, timezone
import os

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Lightweight metrics collector for Lorien."""
    
    def __init__(self):
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
        self.gauges = defaultdict(float)
        self.enabled = os.getenv("ANALYTICS_ENABLED", "false").lower() == "true"
        
        # Rolling window for latency calculations
        self.latency_window_size = 100
        self.latency_windows = defaultdict(lambda: deque(maxlen=self.latency_window_size))
        
        # Performance thresholds
        self.thresholds = {
            "response_time_p95": 200,  # ms
            "response_time_p99": 500,  # ms
            "error_rate": 0.05,  # 5%
            "conflict_rate": 0.1,  # 10%
        }
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        if not self.enabled:
            return
        
        key = self._build_key(name, tags)
        self.counters[key] += value
        
        logger.debug(f"Counter {key} incremented by {value}")
    
    def record_timer(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None):
        """Record a timing metric."""
        if not self.enabled:
            return
        
        key = self._build_key(name, tags)
        self.timers[key].append(duration_ms)
        
        # Update rolling window
        self.latency_windows[key].append(duration_ms)
        
        logger.debug(f"Timer {key} recorded: {duration_ms}ms")
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric."""
        if not self.enabled:
            return
        
        key = self._build_key(name, tags)
        self.gauges[key] = value
        
        logger.debug(f"Gauge {key} set to {value}")
    
    def _build_key(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """Build a metric key with optional tags."""
        if not tags:
            return name
        
        tag_parts = [f"{k}={v}" for k, v in sorted(tags.items())]
        return f"{name}[{','.join(tag_parts)}]"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all current metrics."""
        if not self.enabled:
            return {"enabled": False}
        
        metrics = {
            "enabled": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "timers": {}
        }
        
        # Calculate timer statistics
        for key, values in self.timers.items():
            if values:
                metrics["timers"][key] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "p50": self._percentile(values, 50),
                    "p95": self._percentile(values, 95),
                    "p99": self._percentile(values, 99)
                }
        
        return metrics
    
    def _percentile(self, values: list, percentile: int) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int((percentile / 100) * (len(sorted_values) - 1))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status based on metrics."""
        if not self.enabled:
            return {"status": "disabled", "message": "Analytics disabled"}
        
        issues = []
        
        # Check response time thresholds
        for key, values in self.timers.items():
            if values:
                p95 = self._percentile(values, 95)
                p99 = self._percentile(values, 99)
                
                if p95 > self.thresholds["response_time_p95"]:
                    issues.append(f"High p95 latency: {key} = {p95:.1f}ms")
                
                if p99 > self.thresholds["response_time_p99"]:
                    issues.append(f"High p99 latency: {key} = {p99:.1f}ms")
        
        # Check error rates
        total_requests = sum(self.counters.values())
        error_requests = self.counters.get("http_errors", 0)
        
        if total_requests > 0:
            error_rate = error_requests / total_requests
            if error_rate > self.thresholds["error_rate"]:
                issues.append(f"High error rate: {error_rate:.2%}")
        
        # Check conflict rates
        conflict_requests = self.counters.get("conflicts", 0)
        if total_requests > 0:
            conflict_rate = conflict_requests / total_requests
            if conflict_rate > self.thresholds["conflict_rate"]:
                issues.append(f"High conflict rate: {conflict_rate:.2%}")
        
        if issues:
            return {
                "status": "degraded",
                "message": "Performance issues detected",
                "issues": issues
            }
        else:
            return {
                "status": "healthy",
                "message": "All metrics within thresholds"
            }
    
    def reset_metrics(self):
        """Reset all metrics (for testing)."""
        self.counters.clear()
        self.timers.clear()
        self.gauges.clear()
        self.latency_windows.clear()
        logger.info("Metrics reset")

# Global metrics collector instance
metrics = MetricsCollector()

def increment_counter(name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
    """Increment a counter metric."""
    metrics.increment_counter(name, value, tags)

def record_timer(name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None):
    """Record a timing metric."""
    metrics.record_timer(name, duration_ms, tags)

def set_gauge(name: str, value: float, tags: Optional[Dict[str, str]] = None):
    """Set a gauge metric."""
    metrics.set_gauge(name, value, tags)

def get_metrics() -> Dict[str, Any]:
    """Get all current metrics."""
    return metrics.get_metrics()

def get_health_status() -> Dict[str, Any]:
    """Get health status based on metrics."""
    return metrics.get_health_status()
