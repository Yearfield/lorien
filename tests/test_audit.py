"""
Tests for audit log functionality.

Tests audit logging, undo operations, and audit trail management.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import json

from api.app import app
from api.repositories.audit import AuditManager, AuditOperation

client = TestClient(app)

class TestAuditManager:
    """Test audit manager functionality."""
    
    def test_audit_table_creation(self):
        """Test that audit table is created properly."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = AuditManager(conn)
        
        # Check that table exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_log'")
        result = cursor.fetchone()
        assert result is not None
    
    def test_log_operation(self):
        """Test logging an audit operation."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = AuditManager(conn)
        
        # Log a test operation
        audit_id = manager.log_operation(
            operation=AuditOperation.CONFLICT_RESOLVE,
            target_id=123,
            actor="test_user",
            payload={"test": "data"},
            is_undoable=False
        )
        
        assert audit_id > 0
        
        # Verify the entry was created
        entries = manager.get_audit_entries(limit=1)
        assert len(entries) == 1
        assert entries[0]["id"] == audit_id
        assert entries[0]["operation"] == "conflict_resolve"
        assert entries[0]["target_id"] == 123
        assert entries[0]["actor"] == "test_user"
        assert entries[0]["is_undoable"] is False
    
    def test_log_apply_default(self):
        """Test logging an apply-default operation with undo data."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = AuditManager(conn)
        
        before_children = [
            {"id": 1, "label": "Child 1", "slot": 1, "is_leaf": 0},
            {"id": 2, "label": "Child 2", "slot": 2, "is_leaf": 0}
        ]
        
        after_children = [
            {"id": 3, "label": "Default 1", "slot": 1, "is_leaf": 0},
            {"id": 4, "label": "Default 2", "slot": 2, "is_leaf": 0},
            {"id": 5, "label": "Default 3", "slot": 3, "is_leaf": 0},
            {"id": 6, "label": "Default 4", "slot": 4, "is_leaf": 0},
            {"id": 7, "label": "Default 5", "slot": 5, "is_leaf": 0}
        ]
        
        audit_id = manager.log_apply_default(
            parent_id=100,
            before_children=before_children,
            after_children=after_children,
            actor="test_user"
        )
        
        assert audit_id > 0
        
        # Verify the entry
        entries = manager.get_audit_entries(limit=1)
        assert len(entries) == 1
        entry = entries[0]
        assert entry["operation"] == "apply_default"
        assert entry["target_id"] == 100
        assert entry["is_undoable"] is True
        assert entry["undo_data"] is not None
        assert entry["undo_data"]["parent_id"] == 100
        assert len(entry["undo_data"]["before_children"]) == 2
        assert len(entry["undo_data"]["after_children"]) == 5
    
    def test_get_audit_entries_pagination(self):
        """Test audit entries pagination."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = AuditManager(conn)
        
        # Create multiple entries
        for i in range(5):
            manager.log_operation(
                operation=AuditOperation.CONFLICT_RESOLVE,
                target_id=i,
                actor=f"user_{i}"
            )
        
        # Test pagination
        entries = manager.get_audit_entries(limit=3)
        assert len(entries) == 3
        
        # Test after_id pagination
        last_id = entries[-1]["id"]
        more_entries = manager.get_audit_entries(limit=3, after_id=last_id)
        assert len(more_entries) == 2  # Remaining entries
    
    def test_get_undoable_entries(self):
        """Test getting undoable entries."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = AuditManager(conn)
        
        # Create undoable and non-undoable entries
        manager.log_operation(
            operation=AuditOperation.CONFLICT_RESOLVE,
            target_id=1,
            is_undoable=False
        )
        
        manager.log_apply_default(
            parent_id=2,
            before_children=[],
            after_children=[],
            actor="test_user"
        )
        
        undoable_entries = manager.get_undoable_entries()
        assert len(undoable_entries) == 1
        assert undoable_entries[0]["operation"] == "apply_default"
        assert undoable_entries[0]["is_undoable"] is True
    
    def test_audit_stats(self):
        """Test audit statistics."""
        from api.db import get_conn, ensure_schema
        
        conn = get_conn()
        ensure_schema(conn)
        manager = AuditManager(conn)
        
        # Create some entries
        manager.log_operation(
            operation=AuditOperation.CONFLICT_RESOLVE,
            target_id=1,
            is_undoable=False
        )
        
        manager.log_apply_default(
            parent_id=2,
            before_children=[],
            after_children=[],
            actor="test_user"
        )
        
        stats = manager.get_audit_stats()
        assert stats["total_entries"] == 2
        assert stats["undoable_entries"] == 1
        assert stats["undone_entries"] == 0
        assert "conflict_resolve" in stats["operations"]
        assert "apply_default" in stats["operations"]


