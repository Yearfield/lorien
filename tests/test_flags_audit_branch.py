import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


class TestFlagsAuditBranch:
    """Test the enhanced flags audit endpoint with branch support."""

    def test_audit_endpoint_exists(self):
        """Test that the audit endpoint exists and responds."""
        response = client.get("/flags/audit/")
        # Should return 200 with audit data
        assert response.status_code == 200

    def test_audit_with_branch_parameter(self):
        """Test audit with branch parameter."""
        # Test with branch=false
        response = client.get("/flags/audit/?node_id=1&branch=false")
        assert response.status_code == 200
        
        # Test with branch=true
        response = client.get("/flags/audit/?node_id=1&branch=true")
        assert response.status_code == 200

    def test_audit_with_filters(self):
        """Test audit with various filters."""
        response = client.get("/flags/audit/?node_id=1&flag_id=1&user=test&branch=true&limit=50")
        assert response.status_code == 200

    def test_audit_dual_mount(self):
        """Test that audit endpoint is available at both mounts."""
        # Test root mount
        response = client.get("/flags/audit/?node_id=1&branch=false")
        assert response.status_code == 200
        
        # Test API v1 mount
        response = client.get("/api/v1/flags/audit/?node_id=1&branch=false")
        assert response.status_code == 200

    def test_audit_branch_parameter_validation(self):
        """Test branch parameter validation."""
        # Valid boolean values
        response = client.get("/flags/audit/?node_id=1&branch=true")
        assert response.status_code == 200
        
        response = client.get("/flags/audit/?node_id=1&branch=false")
        assert response.status_code == 200
        
        # Invalid boolean values should be handled gracefully
        response = client.get("/flags/audit/?node_id=1&branch=invalid")
        assert response.status_code == 422

    def test_audit_branch_performance(self):
        """Test that branch audit doesn't exceed performance threshold."""
        import time
        start_time = time.time()
        
        response = client.get("/flags/audit/?node_id=1&branch=true")
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert response.status_code == 200
        assert duration < 0.1  # Should complete in under 100ms

    def test_audit_response_structure(self):
        """Test that audit responses have the expected structure."""
        response = client.get("/flags/audit/?node_id=1&branch=true")
        assert response.status_code == 200
        
        data = response.json()
        if len(data) > 0:
            # Verify response structure for first item
            item = data[0]
            assert "id" in item
            assert "node_id" in item
            assert "flag_id" in item
            assert "action" in item
            assert "user" in item
            assert "ts" in item
            
            # Check for enhanced fields when branch=true
            if "flag_name" in item:
                assert "node_label" in item
