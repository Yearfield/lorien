"""
Integration tests for atomic slot upsert functionality.
"""

import pytest
import sqlite3
from fastapi.testclient import TestClient
from unittest.mock import patch

from api.app import app
from storage.sqlite import SQLiteRepository
from core.models import Node


@pytest.fixture
def client(test_repository):
    """Create test client with test repository."""
    from unittest.mock import patch
    
    # Override the get_repository dependency to return our test repository
    def get_test_repository():
        return test_repository
    
    # Patch the function where it's actually used
    with patch('api.dependencies.get_repository', get_test_repository):
        client = TestClient(app)
        yield client


@pytest.fixture
def test_repository():
    """Create test repository."""
    import tempfile
    import os
    
    # Create a temporary database file
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    
    try:
        repo = SQLiteRepository(db_path=temp_db.name)
        yield repo
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_db.name):
            os.unlink(temp_db.name)


@pytest.fixture
def sample_parent(test_repository):
    """Create a sample parent node for testing."""
    # First create a root node (depth=0, parent_id=None)
    root = Node(
        parent_id=None,
        depth=0,
        slot=0,
        label="Test Root",
        is_leaf=False
    )
    root_id = test_repository.create_node(root)
    
    # Then create a parent node (depth=1, parent_id=root_id)
    parent = Node(
        parent_id=root_id,
        depth=1,
        slot=1,
        label="Test Parent",
        is_leaf=False
    )
    parent_id = test_repository.create_node(parent)
    return parent_id


