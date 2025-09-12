"""
Authentication middleware for optional token-based access control.

Provides simple token-based authentication for write endpoints while
keeping read endpoints open by default.
"""

import os
import logging
from typing import Optional
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

# Security scheme for OpenAPI docs
security = HTTPBearer(auto_error=False)

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for optional token-based authentication."""
    
    def __init__(self, app: ASGIApp, auth_token: Optional[str] = None):
        super().__init__(app)
        self.auth_token = auth_token or os.getenv("AUTH_TOKEN")
        self.auth_enabled = self.auth_token is not None
        
        # Define write endpoints that require authentication
        self.write_endpoints = {
            # Tree operations
            "/tree/children",
            "/tree/children/",
            "/api/v1/tree/children",
            "/api/v1/tree/children/",
            
            # Dictionary operations
            "/dictionary",
            "/dictionary/",
            "/api/v1/dictionary",
            "/api/v1/dictionary/",
            
            # Outcomes operations
            "/triage",
            "/triage/",
            "/api/v1/triage",
            "/api/v1/triage/",
            
            # Admin operations
            "/admin/",
            "/api/v1/admin/",
            
            # Conflicts and merge operations
            "/conflicts/",
            "/api/v1/conflicts/",
            
            # Apply default operations
            "/apply-default",
            "/api/v1/apply-default",
            
            # Delete subtree operations
            "/delete-subtree",
            "/api/v1/delete-subtree",
            
            # VM builder operations (future)
            "/tree/vm/",
            "/api/v1/tree/vm/",
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request and check authentication for write endpoints."""
        # Check environment variable at runtime
        current_auth_token = os.getenv("AUTH_TOKEN")
        if not current_auth_token:
            return await call_next(request)
        
        # Check if this is a write endpoint
        path = request.url.path
        method = request.method
        
        # GET requests are always allowed
        if method == "GET":
            return await call_next(request)
        
        # Check if path matches any write endpoint pattern
        requires_auth = any(
            path.startswith(endpoint) for endpoint in self.write_endpoints
        )
        
        if not requires_auth:
            return await call_next(request)
        
        # Extract and validate token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "authentication_required",
                    "message": "Authorization header required for write operations"
                }
            )
        
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "invalid_auth_format",
                    "message": "Authorization header must be 'Bearer <token>'"
                }
            )
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        if token != current_auth_token:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "invalid_token",
                    "message": "Invalid authentication token"
                }
            )
        
        # Log successful authentication
        logger.info(f"Authenticated write operation: {method} {path}")
        
        return await call_next(request)

def get_auth_token() -> Optional[str]:
    """Get the current auth token from environment."""
    return os.getenv("AUTH_TOKEN")

def is_auth_enabled() -> bool:
    """Check if authentication is enabled."""
    return get_auth_token() is not None

def require_auth() -> bool:
    """Dependency to require authentication for specific endpoints."""
    if not is_auth_enabled():
        return True  # Allow if auth is disabled
    
    # This would be used in endpoint dependencies
    # The actual token validation is handled by the middleware
    return True
