"""
Deprecation middleware for handling legacy API routes.

Provides:
- Sunset headers for deprecated endpoints
- 301 Permanent Redirect to canonical /api/v1 routes
- Detailed deprecation warnings in responses
"""

import logging
from datetime import datetime, timedelta

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

# Sunset date: 90 days from deployment (adjust as needed)
SUNSET_DATE = (datetime.now() + timedelta(days=90)).strftime("%a, %d %b %Y %H:%M:%S GMT")


class DeprecationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle deprecated API routes.

    Routes mounted at the root (e.g., /tree/..., /export/...) are deprecated
    in favor of versioned routes under /api/v1/.

    This middleware:
    - Adds Sunset and Deprecation headers to responses
    - Returns 301 Permanent Redirect for deprecated routes
    - Logs deprecation warnings for monitoring
    """

    # Map of deprecated routes to their canonical replacements
    DEPRECATED_ROUTES: dict[str, str] = {
        # Tree operations (tree_basic_router mounted without prefix)
        "/tree/roots": "/api/v1/tree/roots",
        "/tree/children": "/api/v1/tree/children",
        "/tree/node": "/api/v1/tree/node",
        "/tree/ancestors": "/api/v1/tree/ancestors",
        "/tree/next-underfilled": "/api/v1/tree/next-underfilled",
        "/tree/edge/flag": "/api/v1/tree/edge/flag",
        "/tree/clone/candidates": "/api/v1/tree/clone/candidates",
        "/tree/clone": "/api/v1/tree/clone",
        # Delete/restore operations (tree_delete_restore_router mounted without prefix)
        "/tree/node": "/api/v1/tree/node",
        "/tree/subtree/restore": "/api/v1/tree/subtree/restore",
        "/tree/root": "/api/v1/tree/root",
        # Export aliases
        "/export/csv": "/api/v1/tree/export",
        "/export.xlsx": "/api/v1/tree/export.xlsx",
        "/tree/export-json": "/api/v1/tree/export-json",
    }

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        logger.info(
            f"Deprecation middleware active - {len(self.DEPRECATED_ROUTES)} routes will be redirected"
        )

    def _is_deprecated_route(self, path: str) -> bool:
        """Check if a route is deprecated."""
        # Exact match
        if path in self.DEPRECATED_ROUTES:
            return True

        # Prefix match for routes with parameters
        for deprecated_path in self.DEPRECATED_ROUTES:
            if path.startswith(deprecated_path + "/"):
                return True

        return False

    def _get_canonical_url(self, path: str, query_string: bytes) -> str:
        """Get the canonical URL for a deprecated route."""
        # Try exact match first
        if path in self.DEPRECATED_ROUTES:
            canonical_path = self.DEPRECATED_ROUTES[path]
        else:
            # Find prefix match
            canonical_path = None
            for deprecated_path, canonical in self.DEPRECATED_ROUTES.items():
                if path.startswith(deprecated_path + "/"):
                    # Preserve the path suffix
                    suffix = path[len(deprecated_path) :]
                    canonical_path = canonical + suffix
                    break

            if not canonical_path:
                # Fallback: prepend /api/v1 to the path
                canonical_path = f"/api/v1{path}"

        # Preserve query string
        if query_string:
            return f"{canonical_path}?{query_string.decode('utf-8')}"
        return canonical_path

    async def dispatch(self, request: Request, call_next):
        """
        Process request and handle deprecated routes.

        For deprecated routes:
        - Return 301 Permanent Redirect to canonical route
        - Add Sunset and Deprecation headers
        - Log deprecation warning
        """
        path = request.url.path

        # Check if this is a deprecated route
        if self._is_deprecated_route(path):
            canonical_url = self._get_canonical_url(path, request.url.query.encode())

            logger.warning(
                f"Deprecated route accessed: {request.method} {path} -> "
                f"Redirecting to {canonical_url}"
            )

            # Return 301 Permanent Redirect with deprecation headers
            return RedirectResponse(
                url=canonical_url,
                status_code=301,
                headers={
                    "Sunset": SUNSET_DATE,
                    "Deprecation": "true",
                    "Link": f'<{canonical_url}>; rel="alternate"',
                    "X-Deprecated-Endpoint": path,
                    "X-Canonical-Endpoint": canonical_url,
                    "Warning": (
                        f'299 - "Deprecated API endpoint. '
                        f"Use {canonical_url} instead. "
                        f'This endpoint will be removed after {SUNSET_DATE}"'
                    ),
                },
            )

        # For non-deprecated routes, continue normally
        return await call_next(request)
