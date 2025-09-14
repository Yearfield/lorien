"""
Tests for conflicts group resolve validation API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


class TestGroupResolveValidation:
    """Test validation for conflicts group resolve endpoint."""

    def test_resolve_must_choose_five_labels(self):
        """Test 422 when chosen length != 5."""
        response = client.post(
            "/api/v1/tree/conflicts/group/resolve",
            json={
                "keep_id": 1,
                "chosen": ["Label1", "Label2", "Label3", "Label4"]  # Only 4 labels
            }
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert any(
            item.get("type") == "value_error.must_choose_five" 
            for item in data["detail"]
        )

    def test_resolve_duplicate_labels(self):
        """Test 422 when chosen has duplicates."""
        response = client.post(
            "/api/v1/tree/conflicts/group/resolve",
            json={
                "keep_id": 1,
                "chosen": ["Label1", "Label2", "Label3", "Label4", "Label1"]  # Duplicate
            }
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert any(
            item.get("type") == "value_error.duplicate_labels" 
            for item in data["detail"]
        )

    def test_resolve_invalid_keep_id(self):
        """Test 422 when keep_id not found."""
        response = client.post(
            "/api/v1/tree/conflicts/group/resolve",
            json={
                "keep_id": 99999,  # Non-existent ID
                "chosen": ["Label1", "Label2", "Label3", "Label4", "Label5"]
            }
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert any(
            item.get("type") == "value_error.keep_id" 
            for item in data["detail"]
        )

    def test_resolve_empty_labels(self):
        """Test 422 when chosen contains empty strings."""
        response = client.post(
            "/api/v1/tree/conflicts/group/resolve",
            json={
                "keep_id": 1,
                "chosen": ["Label1", "", "Label3", "Label4", "Label5"]  # Empty string
            }
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_resolve_whitespace_only_labels(self):
        """Test 422 when chosen contains whitespace-only strings."""
        response = client.post(
            "/api/v1/tree/conflicts/group/resolve",
            json={
                "keep_id": 1,
                "chosen": ["Label1", "   ", "Label3", "Label4", "Label5"]  # Whitespace only
            }
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_resolve_valid_request_structure(self):
        """Test that valid request structure is accepted (even if keep_id doesn't exist)."""
        response = client.post(
            "/api/v1/tree/conflicts/group/resolve",
            json={
                "keep_id": 1,
                "chosen": ["Label1", "Label2", "Label3", "Label4", "Label5"]
            }
        )
        # Should not be 422 for structure validation, might be 422 for keep_id not found
        assert response.status_code in [200, 422]
        if response.status_code == 422:
            data = response.json()
            assert "detail" in data
            # Should be keep_id error, not structure error
            assert any(
                item.get("type") == "value_error.keep_id" 
                for item in data["detail"]
            )
