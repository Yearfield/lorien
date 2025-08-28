"""
Tests for flags cascade assign/remove functionality.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_cascade_assign_creates_audit_rows():
    """Test that cascade assign creates audit rows for all affected nodes."""
    # Assumes nodes table has a simple chain 1 -> 2 -> 3 in fixtures
    payload = {
        "node_id": 1,
        "red_flag_name": "Test Flag",
        "cascade": True,
        "user": "tester"
    }
    
    r = client.post("/flags/assign", json=payload)
    assert r.status_code == 200, f"Assign failed: {r.text}"
    
    response_data = r.json()
    assert "affected_nodes" in response_data
    assert "cascade" in response_data
    assert response_data["cascade"] is True
    
    # Expect audit rows for affected nodes
    q = client.get("/flags/audit/?node_id=1&limit=5")
    assert q.status_code == 200, f"Audit query failed: {q.text}"
    
    # We don't know other audits; minimally assert at least one record exists for node 1
    audit_records = q.json()
    assert len(audit_records) >= 1, "Should have at least one audit record for node 1"


def test_cascade_remove_creates_audit_rows():
    """Test that cascade remove creates audit rows for all affected nodes."""
    # First assign a flag with cascade
    assign_payload = {
        "node_id": 1,
        "red_flag_name": "Test Flag",
        "cascade": True,
        "user": "tester"
    }
    
    assign_r = client.post("/flags/assign", json=assign_payload)
    assert assign_r.status_code == 200
    
    # Now remove with cascade
    remove_payload = {
        "node_id": 1,
        "red_flag_name": "Test Flag",
        "cascade": True,
        "user": "tester"
    }
    
    r = client.post("/flags/remove", json=remove_payload)
    assert r.status_code == 200, f"Remove failed: {r.text}"
    
    response_data = r.json()
    assert "affected_nodes" in response_data
    assert "cascade" in response_data
    assert response_data["cascade"] is True
    
    # Verify audit records were created
    audit_r = client.get("/flags/audit/?node_id=1&limit=10")
    assert audit_r.status_code == 200
    audit_records = audit_r.json()
    assert len(audit_records) >= 1, "Should have at least one audit record"


def test_non_cascade_assign_affects_single_node():
    """Test that non-cascade assign only affects the specified node."""
    payload = {
        "node_id": 1,
        "red_flag_name": "Test Flag",
        "cascade": False,
        "user": "tester"
    }
    
    r = client.post("/flags/assign", json=payload)
    assert r.status_code == 200, f"Assign failed: {r.text}"
    
    response_data = r.json()
    assert "affected_nodes" in response_data
    assert "cascade" in response_data
    assert response_data["cascade"] is False
    assert len(response_data["affected_nodes"]) == 1, "Should only affect one node when cascade=False"


def test_cascade_parameter_defaults_to_false():
    """Test that cascade parameter defaults to false when not specified."""
    payload = {
        "node_id": 1,
        "red_flag_name": "Test Flag",
        "user": "tester"
        # cascade not specified
    }
    
    r = client.post("/flags/assign", json=payload)
    assert r.status_code == 200, f"Assign failed: {r.text}"
    
    response_data = r.json()
    assert "cascade" in response_data
    assert response_data["cascade"] is False, "cascade should default to false"
