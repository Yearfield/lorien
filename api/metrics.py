"""
Telemetry and metrics collection for the decision tree API.

This module provides non-PHI counters and timings for monitoring
API stability and performance.
"""

import time
import os
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from threading import Lock
import logging

# Global metrics storage
_metrics_lock = Lock()
_metrics = {
    "route_hits": defaultdict(int),
    "status_codes": defaultdict(int),
    "response_times": defaultdict(lambda: deque(maxlen=1000)),  # Rolling window
    "import_success": 0,
    "import_errors": 0,
    "export_success": 0,
    "export_errors": 0,
    "conflict_count": 0,
    "validation_errors": 0,
}

# Rolling window for response times (last 1000 requests per route)
_response_times = defaultdict(lambda: deque(maxlen=1000))

def increment_route_hit(route: str) -> None:
    """Increment hit count for a route."""
    with _metrics_lock:
        _metrics["route_hits"][route] += 1

def increment_status_code(status_code: int) -> None:
    """Increment status code counter."""
    with _metrics_lock:
        _metrics["status_codes"][status_code] += 1

def record_response_time(route: str, response_time_ms: float) -> None:
    """Record response time for a route."""
    with _metrics_lock:
        _response_times[route].append(response_time_ms)

def increment_import_success() -> None:
    """Increment import success counter."""
    with _metrics_lock:
        _metrics["import_success"] += 1

def increment_import_error() -> None:
    """Increment import error counter."""
    with _metrics_lock:
        _metrics["import_errors"] += 1

def increment_export_success() -> None:
    """Increment export success counter."""
    with _metrics_lock:
        _metrics["export_success"] += 1

def increment_export_error() -> None:
    """Increment export error counter."""
    with _metrics_lock:
        _metrics["export_errors"] += 1

def increment_conflict(route: str, parent_id: Optional[int] = None, slot: Optional[int] = None) -> None:
    """Increment conflict counter and log single line (no PHI)."""
    with _metrics_lock:
        _metrics["conflict_count"] += 1
    
    # Log single line for 409s with {route, parent_id, slot} (no labels/PHI)
    logging.info(f"409_CONFLICT: route={route}, parent_id={parent_id}, slot={slot}")

def increment_validation_error() -> None:
    """Increment validation error counter."""
    with _metrics_lock:
        _metrics["validation_errors"] += 1

def snapshot() -> Dict[str, Any]:
    """Get current metrics snapshot."""
    with _metrics_lock:
        # Calculate percentiles for response times
        response_stats = {}
        for route, times in _response_times.items():
            if times:
                sorted_times = sorted(times)
                n = len(sorted_times)
                response_stats[route] = {
                    "count": n,
                    "p50": sorted_times[n // 2] if n > 0 else 0,
                    "p95": sorted_times[min(int(n * 0.95), n - 1)] if n > 0 else 0,
                    "avg": sum(times) / n if n > 0 else 0,
                    "min": min(times) if n > 0 else 0,
                    "max": max(times) if n > 0 else 0,
                }
        
        # Convert defaultdicts to regular dicts for JSON serialization
        route_hits = dict(_metrics["route_hits"])
        status_codes = dict(_metrics["status_codes"])
        
        return {
            "route_hits": route_hits,
            "status_codes": status_codes,
            "response_times": response_stats,
            "import_success": _metrics["import_success"],
            "import_errors": _metrics["import_errors"],
            "export_success": _metrics["export_success"],
            "export_errors": _metrics["export_errors"],
            "conflict_count": _metrics["conflict_count"],
            "validation_errors": _metrics["validation_errors"],
            "uptime_seconds": time.time() - _get_start_time(),
        }

def _get_start_time() -> float:
    """Get application start time."""
    if not hasattr(_get_start_time, '_start_time'):
        _get_start_time._start_time = time.time()
    return _get_start_time._start_time

def reset() -> None:
    """Reset all metrics (for testing)."""
    global _metrics, _response_times
    with _metrics_lock:
        _metrics = {
            "route_hits": defaultdict(int),
            "status_codes": defaultdict(int),
            "response_times": defaultdict(lambda: deque(maxlen=1000)),
            "import_success": 0,
            "import_errors": 0,
            "export_success": 0,
            "export_errors": 0,
            "conflict_count": 0,
            "validation_errors": 0,
        }
        _response_times = defaultdict(lambda: deque(maxlen=1000))