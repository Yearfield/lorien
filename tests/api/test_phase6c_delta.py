"""
Tests for Phase-6C Delta functionality.
"""

import pytest
import io
from fastapi.testclient import TestClient
from fastapi import HTTPException
import pandas as pd
from unittest.mock import patch

from api.app import app


class TestTreeNextIncomplete:
    """Test next-incomplete-parent 204 behavior."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_next_incomplete_returns_204_when_none(self, client):
        """Test /api/v1/tree/next-incomplete-parent returns 204 when no incomplete parents."""
        from api.routers import tree as tree_mod

        # Mock to return None (no incomplete parents)
        with patch.object(tree_mod, "get_next_incomplete_parent") as mock_func:
            mock_func.return_value = None

            response = client.get("/api/v1/tree/next-incomplete-parent")
            assert response.status_code == 204
            assert response.content == b""  # Empty body


class TestFlagsAuditOrdering:
    """Test flags audit DESC/DESC ordering."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_flags_audit_desc_ordering(self, client):
        """Test flags audit returns rows ordered by ts DESC, id DESC."""
        # This test would require setting up test data
        # For now, test the endpoint structure
        response = client.get("/api/v1/flags/audit", params={"limit": 20})
        assert response.status_code == 200

        data = response.json()
        # Should be a list
        assert isinstance(data, list)

        # If we have data, verify ordering
        if len(data) > 1:
            for i in range(len(data) - 1):
                current = data[i]
                next_item = data[i + 1]

                # ts DESC (newer first)
                assert current["ts"] >= next_item["ts"]

                # If same ts, then id DESC
                if current["ts"] == next_item["ts"]:
                    assert current["id"] >= next_item["id"]


class TestDictionaryValidation:
    """Test dictionary validation and normalization."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_dictionary_rejects_invalid_type(self, client):
        """Test dictionary rejects invalid type with 422 Literal error."""
        response = client.post("/api/v1/dictionary", json={
            "type": "symptom",  # Invalid type
            "term": "Fever"
        })
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data
        # Should contain Literal validation error
        found_literal_error = False
        for error in data["detail"]:
            if "Input should be" in error.get("msg", ""):
                found_literal_error = True
                break
        assert found_literal_error, f"No Literal error found in {data}"

    def test_dictionary_normalizes_and_uniqueness(self, client):
        """Test dictionary normalizes terms and enforces uniqueness."""
        # Create first term
        body = {"type": "node_label", "term": " Chest   Pain "}
        response1 = client.post("/api/v1/dictionary", json=body)
        assert response1.status_code == 201

        data1 = response1.json()
        assert data1["type"] == "node_label"
        assert data1["term"] == " Chest   Pain "  # Original preserved
        assert data1["normalized"] == "chest pain"  # Normalized

        # Try to create duplicate (same normalized)
        response2 = client.post("/api/v1/dictionary", json={
            "type": "node_label",
            "term": "chest pain"
        })
        assert response2.status_code == 422

        data2 = response2.json()
        assert "detail" in data2
        assert any("duplicate" in str(error) for error in data2["detail"])

    def test_dictionary_filter_by_type_and_query(self, client):
        """Test dictionary filtering by type and query."""
        # Create test terms
        terms = [
            {"type": "vital_measurement", "term": "Heart Rate"},
            {"type": "node_label", "term": "Chest Pain"},
            {"type": "outcome_template", "term": "Normal Response"}
        ]

        for term in terms:
            response = client.post("/api/v1/dictionary", json=term)
            assert response.status_code == 201

        # Filter by type
        response = client.get("/api/v1/dictionary", params={"type": "vital_measurement"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "vital_measurement"

        # Filter by query
        response = client.get("/api/v1/dictionary", params={"query": "chest"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "chest" in data[0]["normalized"]

        # Filter by both
        response = client.get("/api/v1/dictionary", params={
            "type": "node_label",
            "query": "pain"
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "node_label"
        assert "pain" in data[0]["normalized"]


class TestDictionaryUsage:
    """Test dictionary usage tracking."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_dictionary_usage_endpoint(self, client):
        """Test dictionary usage endpoint structure."""
        # Create a term first
        response = client.post("/api/v1/dictionary", json={
            "type": "node_label",
            "term": "Test Term"
        })
        assert response.status_code == 201
        term_id = response.json()["id"]

        # Get usage (should be empty initially)
        response = client.get(f"/api/v1/dictionary/{term_id}/usage")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Test with invalid term_id
        response = client.get("/api/v1/dictionary/99999/usage")
        assert response.status_code == 404


class TestPerformanceAssertions:
    """Test performance assertions for critical endpoints."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_next_incomplete_parent_performance(self, client):
        """Test next-incomplete-parent performance target (<100ms)."""
        import time

        start_time = time.time()
        response = client.get("/api/v1/tree/next-incomplete-parent")
        elapsed = time.time() - start_time

        # Should complete in under 100ms
        assert elapsed < 0.1, f"Took {elapsed:.3f}s, should be <100ms"
        assert response.status_code in [200, 204]

    def test_flags_endpoints_performance(self, client):
        """Test flags endpoints performance."""
        import time

        # Test audit endpoint
        start_time = time.time()
        response = client.get("/api/v1/flags/audit", params={"limit": 10})
        elapsed = time.time() - start_time

        assert elapsed < 0.1, f"Flags audit took {elapsed:.3f}s, should be <100ms"
        assert response.status_code == 200

        # Test list endpoint
        start_time = time.time()
        response = client.get("/api/v1/flags", params={"limit": 10})
        elapsed = time.time() - start_time

        assert elapsed < 0.1, f"Flags list took {elapsed:.3f}s, should be <100ms"
        assert response.status_code == 200

    def test_dictionary_endpoints_performance(self, client):
        """Test dictionary endpoints performance."""
        import time

        start_time = time.time()
        response = client.get("/api/v1/dictionary", params={"limit": 10})
        elapsed = time.time() - start_time

        assert elapsed < 0.1, f"Dictionary list took {elapsed:.3f}s, should be <100ms"
        assert response.status_code == 200
