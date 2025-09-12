"""
ASGI middleware for telemetry and metrics collection.

This middleware tracks per-route hit counts, status codes, response times,
and other non-PHI metrics for monitoring API stability.
"""

import time
import os
from typing import Callable, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
import logging

from ..metrics import (
    increment_route_hit,
    increment_status_code,
    record_response_time,
    increment_conflict,
    increment_validation_error,
)

class TelemetryMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting telemetry and metrics."""
    
    def __init__(self, app, analytics_enabled: bool = False):
        super().__init__(app)
        self.analytics_enabled = analytics_enabled
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect telemetry."""
        # Check environment variable at runtime
        analytics_enabled = os.getenv("ANALYTICS_ENABLED", "false").lower() == "true"
        if not analytics_enabled:
            return await call_next(request)
        
        # Start timing
        start_time = time.time()
        
        # Extract route information
        route = self._extract_route(request)
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000
        
        # Collect metrics
        self._collect_metrics(request, response, route, response_time_ms)
        
        return response
    
    def _extract_route(self, request: Request) -> str:
        """Extract route path for metrics."""
        # Use the route path, removing query parameters
        path = request.url.path
        
        # Normalize path parameters for grouping
        # e.g., /tree/123/children -> /tree/{id}/children
        if hasattr(request, 'route') and request.route:
            # Try to get the route pattern from FastAPI
            try:
                return str(request.route.path)
            except:
                pass
        
        # Fallback to actual path
        return path
    
    def _collect_metrics(self, request: Request, response: Response, route: str, response_time_ms: float) -> None:
        """Collect metrics for the request/response."""
        try:
            # Increment route hit count
            increment_route_hit(route)
            
            # Increment status code counter
            increment_status_code(response.status_code)
            
            # Record response time
            record_response_time(route, response_time_ms)
            
            # Track specific error types
            if response.status_code == 409:
                # Extract parent_id and slot from request if available
                parent_id = None
                slot = None
                
                # Try to extract from path parameters
                if hasattr(request, 'path_params'):
                    parent_id = request.path_params.get('parent_id')
                    slot = request.path_params.get('slot')
                    if parent_id:
                        try:
                            parent_id = int(parent_id)
                        except (ValueError, TypeError):
                            parent_id = None
                    if slot:
                        try:
                            slot = int(slot)
                        except (ValueError, TypeError):
                            slot = None
                
                # Log 409 conflict with route, parent_id, slot (no PHI)
                increment_conflict(route, parent_id, slot)
            
            elif response.status_code == 422:
                # Track validation errors
                increment_validation_error()
            
            # Track import/export operations
            if self._is_import_operation(route):
                if response.status_code < 400:
                    from ..metrics import increment_import_success
                    increment_import_success()
                else:
                    from ..metrics import increment_import_error
                    increment_import_error()
            
            elif self._is_export_operation(route):
                if response.status_code < 400:
                    from ..metrics import increment_export_success
                    increment_export_success()
                else:
                    from ..metrics import increment_export_error
                    increment_export_error()
        
        except Exception as e:
            # Don't let metrics collection break the request
            logging.warning(f"Telemetry collection error: {e}")
    
    def _is_import_operation(self, route: str) -> bool:
        """Check if route is an import operation."""
        import_routes = [
            "/import",
            "/import/excel",
            "/import/preview",
            "/import/jobs",
        ]
        return any(route.startswith(imp_route) for imp_route in import_routes)
    
    def _is_export_operation(self, route: str) -> bool:
        """Check if route is an export operation."""
        export_routes = [
            "/export",
            "/tree/export",
            "/calc/export",
            "/dictionary/export",
        ]
        return any(route.startswith(exp_route) for exp_route in export_routes)