class TestAtomicSlotUpsert:
    """Test atomic slot upsert functionality."""
    
    def test_upsert_children_atomic_creates_new_children(self, test_repository, sample_parent):
        """Test that atomic upsert creates new children correctly."""
        children_data = [
            {"slot": 1, "label": "Child 1"},
            {"slot": 2, "label": "Child 2"},
            {"slot": 3, "label": "Child 3"}
        ]
        
        result = test_repository.upsert_children_atomic(sample_parent, children_data)
        
        assert result["parent_id"] == sample_parent
        assert result["children_processed"] == 3
        assert result["children_created"] == 3
        assert result["children_updated"] == 0
        assert len(result["errors"]) == 0
        
        # Verify children were actually created
        children = test_repository.get_children(sample_parent)
        assert len(children) == 3
        
        # Check specific children
        child_slots = {child.slot for child in children}
        assert child_slots == {1, 2, 3}
        
        child_labels = {child.label for child in children}
        assert child_labels == {"Child 1", "Child 2", "Child 3"}
    
    def test_upsert_children_atomic_updates_existing_children(self, test_repository, sample_parent):
        """Test that atomic upsert updates existing children correctly."""
        # First create some children
        initial_children = [
            {"slot": 1, "label": "Original Child 1"},
            {"slot": 2, "label": "Original Child 2"}
        ]
        test_repository.upsert_children_atomic(sample_parent, initial_children)
        
        # Now update them
        updated_children = [
            {"slot": 1, "label": "Updated Child 1"},
            {"slot": 2, "label": "Updated Child 2"},
            {"slot": 3, "label": "New Child 3"}
        ]
        
        result = test_repository.upsert_children_atomic(sample_parent, updated_children)
        
        assert result["children_processed"] == 3
        assert result["children_created"] == 1
        assert result["children_updated"] == 2
        assert len(result["errors"]) == 0
        
        # Verify updates
        children = test_repository.get_children(sample_parent)
        child_map = {child.slot: child.label for child in children}
        
        assert child_map[1] == "Updated Child 1"
        assert child_map[2] == "Updated Child 2"
        assert child_map[3] == "New Child 3"
    
    def test_upsert_children_atomic_handles_duplicate_slots(self, test_repository, sample_parent):
        """Test that atomic upsert handles duplicate slots within the same request."""
        children_data = [
            {"slot": 1, "label": "Child 1"},
            {"slot": 1, "label": "Child 1 Duplicate"}  # Duplicate slot
        ]
    
        result = test_repository.upsert_children_atomic(sample_parent, children_data)
    
        # Should process both but the second one will update the first one
        assert result["children_processed"] == 2
        assert result["children_created"] == 1
        assert result["children_updated"] == 1  # The second duplicate updates the first
        assert len(result["errors"]) == 0
        
        # Verify only one child exists with the updated label
        children = test_repository.get_children(sample_parent)
        assert len(children) == 1
        assert children[0].label == "Child 1 Duplicate"
    
    def test_upsert_children_atomic_validates_slot_range(self, test_repository, sample_parent):
        """Test that atomic upsert validates slot range (1-5)."""
        children_data = [
            {"slot": 0, "label": "Invalid Slot 0"},
            {"slot": 6, "label": "Invalid Slot 6"},
            {"slot": 1, "label": "Valid Slot 1"}
        ]
        
        result = test_repository.upsert_children_atomic(sample_parent, children_data)
        
        assert result["children_processed"] == 1  # Only valid slot processed
        assert result["children_created"] == 1
        assert len(result["errors"]) == 2
        
        # Check error messages
        error_messages = " ".join(result["errors"])
        assert "Invalid slot 0" in error_messages
        assert "Invalid slot 6" in error_messages
    
    def test_upsert_children_atomic_validates_labels(self, test_repository, sample_parent):
        """Test that atomic upsert validates labels (non-empty)."""
        children_data = [
            {"slot": 1, "label": ""},  # Empty label
            {"slot": 2, "label": "   "},  # Whitespace only
            {"slot": 3, "label": "Valid Label"}
        ]
        
        result = test_repository.upsert_children_atomic(sample_parent, children_data)
        
        assert result["children_processed"] == 1  # Only valid label processed
        assert result["children_created"] == 1
        assert len(result["errors"]) == 2
        
        # Check error messages
        error_messages = " ".join(result["errors"])
        assert "cannot be empty" in error_messages
    
    def test_upsert_children_atomic_rollback_on_error(self, test_repository, sample_parent):
        """Test that atomic upsert rolls back on critical errors."""
        # Create initial children
        initial_children = [
            {"slot": 1, "label": "Original Child 1"},
            {"slot": 2, "label": "Original Child 2"}
        ]
        test_repository.upsert_children_atomic(sample_parent, initial_children)
        
        # Try to upsert with invalid parent (should cause rollback)
        with pytest.raises(ValueError):
            test_repository.upsert_children_atomic(99999, [{"slot": 1, "label": "Should not be created"}])
        
        # Verify original children are still there (rollback worked)
        children = test_repository.get_children(sample_parent)
        assert len(children) == 2
        child_labels = {child.label for child in children}
        assert child_labels == {"Original Child 1", "Original Child 2"}
    
    def test_upsert_children_atomic_leaf_parent_validation(self, test_repository):
        """Test that atomic upsert prevents adding children to leaf nodes."""
        # Create a proper tree structure: root -> depth1 -> depth2 -> depth3 -> depth4 -> leaf
        root = Node(
            parent_id=None,
            depth=0,
            slot=0,
            label="Test Root",
            is_leaf=False
        )
        root_id = test_repository.create_node(root)
        
        # Create nodes at each depth level
        depth1_node = Node(
            parent_id=root_id,
            depth=1,
            slot=1,
            label="Depth 1 Node",
            is_leaf=False
        )
        depth1_id = test_repository.create_node(depth1_node)
        
        depth2_node = Node(
            parent_id=depth1_id,
            depth=2,
            slot=1,
            label="Depth 2 Node",
            is_leaf=False
        )
        depth2_id = test_repository.create_node(depth2_node)
        
        depth3_node = Node(
            parent_id=depth2_id,
            depth=3,
            slot=1,
            label="Depth 3 Node",
            is_leaf=False
        )
        depth3_id = test_repository.create_node(depth3_node)
        
        depth4_node = Node(
            parent_id=depth3_id,
            depth=4,
            slot=1,
            label="Depth 4 Node",
            is_leaf=False
        )
        depth4_id = test_repository.create_node(depth4_node)
        
        # Create a leaf node (depth 5) under the depth4 node
        leaf_node = Node(
            parent_id=depth4_id,
            depth=5,
            slot=1,
            label="Leaf Node",
            is_leaf=True
        )
        leaf_id = test_repository.create_node(leaf_node)
        
        # Try to add children to the leaf node (should fail)
        children_data = [{"slot": 1, "label": "Child of Leaf"}]
        
        with pytest.raises(ValueError, match="leaf node and cannot have children"):
            test_repository.upsert_children_atomic(leaf_id, children_data)
    
    def test_upsert_children_atomic_nonexistent_parent(self, test_repository):
        """Test that atomic upsert handles nonexistent parent."""
        children_data = [{"slot": 1, "label": "Should not be created"}]
        
        with pytest.raises(ValueError) as exc_info:
            test_repository.upsert_children_atomic(99999, children_data)
        
        assert "Parent node 99999 not found" in str(exc_info.value)


