"""
Dictionary Governance System

Provides comprehensive governance features for dictionary terms including
approval workflows, status management, version control, and audit trails.
"""

import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

class DictionaryStatus(Enum):
    """Dictionary term status values."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class DictionaryAction(Enum):
    """Dictionary term actions for workflow."""
    CREATE = "create"
    UPDATE = "update"
    APPROVE = "approve"
    REJECT = "reject"
    DEPRECATE = "deprecate"
    ARCHIVE = "archive"
    RESTORE = "restore"
    BULK_APPROVE = "bulk_approve"
    BULK_REJECT = "bulk_reject"

class ApprovalLevel(Enum):
    """Approval levels for dictionary terms."""
    NONE = "none"  # No approval required
    EDITOR = "editor"  # Editor approval required
    ADMIN = "admin"  # Admin approval required
    MEDICAL_REVIEW = "medical_review"  # Medical review required

@dataclass
class DictionaryTerm:
    """Dictionary term with governance metadata."""
    id: int
    type: str
    term: str
    normalized: str
    hints: Optional[str] = None
    status: DictionaryStatus = DictionaryStatus.DRAFT
    version: int = 1
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    approval_level: ApprovalLevel = ApprovalLevel.NONE
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DictionaryWorkflow:
    """Dictionary workflow configuration."""
    type: str
    approval_level: ApprovalLevel
    requires_medical_review: bool = False
    auto_approve_editors: bool = False
    max_versions: int = 10
    retention_days: int = 365

@dataclass
class DictionaryChange:
    """Dictionary term change record."""
    id: int
    term_id: int
    action: DictionaryAction
    actor: str
    timestamp: datetime
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DictionaryGovernanceManager:
    """Manages dictionary governance operations."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._ensure_governance_tables()
        self._workflows = self._initialize_workflows()
    
    def _ensure_governance_tables(self):
        """Ensure dictionary governance tables exist."""
        cursor = self.conn.cursor()
        
        # Enhanced dictionary_terms table with governance fields
        cursor.execute("""
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
        
        # Dictionary workflows configuration
        cursor.execute("""
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
        
        # Dictionary changes audit trail
        cursor.execute("""
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
        
        # Dictionary approvals queue
        cursor.execute("""
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
        
        # Dictionary term relationships
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dictionary_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER NOT NULL,
                child_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES dictionary_terms_governance(id) ON DELETE CASCADE,
                FOREIGN KEY (child_id) REFERENCES dictionary_terms_governance(id) ON DELETE CASCADE,
                UNIQUE(parent_id, child_id, relationship_type)
            )
        """)
        
        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_dict_gov_type_status 
            ON dictionary_terms_governance(type, status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_dict_gov_created_by 
            ON dictionary_terms_governance(created_by)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_dict_gov_updated_at 
            ON dictionary_terms_governance(updated_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_dict_changes_term_id 
            ON dictionary_changes(term_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_dict_changes_timestamp 
            ON dictionary_changes(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_dict_approvals_term_id 
            ON dictionary_approvals(term_id)
        """)
        
        self.conn.commit()
    
    def _initialize_workflows(self) -> Dict[str, DictionaryWorkflow]:
        """Initialize default workflows for different term types."""
        workflows = {
            "vital_measurement": DictionaryWorkflow(
                type="vital_measurement",
                approval_level=ApprovalLevel.MEDICAL_REVIEW,
                requires_medical_review=True,
                auto_approve_editors=False,
                max_versions=5,
                retention_days=730
            ),
            "node_label": DictionaryWorkflow(
                type="node_label",
                approval_level=ApprovalLevel.EDITOR,
                requires_medical_review=False,
                auto_approve_editors=True,
                max_versions=10,
                retention_days=365
            ),
            "outcome_template": DictionaryWorkflow(
                type="outcome_template",
                approval_level=ApprovalLevel.MEDICAL_REVIEW,
                requires_medical_review=True,
                auto_approve_editors=False,
                max_versions=3,
                retention_days=1095
            )
        }
        
        # Store workflows in database
        cursor = self.conn.cursor()
        for workflow in workflows.values():
            cursor.execute("""
                INSERT OR REPLACE INTO dictionary_workflows 
                (type, approval_level, requires_medical_review, auto_approve_editors, 
                 max_versions, retention_days, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                workflow.type,
                workflow.approval_level.value,
                workflow.requires_medical_review,
                workflow.auto_approve_editors,
                workflow.max_versions,
                workflow.retention_days
            ))
        
        self.conn.commit()
        return workflows
    
    def create_term(
        self,
        type: str,
        term: str,
        normalized: str,
        hints: Optional[str] = None,
        created_by: str = "system",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Create a new dictionary term with governance."""
        cursor = self.conn.cursor()
        
        # Get workflow configuration
        workflow = self._workflows.get(type, DictionaryWorkflow(
            type=type,
            approval_level=ApprovalLevel.NONE
        ))
        
        # Determine initial status
        if workflow.approval_level == ApprovalLevel.NONE:
            status = DictionaryStatus.APPROVED
        elif workflow.auto_approve_editors and created_by in ["editor", "admin"]:
            status = DictionaryStatus.APPROVED
        else:
            status = DictionaryStatus.PENDING_APPROVAL
        
        # Create term
        now = datetime.now(timezone.utc)
        cursor.execute("""
            INSERT INTO dictionary_terms_governance 
            (type, term, normalized, hints, status, version, created_by, created_at, 
             updated_by, updated_at, approval_level, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            type, term, normalized, hints, status.value, 1, created_by, now,
            created_by, now, workflow.approval_level.value,
            json.dumps(tags) if tags else None,
            json.dumps(metadata) if metadata else None
        ))
        
        term_id = cursor.lastrowid
        
        # Log the change
        self._log_change(
            term_id=term_id,
            action=DictionaryAction.CREATE,
            actor=created_by,
            after_state={
                "type": type,
                "term": term,
                "normalized": normalized,
                "hints": hints,
                "status": status.value,
                "tags": tags,
                "metadata": metadata
            }
        )
        
        # If approved, log approval
        if status == DictionaryStatus.APPROVED:
            self._log_change(
                term_id=term_id,
                action=DictionaryAction.APPROVE,
                actor=created_by,
                reason="Auto-approved"
            )
        
        self.conn.commit()
        return term_id
    
    def update_term(
        self,
        term_id: int,
        term: Optional[str] = None,
        normalized: Optional[str] = None,
        hints: Optional[str] = None,
        updated_by: str = "system",
        reason: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update a dictionary term with governance."""
        cursor = self.conn.cursor()
        
        # Get current term
        cursor.execute("""
            SELECT type, term, normalized, hints, status, version, tags, metadata
            FROM dictionary_terms_governance WHERE id = ?
        """, (term_id,))
        
        row = cursor.fetchone()
        if not row:
            return False
        
        current_type, current_term, current_normalized, current_hints, \
        current_status, current_version, current_tags, current_metadata = row
        
        # Get workflow
        workflow = self._workflows.get(current_type, DictionaryWorkflow(
            type=current_type,
            approval_level=ApprovalLevel.NONE
        ))
        
        # Prepare update data
        update_fields = []
        update_values = []
        
        if term is not None:
            update_fields.append("term = ?")
            update_values.append(term)
        
        if normalized is not None:
            update_fields.append("normalized = ?")
            update_values.append(normalized)
        
        if hints is not None:
            update_fields.append("hints = ?")
            update_values.append(hints)
        
        if tags is not None:
            update_fields.append("tags = ?")
            update_values.append(json.dumps(tags))
        
        if metadata is not None:
            update_fields.append("metadata = ?")
            update_values.append(json.dumps(metadata))
        
        # Determine new status
        if current_status == DictionaryStatus.APPROVED.value:
            if workflow.approval_level == ApprovalLevel.NONE:
                new_status = DictionaryStatus.APPROVED
            elif workflow.auto_approve_editors and updated_by in ["editor", "admin"]:
                new_status = DictionaryStatus.APPROVED
            else:
                new_status = DictionaryStatus.PENDING_APPROVAL
        else:
            new_status = DictionaryStatus(current_status)
        
        # Increment version if status changes to pending approval
        new_version = current_version
        if new_status == DictionaryStatus.PENDING_APPROVAL and DictionaryStatus(current_status) != DictionaryStatus.PENDING_APPROVAL:
            new_version += 1
        
        update_fields.extend([
            "status = ?",
            "version = ?",
            "updated_by = ?",
            "updated_at = ?"
        ])
        update_values.extend([
            new_status.value,
            new_version,
            updated_by,
            datetime.now(timezone.utc)
        ])
        
        # Update term
        update_values.append(term_id)
        cursor.execute(f"""
            UPDATE dictionary_terms_governance 
            SET {', '.join(update_fields)}
            WHERE id = ?
        """, update_values)
        
        # Log the change
        self._log_change(
            term_id=term_id,
            action=DictionaryAction.UPDATE,
            actor=updated_by,
            before_state={
                "term": current_term,
                "normalized": current_normalized,
                "hints": current_hints,
                "status": current_status,
                "version": current_version,
                "tags": json.loads(current_tags) if current_tags else None,
                "metadata": json.loads(current_metadata) if current_metadata else None
            },
            after_state={
                "term": term or current_term,
                "normalized": normalized or current_normalized,
                "hints": hints if hints is not None else current_hints,
                "status": new_status.value,
                "version": new_version,
                "tags": tags,
                "metadata": metadata
            },
            reason=reason
        )
        
        # If approved, log approval
        if new_status == DictionaryStatus.APPROVED:
            self._log_change(
                term_id=term_id,
                action=DictionaryAction.APPROVE,
                actor=updated_by,
                reason="Auto-approved"
            )
        
        self.conn.commit()
        return True
    
    def approve_term(
        self,
        term_id: int,
        approver: str,
        reason: Optional[str] = None
    ) -> bool:
        """Approve a dictionary term."""
        cursor = self.conn.cursor()
        
        # Get current term
        cursor.execute("""
            SELECT status FROM dictionary_terms_governance WHERE id = ?
        """, (term_id,))
        
        row = cursor.fetchone()
        if not row:
            return False
        
        current_status = DictionaryStatus(row[0])
        if current_status != DictionaryStatus.PENDING_APPROVAL:
            return False
        
        # Update status
        now = datetime.now(timezone.utc)
        cursor.execute("""
            UPDATE dictionary_terms_governance 
            SET status = ?, approved_by = ?, approved_at = ?, updated_at = ?
            WHERE id = ?
        """, (DictionaryStatus.APPROVED.value, approver, now, now, term_id))
        
        # Log approval
        self._log_change(
            term_id=term_id,
            action=DictionaryAction.APPROVE,
            actor=approver,
            reason=reason
        )
        
        # Record approval
        cursor.execute("""
            INSERT INTO dictionary_approvals (term_id, approver, status, reason)
            VALUES (?, ?, ?, ?)
        """, (term_id, approver, "approved", reason))
        
        self.conn.commit()
        return True
    
    def reject_term(
        self,
        term_id: int,
        approver: str,
        reason: str
    ) -> bool:
        """Reject a dictionary term."""
        cursor = self.conn.cursor()
        
        # Get current term
        cursor.execute("""
            SELECT status FROM dictionary_terms_governance WHERE id = ?
        """, (term_id,))
        
        row = cursor.fetchone()
        if not row:
            return False
        
        current_status = DictionaryStatus(row[0])
        if current_status != DictionaryStatus.PENDING_APPROVAL:
            return False
        
        # Update status
        now = datetime.now(timezone.utc)
        cursor.execute("""
            UPDATE dictionary_terms_governance 
            SET status = ?, rejection_reason = ?, updated_by = ?, updated_at = ?
            WHERE id = ?
        """, (DictionaryStatus.REJECTED.value, reason, approver, now, term_id))
        
        # Log rejection
        self._log_change(
            term_id=term_id,
            action=DictionaryAction.REJECT,
            actor=approver,
            reason=reason
        )
        
        # Record rejection
        cursor.execute("""
            INSERT INTO dictionary_approvals (term_id, approver, status, reason)
            VALUES (?, ?, ?, ?)
        """, (term_id, approver, "rejected", reason))
        
        self.conn.commit()
        return True
    
    def get_terms(
        self,
        type: Optional[str] = None,
        status: Optional[DictionaryStatus] = None,
        created_by: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        search_query: Optional[str] = None
    ) -> List[DictionaryTerm]:
        """Get dictionary terms with filtering."""
        cursor = self.conn.cursor()
        
        query = """
            SELECT id, type, term, normalized, hints, status, version, created_by, 
                   created_at, updated_by, updated_at, approved_by, approved_at, 
                   rejection_reason, approval_level, tags, metadata
            FROM dictionary_terms_governance
        """
        params = []
        conditions = []
        
        if type:
            conditions.append("type = ?")
            params.append(type)
        
        if status:
            conditions.append("status = ?")
            params.append(status.value)
        
        if created_by:
            conditions.append("created_by = ?")
            params.append(created_by)
        
        if search_query:
            conditions.append("(term LIKE ? OR normalized LIKE ?)")
            search_pattern = f"%{search_query}%"
            params.extend([search_pattern, search_pattern])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        terms = []
        for row in rows:
            terms.append(DictionaryTerm(
                id=row[0],
                type=row[1],
                term=row[2],
                normalized=row[3],
                hints=row[4],
                status=DictionaryStatus(row[5]),
                version=row[6],
                created_by=row[7],
                created_at=datetime.fromisoformat(row[8].replace('Z', '+00:00')) if row[8] else None,
                updated_by=row[9],
                updated_at=datetime.fromisoformat(row[10].replace('Z', '+00:00')) if row[10] else None,
                approved_by=row[11],
                approved_at=datetime.fromisoformat(row[12].replace('Z', '+00:00')) if row[12] else None,
                rejection_reason=row[13],
                approval_level=ApprovalLevel(row[14]),
                tags=json.loads(row[15]) if row[15] else None,
                metadata=json.loads(row[16]) if row[16] else None
            ))
        
        return terms
    
    def get_pending_approvals(
        self,
        type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[DictionaryTerm]:
        """Get terms pending approval."""
        return self.get_terms(
            type=type,
            status=DictionaryStatus.PENDING_APPROVAL,
            limit=limit,
            offset=offset
        )
    
    def get_term_changes(
        self,
        term_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[DictionaryChange]:
        """Get change history for a term."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT id, term_id, action, actor, timestamp, before_state, 
                   after_state, reason, metadata
            FROM dictionary_changes
            WHERE term_id = ?
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """, (term_id, limit, offset))
        
        rows = cursor.fetchall()
        changes = []
        
        for row in rows:
            changes.append(DictionaryChange(
                id=row[0],
                term_id=row[1],
                action=DictionaryAction(row[2]),
                actor=row[3],
                timestamp=datetime.fromisoformat(row[4].replace('Z', '+00:00')),
                before_state=json.loads(row[5]) if row[5] else None,
                after_state=json.loads(row[6]) if row[6] else None,
                reason=row[7],
                metadata=json.loads(row[8]) if row[8] else None
            ))
        
        return changes
    
    def bulk_approve(
        self,
        term_ids: List[int],
        approver: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bulk approve multiple terms."""
        results = {
            "approved": [],
            "failed": [],
            "skipped": []
        }
        
        for term_id in term_ids:
            try:
                if self.approve_term(term_id, approver, reason):
                    results["approved"].append(term_id)
                else:
                    results["skipped"].append(term_id)
            except Exception as e:
                logger.error(f"Failed to approve term {term_id}: {e}")
                results["failed"].append({"term_id": term_id, "error": str(e)})
        
        # Log bulk approval
        if results["approved"]:
            self._log_change(
                term_id=0,  # Special ID for bulk operations
                action=DictionaryAction.BULK_APPROVE,
                actor=approver,
                metadata={
                    "approved_count": len(results["approved"]),
                    "approved_terms": results["approved"],
                    "failed_count": len(results["failed"]),
                    "skipped_count": len(results["skipped"])
                },
                reason=reason
            )
        
        return results
    
    def bulk_reject(
        self,
        term_ids: List[int],
        approver: str,
        reason: str
    ) -> Dict[str, Any]:
        """Bulk reject multiple terms."""
        results = {
            "rejected": [],
            "failed": [],
            "skipped": []
        }
        
        for term_id in term_ids:
            try:
                if self.reject_term(term_id, approver, reason):
                    results["rejected"].append(term_id)
                else:
                    results["skipped"].append(term_id)
            except Exception as e:
                logger.error(f"Failed to reject term {term_id}: {e}")
                results["failed"].append({"term_id": term_id, "error": str(e)})
        
        # Log bulk rejection
        if results["rejected"]:
            self._log_change(
                term_id=0,  # Special ID for bulk operations
                action=DictionaryAction.BULK_REJECT,
                actor=approver,
                metadata={
                    "rejected_count": len(results["rejected"]),
                    "rejected_terms": results["rejected"],
                    "failed_count": len(results["failed"]),
                    "skipped_count": len(results["skipped"])
                },
                reason=reason
            )
        
        return results
    
    def get_governance_stats(self) -> Dict[str, Any]:
        """Get dictionary governance statistics."""
        cursor = self.conn.cursor()
        
        # Total terms by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM dictionary_terms_governance
            GROUP BY status
        """)
        status_counts = dict(cursor.fetchall())
        
        # Terms by type
        cursor.execute("""
            SELECT type, COUNT(*) as count
            FROM dictionary_terms_governance
            GROUP BY type
        """)
        type_counts = dict(cursor.fetchall())
        
        # Pending approvals by type
        cursor.execute("""
            SELECT type, COUNT(*) as count
            FROM dictionary_terms_governance
            WHERE status = 'pending_approval'
            GROUP BY type
        """)
        pending_by_type = dict(cursor.fetchall())
        
        # Recent activity (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) FROM dictionary_changes
            WHERE timestamp > datetime('now', '-7 days')
        """)
        recent_changes = cursor.fetchone()[0]
        
        # Approval rate (last 30 days)
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN action = 'approve' THEN 1 END) as approved,
                COUNT(CASE WHEN action IN ('approve', 'reject') THEN 1 END) as total
            FROM dictionary_changes
            WHERE timestamp > datetime('now', '-30 days')
            AND action IN ('approve', 'reject')
        """)
        approval_row = cursor.fetchone()
        approval_rate = 0
        if approval_row[1] > 0:
            approval_rate = (approval_row[0] / approval_row[1]) * 100
        
        return {
            "status_counts": status_counts,
            "type_counts": type_counts,
            "pending_by_type": pending_by_type,
            "recent_changes_7d": recent_changes,
            "approval_rate_30d": approval_rate,
            "total_terms": sum(status_counts.values()),
            "pending_approvals": status_counts.get("pending_approval", 0)
        }
    
    def _log_change(
        self,
        term_id: int,
        action: DictionaryAction,
        actor: str,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log a dictionary change."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO dictionary_changes 
            (term_id, action, actor, before_state, after_state, reason, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            term_id,
            action.value,
            actor,
            json.dumps(before_state) if before_state else None,
            json.dumps(after_state) if after_state else None,
            reason,
            json.dumps(metadata) if metadata else None
        ))