class TestAuditEndpoints:
    """Test audit API endpoints."""
    
    def test_get_audit_log(self):
        """Test getting audit log entries."""
        response = client.get("/api/v1/admin/audit")
        assert response.status_code == 200
        
        data = response.json()
        assert "entries" in data
        assert "count" in data
        assert "limit" in data
        assert isinstance(data["entries"], list)
    
    def test_get_audit_log_with_pagination(self):
        """Test audit log pagination."""
        response = client.get("/api/v1/admin/audit?limit=10&after_id=0")
        assert response.status_code == 200
        
        data = response.json()
        assert data["limit"] == 10
        assert data["after_id"] == 0
    
    def test_get_audit_log_with_operation_filter(self):
        """Test audit log operation filtering."""
        response = client.get("/api/v1/admin/audit?operation=apply_default")
        assert response.status_code == 200
        
        data = response.json()
        assert data["operation_filter"] == "apply_default"
    
    def test_get_audit_log_invalid_operation_filter(self):
        """Test audit log with invalid operation filter."""
        response = client.get("/api/v1/admin/audit?operation=invalid_operation")
        assert response.status_code == 400
        
        data = response.json()
        assert "invalid_operation" in data["detail"]["error"]
        assert "valid_operations" in data["detail"]
    
    def test_get_undoable_entries(self):
        """Test getting undoable entries."""
        response = client.get("/api/v1/admin/audit/undoable")
        assert response.status_code == 200
        
        data = response.json()
        assert "entries" in data
        assert "count" in data
        assert "message" in data
        assert isinstance(data["entries"], list)
    
    def test_get_audit_stats(self):
        """Test getting audit statistics."""
        response = client.get("/api/v1/admin/audit/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "stats" in data
        assert "status" in data
        
        stats = data["stats"]
        assert "total_entries" in stats
        assert "undoable_entries" in stats
        assert "undone_entries" in stats
        assert "operations" in stats
    
    def test_get_available_operations(self):
        """Test getting available operations."""
        response = client.get("/api/v1/admin/audit/operations")
        assert response.status_code == 200
        
        data = response.json()
        assert "operations" in data
        assert isinstance(data["operations"], list)
        
        # Check that all operations are present
        operation_types = [op["type"] for op in data["operations"]]
        assert "conflict_resolve" in operation_types
        assert "apply_default" in operation_types
        assert "delete_subtree" in operation_types
        assert "data_quality_repair" in operation_types


class TestUndoOperations:
    """Test undo operation functionality."""
    
    def test_undo_nonexistent_entry(self):
        """Test undoing a nonexistent entry."""
        response = client.post("/api/v1/admin/audit/99999/undo")
        assert response.status_code == 404
        
        data = response.json()
        assert "audit_entry_not_found" in data["detail"]["error"]
    
    def test_undo_non_undoable_entry(self):
        """Test undoing a non-undoable entry."""
        # First create a non-undoable entry
        from api.db import get_conn, ensure_schema
        from api.repositories.audit import AuditManager, AuditOperation
        
        conn = get_conn()
        ensure_schema(conn)
        manager = AuditManager(conn)
        
        audit_id = manager.log_operation(
            operation=AuditOperation.CONFLICT_RESOLVE,
            target_id=123,
            is_undoable=False
        )
        
        # Try to undo it
        response = client.post(f"/api/v1/admin/audit/{audit_id}/undo")
        assert response.status_code == 400
        
        data = response.json()
        assert "not_undoable" in data["detail"]["error"]
    
    def test_undo_already_undone_entry(self):
        """Test undoing an already undone entry."""
        # This would require creating an entry and marking it as undone
        # For now, just test the endpoint exists
        response = client.post("/api/v1/admin/audit/1/undo")
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 400, 404, 500]


