"""
Tests for Phase 6 UI Parity features.
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app
import pathlib

client = TestClient(app)

def test_csv_header_contract_fixture():
    """Test that CSV export matches frozen contract exactly."""
    fixture_path = pathlib.Path("tests/fixtures/csv_contract.csv")
    assert fixture_path.exists(), "CSV contract fixture must exist"
    
    expected_header = fixture_path.read_text().strip()
    
    # Test both export endpoints
    for endpoint in ["/calc/export", "/tree/export"]:
        r = client.get(endpoint)
        assert r.status_code == 200, f"Export {endpoint} failed"
        
        actual_header = r.text.split('\n')[0]
        assert actual_header == expected_header, f"Header mismatch for {endpoint}: expected '{expected_header}', got '{actual_header}'"

def test_missing_slots_endpoint():
    """Test missing slots endpoint."""
    r = client.get("/tree/missing-slots")
    assert r.status_code == 200
    
    data = r.json()
    assert "parents_with_missing_slots" in data
    assert "total_count" in data
    assert isinstance(data["parents_with_missing_slots"], list)

def test_triage_search_endpoint():
    """Test triage search endpoint."""
    r = client.get("/triage/search?leaf_only=true")
    assert r.status_code == 200
    
    data = r.json()
    assert "results" in data
    assert "total_count" in data
    assert "leaf_only" in data

def test_triage_search_with_query():
    """Test triage search with query parameter."""
    r = client.get("/triage/search?leaf_only=true&query=test")
    assert r.status_code == 200
    
    data = r.json()
    assert "results" in data
    assert "leaf_only" in data

def test_triage_update_leaf_only():
    """Test that triage update only works for leaf nodes."""
    # First, let's find a leaf node
    r = client.get("/triage/search?leaf_only=true")
    assert r.status_code == 200
    
    data = r.json()
    if data["results"]:
        leaf_node = data["results"][0]
        node_id = leaf_node["node_id"]
        
        # Test update on leaf node
        update_payload = {
            "diagnostic_triage": "Test triage update",
            "actions": "Test actions update"
        }
        
        r = client.put(f"/triage/{node_id}", json=update_payload)
        assert r.status_code == 200
        
        response_data = r.json()
        assert "message" in response_data
        assert "node_id" in response_data
        assert "updated_at" in response_data

def test_triage_update_non_leaf_rejected():
    """Test that triage update is rejected for non-leaf nodes."""
    # Find a non-leaf node (depth > 0 and not a leaf)
    r = client.get("/triage/search?leaf_only=false")
    assert r.status_code == 200
    
    data = r.json()
    non_leaf_nodes = [node for node in data["results"] if not node.get("is_leaf", False)]
    
    if non_leaf_nodes:
        non_leaf_node = non_leaf_nodes[0]
        node_id = non_leaf_node["node_id"]
        
        # Test update on non-leaf node
        update_payload = {
            "diagnostic_triage": "Test triage update",
            "actions": "Test actions update"
        }
        
        r = client.put(f"/triage/{node_id}", json=update_payload)
        assert r.status_code == 400, "Non-leaf nodes should be rejected"
        
        response_data = r.json()
        assert "detail" in response_data
        assert "leaf nodes" in response_data["detail"].lower()

def test_dual_mount_consistency():
    """Test that new endpoints work consistently at both root and API v1 paths."""
    endpoints = [
        "/tree/missing-slots",
        "/triage/search",
    ]
    
    for endpoint in endpoints:
        # Test root path
        r1 = client.get(endpoint)
        assert r1.status_code == 200, f"Root path {endpoint} failed"
        
        # Test API v1 path
        r2 = client.get(f"/api/v1{endpoint}")
        assert r2.status_code == 200, f"API v1 path {endpoint} failed"
        
        # Verify responses are identical
        assert r1.json() == r2.json(), f"Responses differ for {endpoint}"

def test_csv_export_headers():
    """Test that CSV export returns proper headers."""
    r = client.get("/calc/export")
    assert r.status_code == 200
    
    # Check content type
    assert "text/csv" in r.headers.get("content-type", ""), "Content-Type should be text/csv"
    
    # Check content disposition
    content_disposition = r.headers.get("content-disposition", "")
    assert "attachment" in content_disposition, "Content-Disposition should include attachment"
    
    # Check that content starts with the frozen header
    expected_header = "Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions"
    actual_header = r.text.split('\n')[0]
    assert actual_header == expected_header, f"Header mismatch: expected '{expected_header}', got '{actual_header}'"
