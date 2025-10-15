"""
Observability infrastructure for Lorien API.

Provides:
- Request/trace ID generation and propagation
- Structured JSON logging with correlation IDs
- OpenTelemetry instrumentation
- Metrics collection and export
- Error tracking and alerting
- Performance profiling
- Business metrics tracking
"""

from .context import get_request_id, get_trace_id, set_request_context
from .error_tracking import get_error_tracker, get_health_status, track_error
from .logging import get_logger, setup_logging
from .metrics import (
    get_business_metrics,
    get_metrics_snapshot,
    increment_counter,
    record_timer,
    set_gauge,
    time_operation,
)
from .middleware import ObservabilityMiddleware
from .telemetry import (
    add_span_attributes,
    create_span,
    get_meter,
    get_tracer,
    is_otel_enabled,
    set_span_status,
    trace_async_operation,
    trace_database_operation,
    trace_sync_operation,
)

__all__ = [
    # Context management
    "get_request_id",
    "get_trace_id",
    "set_request_context",
    # Logging
    "get_logger",
    "setup_logging",
    # Middleware
    "ObservabilityMiddleware",
    # Metrics
    "increment_counter",
    "record_timer",
    "set_gauge",
    "get_metrics_snapshot",
    "get_business_metrics",
    "time_operation",
    # Error tracking
    "get_error_tracker",
    "get_health_status",
    "track_error",
    # Distributed tracing
    "get_tracer",
    "get_meter",
    "is_otel_enabled",
    "create_span",
    "add_span_attributes",
    "set_span_status",
    "trace_async_operation",
    "trace_sync_operation",
    "trace_database_operation",
]
