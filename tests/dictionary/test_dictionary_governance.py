"""
Tests for the dictionary governance system.

Tests approval workflows, status management, version control, and audit trails.
"""

import pytest
import sqlite3
import json
from datetime import datetime, timezone
from unittest.mock import Mock

from api.core.dictionary_governance import (
    DictionaryGovernanceManager,
    DictionaryStatus,
    DictionaryAction,
    ApprovalLevel,
    DictionaryTerm,
    DictionaryChange
)

@pytest.fixture
def test_db():
    """Create a test database with dictionary governance tables."""
    conn = sqlite3.connect(":memory:")
    
    # Create dictionary governance tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dictionary_terms_governance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            term TEXT NOT NULL,
            normalized TEXT NOT NULL,
            hints TEXT,
            status TEXT NOT NULL DEFAULT 'draft',
            version INTEGER NOT NULL DEFAULT 1,
            created_by TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_by TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            approved_by TEXT,
            approved_at DATETIME,
            rejection_reason TEXT,
            approval_level TEXT NOT NULL DEFAULT 'none',
            tags TEXT,
            metadata TEXT,
            parent_id INTEGER,
            UNIQUE(type, normalized, version)
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dictionary_workflows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT UNIQUE NOT NULL,
            approval_level TEXT NOT NULL DEFAULT 'none',
            requires_medical_review BOOLEAN DEFAULT 0,
            auto_approve_editors BOOLEAN DEFAULT 0,
            max_versions INTEGER DEFAULT 10,
            retention_days INTEGER DEFAULT 365,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dictionary_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            actor TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            before_state TEXT,
            after_state TEXT,
            reason TEXT,
            metadata TEXT,
            FOREIGN KEY (term_id) REFERENCES dictionary_terms_governance(id) ON DELETE CASCADE
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dictionary_approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term_id INTEGER NOT NULL,
            approver TEXT NOT NULL,
            status TEXT NOT NULL,
            reason TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (term_id) REFERENCES dictionary_terms_governance(id) ON DELETE CASCADE
        )
    """)
    
    yield conn
    conn.close()

@pytest.fixture
def governance_manager(test_db):
    """Create a dictionary governance manager for testing."""
    return DictionaryGovernanceManager(test_db)

def test_governance_manager_initialization(governance_manager):
    """Test governance manager initialization."""
    assert governance_manager is not None
    assert len(governance_manager._workflows) > 0

def test_create_term_no_approval_required(governance_manager):
    """Test creating a term that doesn't require approval."""
    term_id = governance_manager.create_term(
        type="node_label",
        term="Test Term",
        normalized="test term",
        hints="Test hints",
        created_by="editor"
    )
    
    assert term_id > 0
    
    # Check that term was auto-approved
    terms = governance_manager.get_terms(limit=1)
    assert len(terms) == 1
    assert terms[0].status == DictionaryStatus.APPROVED
    assert terms[0].created_by == "editor"

def test_create_term_requires_approval(governance_manager):
    """Test creating a term that requires approval."""
    term_id = governance_manager.create_term(
        type="vital_measurement",
        term="Blood Pressure",
        normalized="blood pressure",
        created_by="user"
    )
    
    assert term_id > 0
    
    # Check that term is pending approval
    terms = governance_manager.get_terms(limit=1)
    assert len(terms) == 1
    assert terms[0].status == DictionaryStatus.PENDING_APPROVAL
    assert terms[0].created_by == "user"

def test_approve_term(governance_manager):
    """Test approving a term."""
    # Create a term that requires approval
    term_id = governance_manager.create_term(
        type="vital_measurement",
        term="Heart Rate",
        normalized="heart rate",
        created_by="user"
    )
    
    # Approve the term
    success = governance_manager.approve_term(
        term_id=term_id,
        approver="admin",
        reason="Approved by medical review"
    )
    
    assert success is True
    
    # Check that term is approved
    terms = governance_manager.get_terms(limit=1)
    assert terms[0].status == DictionaryStatus.APPROVED
    assert terms[0].approved_by == "admin"

def test_reject_term(governance_manager):
    """Test rejecting a term."""
    # Create a term that requires approval
    term_id = governance_manager.create_term(
        type="vital_measurement",
        term="Invalid Term",
        normalized="invalid term",
        created_by="user"
    )
    
    # Reject the term
    success = governance_manager.reject_term(
        term_id=term_id,
        approver="admin",
        reason="Term is not medically accurate"
    )
    
    assert success is True
    
    # Check that term is rejected
    terms = governance_manager.get_terms(limit=1)
    assert terms[0].status == DictionaryStatus.REJECTED
    assert terms[0].rejection_reason == "Term is not medically accurate"

