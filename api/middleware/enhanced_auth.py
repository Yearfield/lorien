"""
Enhanced authentication middleware with RBAC and ETag support.

Provides comprehensive authentication, authorization, and concurrency control
for all API endpoints.
"""

import os
import logging
from typing import Optional, Set, Dict, Any
from fastapi import HTTPException, Request, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..core.rbac import rbac_manager, Permission, User
from ..core.etag import ETagManager, ConcurrencyError

logger = logging.getLogger(__name__)

# Security scheme for OpenAPI docs
security = HTTPBearer(auto_error=False)

class EnhancedAuthMiddleware(BaseHTTPMiddleware):
    """Enhanced middleware for authentication, authorization, and ETag handling."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.auth_enabled = os.getenv("AUTH_TOKEN") is not None
        self.rbac_enabled = rbac_manager.is_enabled()
        
        # Define endpoint permissions
        self.endpoint_permissions = self._build_endpoint_permissions()
    
    def _build_endpoint_permissions(self) -> Dict[str, Set[Permission]]:
        """Build endpoint to permissions mapping."""
        return {
            # Tree operations
            "/api/v1/tree/children": {Permission.WRITE_TREE},
            "/api/v1/tree/children/": {Permission.WRITE_TREE},
            "/tree/children": {Permission.WRITE_TREE},
            "/tree/children/": {Permission.WRITE_TREE},
            
            # Triage operations
            "/api/v1/triage": {Permission.WRITE_TRIAGE},
            "/api/v1/triage/": {Permission.WRITE_TRIAGE},
            "/triage": {Permission.WRITE_TRIAGE},
            "/triage/": {Permission.WRITE_TRIAGE},
            
            # Dictionary operations
            "/api/v1/dictionary": {Permission.WRITE_DICTIONARY},
            "/api/v1/dictionary/": {Permission.WRITE_DICTIONARY},
            "/dictionary": {Permission.WRITE_DICTIONARY},
            "/dictionary/": {Permission.WRITE_DICTIONARY},
            
            # Flags operations
            "/api/v1/flags": {Permission.WRITE_FLAGS},
            "/api/v1/flags/": {Permission.WRITE_FLAGS},
            "/flags": {Permission.WRITE_FLAGS},
            "/flags/": {Permission.WRITE_FLAGS},
            
            # Export operations
            "/api/v1/tree/export": {Permission.WRITE_EXPORT},
            "/api/v1/export": {Permission.WRITE_EXPORT},
            "/tree/export": {Permission.WRITE_EXPORT},
            "/export": {Permission.WRITE_EXPORT},
            
            # Admin operations
            "/api/v1/admin": {Permission.ADMIN_SYSTEM},
            "/api/v1/admin/": {Permission.ADMIN_SYSTEM},
            "/admin": {Permission.ADMIN_SYSTEM},
            "/admin/": {Permission.ADMIN_SYSTEM},
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request with enhanced authentication and authorization."""
        # Add user context to request
        request.state.user = None
        request.state.permissions = set()
        
        # Handle authentication
        if self.auth_enabled or self.rbac_enabled:
            await self._authenticate_request(request)
        
        # Handle authorization
        if self.rbac_enabled:
            await self._authorize_request(request)
        
        # Handle ETag validation for write operations
        if request.method in ["PUT", "PATCH", "POST", "DELETE"]:
            await self._validate_etag(request)
        
        # Process request
        response = await call_next(request)
        
        # Add ETag headers to response if applicable
        if hasattr(request.state, 'etag'):
            response.headers.update(ETagManager.create_etag_response_headers(request.state.etag))
        
        return response
    
    async def _authenticate_request(self, request: Request):
        """Authenticate the request."""
        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            if self._requires_auth(request):
                raise HTTPException(
                    status_code=401,
                    detail={
                        "error": "authentication_required",
                        "message": "Authorization header required"
                    }
                )
            return
        
        # Parse Bearer token
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "invalid_auth_format",
                    "message": "Authorization header must be 'Bearer <token>'"
                }
            )
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Handle RBAC authentication
        if self.rbac_enabled:
            user = rbac_manager.get_user_by_session(token)
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "error": "invalid_token",
                        "message": "Invalid or expired authentication token"
                    }
                )
            request.state.user = user
            request.state.permissions = rbac_manager.get_user_permissions(user)
            logger.info(f"Authenticated user: {user.username} with permissions: {[p.value for p in request.state.permissions]}")
        
        # Handle simple token authentication
        elif self.auth_enabled:
            expected_token = os.getenv("AUTH_TOKEN")
            if token != expected_token:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "error": "invalid_token",
                        "message": "Invalid authentication token"
                    }
                )
            logger.info(f"Authenticated with simple token: {request.method} {request.url.path}")
    
    async def _authorize_request(self, request: Request):
        """Authorize the request based on user permissions."""
        if not self.rbac_enabled or not request.state.user:
            return
        
        # Check if endpoint requires specific permissions
        path = request.url.path
        required_permissions = self._get_required_permissions(path)
        
        if not required_permissions:
            return  # No specific permissions required
        
        # Check if user has required permissions
        if not rbac_manager.has_any_permission(request.state.user, required_permissions):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "insufficient_permissions",
                    "message": f"Access denied. Required permissions: {[p.value for p in required_permissions]}",
                    "user_permissions": [p.value for p in request.state.permissions]
                }
            )
        
        logger.info(f"Authorized user {request.state.user.username} for {path}")
    
    async def _validate_etag(self, request: Request):
        """Validate ETag for write operations."""
        if_match = request.headers.get("If-Match")
        if not if_match:
            # ETag validation is optional for now
            return
        
        # Store If-Match header for later validation
        request.state.if_match = if_match
    
    def _requires_auth(self, request: Request) -> bool:
        """Check if request requires authentication."""
        # GET requests generally don't require auth
        if request.method == "GET":
            return False
        
        # Check if path matches any write endpoint
        path = request.url.path
        return any(
            path.startswith(endpoint) for endpoint in self.endpoint_permissions.keys()
        )
    
    def _get_required_permissions(self, path: str) -> Set[Permission]:
        """Get required permissions for a path."""
        for endpoint, permissions in self.endpoint_permissions.items():
            if path.startswith(endpoint):
                return permissions
        return set()

