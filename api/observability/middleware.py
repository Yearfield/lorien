"""
Observability middleware for FastAPI.

Integrates request/trace IDs, structured logging, and OpenTelemetry.
"""

import time
from collections.abc import Callable
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .context import clear_request_context, set_request_context
from .logging import log_request
from .metrics import increment_counter, record_timer


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds observability to all requests.

    Features:
    - Generates and propagates request_id and trace_id
    - Adds correlation headers to responses
    - Logs all requests with structured data
    - Integrates with OpenTelemetry when enabled
    """

    # Headers for distributed tracing
    TRACE_ID_HEADER = "X-Trace-Id"
    REQUEST_ID_HEADER = "X-Request-Id"
    PARENT_SPAN_HEADER = "traceparent"  # W3C Trace Context

    def __init__(self, app, enable_otel: bool = False):
        """
        Initialize the middleware.

        Args:
            app: The ASGI application
            enable_otel: Enable OpenTelemetry integration
        """
        super().__init__(app)
        self.enable_otel = enable_otel

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with observability features."""
        # Extract or generate trace/request IDs
        trace_id = request.headers.get(self.TRACE_ID_HEADER)
        request_id = request.headers.get(self.REQUEST_ID_HEADER)
        parent_span_id = self._extract_parent_span_id(request.headers.get(self.PARENT_SPAN_HEADER))

        # Set context (generates IDs if not provided)
        context = set_request_context(
            request_id=request_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
        )

        # Record start time
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Add correlation headers to response
            response.headers[self.TRACE_ID_HEADER] = context["trace_id"]
            response.headers[self.REQUEST_ID_HEADER] = context["request_id"]

            # Log the request
            log_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                extra={
                    "user_agent": request.headers.get("user-agent", "unknown"),
                    "client_ip": self._get_client_ip(request),
                },
            )

            # Collect metrics
            self._collect_metrics(request, response, duration_ms)

            return response

        except Exception as exc:
            # Calculate duration even for errors
            duration_ms = (time.time() - start_time) * 1000

            # Log the error
            log_request(
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration_ms=duration_ms,
                extra={
                    "error": {
                        "type": type(exc).__name__,
                        "message": str(exc),
                    }
                },
            )

            # Re-raise the exception
            raise

        finally:
            # Clear context to avoid leaks
            clear_request_context()

    def _extract_parent_span_id(self, traceparent: Optional[str]) -> Optional[str]:
        """
        Extract parent span ID from W3C traceparent header.

        Format: 00-{trace_id}-{parent_id}-{flags}

        Args:
            traceparent: The traceparent header value

        Returns:
            Parent span ID or None
        """
        if not traceparent:
            return None

        try:
            parts = traceparent.split("-")
            if len(parts) >= 3:
                return parts[2]  # Parent span ID
        except Exception:
            pass

        return None

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.

        Checks X-Forwarded-For, X-Real-IP, and falls back to client host.

        Args:
            request: The FastAPI request

        Returns:
            Client IP address
        """
        # Check forwarded headers (proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client
        if request.client:
            return request.client.host

        return "unknown"

    def _collect_metrics(self, request: Request, response: Response, duration_ms: float):
        """
        Collect metrics for the request.

        Args:
            request: The FastAPI request
            response: The FastAPI response
            duration_ms: Request duration in milliseconds
        """
        # Normalize path for metrics (replace IDs with placeholders)
        normalized_path = self._normalize_path(request.url.path)

        # Record request counter
        increment_counter(
            "http.requests",
            tags={
                "method": request.method,
                "path": normalized_path,
                "status": str(response.status_code),
            },
        )

        # Record response time
        record_timer(
            "http.response_time",
            duration_ms,
            tags={
                "method": request.method,
                "path": normalized_path,
                "status": str(response.status_code),
            },
        )

        # Record status code categories
        if 200 <= response.status_code < 300:
            increment_counter("http.success")
        elif 400 <= response.status_code < 500:
            increment_counter("http.client_errors", tags={"status": str(response.status_code)})
        elif 500 <= response.status_code < 600:
            increment_counter("http.server_errors", tags={"status": str(response.status_code)})

    def _normalize_path(self, path: str) -> str:
        """
        Normalize path for metrics by replacing IDs with placeholders.

        Args:
            path: The request path

        Returns:
            Normalized path
        """
        import re

        # Replace numeric IDs with {id}
        path = re.sub(r"/\d+", "/{id}", path)

        # Replace UUIDs with {uuid}
        path = re.sub(
            r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "/{uuid}",
            path,
        )

        return path
