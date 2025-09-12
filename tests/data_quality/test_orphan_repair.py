"""
Tests for the orphan repair system.

Tests orphan detection, repair actions, and audit trails.
"""

import pytest
import sqlite3
import json
from datetime import datetime, timezone
from unittest.mock import Mock

from api.core.orphan_repair import (
    OrphanRepairManager,
    OrphanType,
    RepairAction,
    OrphanNode,
    RepairResult
)

@pytest.fixture
def test_db():
    """Create a test database with orphan repair tables."""
    conn = sqlite3.connect(":memory:")
    
    # Create nodes table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            label TEXT NOT NULL,
            depth INTEGER NOT NULL,
            slot INTEGER,
            is_leaf INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES nodes(id) ON DELETE CASCADE
        )
    """)
    
    # Create orphan repair audit table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orphan_repair_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orphan_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            actor TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            before_state TEXT,
            after_state TEXT,
            success BOOLEAN NOT NULL,
            message TEXT,
            warnings TEXT,
            FOREIGN KEY (orphan_id) REFERENCES nodes(id) ON DELETE CASCADE
        )
    """)
    
    yield conn
    conn.close()

@pytest.fixture
def repair_manager(test_db):
    """Create an orphan repair manager for testing."""
    return OrphanRepairManager(test_db)

def test_orphan_repair_manager_initialization(repair_manager):
    """Test orphan repair manager initialization."""
    assert repair_manager is not None

def test_detect_missing_parent_orphans(repair_manager, test_db):
    """Test detection of missing parent orphans."""
    # Create test data
    cursor = test_db.cursor()
    
    # Create a parent
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    
    # Create an orphan with missing parent
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (2, 999, 'Orphan', 1, 1, 1)
    """)
    
    test_db.commit()
    
    # Detect orphans
    orphans = repair_manager.detect_orphans()
    
    assert len(orphans) == 1
    assert orphans[0].orphan_type == OrphanType.MISSING_PARENT
    assert orphans[0].severity == "high"
    assert RepairAction.DELETE_ORPHAN in orphans[0].suggested_actions

def test_detect_invalid_depth_orphans(repair_manager, test_db):
    """Test detection of invalid depth orphans."""
    # Create test data
    cursor = test_db.cursor()
    
    # Create a parent
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    
    # Create a child with wrong depth
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (2, 1, 'Child', 3, 1, 1)
    """)
    
    test_db.commit()
    
    # Detect orphans
    orphans = repair_manager.detect_orphans()
    
    assert len(orphans) == 1
    assert orphans[0].orphan_type == OrphanType.INVALID_DEPTH
    assert orphans[0].severity == "medium"
    assert RepairAction.FIX_DEPTH in orphans[0].suggested_actions

def test_detect_invalid_slot_orphans(repair_manager, test_db):
    """Test detection of invalid slot orphans."""
    # Create test data
    cursor = test_db.cursor()
    
    # Create a parent
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    
    # Create a child with invalid slot
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (2, 1, 'Child', 1, 6, 1)
    """)
    
    test_db.commit()
    
    # Detect orphans
    orphans = repair_manager.detect_orphans()
    
    assert len(orphans) == 1
    assert orphans[0].orphan_type == OrphanType.INVALID_SLOT
    assert orphans[0].severity == "medium"
    assert RepairAction.FIX_SLOT in orphans[0].suggested_actions

def test_detect_duplicate_slot_orphans(repair_manager, test_db):
    """Test detection of duplicate slot orphans."""
    # Create test data
    cursor = test_db.cursor()
    
    # Create a parent
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    
    # Create two children with same slot
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (2, 1, 'Child1', 1, 1, 1)
    """)
    
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (3, 1, 'Child2', 1, 1, 1)
    """)
    
    test_db.commit()
    
    # Detect orphans
    orphans = repair_manager.detect_orphans()
    
    assert len(orphans) == 2  # Both children are duplicates
    assert all(orphan.orphan_type == OrphanType.DUPLICATE_SLOT for orphan in orphans)
    assert all(orphan.severity == "high" for orphan in orphans)

def test_get_orphan_summary(repair_manager, test_db):
    """Test getting orphan summary."""
    # Create test data with various orphan types
    cursor = test_db.cursor()
    
    # Missing parent orphan
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (1, 999, 'Missing Parent', 1, 1, 1)
    """)
    
    # Invalid depth orphan
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (2, 1, 'Invalid Depth', 3, 1, 1)
    """)
    
    test_db.commit()
    
    # Get summary
    summary = repair_manager.get_orphan_summary()
    
    assert summary["total_orphans"] == 2
    assert summary["type_counts"]["missing_parent"] == 1
    assert summary["type_counts"]["invalid_depth"] == 1
    assert summary["status"] == "issues_detected"

def test_repair_delete_orphan(repair_manager, test_db):
    """Test deleting an orphan."""
    # Create test data
    cursor = test_db.cursor()
    
    # Create an orphan without children
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (1, 999, 'Orphan', 1, 1, 1)
    """)
    
    test_db.commit()
    
    # Repair by deleting
    result = repair_manager.repair_orphan(
        orphan_id=1,
        action=RepairAction.DELETE_ORPHAN
    )
    
    assert result.success is True
    assert result.action == RepairAction.DELETE_ORPHAN
    assert "deleted successfully" in result.message
    
    # Verify node is deleted
    cursor.execute("SELECT COUNT(*) FROM nodes WHERE id = 1")
    count = cursor.fetchone()[0]
    assert count == 0

