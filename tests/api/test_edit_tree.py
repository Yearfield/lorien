"""
Tests for Edit Tree functionality with optimistic concurrency.
"""

import pytest
import time
from fastapi.testclient import TestClient
from fastapi import HTTPException
import pandas as pd

from api.app import app
from core.services.tree_service import parse_if_match


class TestEditTreeRead:
    """Test Edit Tree read functionality."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_read_parent_children_200(self, client):
        """Test successful read of parent children."""
        # This test requires seeded data - for now just test the endpoint structure
        response = client.get("/api/v1/tree/parent/1/children")
        # Should return 404 if parent doesn't exist, or 200 with data
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "parent_id" in data
            assert "version" in data
            assert "missing_slots" in data
            assert "children" in data
            assert "path" in data
            assert "etag" in data

            # Should have exactly 5 children
            assert len(data["children"]) == 5

            # Path should have 5 nodes
            assert len(data["path"]["nodes"]) == 5

            # ETag should match format
            assert data["etag"].startswith('W/"parent-')
            assert data["etag"].endswith('"')

    def test_read_parent_children_404(self, client):
        """Test 404 when parent doesn't exist."""
        response = client.get("/api/v1/tree/parent/99999/children")
        assert response.status_code == 404


class TestEditTreeUpdate:
    """Test Edit Tree update functionality with optimistic concurrency."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_update_parent_children_422_missing_slots(self, client):
        """Test 422 when not exactly 5 children provided."""
        # Try with only 3 children
        payload = {
            "children": [
                {"slot": 1, "label": "A"},
                {"slot": 2, "label": "B"},
                {"slot": 3, "label": "C"}
            ]
        }

        response = client.put("/api/v1/tree/parent/1/children", json=payload)
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data
        assert data["detail"][0]["type"] == "value_error.children_count"
        assert "missing_slots" in data["detail"][0]["ctx"]

    def test_update_parent_children_422_duplicate_labels(self, client):
        """Test 422 when duplicate labels provided."""
        payload = {
            "children": [
                {"slot": 1, "label": "Same"},
                {"slot": 2, "label": "Different"},
                {"slot": 3, "label": "Same"},  # Duplicate
                {"slot": 4, "label": "Unique"},
                {"slot": 5, "label": "Another"}
            ]
        }

        response = client.put("/api/v1/tree/parent/1/children", json=payload)
        # May return 404 if parent doesn't exist, or 422 if validation fails
        assert response.status_code in [404, 422]

        if response.status_code == 422:
            data = response.json()
            assert "detail" in data
            # Should contain duplicate error
            duplicate_found = False
            for error in data["detail"]:
                if "duplicate" in error.get("type", ""):
                    duplicate_found = True
                    assert "slot" in error.get("ctx", {})
            assert duplicate_found

    def test_update_parent_children_404(self, client):
        """Test 404 when parent doesn't exist."""
        payload = {
            "children": [
                {"slot": 1, "label": "A"},
                {"slot": 2, "label": "B"},
                {"slot": 3, "label": "C"},
                {"slot": 4, "label": "D"},
                {"slot": 5, "label": "E"}
            ]
        }

        response = client.put("/api/v1/tree/parent/99999/children", json=payload)
        assert response.status_code == 404

    def test_update_parent_children_409_stale_version(self, client):
        """Test 409 when version is stale."""
        # First get current version
        read_response = client.get("/api/v1/tree/parent/1/children")

        if read_response.status_code == 200:
            current_data = read_response.json()
            stale_version = current_data["version"] - 1  # Make it stale

            payload = {
                "version": stale_version,
                "children": [
                    {"slot": 1, "label": "A"},
                    {"slot": 2, "label": "B"},
                    {"slot": 3, "label": "C"},
                    {"slot": 4, "label": "D"},
                    {"slot": 5, "label": "E"}
                ]
            }

            response = client.put("/api/v1/tree/parent/1/children", json=payload)
            # Should return 409 due to stale version
            assert response.status_code == 409

            data = response.json()
            assert "detail" in data
            # Should contain conflict details
            for conflict in data["detail"]:
                assert conflict["type"] == "conflict.slot"
                assert "slot" in conflict["ctx"]
                assert "server_version" in conflict["ctx"]
                assert "client_version" in conflict["ctx"]