class TestAPISlotUpsert:
    """Test API endpoints for slot upsert."""
    
    def test_api_upsert_children_success(self, client, test_repository, sample_parent):
        """Test successful upsert via API."""
        upsert_data = {
            "children": [
                {"slot": 1, "label": "API Child 1"},
                {"slot": 2, "label": "API Child 2"},
                {"slot": 3, "label": "API Child 3"}
            ]
        }
        
        response = client.post(f"/api/v1/tree/{sample_parent}/children", json=upsert_data)
        
        # Should return 200
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Successfully upserted" in data["message"]
        assert "details" in data
        assert "created" in data["details"]
        assert "updated" in data["details"]
    
    def test_api_upsert_children_too_many(self, client, test_repository, sample_parent):
        """Test API rejects more than 5 children."""
        upsert_data = {
            "children": [
                {"slot": 1, "label": "Child 1"},
                {"slot": 2, "label": "Child 2"},
                {"slot": 3, "label": "Child 3"},
                {"slot": 4, "label": "Child 4"},
                {"slot": 5, "label": "Child 5"},
                {"slot": 6, "label": "Child 6"}  # Too many
            ]
        }
        
        response = client.post(f"/api/v1/tree/{sample_parent}/children", json=upsert_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Cannot have more than 5 children" in data["detail"]
    
    def test_api_upsert_children_duplicate_slots(self, client, test_repository, sample_parent):
        """Test API rejects duplicate slots."""
        upsert_data = {
            "children": [
                {"slot": 1, "label": "Child 1"},
                {"slot": 1, "label": "Child 1 Duplicate"}  # Duplicate slot
            ]
        }
        
        response = client.post(f"/api/v1/tree/{sample_parent}/children", json=upsert_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Duplicate slots are not allowed" in data["detail"]
    
    def test_api_upsert_children_invalid_slot(self, client, test_repository, sample_parent):
        """Test API rejects invalid slot numbers."""
        upsert_data = {
            "children": [
                {"slot": 0, "label": "Invalid Slot 0"},
                {"slot": 6, "label": "Invalid Slot 6"}
            ]
        }
        
        response = client.post(f"/api/v1/tree/{sample_parent}/children", json=upsert_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Slot must be between 1 and 5" in data["detail"]
    
    def test_api_upsert_children_empty_label(self, client, test_repository, sample_parent):
        """Test API rejects empty labels."""
        upsert_data = {
            "children": [
                {"slot": 1, "label": ""},  # Empty label
                {"slot": 2, "label": "   "}  # Whitespace only
            ]
        }
        
        response = client.post(f"/api/v1/tree/{sample_parent}/children", json=upsert_data)
        
        assert response.status_code == 400


class TestConcurrentUpsert:
    """Test concurrent upsert scenarios."""
    
    def test_concurrent_upsert_avoids_partial_writes(self, test_repository, sample_parent):
        """Test that concurrent upserts don't result in partial writes."""
        import threading
        import time
        
        results = []
        errors = []
        
        def upsert_children(thread_id):
            try:
                children_data = [
                    {"slot": thread_id, "label": f"Thread {thread_id} Child"}
                ]
                result = test_repository.upsert_children_atomic(sample_parent, children_data)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(1, 6):  # Slots 1-5
            thread = threading.Thread(target=upsert_children, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Unexpected errors: {errors}"
        
        # Verify all children were created
        children = test_repository.get_children(sample_parent)
        assert len(children) == 5
        
        child_slots = {child.slot for child in children}
        assert child_slots == {1, 2, 3, 4, 5}
        
        child_labels = {child.label for child in children}
        expected_labels = {f"Thread {i} Child" for i in range(1, 6)}
        assert child_labels == expected_labels
