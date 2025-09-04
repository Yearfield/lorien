"""
Performance tests for critical endpoints.

Targets:
- /tree/next-incomplete-parent: <100 ms
- /tree/path: <50 ms
"""

import pytest
import time
from fastapi.testclient import TestClient
from api.app import app


class TestEndpointPerformance:
    """Performance tests for critical endpoints."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_next_incomplete_parent_performance(self, client):
        """Test /tree/next-incomplete-parent performance target."""
        start_time = time.time()

        response = client.get("/api/v1/tree/next-incomplete-parent")

        elapsed = time.time() - start_time

        # Should complete in under 100ms
        assert elapsed < 0.1, ".2f"

        # Should return 204 if no incomplete parents (or 200 with data)
        assert response.status_code in [200, 204]

        print(".2f")

    def test_path_readout_performance(self, client):
        """Test /tree/path performance target."""
        # First, create a test node by checking if any exist
        response = client.get("/api/v1/tree/next-incomplete-parent")

        if response.status_code == 200:
            # Use the node_id from next-incomplete-parent
            data = response.json()
            node_id = data["parent_id"]
        else:
            # Skip test if no nodes exist
            pytest.skip("No test nodes available for path performance test")

        # Test path readout performance
        start_time = time.time()

        response = client.get(f"/api/v1/tree/path?node_id={node_id}")

        elapsed = time.time() - start_time

        # Should complete in under 50ms
        assert elapsed < 0.05, ".2f"

        # Should return 200 with path data
        assert response.status_code == 200

        data = response.json()
        assert "node_id" in data
        assert "is_leaf" in data
        assert "depth" in data
        assert "vital_measurement" in data
        assert "nodes" in data
        assert "csv_header" in data

        # Nodes should be exactly length 5
        assert len(data["nodes"]) == 5

        # CSV header should match V1 contract
        expected_header = [
            "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
            "Diagnostic Triage", "Actions"
        ]
        assert data["csv_header"] == expected_header

        print(".2f")

    def test_health_endpoints_performance(self, client):
        """Test health endpoints are fast."""
        # Test main health
        start_time = time.time()
        response = client.get("/api/v1/health")
        elapsed = time.time() - start_time

        assert elapsed < 0.05, ".2f"
        assert response.status_code == 200

        data = response.json()
        assert "version" in data
        assert "db" in data
        assert "features" in data

        # Test LLM health
        start_time = time.time()
        response = client.get("/api/v1/llm/health")
        elapsed = time.time() - start_time

        assert elapsed < 0.05, ".2f"
        assert response.status_code in [200, 503]

        data = response.json()
        assert "ok" in data
        assert "llm_enabled" in data
        assert "ready" in data

        if "checked_at" in data:
            assert data["checked_at"].endswith("Z")

        print(".2f")

    def test_flags_endpoints_performance(self, client):
        """Test flags endpoints performance."""
        # Test list flags
        start_time = time.time()
        response = client.get("/api/v1/flags?limit=10")
        elapsed = time.time() - start_time

        assert elapsed < 0.1, ".2f"
        assert response.status_code == 200

        # Test audit endpoint
        start_time = time.time()
        response = client.get("/api/v1/flags/audit?limit=10")
        elapsed = time.time() - start_time

        assert elapsed < 0.1, ".2f"
        assert response.status_code == 200

        print(".2f")

    def test_dictionary_endpoints_performance(self, client):
        """Test dictionary endpoints performance."""
        # Test list terms
        start_time = time.time()
        response = client.get("/api/v1/dictionary?limit=10")
        elapsed = time.time() - start_time

        assert elapsed < 0.1, ".2f"
        assert response.status_code == 200

        print(".2f")

    @pytest.mark.parametrize("endpoint,method,max_time", [
        ("/api/v1/health", "GET", 0.05),
        ("/api/v1/llm/health", "GET", 0.05),
        ("/api/v1/flags", "GET", 0.1),
        ("/api/v1/flags/audit", "GET", 0.1),
        ("/api/v1/dictionary", "GET", 0.1),
        ("/api/v1/tree/next-incomplete-parent", "GET", 0.1),
    ])
    def test_endpoint_response_times(self, client, endpoint, method, max_time):
        """Parameterized test for endpoint response times."""
        start_time = time.time()

        if method == "GET":
            response = client.get(endpoint)
        elif method == "POST":
            response = client.post(endpoint)
        else:
            pytest.fail(f"Unsupported method: {method}")

        elapsed = time.time() - start_time

        assert elapsed < max_time, ".2f"
        assert response.status_code in [200, 204, 503]  # Allow 503 for LLM when disabled

        print(".2f")
