"""
Tests for the enhanced audit system.

Tests audit logging, undo capabilities, and audit trail management.
"""

import pytest
import sqlite3
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock

from api.core.audit_expansion import (
    EnhancedAuditManager,
    ExpandedAuditOperation,
    AuditContext,
    UndoCapability
)

@pytest.fixture
def test_db():
    """Create a test database with enhanced audit tables."""
    conn = sqlite3.connect(":memory:")
    
    # Create enhanced audit tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS enhanced_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            operation TEXT NOT NULL,
            target_id INTEGER,
            target_type TEXT,
            actor TEXT,
            context_json TEXT,
            payload_json TEXT,
            undo_data_json TEXT,
            is_undoable BOOLEAN DEFAULT 0,
            undo_timeout_seconds INTEGER,
            requires_confirmation BOOLEAN DEFAULT 0,
            undone_by INTEGER,
            undone_at DATETIME,
            undo_reason TEXT,
            parent_operation_id INTEGER,
            operation_group_id TEXT,
            severity TEXT DEFAULT 'info',
            tags TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_operation_groups (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME,
            status TEXT DEFAULT 'in_progress',
            total_operations INTEGER DEFAULT 0,
            completed_operations INTEGER DEFAULT 0,
            failed_operations INTEGER DEFAULT 0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            color TEXT DEFAULT '#007bff',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create test tables for undo operations
    conn.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER,
            label TEXT,
            slot INTEGER,
            is_leaf BOOLEAN,
            depth INTEGER
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS node_flags (
            node_id INTEGER,
            flag_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (node_id, flag_id)
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dictionary (
            id INTEGER PRIMARY KEY,
            term TEXT,
            definition TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    yield conn
    conn.close()

@pytest.fixture
def audit_manager(test_db):
    """Create an audit manager for testing."""
    return EnhancedAuditManager(test_db)

def test_enhanced_audit_manager_initialization(audit_manager):
    """Test audit manager initialization."""
    assert audit_manager is not None
    assert len(audit_manager._operation_undo_capabilities) > 0

def test_log_operation(audit_manager):
    """Test logging a basic operation."""
    context = AuditContext(
        user_id="test_user",
        session_id="test_session",
        ip_address="127.0.0.1"
    )
    
    audit_id = audit_manager.log_operation(
        operation=ExpandedAuditOperation.NODE_CREATE,
        target_id=123,
        target_type="node",
        actor="test_user",
        context=context,
        payload={"label": "Test Node"},
        undo_data={"before_state": None},
        severity="info",
        tags=["test", "node"]
    )
    
    assert audit_id > 0
    
    # Verify the entry was created
    entries = audit_manager.get_enhanced_audit_entries(limit=1)
    assert len(entries) == 1
    assert entries[0]["operation"] == "node_create"
    assert entries[0]["target_id"] == 123
    assert entries[0]["actor"] == "test_user"
    assert entries[0]["is_undoable"] is True

def test_operation_group_management(audit_manager):
    """Test operation group creation and completion."""
    group_id = "test_group_123"
    
    # Create operation group
    success = audit_manager.create_operation_group(
        group_id=group_id,
        name="Test Group",
        description="Test operation group",
        total_operations=5
    )
    
    assert success is True
    
    # Complete operation group
    success = audit_manager.complete_operation_group(group_id, "completed")
    assert success is True

def test_undo_capabilities(audit_manager):
    """Test undo capabilities for different operations."""
    # Test undoable operation
    undo_capability = audit_manager._operation_undo_capabilities[ExpandedAuditOperation.NODE_CREATE]
    assert undo_capability.is_undoable is True
    assert undo_capability.undo_timeout_seconds == 1800
    assert undo_capability.requires_confirmation is True
    
    # Test non-undoable operation
    undo_capability = audit_manager._operation_undo_capabilities[ExpandedAuditOperation.DELETE_SUBTREE]
    assert undo_capability.is_undoable is False

def test_audit_filtering(audit_manager):
    """Test audit entry filtering."""
    # Log multiple operations
    audit_manager.log_operation(
        operation=ExpandedAuditOperation.NODE_CREATE,
        target_id=1,
        target_type="node",
        actor="user1",
        severity="info",
        tags=["test"]
    )
    
    audit_manager.log_operation(
        operation=ExpandedAuditOperation.FLAG_ASSIGN,
        target_id=1,
        target_type="node_flag",
        actor="user2",
        severity="warning",
        tags=["flag"]
    )
    
    # Test filtering by operation
    entries = audit_manager.get_enhanced_audit_entries(
        operation_filter=ExpandedAuditOperation.NODE_CREATE
    )
    assert len(entries) == 1
    assert entries[0]["operation"] == "node_create"
    
    # Test filtering by actor
    entries = audit_manager.get_enhanced_audit_entries(actor_filter="user1")
    assert len(entries) == 1
    assert entries[0]["actor"] == "user1"
    
    # Test filtering by severity
    entries = audit_manager.get_enhanced_audit_entries(severity_filter="warning")
    assert len(entries) == 1
    assert entries[0]["severity"] == "warning"
    
    # Test filtering by tag
    entries = audit_manager.get_enhanced_audit_entries(tag_filter="flag")
    assert len(entries) == 1
    assert "flag" in entries[0]["tags"]

def test_undo_operation(audit_manager, test_db):
    """Test undoing an operation."""
    # Create test data
    test_db.execute("""
        INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
        VALUES (1, NULL, 'Test Node', 0, 1, 0)
    """)
    test_db.commit()
    
    # Log a node creation operation
    audit_id = audit_manager.log_operation(
        operation=ExpandedAuditOperation.NODE_CREATE,
        target_id=1,
        target_type="node",
        actor="test_user",
        undo_data={"node_id": 1, "operation": "node_create"}
    )
    
    # Undo the operation
    result = audit_manager.undo_operation(
        audit_id=audit_id,
        actor="admin",
        reason="Test undo"
    )
    
    assert result["success"] is True
    assert result["audit_id"] == audit_id
    
    # Verify the operation was marked as undone
    entries = audit_manager.get_enhanced_audit_entries(limit=1)
    assert entries[0]["undone_by"] == audit_id
    assert entries[0]["undo_reason"] == "Test undo"

def test_undo_timeout(audit_manager):
    """Test undo timeout functionality."""
    # Log an operation with a short timeout
    audit_id = audit_manager.log_operation(
        operation=ExpandedAuditOperation.NODE_CREATE,
        target_id=1,
        target_type="node",
        actor="test_user",
        undo_data={"node_id": 1}
    )
    
    # Mock the timestamp to be past the timeout
    old_timestamp = datetime.now(timezone.utc) - timedelta(hours=1)
    
    # Update the timestamp in the database
    test_db = audit_manager.conn
    test_db.execute("""
        UPDATE enhanced_audit_log 
        SET timestamp = ? 
        WHERE id = ?
    """, (old_timestamp.isoformat(), audit_id))
    test_db.commit()
    
    # Try to undo (should fail due to timeout)
    result = audit_manager.undo_operation(audit_id=audit_id, actor="admin")
    
    assert result["success"] is False
    assert "undo_timeout_expired" in result["error"]

def test_undo_nonexistent_operation(audit_manager):
    """Test undoing a non-existent operation."""
    result = audit_manager.undo_operation(audit_id=99999, actor="admin")
    
    assert result["success"] is False
    assert "audit_entry_not_found" in result["error"]

def test_undo_already_undone_operation(audit_manager, test_db):
    """Test undoing an already undone operation."""
    # Create test data
    test_db.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER,
            label TEXT,
            slot INTEGER,
            is_leaf BOOLEAN,
            depth INTEGER
        )
    """)
    test_db.execute("""
        INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
        VALUES (1, NULL, 'Test Node', 0, 1, 0)
    """)
    test_db.commit()
    
    # Log an operation
    audit_id = audit_manager.log_operation(
        operation=ExpandedAuditOperation.NODE_CREATE,
        target_id=1,
        target_type="node",
        actor="test_user",
        undo_data={"node_id": 1}
    )
    
    # Undo it once
    result1 = audit_manager.undo_operation(audit_id=audit_id, actor="admin")
    assert result1["success"] is True
    
    # Try to undo it again (should fail)
    result2 = audit_manager.undo_operation(audit_id=audit_id, actor="admin")
    assert result2["success"] is False
    assert "already_undone" in result2["error"]

def test_undo_non_undoable_operation(audit_manager):
    """Test undoing a non-undoable operation."""
    # Log a non-undoable operation
    audit_id = audit_manager.log_operation(
        operation=ExpandedAuditOperation.DELETE_SUBTREE,
        target_id=1,
        target_type="node",
        actor="test_user"
    )
    
    # Try to undo (should fail)
    result = audit_manager.undo_operation(audit_id=audit_id, actor="admin")
    
    assert result["success"] is False
    assert "not_undoable" in result["error"]

def test_audit_stats(audit_manager):
    """Test audit statistics generation."""
    # Log some operations
    audit_manager.log_operation(
        operation=ExpandedAuditOperation.NODE_CREATE,
        target_id=1,
        target_type="node",
        actor="user1"
    )
    
    audit_manager.log_operation(
        operation=ExpandedAuditOperation.FLAG_ASSIGN,
        target_id=1,
        target_type="node_flag",
        actor="user2"
    )
    
    # Get stats
    stats = audit_manager.get_enhanced_audit_stats()
    
    assert stats["total_entries"] == 2
    assert stats["undoable_entries"] == 2
    assert stats["undone_entries"] == 0
    assert "node_create" in stats["operations"]
    assert "flag_assign" in stats["operations"]

def test_operation_group_context_manager(audit_manager):
    """Test operation group context manager."""
    with audit_manager.operation_group("test_group", "Test Group") as group_id:
        assert group_id == "test_group"
        
        # Log operations within the group
        audit_manager.log_operation(
            operation=ExpandedAuditOperation.NODE_CREATE,
            target_id=1,
            target_type="node",
            operation_group_id=group_id
        )
    
    # Verify the group was completed
    test_db = audit_manager.conn
    cursor = test_db.cursor()
    cursor.execute("SELECT status FROM audit_operation_groups WHERE id = ?", (group_id,))
    status = cursor.fetchone()[0]
    assert status == "completed"

def test_undo_node_create(audit_manager, test_db):
    """Test undoing a node creation operation."""
    # Create test data
    test_db.execute("""
        INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
        VALUES (1, NULL, 'Test Node', 0, 1, 0)
    """)
    test_db.commit()
    
    # Log node creation
    audit_id = audit_manager.log_operation(
        operation=ExpandedAuditOperation.NODE_CREATE,
        target_id=1,
        target_type="node",
        actor="test_user",
        undo_data={"node_id": 1, "operation": "node_create"}
    )
    
    # Undo the operation
    result = audit_manager._undo_node_create(1, {"node_id": 1})
    
    assert result["success"] is True
    
    # Verify the node was deleted
    cursor = test_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM nodes WHERE id = 1")
    count = cursor.fetchone()[0]
    assert count == 0

def test_undo_flag_assign(audit_manager, test_db):
    """Test undoing a flag assignment operation."""
    # Create test data
    test_db.execute("""
        INSERT INTO node_flags (node_id, flag_id)
        VALUES (1, 1)
    """)
    test_db.commit()
    
    # Undo flag assignment
    result = audit_manager._undo_flag_assign(1, {"flag_id": 1})
    
    assert result["success"] is True
    
    # Verify the flag was removed
    cursor = test_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM node_flags WHERE node_id = 1 AND flag_id = 1")
    count = cursor.fetchone()[0]
    assert count == 0

def test_undo_flag_remove(audit_manager, test_db):
    """Test undoing a flag removal operation."""
    # Undo flag removal (should add the flag back)
    result = audit_manager._undo_flag_remove(1, {"flag_id": 1})
    
    assert result["success"] is True
    
    # Verify the flag was added back
    cursor = test_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM node_flags WHERE node_id = 1 AND flag_id = 1")
    count = cursor.fetchone()[0]
    assert count == 1

def test_undo_bulk_flag_operation(audit_manager, test_db):
    """Test undoing a bulk flag operation."""
    # Create test data - only insert the flag that will be assigned (not removed)
    test_db.execute("""
        INSERT INTO node_flags (node_id, flag_id)
        VALUES (1, 1)
    """)
    test_db.commit()
    
    # Undo bulk operation
    operations = [
        {"action": "assign", "node_id": 1, "flag_id": 1},
        {"action": "remove", "node_id": 2, "flag_id": 1}
    ]
    
    result = audit_manager._undo_bulk_flag_operation(1, {"operations": operations})
    
    assert result["success"] is True
    # Should succeed for both operations: remove existing flag, add missing flag
    assert "2/2 operations" in result["message"]
    
    # Verify the operations were undone
    cursor = test_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM node_flags WHERE node_id = 1 AND flag_id = 1")
    count1 = cursor.fetchone()[0]
    assert count1 == 0  # Assignment was undone (flag removed)
    
    cursor.execute("SELECT COUNT(*) FROM node_flags WHERE node_id = 2 AND flag_id = 1")
    count2 = cursor.fetchone()[0]
    assert count2 == 1  # Removal was undone (flag added back)

def test_audit_context_serialization(audit_manager):
    """Test audit context serialization and deserialization."""
    context = AuditContext(
        user_id="test_user",
        session_id="test_session",
        ip_address="127.0.0.1",
        user_agent="Test Agent",
        request_id="req_123",
        parent_operation_id=456
    )
    
    audit_id = audit_manager.log_operation(
        operation=ExpandedAuditOperation.NODE_CREATE,
        target_id=1,
        target_type="node",
        actor="test_user",
        context=context
    )
    
    # Retrieve the entry
    entries = audit_manager.get_enhanced_audit_entries(limit=1)
    retrieved_context = entries[0]["context"]
    
    assert retrieved_context["user_id"] == "test_user"
    assert retrieved_context["session_id"] == "test_session"
    assert retrieved_context["ip_address"] == "127.0.0.1"
    assert retrieved_context["user_agent"] == "Test Agent"
    assert retrieved_context["request_id"] == "req_123"
    assert retrieved_context["parent_operation_id"] == 456
