"""
Tests for the enhanced VM Builder system.

Tests enhanced draft management, planning, validation, and publishing.
"""

import pytest
import sqlite3
import json
from datetime import datetime, timezone
from unittest.mock import Mock

from api.core.vm_builder_enhanced import (
    EnhancedVMBuilderManager,
    VMBuilderStatus,
    VMOperationType,
    ValidationSeverity,
    DiffOperation,
    DiffPlan,
    ValidationIssue
)

@pytest.fixture
def test_db():
    """Create a test database with enhanced VM Builder tables."""
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
    
    # Create enhanced VM Builder tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vm_drafts_enhanced (
            id TEXT PRIMARY KEY,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            parent_id INTEGER,
            draft_data TEXT,
            status TEXT DEFAULT 'draft',
            published_at DATETIME,
            published_by TEXT,
            plan_data TEXT,
            validation_data TEXT,
            metadata TEXT,
            FOREIGN KEY (parent_id) REFERENCES nodes(id) ON DELETE CASCADE
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vm_builder_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draft_id TEXT NOT NULL,
            action TEXT NOT NULL,
            actor TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            before_state TEXT,
            after_state TEXT,
            success BOOLEAN NOT NULL,
            message TEXT,
            metadata TEXT,
            FOREIGN KEY (draft_id) REFERENCES vm_drafts_enhanced(id) ON DELETE CASCADE
        )
    """)
    
    yield conn
    conn.close()

@pytest.fixture
def enhanced_manager(test_db):
    """Create an enhanced VM Builder manager for testing."""
    return EnhancedVMBuilderManager(test_db)

def test_enhanced_manager_initialization(enhanced_manager, test_db):
    """Test enhanced VM Builder manager initialization."""
    assert enhanced_manager is not None
    
    # Check that tables were created
    cursor = test_db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vm_drafts_enhanced'")
    assert cursor.fetchone() is not None

def test_create_enhanced_draft(enhanced_manager, test_db):
    """Test creating an enhanced draft."""
    # Create a parent node
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    test_db.commit()
    
    # Create draft
    draft_data = {
        'children': [
            {'id': 2, 'label': 'Child 1', 'slot': 1, 'is_leaf': True, 'depth': 1},
            {'id': 3, 'label': 'Child 2', 'slot': 2, 'is_leaf': True, 'depth': 1}
        ]
    }
    
    metadata = {'created_via': 'test'}
    
    draft_id = enhanced_manager.create_draft(
        parent_id=1,
        draft_data=draft_data,
        actor='test_user',
        metadata=metadata
    )
    
    assert draft_id is not None
    
    # Verify draft was created
    draft = enhanced_manager.get_draft(draft_id)
    assert draft is not None
    assert draft['parent_id'] == 1
    assert draft['status'] == VMBuilderStatus.DRAFT.value
    assert draft['metadata'] == metadata

def test_update_enhanced_draft(enhanced_manager, test_db):
    """Test updating an enhanced draft."""
    # Create a parent node
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    test_db.commit()
    
    # Create draft
    draft_id = enhanced_manager.create_draft(
        parent_id=1,
        draft_data={'children': []},
        actor='test_user'
    )
    
    # Update draft
    updated_data = {
        'children': [
            {'id': 2, 'label': 'Updated Child', 'slot': 1, 'is_leaf': True, 'depth': 1}
        ]
    }
    
    success = enhanced_manager.update_draft(
        draft_id=draft_id,
        draft_data=updated_data,
        actor='test_user'
    )
    
    assert success is True
    
    # Verify update
    draft = enhanced_manager.get_draft(draft_id)
    assert draft['draft_data']['children'] == updated_data['children']

def test_plan_enhanced_draft(enhanced_manager, test_db):
    """Test planning an enhanced draft."""
    # Create a parent node with existing children
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (2, 1, 'Existing Child', 1, 1, 1)
    """)
    test_db.commit()
    
    # Create draft with different children
    draft_data = {
        'children': [
            {'id': 3, 'label': 'New Child', 'slot': 1, 'is_leaf': True, 'depth': 1},
            {'id': 2, 'label': 'Updated Child', 'slot': 2, 'is_leaf': True, 'depth': 1}
        ]
    }
    
    draft_id = enhanced_manager.create_draft(
        parent_id=1,
        draft_data=draft_data,
        actor='test_user'
    )
    
    # Plan draft
    diff_plan = enhanced_manager.plan_draft(draft_id, 'test_user')
    
    assert diff_plan is not None
    assert diff_plan.draft_id == draft_id
    assert diff_plan.parent_id == 1
    assert len(diff_plan.operations) > 0
    assert diff_plan.can_publish is True