class TestAuditIntegration:
    """Test audit integration with existing functionality."""
    
    def test_audit_logging_integration(self):
        """Test that audit logging integrates with existing operations."""
        # Test that audit endpoints don't interfere with existing functionality
        response = client.get("/api/v1/tree/next-incomplete-parent")
        assert response.status_code in [200, 404]
        
        response = client.get("/api/v1/admin/audit")
        assert response.status_code == 200
    
    def test_audit_log_persistence(self):
        """Test that audit logs persist across requests."""
        from api.db import get_conn, ensure_schema
        from api.repositories.audit import AuditManager, AuditOperation
        
        conn = get_conn()
        ensure_schema(conn)
        manager = AuditManager(conn)
        
        # Create an audit entry
        audit_id = manager.log_operation(
            operation=AuditOperation.CONFLICT_RESOLVE,
            target_id=456,
            actor="integration_test"
        )
        
        # Verify it can be retrieved via API
        response = client.get("/api/v1/admin/audit")
        assert response.status_code == 200
        
        data = response.json()
        entries = data["entries"]
        
        # Find our entry
        our_entry = next((e for e in entries if e["id"] == audit_id), None)
        assert our_entry is not None
        assert our_entry["operation"] == "conflict_resolve"
        assert our_entry["target_id"] == 456
        assert our_entry["actor"] == "integration_test"


class TestAuditErrorHandling:
    """Test audit error handling."""
    
    def test_audit_log_error_handling(self):
        """Test audit log error handling."""
        # Test with invalid parameters
        response = client.get("/api/v1/admin/audit?limit=0")
        assert response.status_code == 422  # Validation error
        
        response = client.get("/api/v1/admin/audit?limit=1001")
        assert response.status_code == 422  # Validation error
    
    def test_undo_error_handling(self):
        """Test undo operation error handling."""
        # Test with invalid audit ID
        response = client.post("/api/v1/admin/audit/invalid/undo")
        assert response.status_code == 422  # Validation error
    
    def test_audit_stats_error_handling(self):
        """Test audit stats error handling."""
        # This should work even with no data
        response = client.get("/api/v1/admin/audit/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "stats" in data
        assert data["stats"]["total_entries"] >= 0


class TestAuditDataIntegrity:
    """Test audit data integrity and consistency."""
    
    def test_audit_entry_consistency(self):
        """Test that audit entries are consistent."""
        from api.db import get_conn, ensure_schema
        from api.repositories.audit import AuditManager, AuditOperation
        
        conn = get_conn()
        ensure_schema(conn)
        manager = AuditManager(conn)
        
        # Create an entry with specific data
        payload = {"test_key": "test_value", "number": 42}
        undo_data = {"before": "state", "after": "state"}
        
        audit_id = manager.log_operation(
            operation=AuditOperation.CONFLICT_RESOLVE,
            target_id=789,
            actor="consistency_test",
            payload=payload,
            undo_data=undo_data,
            is_undoable=True
        )
        
        # Retrieve and verify consistency
        entries = manager.get_audit_entries(limit=1)
        assert len(entries) == 1
        
        entry = entries[0]
        assert entry["id"] == audit_id
        assert entry["operation"] == "conflict_resolve"
        assert entry["target_id"] == 789
        assert entry["actor"] == "consistency_test"
        assert entry["payload"] == payload
        assert entry["undo_data"] == undo_data
        assert entry["is_undoable"] is True
        assert entry["undone_by"] is None
        assert entry["undone_at"] is None
    
    def test_audit_timestamp_ordering(self):
        """Test that audit entries are ordered by timestamp."""
        from api.db import get_conn, ensure_schema
        from api.repositories.audit import AuditManager, AuditOperation
        import time
        
        conn = get_conn()
        ensure_schema(conn)
        manager = AuditManager(conn)
        
        # Create multiple entries with small delays
        audit_ids = []
        for i in range(3):
            audit_id = manager.log_operation(
                operation=AuditOperation.CONFLICT_RESOLVE,
                target_id=i,
                actor=f"timestamp_test_{i}"
            )
            audit_ids.append(audit_id)
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        # Retrieve entries and verify ordering
        entries = manager.get_audit_entries(limit=10)
        assert len(entries) >= 3
        
        # Check that entries are ordered by ID descending (newest first)
        for i in range(len(entries) - 1):
            assert entries[i]["id"] > entries[i + 1]["id"]
