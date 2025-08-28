"""
Tests for red flag audit endpoints.
"""

import pytest
from tests.utils.api_client import get, post, both_paths, assert_both_paths_ok


def test_audit_list_empty_initially():
    """Test that audit list returns data (may not be empty due to previous tests)."""
    root_response, v1_response = both_paths("/flags/audit/")

    assert root_response.status_code == 200
    assert v1_response.status_code == 200

    # Both should return lists (may contain existing data)
    assert isinstance(root_response.json(), list)
    assert isinstance(v1_response.json(), list)
    
    # Verify the structure of audit records
    if root_response.json():
        record = root_response.json()[0]
        assert "id" in record
        assert "node_id" in record
        assert "flag_id" in record
        assert "action" in record
        assert "ts" in record


def test_audit_insert_and_fetch():
    """Test audit record creation and retrieval."""
    # Create an audit record
    body = {
        "node_id": 1, 
        "flag_id": 1, 
        "action": "assign", 
        "user": "test_user"
    }
    
    # Test both root and v1 paths
    root_response = post("/flags/audit/", json=body)
    v1_response = post("/api/v1/flags/audit/", json=body)
    
    assert root_response.status_code == 201
    assert v1_response.status_code == 201
    
    # Verify the created records
    root_data = root_response.json()
    v1_data = v1_response.json()
    
    assert root_data["node_id"] == 1
    assert root_data["flag_id"] == 1
    assert root_data["action"] == "assign"
    assert root_data["user"] == "test_user"
    assert "ts" in root_data
    
    assert v1_data["node_id"] == 1
    assert v1_data["flag_id"] == 1
    assert v1_data["action"] == "assign"
    assert v1_data["user"] == "test_user"
    assert "ts" in v1_data
    
    # Test retrieval
    query_response = get("/flags/audit/?node_id=1&limit=5")
    assert query_response.status_code == 200
    
    records = query_response.json()
    assert len(records) >= 2  # Should have at least our 2 test records
    
    # Verify our records are in the list
    record_ids = [record["id"] for record in records]
    assert root_data["id"] in record_ids
    assert v1_data["id"] in record_ids


def test_audit_invalid_action():
    """Test that invalid actions are rejected."""
    body = {
        "node_id": 1,
        "flag_id": 1,
        "action": "invalid_action",
        "user": "test_user"
    }
    
    root_response = post("/flags/audit/", json=body)
    v1_response = post("/api/v1/flags/audit/", json=body)
    
    # Both should return 422 for invalid action
    assert root_response.status_code == 422
    assert v1_response.status_code == 422


def test_audit_filtering():
    """Test audit record filtering."""
    # Create a record for node 2
    body = {
        "node_id": 2,
        "flag_id": 1,
        "action": "assign",
        "user": "test_user"
    }
    
    post("/flags/audit/", json=body)
    
    # Test filtering by node_id
    response = get("/flags/audit/?node_id=2&limit=10")
    assert response.status_code == 200
    
    records = response.json()
    assert all(record["node_id"] == 2 for record in records)
    
    # Test filtering by user
    response = get("/flags/audit/?user=test_user&limit=10")
    assert response.status_code == 200
    
    records = response.json()
    assert all(record["user"] == "test_user" for record in records)


def test_audit_limit_enforcement():
    """Test that limit parameter is enforced."""
    # Create multiple records
    for i in range(5):
        body = {
            "node_id": 1,
            "flag_id": 1,
            "action": "assign",
            "user": f"user_{i}"
        }
        post("/flags/audit/", json=body)
    
    # Test limit enforcement
    response = get("/flags/audit/?limit=3")
    assert response.status_code == 200
    
    records = response.json()
    assert len(records) <= 3


def test_audit_dual_mount_consistency():
    """Test that both root and v1 paths return consistent data."""
    # Get audit records from both paths
    root_response, v1_response = both_paths("/flags/audit/")
    
    assert root_response.status_code == 200
    assert v1_response.status_code == 200
    
    root_data = root_response.json()
    v1_data = v1_response.json()
    
    # Both should return the same data structure
    assert len(root_data) == len(v1_data)
    
    # Verify data consistency (assuming same order due to ORDER BY)
    for i, (root_record, v1_record) in enumerate(zip(root_data, v1_data)):
        assert root_record["id"] == v1_record["id"], f"Record {i} ID mismatch"
        assert root_record["node_id"] == v1_record["node_id"], f"Record {i} node_id mismatch"
        assert root_record["flag_id"] == v1_record["flag_id"], f"Record {i} flag_id mismatch"
        assert root_record["action"] == v1_record["action"], f"Record {i} action mismatch"
        assert root_record["user"] == v1_record["user"], f"Record {i} user mismatch"
        assert root_record["ts"] == v1_record["ts"], f"Record {i} ts mismatch"
