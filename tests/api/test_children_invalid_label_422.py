"""Tests for child label validation returning 422 with field context."""

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_invalid_child_label_returns_422():
    """Test that invalid child label returns 422 with correct field location."""
    # Test with empty label (after trimming)
    body = {
        "children": [
            {"slot": 1, "label": "Valid Label"},
            {"slot": 2, "label": ""},  # Empty label
            {"slot": 3, "label": "Another Valid"},
            {"slot": 4, "label": "Valid Four"},
            {"slot": 5, "label": "Valid Five"}
        ]
    }

    response = client.post("/api/v1/tree/1/children", json=body)
    assert response.status_code == 422

    detail = response.json()["detail"][0]
    assert detail["loc"] == ["body", "children", 1, "label"]  # Index 1 is the empty label
    assert detail["type"] == "value_error"
    assert "cannot be empty" in detail["msg"].lower()

def test_invalid_characters_in_child_label_returns_422():
    """Test that child label with invalid characters returns 422."""
    body = {
        "children": [
            {"slot": 1, "label": "Valid Label"},
            {"slot": 2, "label": "Invalid@Chars!"},  # Invalid characters
            {"slot": 3, "label": "Another Valid"},
            {"slot": 4, "label": "Valid Four"},
            {"slot": 5, "label": "Valid Five"}
        ]
    }

    response = client.post("/api/v1/tree/1/children", json=body)
    assert response.status_code == 422

    detail = response.json()["detail"][0]
    assert detail["loc"] == ["body", "children", 1, "label"]  # Index 1 has invalid chars
    assert detail["type"] == "value_error"
    assert "must be alnum" in detail["msg"].lower()

def test_valid_child_labels_pass_validation():
    """Test that valid child labels pass validation."""
    # This test may fail if parent_id=1 doesn't exist, but we're testing the validation path
    body = {
        "children": [
            {"slot": 1, "label": "Valid Label One"},
            {"slot": 2, "label": "Valid Label Two"},
            {"slot": 3, "label": "Valid Label Three"},
            {"slot": 4, "label": "Valid Label Four"},
            {"slot": 5, "label": "Valid Label Five"}
        ]
    }

    response = client.post("/api/v1/tree/1/children", json=body)

    # Either succeeds (200) if parent exists, or fails with 404, but not 422
    assert response.status_code in [200, 404]
    if response.status_code == 422:
        # If it fails with 422, it shouldn't be due to label validation
        detail = response.json()["detail"][0]
        assert "children" not in str(detail["loc"])  # Not a child label validation error

def test_multiple_invalid_labels_return_correct_indices():
    """Test that multiple invalid labels return correct indices."""
    body = {
        "children": [
            {"slot": 1, "label": ""},  # Invalid: empty
            {"slot": 2, "label": "Valid Two"},
            {"slot": 3, "label": "Invalid#Chars"},  # Invalid: special chars
            {"slot": 4, "label": "Valid Four"},
            {"slot": 5, "label": ""}   # Invalid: empty
        ]
    }

    response = client.post("/api/v1/tree/1/children", json=body)
    assert response.status_code == 422

    detail = response.json()["detail"][0]  # Should catch first error
    assert detail["loc"] == ["body", "children", 0, "label"]  # First empty label at index 0
