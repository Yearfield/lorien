"""
Context management for distributed tracing and request correlation.

Provides thread-safe context variables for request_id and trace_id that
propagate through async contexts.
"""

import contextvars
import uuid
from typing import Optional

# Context variables for request correlation
_request_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)
_trace_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("trace_id", default=None)
_parent_span_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "parent_span_id", default=None
)


def generate_request_id() -> str:
    """Generate a new request ID."""
    return f"req_{uuid.uuid4().hex[:16]}"


def generate_trace_id() -> str:
    """Generate a new trace ID compatible with OpenTelemetry (32 hex chars)."""
    return uuid.uuid4().hex + uuid.uuid4().hex[:16]


def get_request_id() -> Optional[str]:
    """Get the current request ID from context."""
    return _request_id.get()


def get_trace_id() -> Optional[str]:
    """Get the current trace ID from context."""
    return _trace_id.get()


def get_parent_span_id() -> Optional[str]:
    """Get the parent span ID from context."""
    return _parent_span_id.get()


def set_request_context(
    request_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    parent_span_id: Optional[str] = None,
) -> dict[str, str]:
    """
    Set request context variables.

    Args:
        request_id: Request ID (generated if not provided)
        trace_id: Trace ID (generated if not provided)
        parent_span_id: Parent span ID (optional)

    Returns:
        Dictionary with the set context values
    """
    if request_id is None:
        request_id = generate_request_id()
    if trace_id is None:
        trace_id = generate_trace_id()

    _request_id.set(request_id)
    _trace_id.set(trace_id)
    if parent_span_id:
        _parent_span_id.set(parent_span_id)

    return {
        "request_id": request_id,
        "trace_id": trace_id,
        "parent_span_id": parent_span_id or "",
    }


def clear_request_context():
    """Clear all request context variables."""
    _request_id.set(None)
    _trace_id.set(None)
    _parent_span_id.set(None)


def get_context_dict() -> dict[str, Optional[str]]:
    """
    Get all context variables as a dictionary.

    Returns:
        Dictionary with request_id, trace_id, and parent_span_id
    """
    return {
        "request_id": get_request_id(),
        "trace_id": get_trace_id(),
        "parent_span_id": get_parent_span_id(),
    }
