"""
Integration tests for red flags API functionality using real database.
"""

import pytest
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient

from api.app import app


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    test_db.close()
    
    # Set environment variable for test database
    os.environ['LORIEN_DB_PATH'] = test_db.name
    
    yield test_db.name
    
    # Clean up
    if os.path.exists(test_db.name):
        os.unlink(test_db.name)


@pytest.fixture
def client(test_db):
    """Create test client with test database."""
    return TestClient(app)


@pytest.fixture
def setup_test_data(client, test_db):
    """Set up test data including red flags and nodes."""
    import sqlite3
    from storage.sqlite import SQLiteRepository
    
    # Initialize the database schema
    repo = SQLiteRepository(db_path=test_db)
    
    # Apply the red flag audit migration
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # Read and execute the migration
    migration_path = Path(__file__).parent.parent.parent / 'storage' / 'migrations' / '001_add_red_flag_audit.sql'
    with open(migration_path, 'r') as f:
        migration_sql = f.read()
    cursor.executescript(migration_sql)
    conn.commit()
    conn.close()
    
    # Connect to the test database and create test data
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # Create a test red flag
    cursor.execute("INSERT INTO red_flags (name, description) VALUES (?, ?)", ("Test Flag", "Test flag for integration tests"))
    flag_id = cursor.lastrowid
    
    # Create a test node (parent node)
    cursor.execute("INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (?, ?, ?, ?, ?)", 
                   (None, 0, 0, "Test Parent", False))
    node_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return {"flag_id": flag_id, "node_id": node_id}


class TestRedFlagsIntegration:
    """Integration tests for red flags API endpoints."""
    
    def test_bulk_attach_success(self, client, setup_test_data):
        """Test successful bulk attach operation."""
        flag_id = setup_test_data["flag_id"]
        node_id = setup_test_data["node_id"]
        
        response = client.post(
            "/api/v1/red-flags/bulk-attach",
            json={
                "node_id": node_id,
                "red_flag_ids": [flag_id]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["attached_count"] == 1
        assert data["total_requested"] == 1
        assert "Successfully attached 1 red flags" in data["message"]
    
    def test_bulk_attach_idempotent(self, client, setup_test_data):
        """Test that bulk attach is idempotent."""
        flag_id = setup_test_data["flag_id"]
        node_id = setup_test_data["node_id"]
        
        # First attach
        response1 = client.post(
            "/api/v1/red-flags/bulk-attach",
            json={
                "node_id": node_id,
                "red_flag_ids": [flag_id]
            }
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["attached_count"] == 1
        
        # Second attach (should be idempotent)
        response2 = client.post(
            "/api/v1/red-flags/bulk-attach",
            json={
                "node_id": node_id,
                "red_flag_ids": [flag_id]
            }
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["attached_count"] == 0  # Already attached
    
    def test_bulk_detach_success(self, client, setup_test_data):
        """Test successful bulk detach operation."""
        flag_id = setup_test_data["flag_id"]
        node_id = setup_test_data["node_id"]
        
        # First attach the flag
        response = client.post(
            "/api/v1/red-flags/bulk-attach",
            json={
                "node_id": node_id,
                "red_flag_ids": [flag_id]
            }
        )
        assert response.status_code == 200
        
        # Then detach it
        response = client.post(
            "/api/v1/red-flags/bulk-detach",
            json={
                "node_id": node_id,
                "red_flag_ids": [flag_id]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["detached_count"] == 1
        assert data["total_requested"] == 1
        assert "Successfully detached 1 red flags" in data["message"]
    
    def test_bulk_detach_nonexistent(self, client, setup_test_data):
        """Test detaching a flag that's not attached."""
        flag_id = setup_test_data["flag_id"]
        node_id = setup_test_data["node_id"]
        
        # Try to detach without attaching first
        response = client.post(
            "/api/v1/red-flags/bulk-detach",
            json={
                "node_id": node_id,
                "red_flag_ids": [flag_id]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["detached_count"] == 0  # Nothing to detach
        assert data["total_requested"] == 1
    
    def test_get_audit_all(self, client, setup_test_data):
        """Test getting all audit records."""
        flag_id = setup_test_data["flag_id"]
        node_id = setup_test_data["node_id"]
        
        # Perform an attach operation to create audit record
        response = client.post(
            "/api/v1/red-flags/bulk-attach",
            json={
                "node_id": node_id,
                "red_flag_ids": [flag_id]
            }
        )
        assert response.status_code == 200
        
        # Get audit records
        response = client.get("/api/v1/red-flags/audit")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check that our operation is in the audit
        audit_record = data[0]
        assert "id" in audit_record
        assert "node_id" in audit_record
        assert "red_flag_id" in audit_record
        assert "action" in audit_record
        assert "ts" in audit_record
        assert audit_record["action"] == "attach"
    
    def test_get_audit_by_node(self, client, setup_test_data):
        """Test getting audit records for a specific node."""
        flag_id = setup_test_data["flag_id"]
        node_id = setup_test_data["node_id"]
        
        # Perform an attach operation to create audit record
        response = client.post(
            "/api/v1/red-flags/bulk-attach",
            json={
                "node_id": node_id,
                "red_flag_ids": [flag_id]
            }
        )
        assert response.status_code == 200
        
        # Get audit records for this node
        response = client.get(f"/api/v1/red-flags/audit?node_id={node_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # All records should be for this node
        for record in data:
            assert record["node_id"] == node_id
    
    def test_bulk_attach_nonexistent_flag(self, client, setup_test_data):
        """Test attaching a non-existent flag."""
        node_id = setup_test_data["node_id"]
        
        response = client.post(
            "/api/v1/red-flags/bulk-attach",
            json={
                "node_id": node_id,
                "red_flag_ids": [999]  # Non-existent flag ID
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["attached_count"] == 0  # No flags attached
        assert data["total_requested"] == 1
    
    def test_bulk_attach_nonexistent_node(self, client, setup_test_data):
        """Test attaching to a non-existent node."""
        flag_id = setup_test_data["flag_id"]
        
        response = client.post(
            "/api/v1/red-flags/bulk-attach",
            json={
                "node_id": 999,  # Non-existent node ID
                "red_flag_ids": [flag_id]
            }
        )
        
        # This should return 200 but with 0 attached due to foreign key constraint
        assert response.status_code == 200
        data = response.json()
        assert data["attached_count"] == 0
        assert data["total_requested"] == 1
