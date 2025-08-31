from fastapi.testclient import TestClient
from api.app import app
import pytest

client = TestClient(app)

def test_preview_assign_returns_count_and_nodes():
    """Test that preview-assign returns the expected structure."""
    r = client.get("/api/v1/flags/preview-assign", params={
        "node_id": 1, 
        "flag_id": 1, 
        "cascade": True, 
        "limit": 5
    })
    assert r.status_code == 200
    j = r.json()
    assert "count" in j and isinstance(j["count"], int)
    assert "flag_name" in j and isinstance(j["flag_name"], str)
    assert "node_id" in j and j["node_id"] == 1
    assert "cascade" in j and j["cascade"] is True

def test_preview_assign_no_cascade():
    """Test preview without cascade returns single node."""
    r = client.get("/api/v1/flags/preview-assign", params={
        "node_id": 1, 
        "flag_id": 1, 
        "cascade": False
    })
    assert r.status_code == 200
    j = r.json()
    assert j["count"] == 1
    assert j["cascade"] is False

def test_preview_assign_node_not_found():
    """Test preview with non-existent node returns 404."""
    r = client.get("/api/v1/flags/preview-assign", params={
        "node_id": 99999, 
        "flag_id": 1, 
        "cascade": True
    })
    assert r.status_code == 404

def test_preview_assign_flag_not_found():
    """Test preview with non-existent flag returns 404."""
    r = client.get("/api/v1/flags/preview-assign", params={
        "node_id": 1, 
        "flag_id": 99999, 
        "cascade": True
    })
    assert r.status_code == 404

def test_audit_branch_scope_lists_recent():
    """Test audit with branch scope returns records."""
    r = client.get("/api/v1/flags/audit", params={
        "node_id": 1, 
        "branch": True, 
        "limit": 20
    })
    assert r.status_code == 200
    # Structure check only; data existence depends on seed
    assert isinstance(r.json(), list)

def test_audit_no_branch_scope():
    """Test audit without branch scope returns single node records."""
    r = client.get("/api/v1/flags/audit", params={
        "node_id": 1, 
        "branch": False, 
        "limit": 20
    })
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_audit_with_limit():
    """Test audit respects limit parameter."""
    r = client.get("/api/v1/flags/audit", params={
        "limit": 5
    })
    assert r.status_code == 200
    records = r.json()
    assert len(records) <= 5

def test_audit_with_user_filter():
    """Test audit filtering by user."""
    r = client.get("/api/v1/flags/audit", params={
        "user": "test_user"
    })
    assert r.status_code == 200
    assert isinstance(r.json(), list)
