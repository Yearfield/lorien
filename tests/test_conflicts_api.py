"""
Tests for the conflicts validation API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


class TestDuplicateLabels:
    """Test duplicate labels conflict detection."""
    
    def test_duplicate_labels_endpoint_returns_200(self):
        """Test that /tree/conflicts/duplicate-labels returns 200."""
        response = client.get("/tree/conflicts/duplicate-labels")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_duplicate_labels_pagination_works(self):
        """Test that pagination parameters are respected."""
        response = client.get("/tree/conflicts/duplicate-labels?limit=10&offset=0")
        assert response.status_code == 200
        
        response2 = client.get("/tree/conflicts/duplicate-labels?limit=5&offset=10")
        assert response2.status_code == 200
        
        # Results should be different (unless we have exactly 10 duplicates)
        assert len(response.json()) <= 10
        assert len(response2.json()) <= 5
    
    def test_duplicate_labels_dual_mount(self):
        """Test that endpoint works at both root and /api/v1 paths."""
        root_response = client.get("/tree/conflicts/duplicate-labels")
        v1_response = client.get("/api/v1/tree/conflicts/duplicate-labels")
        
        assert root_response.status_code == 200
        assert v1_response.status_code == 200
        assert root_response.json() == v1_response.json()
    
    def test_duplicate_labels_structure(self):
        """Test that duplicate labels response has correct structure."""
        response = client.get("/tree/conflicts/duplicate-labels?limit=1")
        assert response.status_code == 200
        
        data = response.json()
        if data:  # If we have duplicates
            duplicate = data[0]
            required_keys = ["parent_id", "parent_label", "label", "count", "child_ids"]
            for key in required_keys:
                assert key in duplicate
            
            assert isinstance(duplicate["parent_id"], int)
            assert isinstance(duplicate["parent_label"], str)
            assert isinstance(duplicate["label"], str)
            assert isinstance(duplicate["count"], int)
            assert isinstance(duplicate["child_ids"], list)
            assert duplicate["count"] > 1


class TestOrphanNodes:
    """Test orphan node detection."""
    
    def test_orphan_nodes_endpoint_returns_200(self):
        """Test that /tree/conflicts/orphans returns 200."""
        response = client.get("/tree/conflicts/orphans")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_orphan_nodes_pagination_works(self):
        """Test that pagination parameters are respected."""
        response = client.get("/tree/conflicts/orphans?limit=10&offset=0")
        assert response.status_code == 200
        
        response2 = client.get("/tree/conflicts/orphans?limit=5&offset=10")
        assert response2.status_code == 200
        
        assert len(response.json()) <= 10
        assert len(response2.json()) <= 5
    
    def test_orphan_nodes_dual_mount(self):
        """Test that endpoint works at both root and /api/v1 paths."""
        root_response = client.get("/tree/conflicts/orphans")
        v1_response = client.get("/api/v1/tree/conflicts/orphans")
        
        assert root_response.status_code == 200
        assert v1_response.status_code == 200
        assert root_response.json() == v1_response.json()
    
    def test_orphan_nodes_structure(self):
        """Test that orphan nodes response has correct structure."""
        response = client.get("/tree/conflicts/orphans?limit=1")
        assert response.status_code == 200
        
        data = response.json()
        if data:  # If we have orphans
            orphan = data[0]
            required_keys = ["id", "parent_id", "label", "depth"]
            for key in required_keys:
                assert key in orphan
            
            assert isinstance(orphan["id"], int)
            assert isinstance(orphan["parent_id"], int)
            assert isinstance(orphan["label"], str)
            assert isinstance(orphan["depth"], int)
    
    def test_orphan_nodes_empty_in_healthy_db(self):
        """Test that healthy databases may return empty orphan lists."""
        response = client.get("/tree/conflicts/orphans")
        assert response.status_code == 200
        
        # Empty list is valid for healthy databases
        data = response.json()
        assert isinstance(data, list)


class TestDepthAnomalies:
    """Test depth anomaly detection."""
    
    def test_depth_anomalies_endpoint_returns_200(self):
        """Test that /tree/conflicts/depth-anomalies returns 200."""
        response = client.get("/tree/conflicts/depth-anomalies")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_depth_anomalies_pagination_works(self):
        """Test that pagination parameters are respected."""
        response = client.get("/tree/conflicts/depth-anomalies?limit=10&offset=0")
        assert response.status_code == 200
        
        response2 = client.get("/tree/conflicts/depth-anomalies?limit=5&offset=10")
        assert response2.status_code == 200
        
        assert len(response.json()) <= 10
        assert len(response2.json()) <= 5
    
    def test_depth_anomalies_dual_mount(self):
        """Test that endpoint works at both root and /api/v1 paths."""
        root_response = client.get("/tree/conflicts/depth-anomalies")
        v1_response = client.get("/api/v1/tree/conflicts/depth-anomalies")
        
        assert root_response.status_code == 200
        assert v1_response.status_code == 200
        assert root_response.json() == v1_response.json()
    
    def test_depth_anomalies_structure(self):
        """Test that depth anomalies response has correct structure."""
        response = client.get("/tree/conflicts/depth-anomalies?limit=1")
        assert response.status_code == 200
        
        data = response.json()
        if data:  # If we have anomalies
            anomaly = data[0]
            required_keys = ["id", "parent_id", "label", "depth", "anomaly"]
            for key in required_keys:
                assert key in anomaly
            
            assert isinstance(anomaly["id"], int)
            assert isinstance(anomaly["label"], str)
            assert isinstance(anomaly["depth"], int)
            assert isinstance(anomaly["anomaly"], str)
            
            # parent_id can be None for root nodes
            if anomaly["parent_id"] is not None:
                assert isinstance(anomaly["parent_id"], int)
            
            # Check anomaly types
            assert anomaly["anomaly"] in ["ROOT_DEPTH", "PARENT_CHILD_DEPTH"]


class TestPaginationValidation:
    """Test pagination parameter validation."""
    
    def test_invalid_limit_rejected(self):
        """Test that invalid limit values are rejected."""
        # Too high limit
        response = client.get("/tree/conflicts/duplicate-labels?limit=1001")
        assert response.status_code == 422  # Validation error
        
        # Too low limit
        response = client.get("/tree/conflicts/duplicate-labels?limit=0")
        assert response.status_code == 422  # Validation error
        
        # Negative limit
        response = client.get("/tree/conflicts/duplicate-labels?limit=-1")
        assert response.status_code == 422  # Validation error
    
    def test_invalid_offset_rejected(self):
        """Test that invalid offset values are rejected."""
        # Negative offset
        response = client.get("/tree/conflicts/duplicate-labels?offset=-1")
        assert response.status_code == 422  # Validation error
    
    def test_valid_pagination_parameters(self):
        """Test that valid pagination parameters are accepted."""
        valid_limits = [1, 25, 50, 100, 1000]
        valid_offsets = [0, 10, 100, 1000]
        
        for limit in valid_limits:
            for offset in valid_offsets:
                response = client.get(f"/tree/conflicts/duplicate-labels?limit={limit}&offset={offset}")
                assert response.status_code == 200


class TestPerformance:
    """Test that endpoints return results quickly."""
    
    def test_duplicate_labels_fast_response(self):
        """Test that duplicate labels endpoint responds quickly."""
        import time
        start_time = time.time()
        
        response = client.get("/tree/conflicts/duplicate-labels?limit=100")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 0.1  # Should respond in under 100ms
    
    def test_orphan_nodes_fast_response(self):
        """Test that orphan nodes endpoint responds quickly."""
        import time
        start_time = time.time()
        
        response = client.get("/tree/conflicts/orphans?limit=100")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 0.1  # Should respond in under 100ms
    
    def test_depth_anomalies_fast_response(self):
        """Test that depth anomalies endpoint responds quickly."""
        import time
        start_time = time.time()
        
        response = client.get("/tree/conflicts/depth-anomalies?limit=100")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 0.1  # Should respond in under 100ms


if __name__ == "__main__":
    pytest.main([__file__])