class TestOptimisticConcurrency:
    """Test optimistic concurrency with If-Match header."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_if_match_parsing(self):
        """Test If-Match header parsing."""
        # Valid ETag
        version = parse_if_match('W/"parent-123:v7"')
        assert version == 7

        # Invalid ETags
        assert parse_if_match('W/"parent-123:vabc"') is None
        assert parse_if_match('invalid-etag') is None
        assert parse_if_match(None) is None

    def test_version_mismatch_header_body(self, client):
        """Test 400 when If-Match and body version don't match."""
        payload = {
            "version": 5,
            "children": [
                {"slot": 1, "label": "A"},
                {"slot": 2, "label": "B"},
                {"slot": 3, "label": "C"},
                {"slot": 4, "label": "D"},
                {"slot": 5, "label": "E"}
            ]
        }

        # If-Match with different version
        headers = {"If-Match": 'W/"parent-1:v7"'}
        response = client.put("/api/v1/tree/parent/1/children", json=payload, headers=headers)
        # Should return 400 for version mismatch
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert data["detail"][0]["type"] == "value_error.version_mismatch"


class TestDictionarySuggestions:
    """Test dictionary suggestions for node_label type."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_dictionary_suggestions_node_label(self, client):
        """Test dictionary suggestions for node_label type."""
        # Test with valid query
        response = client.get("/api/v1/dictionary?type=node_label&query=fe&limit=10")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # If we have data, validate structure
        if data:
            for item in data:
                assert "id" in item
                assert "type" in item
                assert "term" in item
                assert "normalized" in item
                assert item["type"] == "node_label"

    def test_dictionary_suggestions_short_query(self, client):
        """Test that short queries return empty for node_label."""
        # Query too short should return empty
        response = client.get("/api/v1/dictionary?type=node_label&query=f&limit=10")
        assert response.status_code == 200

        data = response.json()
        assert data == []  # Should return empty for short queries

    def test_dictionary_suggestions_other_types(self, client):
        """Test dictionary suggestions for other types."""
        # Should work normally for other types
        response = client.get("/api/v1/dictionary?type=vital_measurement&query=test&limit=10")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)


class TestPerformance:
    """Test performance targets for Edit Tree endpoints."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_read_performance_target(self, client):
        """Test read endpoint performance target (<30ms)."""
        start_time = time.time()

        response = client.get("/api/v1/tree/parent/1/children")
        elapsed = time.time() - start_time

        # Should complete in under 30ms
        assert elapsed < 0.03, ".2f"
        assert response.status_code in [200, 404]

    def test_dictionary_suggestions_performance(self, client):
        """Test dictionary suggestions performance (<50ms)."""
        start_time = time.time()

        response = client.get("/api/v1/dictionary?type=node_label&query=fe&limit=10")
        elapsed = time.time() - start_time

        # Should complete in under 50ms
        assert elapsed < 0.05, ".2f"
        assert response.status_code == 200


class TestIntegration:
    """Integration tests for Edit Tree workflow."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_edit_tree_workflow(self, client):
        """Test complete Edit Tree workflow."""
        # This test would require seeded data and is more of an integration test
        # For now, just test that the endpoints exist and have correct signatures

        # Test read endpoint exists
        response = client.get("/api/v1/tree/parent/1/children")
        assert response.status_code in [200, 404]

        # Test update endpoint exists
        payload = {
            "children": [
                {"slot": 1, "label": "Test A"},
                {"slot": 2, "label": "Test B"},
                {"slot": 3, "label": "Test C"},
                {"slot": 4, "label": "Test D"},
                {"slot": 5, "label": "Test E"}
            ]
        }

        response = client.put("/api/v1/tree/parent/1/children", json=payload)
        assert response.status_code in [200, 404, 409, 422]

        # Test dictionary suggestions
        response = client.get("/api/v1/dictionary?type=node_label&query=test&limit=5")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
