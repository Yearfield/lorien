"""
Tests for VM Builder functionality.

Tests draft management, diff calculation, and publishing capabilities
for the Vital Measurement Builder.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import json

from api.app import app
from api.repositories.vm_builder import VMBuilderManager, VMOperationType

client = TestClient(app)

class TestVMBuilderManager:
    """Test VM Builder manager functionality."""
    
    def test_vm_drafts_table_creation(self):
        """Test that vm_drafts table is created properly."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Check that table exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vm_drafts'")
        result = cursor.fetchone()
        assert result is not None
    
    def test_create_draft(self):
        """Test creating a VM Builder draft."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Create a test parent node
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
            VALUES (100, NULL, 'Test Parent', 0, 0, 0)
        """)
        conn.commit()
        
        draft_data = {
            "children": [
                {"id": 1, "label": "Child 1", "slot": 1, "is_leaf": 0, "depth": 1},
                {"id": 2, "label": "Child 2", "slot": 2, "is_leaf": 0, "depth": 1}
            ],
            "metadata": {"description": "Test draft"}
        }
        
        draft_id = manager.create_draft(100, draft_data, "test_user")
        assert draft_id is not None
        assert len(draft_id) > 0
        
        # Verify draft was created
        draft = manager.get_draft(draft_id)
        assert draft is not None
        assert draft["parent_id"] == 100
        assert draft["status"] == "draft"
        assert draft["draft_data"]["metadata"]["description"] == "Test draft"
    
    def test_get_draft(self):
        """Test getting a VM Builder draft."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Create a draft
        draft_data = {"test": "data"}
        draft_id = manager.create_draft(100, draft_data)
        
        # Get the draft
        draft = manager.get_draft(draft_id)
        assert draft is not None
        assert draft["id"] == draft_id
        assert draft["parent_id"] == 100
        assert draft["draft_data"] == draft_data
        
        # Test getting non-existent draft
        non_existent = manager.get_draft("non-existent")
        assert non_existent is None
    
    def test_update_draft(self):
        """Test updating a VM Builder draft."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Create a draft
        original_data = {"test": "original"}
        draft_id = manager.create_draft(100, original_data)
        
        # Update the draft
        updated_data = {"test": "updated", "new_field": "value"}
        success = manager.update_draft(draft_id, updated_data, "test_user")
        assert success is True
        
        # Verify update
        draft = manager.get_draft(draft_id)
        assert draft["draft_data"] == updated_data
        
        # Test updating non-existent draft
        success = manager.update_draft("non-existent", {})
        assert success is False
    
    def test_delete_draft(self):
        """Test deleting a VM Builder draft."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Create a draft
        draft_id = manager.create_draft(100, {"test": "data"})
        
        # Delete the draft
        success = manager.delete_draft(draft_id)
        assert success is True
        
        # Verify deletion
        draft = manager.get_draft(draft_id)
        assert draft is None
        
        # Test deleting non-existent draft
        success = manager.delete_draft("non-existent")
        assert success is False
    
    def test_list_drafts(self):
        """Test listing VM Builder drafts."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Create multiple drafts
        draft1 = manager.create_draft(100, {"test": "data1"})
        draft2 = manager.create_draft(100, {"test": "data2"})
        draft3 = manager.create_draft(200, {"test": "data3"})
        
        # List all drafts
        all_drafts = manager.list_drafts()
        assert len(all_drafts) == 3
        
        # List drafts for specific parent
        parent_drafts = manager.list_drafts(100)
        assert len(parent_drafts) == 2
        
        # Verify draft summaries
        for draft in all_drafts:
            assert "id" in draft
            assert "parent_id" in draft
            assert "status" in draft
            assert "created_at" in draft
            assert "updated_at" in draft
    
    def test_calculate_diff(self):
        """Test calculating diff for a draft."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Create a parent node with existing children
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
            VALUES (100, NULL, 'Parent', 0, 0, 0)
        """)
        cursor.execute("""
            INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
            VALUES (1, 100, 'Existing Child', 1, 0, 1)
        """)
        conn.commit()
        
        # Create a draft with different children
        draft_data = {
            "children": [
                {"id": 1, "label": "Updated Child", "slot": 1, "is_leaf": 0, "depth": 1},
                {"id": 2, "label": "New Child", "slot": 2, "is_leaf": 0, "depth": 1}
            ]
        }
        draft_id = manager.create_draft(100, draft_data)
        
        # Calculate diff
        diff = manager.calculate_diff(draft_id)
        
        assert "draft_id" in diff
        assert "parent_id" in diff
        assert "operations" in diff
        assert "summary" in diff
        assert "current_state" in diff
        assert "target_state" in diff
        
        # Check operations
        operations = diff["operations"]
        assert len(operations) >= 1  # At least one update operation
        
        # Check summary
        summary = diff["summary"]
        assert "total" in summary
        assert "create" in summary
        assert "update" in summary
        assert "delete" in summary
    
    def test_calculate_operations(self):
        """Test operation calculation logic."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Test create operations
        current = []
        target = [
            {"id": 1, "label": "New Child", "slot": 1, "is_leaf": 0, "depth": 1}
        ]
        operations = manager._calculate_operations(current, target)
        
        create_ops = [op for op in operations if op["type"] == "create"]
        assert len(create_ops) == 1
        assert create_ops[0]["label"] == "New Child"
        
        # Test update operations
        current = [{"id": 1, "label": "Old Label", "slot": 1, "is_leaf": 0, "depth": 1}]
        target = [{"id": 1, "label": "New Label", "slot": 1, "is_leaf": 0, "depth": 1}]
        operations = manager._calculate_operations(current, target)
        
        update_ops = [op for op in operations if op["type"] == "update"]
        assert len(update_ops) == 1
        assert update_ops[0]["old_label"] == "Old Label"
        assert update_ops[0]["new_label"] == "New Label"
        
        # Test delete operations
        current = [{"id": 1, "label": "To Delete", "slot": 1, "is_leaf": 0, "depth": 1}]
        target = []
        operations = manager._calculate_operations(current, target)
        
        delete_ops = [op for op in operations if op["type"] == "delete"]
        assert len(delete_ops) == 1
        assert delete_ops[0]["label"] == "To Delete"
    
    def test_publish_draft(self):
        """Test publishing a VM Builder draft."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Create a parent node
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
            VALUES (100, NULL, 'Parent', 0, 0, 0)
        """)
        conn.commit()
        
        # Create a draft with new children
        draft_data = {
            "children": [
                {"id": 1, "label": "New Child 1", "slot": 1, "is_leaf": 0, "depth": 1},
                {"id": 2, "label": "New Child 2", "slot": 2, "is_leaf": 0, "depth": 1}
            ]
        }
        draft_id = manager.create_draft(100, draft_data)
        
        # Publish the draft
        result = manager.publish_draft(draft_id, "test_user")
        
        assert result["success"] is True
        assert "operations_applied" in result
        assert "audit_id" in result
        
        # Verify draft status changed
        draft = manager.get_draft(draft_id)
        assert draft["status"] == "published"
        assert draft["published_by"] == "test_user"
        
        # Verify children were created
        cursor.execute("SELECT COUNT(*) FROM nodes WHERE parent_id = 100")
        child_count = cursor.fetchone()[0]
        assert child_count == 2
    
    def test_publish_draft_no_changes(self):
        """Test publishing a draft with no changes."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Create a parent node
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
            VALUES (100, NULL, 'Parent', 0, 0, 0)
        """)
        conn.commit()
        
        # Create a draft with no changes
        draft_data = {"children": []}
        draft_id = manager.create_draft(100, draft_data)
        
        # Publish the draft
        result = manager.publish_draft(draft_id, "test_user")
        
        assert result["success"] is True
        assert result["operations_applied"] == 0
        assert "No changes to apply" in result["message"]
    
    def test_get_draft_stats(self):
        """Test getting VM Builder draft statistics."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Create some drafts
        manager.create_draft(100, {"test": "data1"})
        manager.create_draft(100, {"test": "data2"})
        manager.create_draft(200, {"test": "data3"})
        
        stats = manager.get_draft_stats()
        
        assert "total_drafts" in stats
        assert "status_counts" in stats
        assert "recent_drafts" in stats
        assert stats["total_drafts"] == 3
        assert stats["status_counts"]["draft"] == 3


