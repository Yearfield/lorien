"""
Integration test to ensure all routes are mounted under versioned prefix.
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_routes_under_versioned_prefix():
    """Test that all routes (excluding docs/static) are mounted under /api/v1."""
    prefix = "/api/v1"
    excluded = {"/", "/docs", "/redoc", "/openapi.json"}
    
    # Get all routes from the app
    routes = {r.path for r in app.routes}
    
    for path in routes:
        if path in excluded:
            continue
        # Allow swagger/static/openapi paths
        if (path.startswith("/docs") or 
            path.startswith("/openapi") or 
            path.startswith("/redoc") or
            path.startswith("/static")):
            continue
        # All other routes should start with the versioned prefix
        assert path.startswith(prefix), f"Route {path} must be mounted under {prefix}"