def get_current_user(request: Request) -> Optional[User]:
    """Get current user from request state."""
    return getattr(request.state, 'user', None)

def get_current_permissions(request: Request) -> Set[Permission]:
    """Get current user permissions from request state."""
    return getattr(request.state, 'permissions', set())

def require_permission(permission: Permission):
    """Dependency to require a specific permission."""
    def permission_checker(request: Request):
        if not rbac_manager.is_enabled():
            return get_current_user(request)  # Return user if RBAC is disabled
        
        user = get_current_user(request)
        if not user:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "authentication_required",
                    "message": "Authentication required"
                }
            )
        
        if not rbac_manager.has_permission(user, permission):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "insufficient_permissions",
                    "message": f"Permission required: {permission.value}"
                }
            )
        
        return user
    
    return permission_checker

def require_any_permission(permissions: Set[Permission]):
    """Dependency to require any of the specified permissions."""
    def permission_checker(request: Request):
        if not rbac_manager.is_enabled():
            return get_current_user(request)  # Return user if RBAC is disabled
        
        user = get_current_user(request)
        if not user:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "authentication_required",
                    "message": "Authentication required"
                }
            )
        
        if not rbac_manager.has_any_permission(user, permissions):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "insufficient_permissions",
                    "message": f"One of these permissions required: {[p.value for p in permissions]}"
                }
            )
        
        return user
    
    return permission_checker

def validate_etag_match(if_match: Optional[str] = Header(None)) -> Optional[str]:
    """
    Validate If-Match header for ETag concurrency control.
    
    Args:
        if_match: If-Match header value
        
    Returns:
        Parsed ETag value
        
    Raises:
        HTTPException: If If-Match header is malformed
    """
    if not if_match:
        return None
    
    parsed_etag = ETagManager.parse_if_match_header(if_match)
    if not parsed_etag:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_if_match_header",
                "message": "If-Match header must be a valid ETag",
                "expected_format": 'W/"etag" or "etag"'
            }
        )
    
    return parsed_etag

def check_etag_concurrency(
    if_match: Optional[str],
    current_etag: str,
    resource_id: Optional[str] = None
) -> None:
    """
    Check ETag concurrency and raise appropriate error if mismatch.
    
    Args:
        if_match: If-Match header value
        current_etag: Current resource ETag
        resource_id: Optional resource identifier for error context
        
    Raises:
        HTTPException: If ETags don't match (412 Precondition Failed)
    """
    if not if_match:
        return  # No ETag validation required
    
    if not ETagManager.check_etag_match(if_match, current_etag):
        error_detail = ETagManager.create_etag_error_response(if_match, current_etag)
        if resource_id:
            error_detail["resource_id"] = resource_id
        
        raise HTTPException(
            status_code=412,
            detail=error_detail
        )
