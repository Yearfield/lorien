"""
Simple e2e smoke test for tree upsert functionality.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_upsert_children_and_readback():
    """Test that we can upsert children and read them back."""
    parent_id = 1
    
    # Test payload with exactly 5 children
    payload = {
        "children": [
            {"slot": 1, "label": "A"},
            {"slot": 2, "label": "B"},
            {"slot": 3, "label": "C"},
            {"slot": 4, "label": "D"},
            {"slot": 5, "label": "E"}
        ]
    }
    
    # Perform upsert
    r = client.post(f"/tree/{parent_id}/children", json=payload)
    assert r.status_code == 200, f"Upsert failed: {r.text}"
    
    # Read back the children
    r2 = client.get(f"/tree/{parent_id}/children")
    assert r2.status_code == 200, f"Get children failed: {r2.text}"
    
    # Verify the data
    children_data = r2.json()
    assert "children" in children_data, "Response missing 'children' field"
    
    children = children_data["children"]
    assert len(children) == 5, f"Expected 5 children, got {len(children)}"
    
    # Verify slot labels
    labels = {c["slot"]: c["label"] for c in children}
    assert labels[1] == "A", f"Slot 1 should be 'A', got '{labels[1]}'"
    assert labels[5] == "E", f"Slot 5 should be 'E', got '{labels[5]}'"


def test_upsert_validation_exactly_5_children():
    """Test that upsert enforces exactly 5 children."""
    parent_id = 1
    
    # Test with too many children
    payload_too_many = {
        "children": [
            {"slot": 1, "label": "A"},
            {"slot": 2, "label": "B"},
            {"slot": 3, "label": "C"},
            {"slot": 4, "label": "D"},
            {"slot": 5, "label": "E"},
            {"slot": 6, "label": "F"}  # Too many!
        ]
    }
    
    r = client.post(f"/tree/{parent_id}/children", json=payload_too_many)
    assert r.status_code == 422, "Should reject more than 5 children (422 Unprocessable Entity - validation error)"
    
    # Test with too few children
    payload_too_few = {
        "children": [
            {"slot": 1, "label": "A"},
            {"slot": 2, "label": "B"},
            {"slot": 3, "label": "C"}
        ]
    }
    
    r = client.post(f"/tree/{parent_id}/children", json=payload_too_few)
    assert r.status_code == 422, "Should reject fewer than 5 children (422 Unprocessable Entity - validation error)"


def test_upsert_duplicate_slots_rejected():
    """Test that duplicate slots are rejected."""
    parent_id = 1
    
    payload_duplicate = {
        "children": [
            {"slot": 1, "label": "A"},
            {"slot": 2, "label": "B"},
            {"slot": 3, "label": "C"},
            {"slot": 4, "label": "D"},
            {"slot": 1, "label": "Duplicate"}  # Duplicate slot 1
        ]
    }
    
    r = client.post(f"/tree/{parent_id}/children", json=payload_duplicate)
    assert r.status_code == 409, "Should reject duplicate slots (409 Conflict)"
