"""
Tests for the Flags namespace API endpoints.
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
    """Set up test data including flags and nodes."""
    import sqlite3
    from storage.sqlite import SQLiteRepository
    
    # Initialize the database schema
    repo = SQLiteRepository(db_path=test_db)
    
    # Apply the flags migration
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # Read and execute the migration
    migration_path = Path(__file__).parent.parent.parent / 'storage' / 'migrations' / '002_add_flags_namespace.sql'
    with open(migration_path, 'r') as f:
        migration_sql = f.read()
    cursor.executescript(migration_sql)
    conn.commit()
    conn.close()
    
    # Connect to the test database and create test data
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # Create test flags
    cursor.execute("INSERT INTO flags (label) VALUES (?)", ("Test Flag 1",))
    flag1_id = cursor.lastrowid
    
    cursor.execute("INSERT INTO flags (label) VALUES (?)", ("Test Flag 2",))
    flag2_id = cursor.lastrowid
    
    # Create test nodes
    cursor.execute("INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (?, ?, ?, ?, ?)", 
                   (None, 0, 0, "Test Root", False))
    root_id = cursor.lastrowid
    
    cursor.execute("INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (?, ?, ?, ?, ?)", 
                   (root_id, 1, 1, "Test Child 1", True))
    child1_id = cursor.lastrowid
    
    cursor.execute("INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (?, ?, ?, ?, ?)", 
                   (root_id, 1, 2, "Test Child 2", True))
    child2_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return {
        "flag1_id": flag1_id,
        "flag2_id": flag2_id,
        "root_id": root_id,
        "child1_id": child1_id,
        "child2_id": child2_id
    }


class TestFlagsNamespace:
    """Tests for the Flags namespace API endpoints."""
    
    def test_list_flags(self, client, setup_test_data):
        """Test listing flags."""
        response = client.get("/api/v1/flags/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Check that flags are returned with id and label
        flag_labels = [flag["label"] for flag in data]
        assert "Test Flag 1" in flag_labels
        assert "Test Flag 2" in flag_labels
    
    def test_list_flags_with_query(self, client, setup_test_data):
        """Test listing flags with search query."""
        response = client.get("/api/v1/flags/?query=Flag 1")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["label"] == "Test Flag 1"
    
    def test_assign_flag_non_cascade(self, client, setup_test_data):
        """Test assigning flag to single node (non-cascade)."""
        flag_id = setup_test_data["flag1_id"]
        node_id = setup_test_data["child1_id"]
        
        response = client.post(
            "/api/v1/flags/assign",
            json={
                "node_id": node_id,
                "flag_id": flag_id,
                "cascade": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["affected"] == 1
        assert data["node_ids"] == [node_id]
    
    def test_assign_flag_cascade(self, client, setup_test_data):
        """Test assigning flag with cascade to descendants."""
        flag_id = setup_test_data["flag1_id"]
        root_id = setup_test_data["root_id"]
        child1_id = setup_test_data["child1_id"]
        child2_id = setup_test_data["child2_id"]
        
        response = client.post(
            "/api/v1/flags/assign",
            json={
                "node_id": root_id,
                "flag_id": flag_id,
                "cascade": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["affected"] == 3  # root + 2 children
        assert set(data["node_ids"]) == {root_id, child1_id, child2_id}
    
    def test_assign_flag_idempotent(self, client, setup_test_data):
        """Test that flag assignment is idempotent."""
        flag_id = setup_test_data["flag1_id"]
        node_id = setup_test_data["child1_id"]
        
        # First assignment
        response1 = client.post(
            "/api/v1/flags/assign",
            json={
                "node_id": node_id,
                "flag_id": flag_id,
                "cascade": False
            }
        )
        assert response1.status_code == 200
        assert response1.json()["affected"] == 1
        
        # Second assignment (should be idempotent)
        response2 = client.post(
            "/api/v1/flags/assign",
            json={
                "node_id": node_id,
                "flag_id": flag_id,
                "cascade": False
            }
        )
        assert response2.status_code == 200
        assert response2.json()["affected"] == 0  # Already assigned
    
    def test_remove_flag(self, client, setup_test_data):
        """Test removing flag from node."""
        flag_id = setup_test_data["flag1_id"]
        node_id = setup_test_data["child1_id"]
        
        # First assign the flag
        client.post(
            "/api/v1/flags/assign",
            json={
                "node_id": node_id,
                "flag_id": flag_id,
                "cascade": False
            }
        )
        
        # Then remove it
        response = client.post(
            "/api/v1/flags/remove",
            json={
                "node_id": node_id,
                "flag_id": flag_id,
                "cascade": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["affected"] == 1
        assert data["node_ids"] == [node_id]
    
    def test_remove_flag_nonexistent(self, client, setup_test_data):
        """Test removing flag that's not assigned."""
        flag_id = setup_test_data["flag1_id"]
        node_id = setup_test_data["child1_id"]
        
        response = client.post(
            "/api/v1/flags/remove",
            json={
                "node_id": node_id,
                "flag_id": flag_id,
                "cascade": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["affected"] == 0  # Nothing to remove
    
    def test_assign_flag_nonexistent_node(self, client, setup_test_data):
        """Test assigning flag to non-existent node."""
        flag_id = setup_test_data["flag1_id"]
        
        response = client.post(
            "/api/v1/flags/assign",
            json={
                "node_id": 999,  # Non-existent node
                "flag_id": flag_id,
                "cascade": False
            }
        )
        
        assert response.status_code == 404
        assert "Node 999 not found" in response.json()["detail"]
    
    def test_assign_flag_nonexistent_flag(self, client, setup_test_data):
        """Test assigning non-existent flag."""
        node_id = setup_test_data["child1_id"]
        
        response = client.post(
            "/api/v1/flags/assign",
            json={
                "node_id": node_id,
                "flag_id": 999,  # Non-existent flag
                "cascade": False
            }
        )
        
        assert response.status_code == 404
        assert "Flag 999 not found" in response.json()["detail"]
    
    def test_flags_audit(self, client, setup_test_data):
        """Test getting flag audit records."""
        flag_id = setup_test_data["flag1_id"]
        node_id = setup_test_data["child1_id"]
        
        # Perform an assign operation to create audit record
        response = client.post(
            "/api/v1/flags/assign",
            json={
                "node_id": node_id,
                "flag_id": flag_id,
                "cascade": False
            }
        )
        assert response.status_code == 200
        
        # Get audit records
        response = client.get("/api/v1/flags/audit")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        # Check that our operation is in the audit
        audit_record = data[0]
        assert "id" in audit_record
        assert "node_id" in audit_record
        assert "flag_id" in audit_record
        assert "action" in audit_record
        assert "ts" in audit_record
        assert audit_record["action"] == "assign"
    
    def test_flags_audit_by_node(self, client, setup_test_data):
        """Test getting flag audit records for a specific node."""
        flag_id = setup_test_data["flag1_id"]
        node_id = setup_test_data["child1_id"]
        
        # Perform an assign operation to create audit record
        response = client.post(
            "/api/v1/flags/assign",
            json={
                "node_id": node_id,
                "flag_id": flag_id,
                "cascade": False
            }
        )
        assert response.status_code == 200
        
        # Get audit records for this node
        response = client.get(f"/api/v1/flags/audit?node_id={node_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        # All records should be for this node
        for record in data:
            assert record["node_id"] == node_id
