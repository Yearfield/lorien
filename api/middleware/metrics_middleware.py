"""
Metrics middleware for FastAPI.

Collects request metrics, response times, and error rates.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.metrics import increment_counter, record_timer

logger = logging.getLogger(__name__)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect request metrics."""
    
    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        if not self.enabled:
            return await call_next(request)
        
        # Record request start time
        start_time = time.time()
        
        # Extract request info
        method = request.method
        path = request.url.path
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Increment request counter
        increment_counter("http_requests", tags={
            "method": method,
            "path": self._normalize_path(path),
            "user_agent": self._categorize_user_agent(user_agent)
        })
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record response metrics
            duration_ms = (time.time() - start_time) * 1000
            
            # Record response time
            record_timer("http_response_time", duration_ms, tags={
                "method": method,
                "path": self._normalize_path(path),
                "status_code": str(response.status_code)
            })
            
            # Record status code
            increment_counter("http_responses", tags={
                "status_code": str(response.status_code),
                "method": method,
                "path": self._normalize_path(path)
            })
            
            # Record success/error
            if 200 <= response.status_code < 300:
                increment_counter("http_success")
            elif 400 <= response.status_code < 500:
                increment_counter("http_client_errors")
            elif 500 <= response.status_code < 600:
                increment_counter("http_server_errors")
            
            # Record specific error types
            if response.status_code == 409:
                increment_counter("conflicts", tags={
                    "path": self._normalize_path(path)
                })
            elif response.status_code == 422:
                increment_counter("validation_errors", tags={
                    "path": self._normalize_path(path)
                })
            
            return response
            
        except Exception as e:
            # Record error metrics
            duration_ms = (time.time() - start_time) * 1000
            
            record_timer("http_response_time", duration_ms, tags={
                "method": method,
                "path": self._normalize_path(path),
                "status_code": "500"
            })
            
            increment_counter("http_server_errors")
            increment_counter("http_exceptions", tags={
                "exception_type": type(e).__name__,
                "path": self._normalize_path(path)
            })
            
            # Re-raise the exception
            raise
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path for metrics (remove IDs, etc.)."""
        # Remove common ID patterns
        import re
        
        # Replace numeric IDs with {id}
        path = re.sub(r'/\d+', '/{id}', path)
        
        # Replace UUIDs with {uuid}
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{uuid}', path)
        
        # Limit path length
        if len(path) > 100:
            path = path[:100] + "..."
        
        return path
    
    def _categorize_user_agent(self, user_agent: str) -> str:
        """Categorize user agent for metrics."""
        if not user_agent or user_agent == "unknown":
            return "unknown"
        
        user_agent_lower = user_agent.lower()
        
        if "curl" in user_agent_lower:
            return "curl"
        elif "python" in user_agent_lower:
            return "python"
        elif "postman" in user_agent_lower:
            return "postman"
        elif "chrome" in user_agent_lower:
            return "chrome"
        elif "firefox" in user_agent_lower:
            return "firefox"
        elif "safari" in user_agent_lower:
            return "safari"
        else:
            return "other"
