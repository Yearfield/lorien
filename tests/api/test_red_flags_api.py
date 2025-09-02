"""
Tests for red flags bulk operations API.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock, patch

from api.app import app
from api.routers.red_flags import BulkAttachRequest, BulkDetachRequest


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_repository():
    """Create mock repository."""
    return Mock()


class TestRedFlagsBulkOperations:
    """Test red flags bulk attach/detach operations."""
    
    @patch('api.routers.red_flags.get_repository')
    def test_bulk_attach_success(self, mock_get_repo, client):
        """Test successful bulk attach operation."""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Mock the connection context manager
        mock_conn = MagicMock()
        mock_repo._get_connection.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None
        
        # Mock cursor operations
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock flag exists check and already attached check
        # For each flag: 1) check if exists, 2) check if already attached
        mock_cursor.fetchone.side_effect = [
            (1,),  # Flag 1 exists
            None,  # Flag 1 not already attached
        ]
        
        # Mock successful operations
        mock_cursor.execute.return_value = None
        mock_cursor.lastrowid = 1
        
        response = client.post(
            "/api/v1/red-flags/bulk-attach",
            json={
                "node_id": 42,
                "red_flag_ids": [1]  # Only use flag 1 which exists in DB
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully attached 1 red flags"
        assert data["node_id"] == 42
        assert data["attached_count"] == 1
        assert data["total_requested"] == 1
    
    @patch('api.routers.red_flags.get_repository')
    def test_bulk_attach_idempotent(self, mock_get_repo, client):
        """Test that bulk attach is idempotent (duplicate flags ignored)."""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Mock the connection context manager
        mock_conn = MagicMock()
        mock_repo._get_connection.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None
        
        # Mock cursor operations
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock flag exists check and already attached check
        # For each flag: 1) check if exists, 2) check if already attached
        mock_cursor.fetchone.side_effect = [
            (1,),  # Flag 1 exists
            None,  # Flag 1 not already attached
            (2,),  # Flag 2 exists  
            None,  # Flag 2 not already attached
        ]
        
        # Mock successful operations
        mock_cursor.execute.return_value = None
        mock_cursor.lastrowid = 1
        
        response = client.post(
            "/api/v1/red-flags/bulk-attach",
            json={
                "node_id": 42,
                "red_flag_ids": [1, 1, 2]  # Duplicate flag 1
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["attached_count"] == 2  # Both flags attached
        assert data["total_requested"] == 3  # Total requested
    
    @patch('api.routers.red_flags.get_repository')
    def test_bulk_attach_flag_not_found(self, mock_get_repo, client):
        """Test bulk attach with non-existent flag."""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Mock the connection context manager
        mock_conn = MagicMock()
        mock_repo._get_connection.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None
        
        # Mock cursor operations
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock flag not found
        mock_cursor.fetchone.return_value = None
        
        response = client.post(
            "/api/v1/red-flags/bulk-attach",
            json={
                "node_id": 42,
                "red_flag_ids": [999]  # Non-existent flag
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["attached_count"] == 0  # No flags attached
        assert data["total_requested"] == 1
    
    @patch('api.routers.red_flags.get_repository')
    def test_bulk_detach_success(self, mock_get_repo, client):
        """Test successful bulk detach operation."""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Mock the connection context manager
        mock_conn = MagicMock()
        mock_repo._get_connection.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None
        
        # Mock cursor operations
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock flag currently attached
        mock_cursor.fetchone.side_effect = [
            (1,),  # Currently attached
            (1,),  # Currently attached
        ]
        
        # Mock successful operations
        mock_cursor.execute.return_value = None
        
        response = client.post(
            "/api/v1/red-flags/bulk-detach",
            json={
                "node_id": 42,
                "red_flag_ids": [1, 2]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully detached 2 red flags"
        assert data["node_id"] == 42
        assert data["detached_count"] == 2
        assert data["total_requested"] == 2
    
    @patch('api.routers.red_flags.get_repository')
    def test_bulk_detach_not_attached(self, mock_get_repo, client):
        """Test bulk detach with flags not currently attached."""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Mock the connection context manager
        mock_conn = MagicMock()
        mock_repo._get_connection.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None
        
        # Mock cursor operations
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock flag not currently attached
        mock_cursor.fetchone.return_value = None
        
        response = client.post(
            "/api/v1/red-flags/bulk-detach",
            json={
                "node_id": 42,
                "red_flag_ids": [1, 2]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["detached_count"] == 0  # No flags detached
        assert data["total_requested"] == 2


class TestRedFlagsAudit:
    """Test red flags audit functionality."""
    
    @patch('api.routers.red_flags.get_repository')
    def test_get_audit_all(self, mock_get_repo, client):
        """Test getting all audit records."""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Mock the connection context manager
        mock_conn = MagicMock()
        mock_repo._get_connection.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None
        
        # Mock cursor operations
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock audit records
        mock_cursor.fetchall.return_value = [
            (1, 42, 1, "attach", "2024-01-01T10:00:00Z", "Flag 1"),
            (2, 42, 2, "detach", "2024-01-01T11:00:00Z", "Flag 2"),
        ]
        
        response = client.get("/api/v1/red-flags/audit")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Check first record
        assert data[0]["id"] == 1
        assert data[0]["node_id"] == 42
        assert data[0]["red_flag_id"] == 1
        assert data[0]["action"] == "attach"
        assert data[0]["red_flag_name"] == "Flag 1"
        
        # Check second record
        assert data[1]["id"] == 2
        assert data[1]["node_id"] == 42
        assert data[1]["red_flag_id"] == 2
        assert data[1]["action"] == "detach"
        assert data[1]["red_flag_name"] == "Flag 2"
    
    @patch('api.routers.red_flags.get_repository')
    def test_get_audit_by_node(self, mock_get_repo, client):
        """Test getting audit records for specific node."""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Mock the connection context manager
        mock_conn = MagicMock()
        mock_repo._get_connection.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None
        
        # Mock cursor operations
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock audit records for specific node
        mock_cursor.fetchall.return_value = [
            (1, 42, 1, "attach", "2024-01-01T10:00:00Z", "Flag 1"),
        ]
        
        response = client.get("/api/v1/red-flags/audit?node_id=42")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["node_id"] == 42
        assert data[0]["action"] == "attach"
