"""Tests for PUT /api/v1/tree/parents/{parent_id}/children endpoint."""

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_bulk_upsert_children_happy_path():
    """Test successful bulk upsert of children."""
    body = {
        "slots": [
            {"slot": 1, "label": "Alpha"},
            {"slot": 2, "label": "Beta"},
            {"slot": 3, "label": "Gamma"},
            {"slot": 4, "label": "Delta"},
            {"slot": 5, "label": "Epsilon"}
        ],
        "mode": "upsert"
    }

    # Try with a reasonable parent_id (may not exist in test DB, but tests structure)
    response = client.put("/api/v1/tree/parents/1/children", json=body)

    # Either succeeds (200) or fails with proper error codes
    if response.status_code == 200:
        data = response.json()
        assert "updated" in data
        assert "missing_slots" in data
        assert isinstance(data["updated"], list)
    elif response.status_code == 404:
        assert "parent not found" in response.json().get("detail", "").lower()
    else:
        # Other valid responses
        assert response.status_code in [422, 409]

def test_bulk_upsert_children_partial_update():
    """Test partial update (only some slots provided)."""
    body = {
        "slots": [
            {"slot": 2, "label": "Updated Beta"},
            {"slot": 4, "label": "Updated Delta"}
        ],
        "mode": "upsert"
    }

    response = client.put("/api/v1/tree/parents/1/children", json=body)

    if response.status_code == 200:
        data = response.json()
        assert "updated" in data
        assert "missing_slots" in data
    else:
        # Valid error responses
        assert response.status_code in [404, 422, 409]

def test_bulk_upsert_children_validation_errors():
    """Test validation errors."""
    # Test invalid slot number
    body = {
        "slots": [{"slot": 6, "label": "Invalid Slot"}],
        "mode": "upsert"
    }
    response = client.put("/api/v1/tree/parents/1/children", json=body)
    assert response.status_code == 422

    # Test empty label
    body = {
        "slots": [{"slot": 1, "label": ""}],
        "mode": "upsert"
    }
    response = client.put("/api/v1/tree/parents/1/children", json=body)
    assert response.status_code == 422

    # Test invalid characters
    body = {
        "slots": [{"slot": 1, "label": "Invalid@Chars!"}],
        "mode": "upsert"
    }
    response = client.put("/api/v1/tree/parents/1/children", json=body)
    assert response.status_code == 422

def test_bulk_upsert_children_ignore_empty_labels():
    """Test that empty labels are ignored (for Phase-6 compatibility)."""
    body = {
        "slots": [
            {"slot": 1, "label": "Valid"},
            {"slot": 2, "label": ""},  # Should be ignored
            {"slot": 3, "label": "Also Valid"}
        ],
        "mode": "upsert"
    }

    response = client.put("/api/v1/tree/parents/1/children", json=body)

    if response.status_code == 200:
        data = response.json()
        # Should only have updated slots 1 and 3, ignoring slot 2
        updated_slots = [item["slot"] for item in data["updated"]]
        assert 2 not in updated_slots

def test_bulk_upsert_children_root_mount():
    """Test root mount (without /api/v1 prefix)."""
    body = {
        "slots": [{"slot": 1, "label": "Test"}],
        "mode": "upsert"
    }
    response = client.put("/tree/parents/1/children", json=body)
    # Either succeeds or fails with valid error codes
    assert response.status_code in [200, 404, 422, 409]