def test_publish_enhanced_draft(enhanced_manager, test_db):
    """Test publishing an enhanced draft."""
    # Create a parent node
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    test_db.commit()
    
    # Create draft
    draft_data = {
        'children': [
            {'id': 2, 'label': 'New Child', 'slot': 1, 'is_leaf': True, 'depth': 1}
        ]
    }
    
    draft_id = enhanced_manager.create_draft(
        parent_id=1,
        draft_data=draft_data,
        actor='test_user'
    )
    
    # Publish draft
    result = enhanced_manager.publish_draft(draft_id, 'test_user')
    
    assert result['success'] is True
    assert result['operations_applied'] > 0
    
    # Verify draft status
    draft = enhanced_manager.get_draft(draft_id)
    assert draft['status'] == VMBuilderStatus.PUBLISHED.value
    assert draft['published_by'] == 'test_user'

def test_enhanced_diff_calculation(enhanced_manager, test_db):
    """Test enhanced diff calculation."""
    # Create a parent node with existing children
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
        VALUES (2, 1, 'Existing Child', 1, 1, 1)
    """)
    test_db.commit()
    
    # Create draft with different children
    draft_data = {
        'children': [
            {'id': 3, 'label': 'New Child', 'slot': 1, 'is_leaf': True, 'depth': 1},
            {'id': 2, 'label': 'Updated Child', 'slot': 2, 'is_leaf': True, 'depth': 1}
        ]
    }
    
    draft_id = enhanced_manager.create_draft(
        parent_id=1,
        draft_data=draft_data,
        actor='test_user'
    )
    
    # Calculate diff
    diff_plan = enhanced_manager._calculate_enhanced_diff({
        'id': draft_id,
        'parent_id': 1,
        'draft_data': draft_data
    })
    
    assert diff_plan is not None
    assert len(diff_plan.operations) > 0
    
    # Check operation types
    operation_types = [op.type.value for op in diff_plan.operations]
    assert 'create' in operation_types
    assert 'update' in operation_types

def test_enhanced_validation(enhanced_manager, test_db):
    """Test enhanced validation."""
    # Create a parent node
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    test_db.commit()
    
    # Create draft with validation issues
    draft_data = {
        'children': [
            {'id': 2, 'label': 'Child 1', 'slot': 1, 'is_leaf': True, 'depth': 1},
            {'id': 3, 'label': 'Child 1', 'slot': 2, 'is_leaf': True, 'depth': 1}  # Duplicate label
        ]
    }
    
    draft_id = enhanced_manager.create_draft(
        parent_id=1,
        draft_data=draft_data,
        actor='test_user'
    )
    
    # Plan draft (should trigger validation)
    diff_plan = enhanced_manager.plan_draft(draft_id, 'test_user')
    
    assert diff_plan is not None
    assert len(diff_plan.validation_issues) > 0
    
    # Check for duplicate label issue
    duplicate_issues = [
        issue for issue in diff_plan.validation_issues
        if issue.code == 'label_duplicate'
    ]
    assert len(duplicate_issues) > 0

def test_enhanced_operation_application(enhanced_manager, test_db):
    """Test enhanced operation application."""
    # Create a parent node
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    test_db.commit()
    
    # Create operation
    operation = DiffOperation(
        type=VMOperationType.CREATE,
        node_id=2,
        old_data=None,
        new_data={
            'label': 'New Child',
            'slot': 1,
            'is_leaf': True,
            'depth': 1
        },
        impact_level='medium',
        description='Create new child',
        affected_children=[]
    )
    
    # Apply operation
    enhanced_manager._apply_enhanced_operation(operation, 1)
    
    # Verify node was created
    cursor.execute("SELECT * FROM nodes WHERE id = 2")
    row = cursor.fetchone()
    assert row is not None
    assert row[1] == 1  # parent_id
    assert row[2] == 'New Child'  # label
    assert row[3] == 1  # slot

def test_enhanced_draft_stats(enhanced_manager, test_db):
    """Test enhanced draft statistics."""
    # Create some test drafts
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    test_db.commit()
    
    # Create drafts with different statuses
    enhanced_manager.create_draft(1, {'children': []}, 'test_user')
    enhanced_manager.create_draft(1, {'children': []}, 'test_user')
    
    # Update one to published
    drafts = enhanced_manager.list_drafts()
    if drafts:
        draft_id = drafts[0]['id']
        enhanced_manager.publish_draft(draft_id, 'test_user')
    
    # Get stats
    stats = enhanced_manager.get_draft_stats()
    
    assert stats['total_drafts'] >= 2
    assert 'draft' in stats['status_counts']
    assert stats['published_drafts'] >= 1

def test_enhanced_audit_logging(enhanced_manager, test_db):
    """Test enhanced audit logging."""
    # Create a parent node
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    test_db.commit()
    
    # Create draft
    draft_id = enhanced_manager.create_draft(
        parent_id=1,
        draft_data={'children': []},
        actor='test_user'
    )
    
    # Check audit log
    cursor.execute("""
        SELECT action, actor, success, message
        FROM vm_builder_audit
        WHERE draft_id = ?
    """, (draft_id,))
    
    audit_rows = cursor.fetchall()
    assert len(audit_rows) > 0
    
    # Check for create action
    create_actions = [row for row in audit_rows if row[0] == 'create_draft']
    assert len(create_actions) > 0
    assert create_actions[0][1] == 'test_user'  # actor
    assert create_actions[0][2] == 1  # success

def test_enhanced_draft_status_transitions(enhanced_manager, test_db):
    """Test enhanced draft status transitions."""
    # Create a parent node
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    test_db.commit()
    
    # Create draft
    draft_id = enhanced_manager.create_draft(
        parent_id=1,
        draft_data={'children': []},
        actor='test_user'
    )
    
    # Check initial status
    draft = enhanced_manager.get_draft(draft_id)
    assert draft['status'] == VMBuilderStatus.DRAFT.value
    
    # Plan draft
    enhanced_manager.plan_draft(draft_id, 'test_user')
    
    # Check status after planning
    draft = enhanced_manager.get_draft(draft_id)
    assert draft['status'] == VMBuilderStatus.READY_TO_PUBLISH.value

def test_enhanced_draft_metadata(enhanced_manager, test_db):
    """Test enhanced draft metadata handling."""
    # Create a parent node
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    test_db.commit()
    
    # Create draft with metadata
    metadata = {
        'created_via': 'test',
        'version': '1.0',
        'tags': ['test', 'enhanced']
    }
    
    draft_id = enhanced_manager.create_draft(
        parent_id=1,
        draft_data={'children': []},
        actor='test_user',
        metadata=metadata
    )
    
    # Verify metadata
    draft = enhanced_manager.get_draft(draft_id)
    assert draft['metadata'] == metadata

def test_enhanced_draft_error_handling(enhanced_manager, test_db):
    """Test enhanced draft error handling."""
    # Try to create draft with non-existent parent
    with pytest.raises(ValueError, match="Parent node 999 not found"):
        enhanced_manager.create_draft(
            parent_id=999,
            draft_data={'children': []},
            actor='test_user'
        )
    
    # Try to get non-existent draft
    draft = enhanced_manager.get_draft('non-existent')
    assert draft is None
    
    # Try to update non-existent draft
    success = enhanced_manager.update_draft(
        draft_id='non-existent',
        draft_data={'children': []},
        actor='test_user'
    )
    assert success is False

def test_enhanced_draft_force_publish(enhanced_manager, test_db):
    """Test enhanced draft force publish."""
    # Create a parent node
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO nodes (id, label, depth, slot, is_leaf)
        VALUES (1, 'Root', 0, 0, 0)
    """)
    test_db.commit()
    
    # Create draft with validation issues
    draft_data = {
        'children': [
            {'id': 2, 'label': 'Child 1', 'slot': 1, 'is_leaf': True, 'depth': 1},
            {'id': 3, 'label': 'Child 1', 'slot': 2, 'is_leaf': True, 'depth': 1}  # Duplicate label
        ]
    }
    
    draft_id = enhanced_manager.create_draft(
        parent_id=1,
        draft_data=draft_data,
        actor='test_user'
    )
    
    # Force publish despite validation issues
    result = enhanced_manager.publish_draft(draft_id, 'test_user', force=True)
    
    assert result['success'] is True
    
    # Verify draft status
    draft = enhanced_manager.get_draft(draft_id)
    assert draft['status'] == VMBuilderStatus.PUBLISHED.value
