"""
Test utilities for API testing with versioned API support.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def get(path: str, **kw):
    """GET request helper."""
    return client.get(path, **kw)


def post(path: str, **kw):
    """POST request helper."""
    return client.post(path, **kw)


def delete(path: str, **kw):
    """DELETE request helper."""
    return client.delete(path, **kw)


def put(path: str, **kw):
    """PUT request helper."""
    return client.put(path, **kw)


def api_v1_path(path_no_version: str) -> str:
    """
    Convert a path to the versioned API path.
    
    Args:
        path_no_version: Path without version prefix (e.g., "/health")
        
    Returns:
        Versioned path (e.g., "/api/v1/health")
    """
    return f"/api/v1{path_no_version}"


def assert_api_v1_path_ok(path_no_version: str, expected_status: int = 200):
    """
    Assert that the API v1 path returns the expected status.
    
    Args:
        path_no_version: Path without version prefix
        expected_status: Expected HTTP status code
    """
    v1_path = api_v1_path(path_no_version)
    response = get(v1_path)
    
    assert response.status_code == expected_status, \
        f"API v1 path {v1_path} returned {response.status_code}, expected {expected_status}"
    
    return response
