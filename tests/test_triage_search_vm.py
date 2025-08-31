"""
Tests for triage search with VM filtering functionality.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_search_vm_returns_latest_one():
    """Test that triage search with VM parameter returns the latest record."""
    r = client.get("/api/v1/triage/search", params={
        "vm": "Pulse",
        "leaf_only": "true",
        "sort": "updated_at:desc",
        "limit": 1
    })
    assert r.status_code == 200
    
    # Response may be {"items":[...]} or list; accept both
    data = r.json()
    items = data["items"] if isinstance(data, dict) and "items" in data else data
    assert isinstance(items, list)
    
    if items:
        assert "diagnostic_triage" in items[0] and "actions" in items[0]

def test_search_vm_supports_optional_parameters():
    """Test that triage search supports all optional parameters."""
    r = client.get("/api/v1/triage/search", params={
        "leaf_only": "true",
        "query": "chest pain",
        "vm": "Chest Pain Assessment",
        "sort": "updated_at:asc",
        "limit": 50
    })
    assert r.status_code == 200
    
    data = r.json()
    assert "items" in data
    assert "total_count" in data
    assert "leaf_only" in data
    assert "vm" in data
    assert "sort" in data
    assert "limit" in data

def test_search_vm_defaults_work():
    """Test that triage search works with default parameters."""
    r = client.get("/api/v1/triage/search")
    assert r.status_code == 200
    
    data = r.json()
    assert "items" in data
    assert "total_count" in data
    assert "leaf_only" in data
    # Default values should be applied
    assert data.get("leaf_only") == True
    assert data.get("sort") == "updated_at:desc"
    assert data.get("limit") == 100

def test_search_vm_limit_validation():
    """Test that triage search validates limit parameter."""
    # Test limit too low
    r = client.get("/api/v1/triage/search", params={"limit": 0})
    assert r.status_code == 422
    
    # Test limit too high
    r2 = client.get("/api/v1/triage/search", params={"limit": 1001})
    assert r2.status_code == 422
    
    # Test valid limit
    r3 = client.get("/api/v1/triage/search", params={"limit": 500})
    assert r3.status_code == 200