class TestVMBuilderEndpoints:
    """Test VM Builder API endpoints."""
    
    def test_create_draft_endpoint(self):
        """Test creating a draft via API."""
        # First create a parent node
        from api.db import get_conn, ensure_schema
        conn = get_conn()
        ensure_schema(conn)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
            VALUES (100, NULL, 'Test Parent', 0, 0, 0)
        """)
        conn.commit()
        
        draft_data = {
            "children": [],
            "metadata": {"description": "Test draft"}
        }
        
        response = client.post(
            "/api/v1/tree/vm/draft",
            json={
                "parent_id": 100,
                "draft_data": draft_data,
                "actor": "test_user"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "draft_id" in data
        assert data["parent_id"] == 100
    
    def test_create_draft_nonexistent_parent(self):
        """Test creating a draft with nonexistent parent."""
        draft_data = {"children": []}
        
        response = client.post(
            "/api/v1/tree/vm/draft",
            json={
                "parent_id": 99999,
                "draft_data": draft_data,
                "actor": "test_user"
            }
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "parent_not_found" in data["detail"]["error"]
    
    def test_get_draft_endpoint(self):
        """Test getting a draft via API."""
        # Create a draft first
        from api.db import get_conn, ensure_schema
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Create parent node
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
            VALUES (100, NULL, 'Parent', 0, 0, 0)
        """)
        conn.commit()
        
        draft_id = manager.create_draft(100, {"test": "data"})
        
        # Get the draft via API
        response = client.get(f"/api/v1/tree/vm/draft/{draft_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "draft" in data
        assert data["draft"]["id"] == draft_id
    
    def test_get_nonexistent_draft(self):
        """Test getting a nonexistent draft."""
        response = client.get("/api/v1/tree/vm/draft/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "draft_not_found" in data["detail"]["error"]
    
    def test_update_draft_endpoint(self):
        """Test updating a draft via API."""
        # Create a draft first
        from api.db import get_conn, ensure_schema
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Create parent node
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
            VALUES (100, NULL, 'Parent', 0, 0, 0)
        """)
        conn.commit()
        
        draft_id = manager.create_draft(100, {"test": "original"})
        
        # Update the draft
        updated_data = {"test": "updated"}
        response = client.put(
            f"/api/v1/tree/vm/draft/{draft_id}",
            json={
                "draft_data": updated_data,
                "actor": "test_user"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_delete_draft_endpoint(self):
        """Test deleting a draft via API."""
        # Create a draft first
        from api.db import get_conn, ensure_schema
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Create parent node
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
            VALUES (100, NULL, 'Parent', 0, 0, 0)
        """)
        conn.commit()
        
        draft_id = manager.create_draft(100, {"test": "data"})
        
        # Delete the draft
        response = client.delete(f"/api/v1/tree/vm/draft/{draft_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_list_drafts_endpoint(self):
        """Test listing drafts via API."""
        response = client.get("/api/v1/tree/vm/drafts")
        
        assert response.status_code == 200
        data = response.json()
        assert "drafts" in data
        assert "count" in data
        assert isinstance(data["drafts"], list)
    
    def test_plan_draft_endpoint(self):
        """Test planning a draft via API."""
        # Create a draft first
        from api.db import get_conn, ensure_schema
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Create parent node with existing children
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
            VALUES (100, NULL, 'Parent', 0, 0, 0)
        """)
        cursor.execute("""
            INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
            VALUES (1, 100, 'Existing Child', 1, 0, 1)
        """)
        conn.commit()
        
        draft_data = {
            "children": [
                {"id": 1, "label": "Updated Child", "slot": 1, "is_leaf": 0, "depth": 1}
            ]
        }
        draft_id = manager.create_draft(100, draft_data)
        
        # Plan the draft
        response = client.post(f"/api/v1/tree/vm/draft/{draft_id}/plan")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "diff" in data
        assert "operations" in data["diff"]
    
    def test_publish_draft_endpoint(self):
        """Test publishing a draft via API."""
        # Create a draft first
        from api.db import get_conn, ensure_schema
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Create parent node
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
            VALUES (100, NULL, 'Parent', 0, 0, 0)
        """)
        conn.commit()
        
        draft_data = {
            "children": [
                {"id": 1, "label": "New Child", "slot": 1, "is_leaf": 0, "depth": 1}
            ]
        }
        draft_id = manager.create_draft(100, draft_data)
        
        # Publish the draft
        response = client.post(
            f"/api/v1/tree/vm/draft/{draft_id}/publish",
            json={"actor": "test_user"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data
        assert data["result"]["success"] is True
    
    def test_get_vm_stats_endpoint(self):
        """Test getting VM Builder statistics via API."""
        response = client.get("/api/v1/tree/vm/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert "status" in data
        assert data["status"] == "healthy"


class TestVMBuilderIntegration:
    """Test VM Builder integration with existing functionality."""
    
    def test_vm_builder_audit_integration(self):
        """Test that VM Builder operations are audited."""
        from api.db import get_conn, ensure_schema
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Create parent node
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
            VALUES (100, NULL, 'Parent', 0, 0, 0)
        """)
        conn.commit()
        
        # Create and publish a draft
        draft_data = {
            "children": [
                {"id": 1, "label": "New Child", "slot": 1, "is_leaf": 0, "depth": 1}
            ]
        }
        draft_id = manager.create_draft(100, draft_data)
        result = manager.publish_draft(draft_id, "test_user")
        
        # Check that audit entry was created
        from api.repositories.audit import AuditManager
        audit_manager = AuditManager(conn)
        entries = audit_manager.get_audit_entries(limit=10)
        
        # Find our audit entry
        vm_entries = [e for e in entries if e.get("payload", {}).get("draft_id") == draft_id]
        assert len(vm_entries) == 1
        
        entry = vm_entries[0]
        assert entry["operation"] == "children_update"
        assert entry["target_id"] == 100
        assert entry["actor"] == "test_user"
    
    def test_vm_builder_error_handling(self):
        """Test VM Builder error handling."""
        # Test with invalid draft ID
        response = client.get("/api/v1/tree/vm/draft/invalid-id")
        assert response.status_code == 404
        
        # Test planning non-existent draft
        response = client.post("/api/v1/tree/vm/draft/nonexistent/plan")
        assert response.status_code == 404
        
        # Test publishing non-existent draft
        response = client.post("/api/v1/tree/vm/draft/nonexistent/publish")
        assert response.status_code == 500  # Internal error due to ValueError
    
    def test_vm_builder_data_consistency(self):
        """Test VM Builder data consistency."""
        from api.db import get_conn, ensure_schema
        conn = get_conn()
        ensure_schema(conn)
        manager = VMBuilderManager(conn)
        
        # Create parent node
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
            VALUES (100, NULL, 'Parent', 0, 0, 0)
        """)
        conn.commit()
        
        # Create a draft
        draft_data = {
            "children": [
                {"id": 1, "label": "Child 1", "slot": 1, "is_leaf": 0, "depth": 1},
                {"id": 2, "label": "Child 2", "slot": 2, "is_leaf": 0, "depth": 1}
            ]
        }
        draft_id = manager.create_draft(100, draft_data)
        
        # Verify draft data consistency
        draft = manager.get_draft(draft_id)
        assert draft["draft_data"] == draft_data
        assert draft["parent_id"] == 100
        assert draft["status"] == "draft"
        
        # Publish and verify children were created correctly
        manager.publish_draft(draft_id, "test_user")
        
        cursor.execute("SELECT * FROM nodes WHERE parent_id = 100 ORDER BY slot")
        children = cursor.fetchall()
        assert len(children) == 2
        assert children[0][1] == "Child 1"  # label
        assert children[0][3] == 1  # slot
        assert children[1][1] == "Child 2"  # label
        assert children[1][3] == 2  # slot
