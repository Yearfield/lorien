"""
Enhanced security configuration and utilities for Lorien API.

Provides comprehensive security features including:
- Environment-based security configuration
- Security headers middleware
- Rate limiting
- Input validation helpers
- Security audit logging
"""

import hashlib
import hmac
import logging
import os
import re
import secrets
import time
from typing import Any, Dict, Optional, Set
from urllib.parse import urlparse

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Centralized security configuration management."""
    
    def __init__(self):
        self._load_config()
    
    def _load_config(self):
        """Load security configuration from environment variables."""
        # Environment detection
        self.environment = os.getenv("ENVIRONMENT", "development").lower()
        self.is_production = self.environment in ("production", "prod")
        self.is_development = self.environment in ("development", "dev")
        
        # Authentication settings
        self.auth_token = os.getenv("AUTH_TOKEN")
        self.auth_required = self.is_production or bool(os.getenv("AUTH_REQUIRED", "false").lower() == "true")
        self.auth_session_timeout = int(os.getenv("AUTH_SESSION_TIMEOUT", "3600"))  # 1 hour
        
        # Rate limiting
        self.rate_limit_enabled = self.is_production or bool(os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true")
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))  # per window
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
        
        # CORS settings
        self.cors_origins = self._parse_cors_origins(os.getenv("CORS_ORIGINS", "*"))
        self.cors_allow_credentials = bool(os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true")
        
        # Security headers
        self.security_headers_enabled = self.is_production or bool(os.getenv("SECURITY_HEADERS_ENABLED", "false").lower() == "true")
        self.hsts_max_age = int(os.getenv("HSTS_MAX_AGE", "31536000"))  # 1 year
        self.content_security_policy = os.getenv("CONTENT_SECURITY_POLICY", "default-src 'self'")
        
        # Input validation
        self.input_validation_enabled = self.is_production or bool(os.getenv("INPUT_VALIDATION_ENABLED", "true").lower() == "true")
        self.max_request_size = int(os.getenv("MAX_REQUEST_SIZE", "10485760"))  # 10MB
        
        # Security logging
        self.security_logging_enabled = bool(os.getenv("SECURITY_LOGGING_ENABLED", "true").lower() == "true")
        self.log_failed_auth_attempts = bool(os.getenv("LOG_FAILED_AUTH_ATTEMPTS", "true").lower() == "true")
    
    def _parse_cors_origins(self, origins_str: str) -> Set[str]:
        """Parse CORS origins from comma-separated string."""
        if origins_str == "*":
            return {"*"}
        return {origin.strip() for origin in origins_str.split(",") if origin.strip()}
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for responses."""
        if not self.security_headers_enabled:
            return {}
        
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
        
        if self.is_production:
            headers.update({
                "Strict-Transport-Security": f"max-age={self.hsts_max_age}; includeSubDomains",
                "Content-Security-Policy": self.content_security_policy,
                "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            })
        
        return headers
    
    def validate_auth_token(self, token: str) -> bool:
        """Validate authentication token with timing attack protection."""
        if not self.auth_token:
            return False
        
        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(token, self.auth_token)
    
    def is_endpoint_public(self, path: str) -> bool:
        """Check if endpoint should be publicly accessible."""
        public_endpoints = {
            "/health", "/live", "/ready",
            "/api/v1/health", "/api/v1/live", "/api/v1/ready",
            "/docs", "/redoc", "/openapi.json"
        }
        return any(path.startswith(endpoint) for endpoint in public_endpoints)
    
    def log_security_event(self, event_type: str, request: Request, details: Optional[Dict[str, Any]] = None):
        """Log security-related events."""
        if not self.security_logging_enabled:
            return
        
        log_data = {
            "event_type": event_type,
            "method": request.method,
            "path": request.url.path,
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": time.time(),
        }
        
        if details:
            log_data.update(details)
        
        logger.warning(f"Security event: {event_type}", extra={"security_event": log_data})
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (reverse proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


# Global security configuration instance
_security_config: SecurityConfig | None = None

def get_security_config() -> SecurityConfig:
    """Get the global security configuration instance."""
    global _security_config
    if _security_config is None:
        _security_config = SecurityConfig()
    return _security_config

def reset_security_config():
    """Reset the security configuration singleton. Used for testing."""
    global _security_config
    _security_config = None

# For backward compatibility
security_config = get_security_config()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        headers = security_config.get_security_headers()
        for header, value in headers.items():
            response.headers[header] = value
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to implement rate limiting."""
    
    def __init__(self, app):
        super().__init__(app)
        self.request_counts: Dict[str, Dict[str, Any]] = {}
    
    async def dispatch(self, request: Request, call_next):
        if not security_config.rate_limit_enabled:
            return await call_next(request)
        
        client_ip = security_config._get_client_ip(request)
        current_time = time.time()
        
        # Clean old entries
        self._cleanup_old_entries(current_time)
        
        # Check rate limit
        if self._is_rate_limited(client_ip, current_time):
            security_config.log_security_event("rate_limit_exceeded", request, {
                "client_ip": client_ip,
                "requests_in_window": self._get_request_count(client_ip)
            })
            
            return Response(
                content='{"detail": {"error": "rate_limit_exceeded", "message": "Too many requests"}}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json"
            )
        
        # Record request
        self._record_request(client_ip, current_time)
        
        return await call_next(request)
    
    def _cleanup_old_entries(self, current_time: float):
        """Remove entries older than the rate limit window."""
        cutoff_time = current_time - security_config.rate_limit_window
        for client_ip in list(self.request_counts.keys()):
            if self.request_counts[client_ip]["first_request"] < cutoff_time:
                del self.request_counts[client_ip]
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if client has exceeded rate limit."""
        if client_ip not in self.request_counts:
            return False
        
        client_data = self.request_counts[client_ip]
        window_start = current_time - security_config.rate_limit_window
        
        # Count requests in current window
        request_times = [t for t in client_data["requests"] if t > window_start]
        return len(request_times) >= security_config.rate_limit_requests
    
    def _record_request(self, client_ip: str, current_time: float):
        """Record a request for rate limiting."""
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {
                "first_request": current_time,
                "requests": []
            }
        
        self.request_counts[client_ip]["requests"].append(current_time)
    
    def _get_request_count(self, client_ip: str) -> int:
        """Get current request count for client."""
        if client_ip not in self.request_counts:
            return 0
        
        current_time = time.time()
        window_start = current_time - security_config.rate_limit_window
        request_times = [t for t in self.request_counts[client_ip]["requests"] if t > window_start]
        return len(request_times)


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for input validation and sanitization."""
    
    def __init__(self, app):
        super().__init__(app)
        # Patterns for potentially dangerous inputs
        self.dangerous_patterns = [
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'data:text/html', re.IGNORECASE),
            re.compile(r'vbscript:', re.IGNORECASE),
        ]
    
    async def dispatch(self, request: Request, call_next):
        if not security_config.input_validation_enabled:
            return await call_next(request)
        
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > security_config.max_request_size:
            security_config.log_security_event("request_too_large", request, {
                "content_length": content_length,
                "max_allowed": security_config.max_request_size
            })
            
            return Response(
                content='{"detail": {"error": "request_too_large", "message": "Request too large"}}',
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                media_type="application/json"
            )
        
        # Validate URL parameters for XSS
        if self._contains_dangerous_patterns(str(request.url)):
            security_config.log_security_event("suspicious_input", request, {
                "input_type": "url",
                "url": str(request.url)
            })
            
            return Response(
                content='{"detail": {"error": "invalid_input", "message": "Suspicious input detected"}}',
                status_code=status.HTTP_400_BAD_REQUEST,
                media_type="application/json"
            )
        
        return await call_next(request)
    
    def _contains_dangerous_patterns(self, input_str: str) -> bool:
        """Check if input contains potentially dangerous patterns."""
        return any(pattern.search(input_str) for pattern in self.dangerous_patterns)


def validate_input_safety(input_str: str) -> bool:
    """Validate that input string is safe for processing."""
    if not security_config.input_validation_enabled:
        return True
    
    # Check for dangerous patterns
    dangerous_patterns = [
        re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'data:text/html', re.IGNORECASE),
        re.compile(r'vbscript:', re.IGNORECASE),
    ]
    
    return not any(pattern.search(input_str) for pattern in dangerous_patterns)


def sanitize_input(input_str: str) -> str:
    """Sanitize input string by removing potentially dangerous content."""
    if not security_config.input_validation_enabled:
        return input_str
    
    # Remove HTML tags
    sanitized = re.sub(r'<[^>]+>', '', input_str)
    
    # Remove javascript: and data: URLs
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'data:text/html', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'vbscript:', '', sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    """Hash a token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(token: str, token_hash: str) -> bool:
    """Verify a token against its hash."""
    return hmac.compare_digest(hash_token(token), token_hash)


