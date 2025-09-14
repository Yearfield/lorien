"""
Test that API always returns non-null integers for conflicts.
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_conflicts_endpoint_returns_non_null_ints(client):
    """Test that conflicts endpoint always returns non-null integers."""
    response = client.get("/api/v1/tree/conflicts/conflicts?limit=10")
    assert response.status_code == 200
    
    data = response.json()
    
    # Check top-level fields
    assert isinstance(data["total"], int)
    assert isinstance(data["limit"], int)
    assert isinstance(data["offset"], int)
    assert data["total"] >= 0
    assert data["limit"] > 0
    assert data["offset"] >= 0
    
    # Check items if any exist
    if data["items"]:
        for item in data["items"]:
            # All integer fields should be present and non-null
            assert isinstance(item["parent_id"], int)
            assert isinstance(item["depth"], int)
            assert isinstance(item["child_count"], int)
            assert isinstance(item["duplicate_parents"], int)
            assert isinstance(item["variant_sets"], int)
            
            # String fields should be present
            assert isinstance(item["label"], str)
            
            # Values should be reasonable
            assert item["parent_id"] > 0
            assert item["depth"] >= 0
            assert item["child_count"] >= 0
            assert item["duplicate_parents"] >= 0
            assert item["variant_sets"] >= 0


def test_conflicts_endpoint_empty_response_structure(client):
    """Test that empty response still has correct structure."""
    # Force empty response by using very specific filters
    response = client.get("/api/v1/tree/conflicts/conflicts?limit=1&offset=999999")
    assert response.status_code == 200
    
    data = response.json()
    
    # Should have correct structure even when empty
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)
    assert isinstance(data["limit"], int)
    assert isinstance(data["offset"], int)
    
    assert data["items"] == []
    assert data["total"] == 0
    assert data["limit"] == 1  # We requested limit=1
    assert data["offset"] == 999999


def test_group_endpoint_returns_non_null_ints(client):
    """Test that group endpoint returns non-null integers."""
    # First get a conflict to test with
    conflicts_response = client.get("/api/v1/tree/conflicts/conflicts?limit=1")
    assert conflicts_response.status_code == 200
    
    conflicts_data = conflicts_response.json()
    if conflicts_data["items"]:
        parent_id = conflicts_data["items"][0]["parent_id"]
        
        # Test group endpoint
        response = client.get(f"/api/v1/tree/conflicts/group?node_id={parent_id}")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check structure
        assert "group" in data
        assert "children" in data
        assert "summary" in data
        
        # Check group items
        for group_item in data["group"]:
            assert isinstance(group_item["id"], int)
            assert group_item["id"] > 0
        
        # Check children
        for child in data["children"]:
            assert isinstance(child["child_id"], int)
            assert isinstance(child["from_id"], int)
            assert isinstance(child["slot"], int)
            assert isinstance(child["label"], str)
            
            assert child["child_id"] > 0
            assert child["from_id"] > 0
            assert child["slot"] > 0
        
        # Check summary
        summary = data["summary"]
        assert isinstance(summary["unique_children"], int)
        assert isinstance(summary["total_children"], int)
        assert summary["unique_children"] >= 0
        assert summary["total_children"] >= 0