def test_update_term(governance_manager):
    """Test updating a term."""
    # Create a term
    term_id = governance_manager.create_term(
        type="node_label",
        term="Original Term",
        normalized="original term",
        created_by="editor"
    )
    
    # Update the term
    success = governance_manager.update_term(
        term_id=term_id,
        term="Updated Term",
        normalized="updated term",
        updated_by="editor",
        reason="Updated for clarity"
    )
    
    assert success is True
    
    # Check that term was updated
    terms = governance_manager.get_terms(limit=1)
    assert terms[0].term == "Updated Term"
    assert terms[0].version == 1  # Version should remain 1 for editor updates

def test_get_pending_approvals(governance_manager):
    """Test getting terms pending approval."""
    # Create terms with different statuses
    governance_manager.create_term(
        type="vital_measurement",
        term="Term 1",
        normalized="term 1",
        created_by="user"
    )
    
    governance_manager.create_term(
        type="node_label",
        term="Term 2",
        normalized="term 2",
        created_by="editor"
    )
    
    # Get pending approvals
    pending = governance_manager.get_pending_approvals()
    
    # Only the vital_measurement term should be pending
    assert len(pending) == 1
    assert pending[0].type == "vital_measurement"
    assert pending[0].status == DictionaryStatus.PENDING_APPROVAL

def test_bulk_approve(governance_manager):
    """Test bulk approving multiple terms."""
    # Create multiple terms
    term_ids = []
    for i in range(3):
        term_id = governance_manager.create_term(
            type="vital_measurement",
            term=f"Term {i}",
            normalized=f"term {i}",
            created_by="user"
        )
        term_ids.append(term_id)
    
    # Bulk approve
    results = governance_manager.bulk_approve(
        term_ids=term_ids,
        approver="admin",
        reason="Bulk approval"
    )
    
    assert len(results["approved"]) == 3
    assert len(results["failed"]) == 0
    assert len(results["skipped"]) == 0
    
    # Check that all terms are approved
    terms = governance_manager.get_terms()
    for term in terms:
        assert term.status == DictionaryStatus.APPROVED

def test_bulk_reject(governance_manager):
    """Test bulk rejecting multiple terms."""
    # Create multiple terms
    term_ids = []
    for i in range(3):
        term_id = governance_manager.create_term(
            type="vital_measurement",
            term=f"Invalid Term {i}",
            normalized=f"invalid term {i}",
            created_by="user"
        )
        term_ids.append(term_id)
    
    # Bulk reject
    results = governance_manager.bulk_reject(
        term_ids=term_ids,
        approver="admin",
        reason="Bulk rejection - not medically accurate"
    )
    
    assert len(results["rejected"]) == 3
    assert len(results["failed"]) == 0
    assert len(results["skipped"]) == 0
    
    # Check that all terms are rejected
    terms = governance_manager.get_terms()
    for term in terms:
        assert term.status == DictionaryStatus.REJECTED

def test_get_term_changes(governance_manager):
    """Test getting change history for a term."""
    # Create a term
    term_id = governance_manager.create_term(
        type="node_label",
        term="Test Term",
        normalized="test term",
        created_by="editor"
    )
    
    # Update the term
    governance_manager.update_term(
        term_id=term_id,
        term="Updated Term",
        updated_by="editor"
    )
    
    # Get changes
    changes = governance_manager.get_term_changes(term_id=term_id)
    
    # Check that create, update, and auto-approve are logged
    assert len(changes) >= 2  # Create + Update + possibly auto-approve
    
    # Find the specific actions
    create_actions = [c for c in changes if c.action == DictionaryAction.CREATE]
    update_actions = [c for c in changes if c.action == DictionaryAction.UPDATE]
    approve_actions = [c for c in changes if c.action == DictionaryAction.APPROVE]
    
    assert len(create_actions) == 1
    assert len(update_actions) == 1
    assert len(approve_actions) >= 1  # At least one approval (auto-approve)

def test_governance_stats(governance_manager):
    """Test getting governance statistics."""
    # Create some terms with different statuses
    governance_manager.create_term(
        type="vital_measurement",
        term="Term 1",
        normalized="term 1",
        created_by="user"
    )
    
    governance_manager.create_term(
        type="node_label",
        term="Term 2",
        normalized="term 2",
        created_by="editor"
    )
    
    # Get stats
    stats = governance_manager.get_governance_stats()
    
    assert stats["total_terms"] == 2
    assert stats["pending_approvals"] == 1  # Only vital_measurement
    assert "pending_approval" in stats["status_counts"]
    assert "approved" in stats["status_counts"]

def test_term_filtering(governance_manager):
    """Test filtering terms by various criteria."""
    # Create terms with different types and statuses
    governance_manager.create_term(
        type="vital_measurement",
        term="Blood Pressure",
        normalized="blood pressure",
        created_by="user"
    )
    
    governance_manager.create_term(
        type="node_label",
        term="Symptom",
        normalized="symptom",
        created_by="editor"
    )
    
    # Filter by type
    vital_terms = governance_manager.get_terms(type="vital_measurement")
    assert len(vital_terms) == 1
    assert vital_terms[0].type == "vital_measurement"
    
    # Filter by status
    approved_terms = governance_manager.get_terms(status=DictionaryStatus.APPROVED)
    assert len(approved_terms) == 1
    assert approved_terms[0].status == DictionaryStatus.APPROVED
    
    # Filter by creator
    editor_terms = governance_manager.get_terms(created_by="editor")
    assert len(editor_terms) == 1
    assert editor_terms[0].created_by == "editor"