def test_repair_delete_orphan_with_children(repair_manager, test_db):
    """Test deleting an orphan with children (should fail)."""
    # Create test data
    cursor = test_db.cursor()
    
    # Create an orphan with children
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (1, 999, 'Orphan', 1, 1, 0)
    """)
    
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (2, 1, 'Child', 2, 1, 1)
    """)
    
    test_db.commit()
    
    # Try to repair by deleting (should fail)
    result = repair_manager.repair_orphan(
        orphan_id=1,
        action=RepairAction.DELETE_ORPHAN
    )
    
    assert result.success is False
    assert "Cannot delete orphan with" in result.message

def test_repair_fix_depth(repair_manager, test_db):
    """Test fixing depth of an orphan."""
    # Create test data
    cursor = test_db.cursor()
    
    # Create a parent
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    
    # Create a child with wrong depth
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (2, 1, 'Child', 3, 1, 1)
    """)
    
    test_db.commit()
    
    # Repair by fixing depth
    result = repair_manager.repair_orphan(
        orphan_id=2,
        action=RepairAction.FIX_DEPTH
    )
    
    assert result.success is True
    assert result.action == RepairAction.FIX_DEPTH
    assert "Depth fixed to 1" in result.message
    
    # Verify depth is fixed
    cursor.execute("SELECT depth FROM nodes WHERE id = 2")
    depth = cursor.fetchone()[0]
    assert depth == 1

def test_repair_fix_slot(repair_manager, test_db):
    """Test fixing slot of an orphan."""
    # Create test data
    cursor = test_db.cursor()
    
    # Create a parent
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    
    # Create a child with invalid slot
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (2, 1, 'Child', 1, 6, 1)
    """)
    
    test_db.commit()
    
    # Repair by fixing slot
    result = repair_manager.repair_orphan(
        orphan_id=2,
        action=RepairAction.FIX_SLOT
    )
    
    assert result.success is True
    assert result.action == RepairAction.FIX_SLOT
    assert "Slot fixed to 1" in result.message
    
    # Verify slot is fixed
    cursor.execute("SELECT slot FROM nodes WHERE id = 2")
    slot = cursor.fetchone()[0]
    assert slot == 1

def test_repair_convert_to_root(repair_manager, test_db):
    """Test converting orphan to root."""
    # Create test data
    cursor = test_db.cursor()
    
    # Create an orphan
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (1, 999, 'Orphan', 1, 1, 1)
    """)
    
    test_db.commit()
    
    # Repair by converting to root
    result = repair_manager.repair_orphan(
        orphan_id=1,
        action=RepairAction.CONVERT_TO_ROOT
    )
    
    assert result.success is True
    assert result.action == RepairAction.CONVERT_TO_ROOT
    assert "converted to root node" in result.message
    
    # Verify node is now root
    cursor.execute("SELECT parent_id, depth, slot FROM nodes WHERE id = 1")
    parent_id, depth, slot = cursor.fetchone()
    assert parent_id is None
    assert depth == 0
    assert slot == 0

def test_repair_reassign_parent(repair_manager, test_db):
    """Test reassigning orphan to new parent."""
    # Create test data
    cursor = test_db.cursor()
    
    # Create a valid parent
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    
    # Create an orphan
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (2, 999, 'Orphan', 1, 1, 1)
    """)
    
    test_db.commit()
    
    # Repair by reassigning parent
    result = repair_manager.repair_orphan(
        orphan_id=2,
        action=RepairAction.REASSIGN_PARENT,
        new_parent_id=1
    )
    
    assert result.success is True
    assert result.action == RepairAction.REASSIGN_PARENT
    assert "reassigned to parent 1" in result.message
    
    # Verify parent is reassigned
    cursor.execute("SELECT parent_id, depth FROM nodes WHERE id = 2")
    parent_id, depth = cursor.fetchone()
    assert parent_id == 1
    assert depth == 1

