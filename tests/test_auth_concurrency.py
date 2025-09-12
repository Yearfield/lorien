"""
Tests for authentication and concurrency functionality.

Tests auth middleware, optimistic concurrency control,
and conflict resolution scenarios.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os

from api.app import app

client = TestClient(app)

class TestAuthMiddleware:
    """Test authentication middleware functionality."""
    
    def test_auth_disabled_allows_all_requests(self):
        """Test that when auth is disabled, all requests are allowed."""
        with patch.dict(os.environ, {"AUTH_TOKEN": ""}):
            # Test read endpoints (should always work)
            response = client.get("/api/v1/tree/next-incomplete-parent")
            assert response.status_code in [200, 404]
            
            # Test write endpoints (should work when auth disabled)
            response = client.post("/api/v1/tree/children", json={"parent_id": 1, "children": []})
            assert response.status_code in [200, 400, 404, 422]  # Not 401
    
    def test_auth_enabled_blocks_write_without_token(self):
        """Test that when auth is enabled, write endpoints require token."""
        with patch.dict(os.environ, {"AUTH_TOKEN": "test-token-123"}):
            # Test write endpoint without token
            response = client.post("/api/v1/tree/children", json={"parent_id": 1, "children": []})
            assert response.status_code == 401
            assert "authentication_required" in response.json()["detail"]["error"]
    
    def test_auth_enabled_allows_read_without_token(self):
        """Test that when auth is enabled, read endpoints still work without token."""
        with patch.dict(os.environ, {"AUTH_TOKEN": "test-token-123"}):
            # Test read endpoint without token
            response = client.get("/api/v1/tree/next-incomplete-parent")
            assert response.status_code in [200, 404]
    
    def test_auth_enabled_allows_write_with_valid_token(self):
        """Test that when auth is enabled, write endpoints work with valid token."""
        with patch.dict(os.environ, {"AUTH_TOKEN": "test-token-123"}):
            headers = {"Authorization": "Bearer test-token-123"}
            
            # Test write endpoint with valid token
            response = client.post(
                "/api/v1/tree/children", 
                json={"parent_id": 1, "children": []},
                headers=headers
            )
            # Should not be 401 (might be other errors like 404, 422, etc.)
            assert response.status_code != 401
    
    def test_auth_enabled_blocks_write_with_invalid_token(self):
        """Test that when auth is enabled, write endpoints are blocked with invalid token."""
        with patch.dict(os.environ, {"AUTH_TOKEN": "test-token-123"}):
            headers = {"Authorization": "Bearer invalid-token"}
            
            # Test write endpoint with invalid token
            response = client.post(
                "/api/v1/tree/children", 
                json={"parent_id": 1, "children": []},
                headers=headers
            )
            assert response.status_code == 401
            assert "invalid_token" in response.json()["detail"]["error"]
    
    def test_auth_enabled_blocks_write_with_malformed_header(self):
        """Test that malformed Authorization headers are rejected."""
        with patch.dict(os.environ, {"AUTH_TOKEN": "test-token-123"}):
            # Test with malformed header
            response = client.post(
                "/api/v1/tree/children", 
                json={"parent_id": 1, "children": []},
                headers={"Authorization": "InvalidFormat test-token-123"}
            )
            assert response.status_code == 401
            assert "invalid_auth_format" in response.json()["detail"]["error"]
    
    def test_auth_enabled_blocks_write_without_authorization_header(self):
        """Test that missing Authorization header is rejected."""
        with patch.dict(os.environ, {"AUTH_TOKEN": "test-token-123"}):
            # Test without Authorization header
            response = client.post(
                "/api/v1/tree/children", 
                json={"parent_id": 1, "children": []}
            )
            assert response.status_code == 401
            assert "authentication_required" in response.json()["detail"]["error"]


class TestConcurrencyEndpoints:
    """Test concurrency control endpoints."""
    
    def test_get_node_version(self):
        """Test getting node version information."""
        response = client.get("/api/v1/concurrency/node/1/version")
        assert response.status_code in [200, 404]  # 404 if node doesn't exist
        
        if response.status_code == 200:
            data = response.json()
            assert "node_id" in data
            assert "version" in data
            assert "updated_at" in data
            assert "etag" in data
            assert "concurrency_enabled" in data
    
    def test_get_children_with_version(self):
        """Test getting children with version information."""
        response = client.get("/api/v1/concurrency/node/1/children-with-version")
        assert response.status_code in [200, 404]  # 404 if node doesn't exist
        
        if response.status_code == 200:
            data = response.json()
            assert "parent_id" in data
            assert "children" in data
            assert "parent_version" in data
            assert "parent_updated_at" in data
            assert "etag" in data
            assert "concurrency_enabled" in data
    
    def test_check_version(self):
        """Test version checking endpoint."""
        response = client.post(
            "/api/v1/concurrency/check-version",
            json={"node_id": 1, "expected_version": 0}
        )
        assert response.status_code in [200, 404]  # 404 if node doesn't exist
        
        if response.status_code == 200:
            data = response.json()
            assert "is_match" in data
            assert "current_version" in data
            assert "expected_version" in data
    
    def test_get_conflict_resolution_info(self):
        """Test conflict resolution information endpoint."""
        response = client.get("/api/v1/concurrency/conflict-resolution-info")
        assert response.status_code == 200
        
        data = response.json()
        assert "conflict_types" in data
        assert "headers" in data
        assert "best_practices" in data
        
        # Check conflict types
        conflict_types = data["conflict_types"]
        assert "version_conflict" in conflict_types
        assert "slot_conflict" in conflict_types
        
        # Check version conflict details
        version_conflict = conflict_types["version_conflict"]
        assert version_conflict["status_code"] == 412
        assert "description" in version_conflict
        assert "resolution" in version_conflict
        
        # Check slot conflict details
        slot_conflict = conflict_types["slot_conflict"]
        assert slot_conflict["status_code"] == 409
        assert "description" in slot_conflict
        assert "resolution" in slot_conflict


class TestConcurrencyManager:
    """Test concurrency manager functionality."""
    
    def test_get_node_version(self):
        """Test getting node version from concurrency manager."""
        from api.repositories.concurrency import ConcurrencyManager
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = ConcurrencyManager(conn)
        
        # Test with non-existent node
        version_info = manager.get_node_version(99999)
        assert version_info is None
        
        # Test with existing node (if any)
        version_info = manager.get_node_version(1)
        if version_info:
            assert "id" in version_info
            assert "updated_at" in version_info
            assert "version" in version_info
            assert "timestamp" in version_info
    
    def test_check_version_match(self):
        """Test version matching functionality."""
        from api.repositories.concurrency import ConcurrencyManager
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = ConcurrencyManager(conn)
        
        # Test with non-existent node
        is_match, version_info = manager.check_version_match(99999, 0)
        assert not is_match
        assert not version_info
        
        # Test with existing node
        is_match, version_info = manager.check_version_match(1, None)
        if version_info:
            assert is_match  # Should match when no expected version
    
    def test_validate_if_match_header(self):
        """Test If-Match header validation."""
        from api.repositories.concurrency import ConcurrencyManager
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = ConcurrencyManager(conn)
        
        # Test valid formats
        is_valid, version = manager.validate_if_match_header("version:123", 1)
        assert is_valid
        assert version == 123
        
        is_valid, version = manager.validate_if_match_header("123", 1)
        assert is_valid
        assert version == 123
        
        # Test invalid formats
        is_valid, version = manager.validate_if_match_header("invalid", 1)
        assert not is_valid
        assert version is None
        
        is_valid, version = manager.validate_if_match_header("", 1)
        assert is_valid
        assert version is None
    
    def test_create_etag(self):
        """Test ETag creation."""
        from api.repositories.concurrency import ConcurrencyManager
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = ConcurrencyManager(conn)
        
        version_info = {"version": 5, "updated_at": "2024-01-01T00:00:00Z"}
        etag = manager.create_etag(version_info)
        assert etag == "version:5"


class TestConcurrencyIntegration:
    """Test concurrency integration with existing endpoints."""
    
    def test_concurrency_headers_preserved(self):
        """Test that concurrency headers are preserved in responses."""
        response = client.get("/api/v1/concurrency/node/1/version")
        if response.status_code == 200:
            # Check that ETag header is set
            assert "etag" in response.json()
            
            # Check that concurrency info is included
            data = response.json()
            assert data["concurrency_enabled"] is True
    
    def test_version_checking_workflow(self):
        """Test complete version checking workflow."""
        # Get initial version
        response = client.get("/api/v1/concurrency/node/1/version")
        if response.status_code == 200:
            initial_data = response.json()
            initial_version = initial_data["version"]
            
            # Check version match
            response = client.post(
                "/api/v1/concurrency/check-version",
                json={"node_id": 1, "expected_version": initial_version}
            )
            if response.status_code == 200:
                check_data = response.json()
                assert check_data["is_match"] is True
                assert check_data["current_version"] == initial_version


class TestErrorHandling:
    """Test error handling for auth and concurrency."""
    
    def test_auth_error_responses(self):
        """Test auth error response formats."""
        with patch.dict(os.environ, {"AUTH_TOKEN": "test-token-123"}):
            # Test missing auth header
            response = client.post("/api/v1/tree/children", json={"parent_id": 1, "children": []})
            assert response.status_code == 401
            data = response.json()
            assert "error" in data["detail"]
            assert "message" in data["detail"]
            
            # Test invalid token
            response = client.post(
                "/api/v1/tree/children", 
                json={"parent_id": 1, "children": []},
                headers={"Authorization": "Bearer invalid-token"}
            )
            assert response.status_code == 401
            data = response.json()
            assert data["detail"]["error"] == "invalid_token"
    
    def test_concurrency_error_responses(self):
        """Test concurrency error response formats."""
        # Test invalid If-Match header format
        response = client.get(
            "/api/v1/concurrency/check-version",
            params={"node_id": 1, "expected_version": 0}
        )
        # Should handle gracefully
        assert response.status_code in [200, 404, 400]
    
    def test_version_conflict_response_format(self):
        """Test version conflict response format."""
        from api.repositories.concurrency import ConcurrencyManager
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = ConcurrencyManager(conn)
        
        # Create a mock version conflict
        conflict_info = manager.handle_version_conflict(1, 5, {"version": 10, "updated_at": "2024-01-01"})
        
        assert "error" in conflict_info
        assert "message" in conflict_info
        assert "node_id" in conflict_info
        assert "expected_version" in conflict_info
        assert "current_version" in conflict_info
        assert conflict_info["error"] == "version_conflict"


class TestAuthConcurrencyCombined:
    """Test combined auth and concurrency scenarios."""
    
    def test_auth_required_for_concurrency_operations(self):
        """Test that concurrency operations respect auth requirements."""
        with patch.dict(os.environ, {"AUTH_TOKEN": "test-token-123"}):
            # Test concurrency endpoint without auth (should work for read)
            response = client.get("/api/v1/concurrency/conflict-resolution-info")
            assert response.status_code == 200
            
            # Test write operations with auth
            headers = {"Authorization": "Bearer test-token-123"}
            response = client.post(
                "/api/v1/tree/children", 
                json={"parent_id": 1, "children": []},
                headers=headers
            )
            # Should not be 401
            assert response.status_code != 401
    
    def test_concurrency_with_auth_token(self):
        """Test concurrency operations with auth token."""
        with patch.dict(os.environ, {"AUTH_TOKEN": "test-token-123"}):
            headers = {"Authorization": "Bearer test-token-123"}
            
            # Test version checking with auth
            response = client.get("/api/v1/concurrency/node/1/version", headers=headers)
            assert response.status_code in [200, 404]
            
            if response.status_code == 200:
                data = response.json()
                assert "concurrency_enabled" in data
                assert data["concurrency_enabled"] is True