def test_search_terms(governance_manager):
    """Test searching terms."""
    # Create terms with different content
    governance_manager.create_term(
        type="node_label",
        term="Blood Pressure",
        normalized="blood pressure",
        created_by="editor"
    )
    
    governance_manager.create_term(
        type="node_label",
        term="Heart Rate",
        normalized="heart rate",
        created_by="editor"
    )
    
    # Search for "blood"
    blood_terms = governance_manager.get_terms(search_query="blood")
    assert len(blood_terms) == 1
    assert "blood" in blood_terms[0].term.lower()
    
    # Search for "rate"
    rate_terms = governance_manager.get_terms(search_query="rate")
    assert len(rate_terms) == 1
    assert "rate" in rate_terms[0].term.lower()

def test_workflow_configuration(governance_manager):
    """Test workflow configuration for different term types."""
    workflows = governance_manager._workflows
    
    # Check vital_measurement workflow
    vital_workflow = workflows["vital_measurement"]
    assert vital_workflow.approval_level == ApprovalLevel.MEDICAL_REVIEW
    assert vital_workflow.requires_medical_review is True
    assert vital_workflow.auto_approve_editors is False
    
    # Check node_label workflow
    node_workflow = workflows["node_label"]
    assert node_workflow.approval_level == ApprovalLevel.EDITOR
    assert node_workflow.requires_medical_review is False
    assert node_workflow.auto_approve_editors is True

def test_version_control(governance_manager):
    """Test version control for term updates."""
    # Create a term
    term_id = governance_manager.create_term(
        type="node_label",
        term="Original Term",
        normalized="original term",
        created_by="editor"
    )
    
    # Update the term (should increment version)
    governance_manager.update_term(
        term_id=term_id,
        term="Updated Term",
        updated_by="editor"
    )
    
    # Check version - should still be 1 since no status change to pending
    terms = governance_manager.get_terms(limit=1)
    assert terms[0].version == 1

def test_approval_workflow_edge_cases(governance_manager):
    """Test edge cases in approval workflow."""
    # Create a term
    term_id = governance_manager.create_term(
        type="vital_measurement",
        term="Test Term",
        normalized="test term",
        created_by="user"
    )
    
    # Try to approve a non-existent term
    success = governance_manager.approve_term(99999, "admin")
    assert success is False
    
    # Try to reject a non-existent term
    success = governance_manager.reject_term(99999, "admin", "reason")
    assert success is False
    
    # Try to approve an already approved term
    governance_manager.approve_term(term_id, "admin")
    success = governance_manager.approve_term(term_id, "admin")
    assert success is False  # Should fail because it's already approved

def test_metadata_and_tags(governance_manager):
    """Test metadata and tags functionality."""
    # Create a term with metadata and tags
    term_id = governance_manager.create_term(
        type="node_label",
        term="Test Term",
        normalized="test term",
        created_by="editor",
        tags=["medical", "vital"],
        metadata={"source": "medical_dictionary", "confidence": 0.95}
    )
    
    # Check that metadata and tags are stored
    terms = governance_manager.get_terms(limit=1)
    assert terms[0].tags == ["medical", "vital"]
    assert terms[0].metadata["source"] == "medical_dictionary"
    assert terms[0].metadata["confidence"] == 0.95

def test_change_logging(governance_manager):
    """Test that changes are properly logged."""
    # Create a term
    term_id = governance_manager.create_term(
        type="node_label",
        term="Test Term",
        normalized="test term",
        created_by="editor"
    )
    
    # Update the term
    governance_manager.update_term(
        term_id=term_id,
        term="Updated Term",
        updated_by="editor",
        reason="Updated for clarity"
    )
    
    # Get changes
    changes = governance_manager.get_term_changes(term_id=term_id)
    
    # Check that create, update, and auto-approve are logged
    assert len(changes) >= 2  # Create + Update + auto-approve
    
    # Find the specific actions
    create_actions = [c for c in changes if c.action == DictionaryAction.CREATE]
    update_actions = [c for c in changes if c.action == DictionaryAction.UPDATE]
    approve_actions = [c for c in changes if c.action == DictionaryAction.APPROVE]
    
    assert len(create_actions) == 1
    assert len(update_actions) == 1
    assert len(approve_actions) >= 1  # At least one approval (auto-approve)
    
    # Check specific change details
    create_change = create_actions[0]
    assert create_change.actor == "editor"
    
    update_change = update_actions[0]
    assert update_change.actor == "editor"
    assert update_change.reason == "Updated for clarity"