def test_repair_merge_with_sibling(repair_manager, test_db):
    """Test merging orphan with sibling."""
    # Create test data
    cursor = test_db.cursor()
    
    # Create a parent
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    
    # Create two children with same slot (duplicates)
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (2, 1, 'Child1', 1, 1, 1)
    """)
    
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (3, 1, 'Child2', 1, 1, 1)
    """)
    
    test_db.commit()
    
    # Repair by merging
    result = repair_manager.repair_orphan(
        orphan_id=3,
        action=RepairAction.MERGE_WITH_SIBLING,
        sibling_id=2
    )
    
    assert result.success is True
    assert result.action == RepairAction.MERGE_WITH_SIBLING
    assert "merged with sibling 2" in result.message
    
    # Verify merge occurred
    cursor.execute("SELECT label FROM nodes WHERE id = 2")
    label = cursor.fetchone()[0]
    assert "Child1 / Child2" in label
    
    # Verify orphan is deleted
    cursor.execute("SELECT COUNT(*) FROM nodes WHERE id = 3")
    count = cursor.fetchone()[0]
    assert count == 0

def test_repair_audit_logging(repair_manager, test_db):
    """Test that repair actions are logged."""
    # Create test data
    cursor = test_db.cursor()
    
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (1, 999, 'Orphan', 1, 1, 1)
    """)
    
    test_db.commit()
    
    # Perform repair
    result = repair_manager.repair_orphan(
        orphan_id=1,
        action=RepairAction.DELETE_ORPHAN,
        actor="test_user"
    )
    
    assert result.success is True
    
    # Check audit log
    cursor.execute("""
        SELECT orphan_id, action, actor, success, message
        FROM orphan_repair_audit
        WHERE orphan_id = 1
    """)
    
    audit_row = cursor.fetchone()
    assert audit_row is not None
    assert audit_row[0] == 1  # orphan_id
    assert audit_row[1] == "delete_orphan"  # action
    assert audit_row[2] == "test_user"  # actor
    assert audit_row[3] == 1  # success
    assert "deleted successfully" in audit_row[4]  # message

def test_get_repair_history(repair_manager, test_db):
    """Test getting repair history."""
    # Create test data
    cursor = test_db.cursor()
    
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (1, 999, 'Orphan', 1, 1, 1)
    """)
    
    test_db.commit()
    
    # Perform repair
    repair_manager.repair_orphan(
        orphan_id=1,
        action=RepairAction.DELETE_ORPHAN,
        actor="test_user"
    )
    
    # Get history
    history = repair_manager.get_repair_history(orphan_id=1)
    
    assert len(history) == 1
    assert history[0]["orphan_id"] == 1
    assert history[0]["action"] == "delete_orphan"
    assert history[0]["actor"] == "test_user"
    assert history[0]["success"] is True

def test_repair_invalid_action(repair_manager, test_db):
    """Test repair with invalid action."""
    # Create test data
    cursor = test_db.cursor()
    
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (1, 999, 'Orphan', 1, 1, 1)
    """)
    
    test_db.commit()
    
    # Try invalid action
    result = repair_manager.repair_orphan(
        orphan_id=1,
        action=RepairAction.DELETE_ORPHAN  # This should work
    )
    
    # This should succeed, but let's test with a non-existent orphan
    result = repair_manager.repair_orphan(
        orphan_id=999,
        action=RepairAction.DELETE_ORPHAN
    )
    
    assert result.success is False
    assert "not found" in result.message

def test_repair_circular_reference(repair_manager, test_db):
    """Test repair with circular reference."""
    # Create test data
    cursor = test_db.cursor()
    
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (1, 999, 'Orphan', 1, 1, 1)
    """)
    
    test_db.commit()
    
    # Try to assign node as its own parent
    result = repair_manager.repair_orphan(
        orphan_id=1,
        action=RepairAction.REASSIGN_PARENT,
        new_parent_id=1
    )
    
    assert result.success is False
    assert "Cannot assign node as its own parent" in result.message

def test_repair_no_available_slots(repair_manager, test_db):
    """Test repair when no slots are available."""
    # Create test data
    cursor = test_db.cursor()
    
    # Create a parent with all slots filled
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    
    for slot in range(1, 6):
        cursor.execute("""
            INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
            VALUES (?, 1, 'Child', 1, ?, 1)
        """, (slot + 1, slot))
    
    # Create an orphan with invalid slot
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (7, 1, 'Orphan', 1, 6, 1)
    """)
    
    test_db.commit()
    
    # Try to fix slot (should fail - no available slots)
    result = repair_manager.repair_orphan(
        orphan_id=7,
        action=RepairAction.FIX_SLOT
    )
    
    assert result.success is False
    assert "No available slots" in result.message
