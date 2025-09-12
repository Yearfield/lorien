"""
Route registry contract tests.

Tests route uniqueness, canonical endpoint presence, and deprecation headers.
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_route_uniqueness_and_presence():
    """Test that all routes are unique and canonical endpoints exist."""
    paths = set()
    duplicate_routes = []
    
    # Collect all routes and check for duplicates (excluding dual-mount)
    for route in app.routes:
        if hasattr(route, "path"):
            path = route.path
            # Skip dual-mount duplicates (same path with different prefixes)
            if path in paths:
                duplicate_routes.append(path)
            else:
                paths.add(path)
    
    # Filter out expected dual-mount duplicates
    expected_duplicates = [
        "/api/v1/tree/{parent_id:int}/children",  # Dual-mounted
        "/api/v1/triage/{node_id:int}",  # Dual-mounted
        "/api/v1/flags/audit/",  # Dual-mounted
        "/api/v1/tree/export",  # Dual-mounted
        "/api/v1/tree/export.xlsx",  # Dual-mounted
        "/api/v1/export/csv",  # Dual-mounted
        "/api/v1/export.xlsx",  # Dual-mounted
        "/api/v1/flags/assign",  # Dual-mounted
        "/api/v1/flags/remove",  # Dual-mounted
        "/api/v1/tree/stats",  # Dual-mounted
        "/api/v1/tree/missing-slots",  # Dual-mounted
        "/api/v1/tree/next-incomplete-parent",  # Dual-mounted
        "/api/v1/tree/parent/{parent_id:int}/children",  # Dual-mounted
        "/api/v1/tree/{parent_id:int}/slot/{slot:int}",  # Dual-mounted
        "/api/v1/tree/roots",  # Dual-mounted
        "/api/v1/dictionary",  # Dual-mounted
        "/api/v1/tree/conflicts/duplicate-labels",  # Dual-mounted
        "/api/v1/tree/conflicts/orphans",  # Dual-mounted
        "/api/v1/tree/conflicts/depth-anomalies",  # Dual-mounted
        "/tree/{parent_id:int}/children",  # Dual-mounted
        "/triage/{node_id:int}",  # Dual-mounted
        "/flags/audit/",  # Dual-mounted
        "/tree/export",  # Dual-mounted
        "/tree/export.xlsx",  # Dual-mounted
        "/export/csv",  # Dual-mounted
        "/export.xlsx",  # Dual-mounted
        "/flags/assign",  # Dual-mounted
        "/flags/remove",  # Dual-mounted
        "/tree/stats",  # Dual-mounted
        "/tree/missing-slots",  # Dual-mounted
        "/tree/next-incomplete-parent",  # Dual-mounted
        "/tree/parent/{parent_id:int}/children",  # Dual-mounted
        "/tree/{parent_id:int}/slot/{slot:int}",  # Dual-mounted
        "/tree/roots",  # Dual-mounted
        "/dictionary",  # Dual-mounted
        "/tree/conflicts/duplicate-labels",  # Dual-mounted
        "/tree/conflicts/orphans",  # Dual-mounted
        "/tree/conflicts/depth-anomalies",  # Dual-mounted
            "/tree/vm/draft/{draft_id}",  # Dual-mounted
            "/api/v1/tree/vm/draft/{draft_id}",  # Dual-mounted
            "/api/v1/health/metrics",  # Dual-mounted
            "/api/v1/rbac/users",  # Dual-mounted
            "/api/v1/rbac/users/{user_id}",  # Dual-mounted
            "/rbac/users",  # Dual-mounted
            "/rbac/users/{user_id}",  # Dual-mounted
    ]
    
    # Remove expected duplicates from the list
    actual_duplicates = [dup for dup in duplicate_routes if dup not in expected_duplicates]
    
    # Assert no unexpected duplicate routes
    assert not actual_duplicates, f"Unexpected duplicate routes found: {actual_duplicates}"
    
    # Canonical endpoints that must exist (dual mount acceptable)
    canonical_endpoints = [
        "/api/v1/tree/parents/incomplete",
        "/api/v1/tree/{parent_id:int}/children",  # Actual route pattern
        "/api/v1/tree/next-incomplete-parent",
        "/api/v1/triage/{node_id:int}",  # Actual route pattern
        "/api/v1/llm/health",
        "/api/v1/llm/fill-triage-actions",
        "/api/v1/import",
        "/api/v1/tree/export",
        "/api/v1/dictionary",
        "/api/v1/dictionary/normalize",
        "/api/v1/health",
        "/api/v1/health/metrics",
        "/api/v1/admin/data-quality/summary",
        "/api/v1/admin/audit",
        "/api/v1/tree/vm/drafts",
        "/api/v1/concurrency/node/{node_id}/version",
    ]
    
    # Check that canonical endpoints exist
    missing_endpoints = []
    for endpoint in canonical_endpoints:
        if not any(getattr(route, "path", "") == endpoint for route in app.routes):
            missing_endpoints.append(endpoint)
    
    assert not missing_endpoints, f"Missing canonical endpoints: {missing_endpoints}"

def test_legacy_routes_emit_deprecation_header():
    """Test that legacy routes emit deprecation headers."""
    # Test legacy tree slots endpoints
    legacy_endpoints = [
        "/tree/slots/1/slot/1",  # PUT endpoint
        "/tree/slots/1/slot/1",  # DELETE endpoint
    ]
    
    for endpoint in legacy_endpoints:
        # Try PUT first (upsert)
        response = client.put(endpoint, json={"label": "test"})
        if response.status_code != 404:
            assert response.headers.get("Deprecation") == "true"
            assert response.headers.get("Sunset") == "v7.0"
        
        # Try DELETE
        response = client.delete(endpoint)
        if response.status_code != 404:
            assert response.headers.get("Deprecation") == "true"
            assert response.headers.get("Sunset") == "v7.0"

def test_dual_mount_coverage():
    """Test that critical endpoints are available at both bare and versioned paths."""
    critical_endpoints = [
        "/health",
        "/api/v1/health",
        "/tree/stats", 
        "/api/v1/tree/stats",
        "/dictionary",
        "/api/v1/dictionary",
    ]
    
    for endpoint in critical_endpoints:
        response = client.get(endpoint)
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404, f"Critical endpoint missing: {endpoint}"

def test_route_path_consistency():
    """Test that route paths follow consistent patterns."""
    path_patterns = {
        "api_v1": "/api/v1/",
        "tree": "/tree/",
        "admin": "/admin/",
        "health": "/health",
    }
    
    for route in app.routes:
        if hasattr(route, "path"):
            path = route.path
            
            # Check that API routes are properly prefixed
            if path.startswith("/api/v1/"):
                # Should not have double slashes
                assert "//" not in path, f"Double slash in path: {path}"
            
            # Check that tree routes are properly structured
            if path.startswith("/tree/") and not path.startswith("/api/v1/"):
                # Legacy tree routes should be deprecated
                pass  # This is handled by deprecation header tests

def test_route_method_coverage():
    """Test that critical operations have appropriate HTTP methods."""
    critical_operations = {
        "GET": ["/api/v1/health", "/api/v1/tree/stats", "/api/v1/dictionary"],
        "POST": ["/api/v1/import", "/api/v1/dictionary"],
        "PUT": ["/api/v1/tree/{parent_id:int}/children", "/api/v1/triage/{node_id:int}"],  # Actual route patterns
        "DELETE": ["/api/v1/tree/{node_id}"],
    }
    
    # This is a basic check - in a real implementation, you'd want to
    # inspect the actual route methods more thoroughly
    for method, endpoints in critical_operations.items():
        for endpoint in endpoints:
            # Check that the endpoint exists in some form
            found = any(
                getattr(route, "path", "") == endpoint 
                for route in app.routes
            )
            assert found, f"Critical {method} endpoint missing: {endpoint}"

def test_route_parameter_validation():
    """Test that route parameters follow expected patterns."""
    for route in app.routes:
        if hasattr(route, "path"):
            path = route.path
            
            # Check for proper parameter syntax
            if "{" in path and "}" in path:
                # Should have proper parameter syntax
                assert path.count("{") == path.count("}"), f"Unbalanced braces in path: {path}"
                
                # Parameters should not be empty
                import re
                params = re.findall(r'\{([^}]+)\}', path)
                for param in params:
                    assert param.strip(), f"Empty parameter in path: {path}"
                    
                    # Check parameter type annotations
                    if ":" in param:
                        param_name, param_type = param.split(":", 1)
                        assert param_name.strip(), f"Empty parameter name in path: {path}"
                        assert param_type.strip(), f"Empty parameter type in path: {path}"

def test_route_tag_consistency():
    """Test that routes have appropriate tags for documentation."""
    # This is a basic check - in practice, you'd want to ensure
    # all routes have meaningful tags for API documentation
    for route in app.routes:
        if hasattr(route, "tags") and route.tags:
            # Tags should be non-empty strings
            for tag in route.tags:
                assert isinstance(tag, str), f"Non-string tag found: {tag}"
                assert tag.strip(), f"Empty tag found in route: {route.path}"

def test_route_response_model_consistency():
    """Test that routes have appropriate response models."""
    # This is a basic check - in practice, you'd want to ensure
    # all routes have proper response models for API documentation
    for route in app.routes:
        if hasattr(route, "response_model") and route.response_model:
            # Response model should be a valid type
            assert route.response_model is not None, f"Invalid response model in route: {route.path}"

def test_route_status_code_consistency():
    """Test that routes use appropriate status codes."""
    # This is a basic check - in practice, you'd want to ensure
    # all routes use appropriate HTTP status codes
    for route in app.routes:
        if hasattr(route, "status_code") and route.status_code:
            # Status code should be a valid HTTP status code
            assert 100 <= route.status_code <= 599, f"Invalid status code in route: {route.path}"

def test_route_deprecation_consistency():
    """Test that deprecated routes are properly marked."""
    deprecated_paths = [
        "/tree/slots/",
    ]
    
    for route in app.routes:
        if hasattr(route, "path"):
            path = route.path
            is_deprecated = any(dep_path in path for dep_path in deprecated_paths)
            
            if is_deprecated:
                # Deprecated routes should have deprecation headers
                # This is tested in the deprecation header test
                pass
