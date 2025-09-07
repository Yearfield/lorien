"""Tests for GET /api/v1/tree/parents/incomplete endpoint."""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_list_incomplete_parents_basic():
    """Test basic functionality of incomplete parents listing."""
    response = client.get("/api/v1/tree/parents/incomplete", params={"limit": 10})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert isinstance(data["items"], list)
    assert data["limit"] == 10

def test_list_incomplete_parents_with_query():
    """Test filtering by query string."""
    response = client.get("/api/v1/tree/parents/incomplete", params={"query": "test", "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["limit"] == 5

def test_list_incomplete_parents_with_depth_filter():
    """Test filtering by depth."""
    response = client.get("/api/v1/tree/parents/incomplete", params={"depth": 1, "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

def test_list_incomplete_parents_pagination():
    """Test pagination parameters."""
    response = client.get("/api/v1/tree/parents/incomplete", params={"limit": 2, "offset": 0})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) <= 2

def test_list_incomplete_parents_root_mount():
    """Test root mount (without /api/v1 prefix)."""
    response = client.get("/tree/parents/incomplete", params={"limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
