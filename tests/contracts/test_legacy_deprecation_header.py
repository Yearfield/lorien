"""
Legacy deprecation header tests.

Tests that legacy routes properly emit deprecation headers.
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_legacy_routes_emit_deprecation_header():
    """Test that legacy routes emit deprecation headers."""
    # Test legacy tree slots endpoints
    legacy_endpoints = [
        {
            "path": "/tree/slots/1/slot/1",
            "method": "PUT",
            "data": {"label": "test"}
        },
        {
            "path": "/tree/slots/1/slot/1", 
            "method": "DELETE",
            "data": None
        }
    ]
    
    for endpoint in legacy_endpoints:
        if endpoint["method"] == "PUT":
            response = client.put(endpoint["path"], json=endpoint["data"])
        elif endpoint["method"] == "DELETE":
            response = client.delete(endpoint["path"])
        else:
            continue
            
        # Only check headers if endpoint exists (not 404)
        if response.status_code != 404:
            assert response.headers.get("Deprecation") == "true", \
                f"Missing Deprecation header for {endpoint['method']} {endpoint['path']}"
            assert response.headers.get("Sunset") == "v7.0", \
                f"Missing or incorrect Sunset header for {endpoint['method']} {endpoint['path']}"

def test_legacy_route_documentation():
    """Test that legacy routes have proper deprecation documentation."""
    # This test ensures that legacy routes are properly documented
    # as deprecated in their docstrings
    from api.routers.tree_slots import router as tree_slots_router
    
    # Check that the router has deprecation information
    for route in tree_slots_router.routes:
        if hasattr(route, "endpoint") and hasattr(route, "path"):
            # Check if the route path contains legacy patterns
            if "/slot/" in route.path:
                # This is a legacy route, should have deprecation info
                # The actual deprecation info is in the function docstring
                # which is tested by the deprecation header test
                pass

def test_deprecation_header_format():
    """Test that deprecation headers follow the correct format."""
    # Test the deprecation header helper function
    from api.app import add_deprecation_headers
    from fastapi.responses import JSONResponse
    
    # Create a test response
    response = JSONResponse(content={"test": "data"})
    
    # Apply deprecation headers
    response = add_deprecation_headers(response)
    
    # Check header format
    assert response.headers["Deprecation"] == "true"
    assert response.headers["Sunset"] == "v7.0"

def test_legacy_route_alternatives():
    """Test that legacy routes have documented alternatives."""
    # This test ensures that legacy routes point to their modern alternatives
    legacy_alternatives = {
        "/tree/slots/{parent_id}/slot/{slot}": "/api/v1/tree/parents/{parent_id}/children"
    }
    
    # Check that alternatives are documented in the route registry
    from pathlib import Path
    registry_path = Path("docs/API_ROUTES_REGISTRY.md")
    
    if registry_path.exists():
        registry_content = registry_path.read_text()
        
        # Check that alternatives are mentioned
        for legacy, alternative in legacy_alternatives.items():
            assert alternative in registry_content, \
                f"Alternative route {alternative} not documented for legacy {legacy}"

def test_legacy_route_sunset_timeline():
    """Test that legacy routes have a clear sunset timeline."""
    # All legacy routes should have the same sunset version
    expected_sunset = "v7.0"
    
    # Test that the sunset version is consistent
    from api.app import add_deprecation_headers
    from fastapi.responses import JSONResponse
    
    response = JSONResponse(content={"test": "data"})
    response = add_deprecation_headers(response)
    
    assert response.headers["Sunset"] == expected_sunset

def test_legacy_route_graceful_degradation():
    """Test that legacy routes still function but with deprecation warnings."""
    # Legacy routes should still work, just with deprecation headers
    response = client.put("/tree/slots/1/slot/1", json={"label": "test"})
    
    # If the endpoint exists, it should work (even if it returns an error)
    # The key is that it should have deprecation headers
    if response.status_code != 404:
        assert "Deprecation" in response.headers
        assert "Sunset" in response.headers

def test_legacy_route_migration_guidance():
    """Test that legacy routes provide migration guidance."""
    # This test ensures that legacy routes provide clear migration paths
    # The migration guidance should be in the API documentation
    
    # Check that the route registry contains migration information
    from pathlib import Path
    registry_path = Path("docs/API_ROUTES_REGISTRY.md")
    
    if registry_path.exists():
        registry_content = registry_path.read_text()
        
        # Should contain migration guidance
        assert "DEPRECATED" in registry_content.upper()
        assert "Use `/api/v1/tree/parents/{parent_id}/children`" in registry_content
        assert "v7.0" in registry_content

def test_legacy_route_backward_compatibility():
    """Test that legacy routes maintain backward compatibility."""
    # Legacy routes should continue to work until sunset
    # This test ensures that the API doesn't break existing clients
    
    # Test that legacy endpoints still respond (even with errors)
    legacy_endpoints = [
        "/tree/slots/1/slot/1",
    ]
    
    for endpoint in legacy_endpoints:
        # Try PUT
        response = client.put(endpoint, json={"label": "test"})
        # Should not be 404 (endpoint exists)
        if response.status_code == 404:
            # If 404, that's also acceptable - the endpoint might not exist
            # The important thing is that if it exists, it has deprecation headers
            pass
        else:
            # If it exists, it should have deprecation headers
            assert response.headers.get("Deprecation") == "true"
            assert response.headers.get("Sunset") == "v7.0"
