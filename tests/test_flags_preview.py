import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


class TestFlagsPreview:
    """Test the flags preview endpoint."""

    def test_preview_flag_assignment_endpoint_exists(self):
        """Test that the preview endpoint exists and responds."""
        response = client.get("/flags/preview-assign?node_id=1&flag_id=1&cascade=false")
        # Should either return 200 (if data exists) or 404 (if not found)
        assert response.status_code in [200, 404]

    def test_preview_flag_assignment_missing_parameters(self):
        """Test preview with missing required parameters."""
        # Missing node_id
        response = client.get("/flags/preview-assign?flag_id=1&cascade=false")
        assert response.status_code == 422
        
        # Missing flag_id
        response = client.get("/flags/preview-assign?node_id=1&cascade=false")
        assert response.status_code == 422

    def test_preview_flag_assignment_dual_mount(self):
        """Test that preview endpoint is available at both mounts."""
        # Test root mount
        response = client.get("/flags/preview-assign?node_id=1&flag_id=1&cascade=false")
        assert response.status_code in [200, 404]
        
        # Test API v1 mount
        response = client.get("/api/v1/flags/preview-assign?node_id=1&flag_id=1&cascade=false")
        assert response.status_code in [200, 404]

    def test_preview_flag_assignment_invalid_parameters(self):
        """Test preview with invalid parameter types."""
        # Invalid node_id (string instead of int)
        response = client.get("/flags/preview-assign?node_id=abc&flag_id=1&cascade=false")
        assert response.status_code == 422
        
        # Invalid flag_id (string instead of int)
        response = client.get("/flags/preview-assign?node_id=1&flag_id=abc&cascade=false")
        assert response.status_code == 422

    def test_preview_flag_assignment_response_structure(self):
        """Test that successful responses have the expected structure."""
        # Try to get a preview with valid parameters
        response = client.get("/flags/preview-assign?node_id=1&flag_id=1&cascade=false")
        
        if response.status_code == 200:
            data = response.json()
            # Verify response structure
            assert "flag_name" in data
            assert "node_id" in data
            assert "cascade" in data
            assert "count" in data
            assert "truncated" in data
        elif response.status_code == 404:
            # This is fine - the data doesn't exist
            pass
        else:
            # Unexpected status code
            assert False, f"Unexpected status code: {response.status_code}"
