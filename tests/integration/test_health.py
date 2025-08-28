"""
Integration tests for health endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from sqlite3 import Connection

from api.app import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_endpoint_returns_200(client):
    """Test that health endpoint returns 200 status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_endpoint_structure(client):
    """Test that health endpoint returns expected JSON structure."""
    response = client.get("/api/v1/health")
    data = response.json()
    
    # Check required top-level fields
    assert "ok" in data
    assert "version" in data
    assert "db" in data
    assert "features" in data
    
    # Check data types
    assert isinstance(data["ok"], bool)
    assert isinstance(data["version"], str)
    assert isinstance(data["db"], dict)
    assert isinstance(data["features"], dict)


def test_health_endpoint_ok_true(client):
    """Test that health endpoint returns ok: true."""
    response = client.get("/api/v1/health")
    data = response.json()
    assert data["ok"] is True


def test_health_endpoint_version_format(client):
    """Test that version is a valid version string."""
    response = client.get("/api/v1/health")
    data = response.json()
    
    # Version should be in format like "v6.7.0" or "6.6.0"
    version = data["version"]
    assert "." in version
    
    # Handle both "v6.7.0" and "6.6.0" formats
    if version.startswith("v"):
        version = version[1:]  # Strip "v" prefix
    
    parts = version.split(".")
    assert len(parts) >= 2
    assert all(part.isdigit() for part in parts)


def test_health_endpoint_db_structure(client):
    """Test that db object has required fields."""
    response = client.get("/api/v1/health")
    data = response.json()
    db_info = data["db"]
    
    # Check required db fields
    assert "wal" in db_info
    assert "foreign_keys" in db_info
    assert "page_size" in db_info
    
    # Check data types
    assert isinstance(db_info["wal"], bool)
    assert isinstance(db_info["foreign_keys"], bool)
    assert isinstance(db_info["page_size"], int)
    
    # Check that WAL and foreign keys are enabled
    assert db_info["wal"] is True
    assert db_info["foreign_keys"] is True
    
    # Check page size is reasonable
    assert db_info["page_size"] > 0
    assert db_info["page_size"] <= 65536  # Max SQLite page size


def test_health_endpoint_features_structure(client):
    """Test that features object has required fields."""
    response = client.get("/api/v1/health")
    data = response.json()
    features = data["features"]
    
    # Check required features fields
    assert "llm" in features
    
    # Check data types
    assert isinstance(features["llm"], bool)


def test_health_endpoint_db_path_present(client):
    """Test that db.path is present (may be None for test environment)."""
    response = client.get("/api/v1/health")
    data = response.json()
    db_info = data["db"]
    
    assert "path" in db_info
    # Path can be None in test environment, but should be present


def test_health_endpoint_no_error_in_db(client):
    """Test that db object doesn't contain error field in normal operation."""
    response = client.get("/api/v1/health")
    data = response.json()
    db_info = data["db"]
    
    # In normal operation, there should be no error field
    assert "error" not in db_info


def test_health_endpoint_consistent_response(client):
    """Test that health endpoint returns consistent response on multiple calls."""
    response1 = client.get("/api/v1/health")
    response2 = client.get("/api/v1/health")
    
    data1 = response1.json()
    data2 = response2.json()
    
    # Version should be consistent
    assert data1["version"] == data2["version"]
    
    # Database settings should be consistent
    assert data1["db"]["wal"] == data2["db"]["wal"]
    assert data1["db"]["foreign_keys"] == data2["db"]["foreign_keys"]
    assert data1["db"]["page_size"] == data2["db"]["page_size"]
