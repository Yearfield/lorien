"""
Tests for the next-incomplete-parent endpoint.
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
def setup_tree_with_holes(client, test_db):
    """Set up a tree with missing slots for testing."""
    import sqlite3
    from storage.sqlite import SQLiteRepository
    
    # Initialize the database schema
    repo = SQLiteRepository(db_path=test_db)
    
    # Connect to the test database and create test data
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # Create root node
    cursor.execute("INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (?, ?, ?, ?, ?)", 
                   (None, 0, 0, "Vital Measurement A", False))
    root1_id = cursor.lastrowid
    
    # Create some children (missing slots 2 and 4)
    cursor.execute("INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (?, ?, ?, ?, ?)", 
                   (root1_id, 1, 1, "Node 1", False))
    child1_id = cursor.lastrowid
    
    cursor.execute("INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (?, ?, ?, ?, ?)", 
                   (root1_id, 1, 3, "Node 3", False))
    child3_id = cursor.lastrowid
    
    cursor.execute("INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (?, ?, ?, ?, ?)", 
                   (root1_id, 1, 5, "Node 5", False))
    child5_id = cursor.lastrowid
    
    # Create another root with complete children
    cursor.execute("INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (?, ?, ?, ?, ?)", 
                   (None, 0, 0, "Vital Measurement B", False))
    root2_id = cursor.lastrowid
    
    for slot in range(1, 6):
        cursor.execute("INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (?, ?, ?, ?, ?)", 
                       (root2_id, 1, slot, f"Complete Node {slot}", False))
    
    conn.commit()
    conn.close()
    
    return {
        "root1_id": root1_id,
        "root2_id": root2_id,
        "child1_id": child1_id,
        "child3_id": child3_id,
        "child5_id": child5_id
    }


class TestNextIncompleteParent:
    """Tests for the next-incomplete-parent endpoint."""
    
    def test_next_incomplete_parent_with_holes(self, client, setup_tree_with_holes):
        """Test getting next incomplete parent with missing slots."""
        response = client.get("/api/v1/tree/next-incomplete-parent")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return the first incomplete parent
        assert data["parent_id"] == setup_tree_with_holes["root1_id"]
        assert data["label"] == "Vital Measurement A"
        assert data["missing_slots"] == "2,4"  # Missing slots 2 and 4
        assert data["depth"] == 0
    
    def test_next_incomplete_parent_when_complete(self, client, test_db):
        """Test when all parents are complete."""
        import sqlite3
        from storage.sqlite import SQLiteRepository
        
        # Initialize the database schema
        repo = SQLiteRepository(db_path=test_db)
        
        # Connect to the test database and create complete tree
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Create root with all 5 children
        cursor.execute("INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (?, ?, ?, ?, ?)", 
                       (None, 0, 0, "Complete Root", False))
        root_id = cursor.lastrowid
        
        for slot in range(1, 6):
            cursor.execute("INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (?, ?, ?, ?, ?)", 
                           (root_id, 1, slot, f"Child {slot}", False))
        
        conn.commit()
        conn.close()
        
        response = client.get("/api/v1/tree/next-incomplete-parent")
        
        assert response.status_code == 204
        assert "No incomplete parents found" in response.json()["detail"]
    
    def test_next_incomplete_parent_performance(self, client, setup_tree_with_holes):
        """Test that the endpoint responds within performance target (<100ms)."""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/tree/next-incomplete-parent")
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 0.1  # Should be under 100ms
    
    def test_next_incomplete_parent_deterministic(self, client, setup_tree_with_holes):
        """Test that the endpoint returns deterministic results."""
        # Call multiple times to ensure consistent results
        responses = []
        for _ in range(3):
            response = client.get("/api/v1/tree/next-incomplete-parent")
            assert response.status_code == 200
            responses.append(response.json())
        
        # All responses should be identical
        for response in responses[1:]:
            assert response == responses[0]
    
    def test_next_incomplete_parent_ordering(self, client, test_db):
        """Test that parents are returned in correct order (depth ASC, parent_id ASC)."""
        import sqlite3
        from storage.sqlite import SQLiteRepository
        
        # Initialize the database schema
        repo = SQLiteRepository(db_path=test_db)
        
        # Connect to the test database and create multiple incomplete parents
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Create multiple roots with missing children
        for i in range(3):
            cursor.execute("INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (?, ?, ?, ?, ?)", 
                           (None, 0, 0, f"Root {i}", False))
            root_id = cursor.lastrowid
            
            # Only add first child to make it incomplete
            cursor.execute("INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (?, ?, ?, ?, ?)", 
                           (root_id, 1, 1, f"Child 1 of Root {i}", False))
        
        conn.commit()
        conn.close()
        
        response = client.get("/api/v1/tree/next-incomplete-parent")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return the first root (lowest ID)
        assert data["label"] == "Root 0"
        assert data["missing_slots"] == "2,3,4,5"
