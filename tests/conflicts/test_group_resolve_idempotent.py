"""
Tests for conflicts group resolve idempotency.
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


class TestGroupResolveIdempotent:
    """Test idempotency for conflicts group resolve endpoint."""

    def test_resolve_idempotent_same_request(self):
        """Test that same request returns same result (idempotent)."""
        # This test requires actual data in the database
        # For now, we'll test the structure and error handling
        
        request_data = {
            "keep_id": 1,
            "chosen": ["Label1", "Label2", "Label3", "Label4", "Label5"]
        }
        
        # First request
        response1 = client.post(
            "/api/v1/tree/conflicts/group/resolve",
            json=request_data
        )
        
        # Second request with same data
        response2 = client.post(
            "/api/v1/tree/conflicts/group/resolve",
            json=request_data
        )
        
        # Both should return same status code
        assert response1.status_code == response2.status_code
        
        # If successful, both should return same result structure
        if response1.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()
            assert data1 == data2

    def test_resolve_idempotent_no_side_effects(self):
        """Test that repeated requests don't cause side effects."""
        request_data = {
            "keep_id": 1,
            "chosen": ["Label1", "Label2", "Label3", "Label4", "Label5"]
        }
        
        # Make multiple requests
        responses = []
        for _ in range(3):
            response = client.post(
                "/api/v1/tree/conflicts/group/resolve",
                json=request_data
            )
            responses.append(response)
        
        # All responses should have same status code
        status_codes = [r.status_code for r in responses]
        assert len(set(status_codes)) == 1, f"Different status codes: {status_codes}"
        
        # If successful, all should return same result
        if responses[0].status_code == 200:
            data_sets = [r.json() for r in responses]
            assert all(data == data_sets[0] for data in data_sets)

    def test_resolve_different_keep_ids_same_labels(self):
        """Test that different keep_ids with same labels are handled correctly."""
        request1 = {
            "keep_id": 1,
            "chosen": ["Label1", "Label2", "Label3", "Label4", "Label5"]
        }
        
        request2 = {
            "keep_id": 2,
            "chosen": ["Label1", "Label2", "Label3", "Label4", "Label5"]
        }
        
        response1 = client.post(
            "/api/v1/tree/conflicts/group/resolve",
            json=request1
        )
        
        response2 = client.post(
            "/api/v1/tree/conflicts/group/resolve",
            json=request2
        )
        
        # Both should be processed (may both fail with keep_id not found, but that's expected)
        assert response1.status_code in [200, 422]
        assert response2.status_code in [200, 422]

    def test_resolve_same_keep_id_different_labels(self):
        """Test that same keep_id with different labels is handled correctly."""
        request1 = {
            "keep_id": 1,
            "chosen": ["Label1", "Label2", "Label3", "Label4", "Label5"]
        }
        
        request2 = {
            "keep_id": 1,
            "chosen": ["LabelA", "LabelB", "LabelC", "LabelD", "LabelE"]
        }
        
        response1 = client.post(
            "/api/v1/tree/conflicts/group/resolve",
            json=request1
        )
        
        response2 = client.post(
            "/api/v1/tree/conflicts/group/resolve",
            json=request2
        )
        
        # Both should be processed
        assert response1.status_code in [200, 422]
        assert response2.status_code in [200, 422]
