#!/usr/bin/env python3
"""Test conflicts group API with node_id parameter."""

import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_conflicts_group_by_node_id():
    """Test getting conflict group by node_id."""
    # First, get conflicts to find a node_id
    conflicts_response = client.get("/api/v1/tree/conflicts/conflicts?limit=10&offset=0")
    assert conflicts_response.status_code == 200
    
    conflicts_data = conflicts_response.json()
    assert "items" in conflicts_data
    assert len(conflicts_data["items"]) >= 1
    
    # Get a parent_id from the conflicts
    parent_id = conflicts_data["items"][0]["parent_id"]
    
    # Test getting group by node_id
    group_response = client.get(f"/api/v1/tree/conflicts/group?node_id={parent_id}")
    assert group_response.status_code == 200
    
    group_data = group_response.json()
    assert "children" in group_data
    assert "group" in group_data
    assert "summary" in group_data


def test_conflicts_group_by_node_id_not_found():
    """Test getting conflict group with non-existent node_id."""
    response = client.get("/api/v1/tree/conflicts/group?node_id=99999")
    assert response.status_code == 422


def test_conflicts_group_missing_parameters():
    """Test getting conflict group without required parameters."""
    response = client.get("/api/v1/tree/conflicts/group")
    assert response.status_code == 422


def test_conflicts_group_dual_mounting():
    """Test that conflicts group endpoint is available at both paths."""
    # Test /api/v1 path
    response_v1 = client.get("/api/v1/tree/conflicts/group?node_id=1")
    # Test / path (dual mounting)
    response_root = client.get("/tree/conflicts/group?node_id=1")
    
    # Both should return the same status (either 200 or 422 depending on data)
    assert response_v1.status_code == response_root.status_code


if __name__ == '__main__':
    pytest.main([__file__])
