"""
Test utilities for API testing with versioned API support.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def get(path: str, **kw):
    """GET request helper with /api/v1 prefix."""
    if not path.startswith("/"):
        path = f"/api/v1/{path}"
    elif not path.startswith("/api/v1"):
        path = f"/api/v1{path}"
    return client.get(path, **kw)


def post(path: str, **kw):
    """POST request helper with /api/v1 prefix."""
    if not path.startswith("/"):
        path = f"/api/v1/{path}"
    elif not path.startswith("/api/v1"):
        path = f"/api/v1{path}"
    return client.post(path, **kw)


def delete(path: str, **kw):
    """DELETE request helper with /api/v1 prefix."""
    if not path.startswith("/"):
        path = f"/api/v1/{path}"
    elif not path.startswith("/api/v1"):
        path = f"/api/v1{path}"
    return client.delete(path, **kw)


def put(path: str, **kw):
    """PUT request helper with /api/v1 prefix."""
    if not path.startswith("/"):
        path = f"/api/v1/{path}"
    elif not path.startswith("/api/v1"):
        path = f"/api/v1{path}"
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


def both_paths(path_no_version: str):
    """
    Return both the root path and API v1 path for testing dual mounts.
    
    Args:
        path_no_version: Path without version prefix (e.g., "/health")
        
    Returns:
        Tuple of (root_path, api_v1_path)
    """
    root_path = path_no_version
    v1_path = api_v1_path(path_no_version)
    return root_path, v1_path


def assert_both_paths_ok(path_no_version: str, expected_status: int = 200):
    """
    Assert that both the root path and API v1 path return the expected status.
    
    Args:
        path_no_version: Path without version prefix
        expected_status: Expected HTTP status code
    """
    root_path, v1_path = both_paths(path_no_version)
    
    # Test root path
    root_response = get(root_path)
    assert root_response.status_code == expected_status, \
        f"Root path {root_path} returned {root_response.status_code}, expected {expected_status}"
    
    # Test API v1 path
    v1_response = get(v1_path)
    assert v1_response.status_code == expected_status, \
        f"API v1 path {v1_path} returned {v1_response.status_code}, expected {expected_status}"
    
    return root_response, v1_response


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
