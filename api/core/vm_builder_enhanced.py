"""
Enhanced VM Builder functionality with advanced planning and publishing features.

Provides sophisticated draft management, diff visualization, validation,
and publishing capabilities for the Vital Measurement Builder.
"""

import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timezone
from enum import Enum
import uuid
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class VMBuilderStatus(Enum):
    """VM Builder draft statuses."""
    DRAFT = "draft"
    PLANNING = "planning"
    READY_TO_PUBLISH = "ready_to_publish"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"

class VMOperationType(Enum):
    """VM Builder operation types."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MOVE = "move"
    REORDER = "reorder"

class ValidationSeverity(Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    severity: ValidationSeverity
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None
    code: Optional[str] = None

@dataclass
class DiffOperation:
    """Represents a single diff operation."""
    type: VMOperationType
    node_id: Optional[int]
    old_data: Optional[Dict[str, Any]]
    new_data: Optional[Dict[str, Any]]
    impact_level: str  # "low", "medium", "high", "critical"
    description: str
    affected_children: List[int] = None

@dataclass
class DiffPlan:
    """Represents a complete diff plan."""
    draft_id: str
    parent_id: int
    operations: List[DiffOperation]
    summary: Dict[str, int]
    validation_issues: List[ValidationIssue]
    estimated_impact: str
    can_publish: bool
    warnings: List[str]

class EnhancedVMBuilderManager:
    """Enhanced VM Builder manager with advanced planning and publishing."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._ensure_enhanced_tables()
    
    def _ensure_enhanced_tables(self):
        """Ensure enhanced VM Builder tables exist."""
        cursor = self.conn.cursor()
        
        # Enhanced VM drafts table
        cursor.execute("""
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
        
        # VM Builder audit table
        cursor.execute("""
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
        
        # VM Builder templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vm_builder_templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                template_data TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                is_public BOOLEAN DEFAULT 0,
                usage_count INTEGER DEFAULT 0
            )
        """)
        
        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_vm_drafts_enhanced_status 
            ON vm_drafts_enhanced(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_vm_drafts_enhanced_parent_id 
            ON vm_drafts_enhanced(parent_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_vm_builder_audit_draft_id 
            ON vm_builder_audit(draft_id)
        """)
        
        self.conn.commit()
    
    def create_draft(
        self,
        parent_id: int,
        draft_data: Dict[str, Any],
        actor: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new enhanced VM Builder draft."""
        draft_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        
        # Validate parent exists
        cursor.execute("SELECT id, label FROM nodes WHERE id = ?", (parent_id,))
        parent_row = cursor.fetchone()
        if not parent_row:
            raise ValueError(f"Parent node {parent_id} not found")
        
        parent_id, parent_label = parent_row
        
        # Create enhanced draft
        cursor.execute("""
            INSERT INTO vm_drafts_enhanced 
            (id, parent_id, draft_data, status, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            draft_id,
            parent_id,
            json.dumps(draft_data),
            VMBuilderStatus.DRAFT.value,
            json.dumps(metadata or {})
        ))
        
        self.conn.commit()
        
        # Log creation
        self._log_audit_action(
            draft_id, "create_draft", actor,
            None, {"parent_id": parent_id, "parent_label": parent_label},
            True, f"Draft created for parent {parent_label}"
        )
        
        logger.info(f"Enhanced VM draft created: {draft_id} for parent {parent_id} by {actor}")
        return draft_id
    
    def get_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """Get an enhanced VM Builder draft."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, created_at, updated_at, parent_id, draft_data, status,
                   published_at, published_by, plan_data, validation_data, metadata
            FROM vm_drafts_enhanced
            WHERE id = ?
        """, (draft_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            "id": row[0],
            "created_at": row[1],
            "updated_at": row[2],
            "parent_id": row[3],
            "draft_data": json.loads(row[4]) if row[4] else {},
            "status": row[5],
            "published_at": row[6],
            "published_by": row[7],
            "plan_data": json.loads(row[8]) if row[8] else None,
            "validation_data": json.loads(row[9]) if row[9] else None,
            "metadata": json.loads(row[10]) if row[10] else {}
        }
    
    def update_draft(
        self,
        draft_id: str,
        draft_data: Dict[str, Any],
        actor: str = "system"
    ) -> bool:
        """Update an enhanced VM Builder draft."""
        cursor = self.conn.cursor()
        
        # Get current state
        current_draft = self.get_draft(draft_id)
        if not current_draft:
            return False
        
        if current_draft["status"] not in [VMBuilderStatus.DRAFT.value, VMBuilderStatus.PLANNING.value]:
            return False
        
        # Update draft
        cursor.execute("""
            UPDATE vm_drafts_enhanced
            SET draft_data = ?, updated_at = CURRENT_TIMESTAMP,
                status = ?, plan_data = NULL, validation_data = NULL
            WHERE id = ? AND status IN ('draft', 'planning')
        """, (json.dumps(draft_data), VMBuilderStatus.DRAFT.value, draft_id))
        
        if cursor.rowcount == 0:
            return False
        
        self.conn.commit()
        
        # Log update
        self._log_audit_action(
            draft_id, "update_draft", actor,
            current_draft["draft_data"], draft_data,
            True, "Draft updated"
        )
        
        logger.info(f"Enhanced VM draft updated: {draft_id} by {actor}")
        return True
    
    def plan_draft(self, draft_id: str, actor: str = "system") -> DiffPlan:
        """Create a detailed plan for a draft."""
        draft = self.get_draft(draft_id)
        if not draft:
            raise ValueError(f"Draft {draft_id} not found")
        
        if draft["status"] not in [VMBuilderStatus.DRAFT.value, VMBuilderStatus.PLANNING.value]:
            raise ValueError(f"Draft {draft_id} is not in draft status")
        
        # Update status to planning
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE vm_drafts_enhanced
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (VMBuilderStatus.PLANNING.value, draft_id))
        self.conn.commit()
        
        try:
            # Calculate diff
            diff_plan = self._calculate_enhanced_diff(draft)
            
            # Validate plan
            validation_issues = self._validate_draft_plan(draft, diff_plan)
            
            # Update draft with plan data
            cursor.execute("""
                UPDATE vm_drafts_enhanced
                SET plan_data = ?, validation_data = ?, status = ?
                WHERE id = ?
            """, (
                json.dumps({
                    'draft_id': diff_plan.draft_id,
                    'parent_id': diff_plan.parent_id,
                    'operations': [{
                        'type': op.type.value,
                        'node_id': op.node_id,
                        'old_data': op.old_data,
                        'new_data': op.new_data,
                        'impact_level': op.impact_level,
                        'description': op.description,
                        'affected_children': op.affected_children or []
                    } for op in diff_plan.operations],
                    'summary': diff_plan.summary,
                    'validation_issues': [{
                        'severity': issue.severity.value,
                        'message': issue.message,
                        'field': issue.field,
                        'suggestion': issue.suggestion,
                        'code': issue.code
                    } for issue in diff_plan.validation_issues],
                    'estimated_impact': diff_plan.estimated_impact,
                    'can_publish': diff_plan.can_publish,
                    'warnings': diff_plan.warnings
                }),
                json.dumps([{
                    'severity': issue.severity.value,
                    'message': issue.message,
                    'field': issue.field,
                    'suggestion': issue.suggestion,
                    'code': issue.code
                } for issue in validation_issues]),
                VMBuilderStatus.READY_TO_PUBLISH.value if diff_plan.can_publish else VMBuilderStatus.PLANNING.value,
                draft_id
            ))
            self.conn.commit()
            
            # Log planning
            self._log_audit_action(
                draft_id, "plan_draft", actor,
                None, {"operations_count": len(diff_plan.operations)},
                True, f"Plan created with {len(diff_plan.operations)} operations"
            )
            
            return diff_plan
            
        except Exception as e:
            # Update status to failed
            cursor.execute("""
                UPDATE vm_drafts_enhanced
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (VMBuilderStatus.FAILED.value, draft_id))
            self.conn.commit()
            
            logger.error(f"Error planning draft {draft_id}: {e}")
            raise
    
    def publish_draft(
        self,
        draft_id: str,
        actor: str = "system",
        force: bool = False
    ) -> Dict[str, Any]:
        """Publish an enhanced VM Builder draft."""
        draft = self.get_draft(draft_id)
        if not draft:
            raise ValueError(f"Draft {draft_id} not found")
        
        if draft["status"] != VMBuilderStatus.READY_TO_PUBLISH.value and not force:
            raise ValueError(f"Draft {draft_id} is not ready to publish")
        
        # Update status to publishing
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE vm_drafts_enhanced
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (VMBuilderStatus.PUBLISHING.value, draft_id))
        self.conn.commit()
        
        try:
            # Get plan data
            plan_data = draft.get("plan_data")
            if not plan_data:
                # Recalculate plan if not available
                diff_plan = self.plan_draft(draft_id, actor)
            else:
                # Reconstruct DiffPlan from stored data
                plan_dict = json.loads(plan_data)
                diff_plan = DiffPlan(**plan_dict)
            
            if not diff_plan.can_publish and not force:
                raise ValueError("Draft has validation issues that prevent publishing")
            
            # Apply operations transactionally
            self.conn.execute("BEGIN TRANSACTION")
            
            applied_operations = []
            for operation in diff_plan.operations:
                try:
                    self._apply_enhanced_operation(operation, draft["parent_id"])
                    applied_operations.append(operation)
                except Exception as e:
                    logger.error(f"Failed to apply operation {operation.type}: {e}")
                    raise
            
            # Mark draft as published
            cursor.execute("""
                UPDATE vm_drafts_enhanced
                SET status = ?, published_at = CURRENT_TIMESTAMP, published_by = ?
                WHERE id = ?
            """, (VMBuilderStatus.PUBLISHED.value, actor, draft_id))
            
            self.conn.commit()
            
            # Log audit entry
            from .audit import AuditManager, AuditOperation
            audit_manager = AuditManager(self.conn)
            audit_id = audit_manager.log_operation(
                operation=AuditOperation.CHILDREN_UPDATE,
                target_id=draft["parent_id"],
                actor=actor,
                payload={
                    "draft_id": draft_id,
                    "operations": [op.__dict__ for op in applied_operations],
                    "summary": diff_plan.summary
                },
                is_undoable=False
            )
            
            # Log publishing
            self._log_audit_action(
                draft_id, "publish_draft", actor,
                None, {"operations_applied": len(applied_operations)},
                True, f"Successfully published {len(applied_operations)} operations"
            )
            
            logger.info(f"Enhanced VM draft published: {draft_id} by {actor}")
            
            return {
                "success": True,
                "message": f"Successfully published {len(applied_operations)} operations",
                "draft_id": draft_id,
                "operations_applied": len(applied_operations),
                "audit_id": audit_id,
                "summary": diff_plan.summary
            }
            
        except Exception as e:
            self.conn.rollback()
            
            # Update status to failed
            cursor.execute("""
                UPDATE vm_drafts_enhanced
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (VMBuilderStatus.FAILED.value, draft_id))
            self.conn.commit()
            
            logger.error(f"Error publishing draft {draft_id}: {e}")
            raise
    
    def _calculate_enhanced_diff(self, draft: Dict[str, Any]) -> DiffPlan:
        """Calculate enhanced diff with detailed operations."""
        parent_id = draft["parent_id"]
        draft_data = draft["draft_data"]
        
        # Get current state
        current_children = self._get_current_children(parent_id)
        
        # Get target state from draft
        target_children = draft_data.get("children", [])
        
        # Calculate operations
        operations = self._calculate_enhanced_operations(current_children, target_children)
        
        # Calculate summary
        summary = self._summarize_operations(operations)
        
        # Determine if can publish
        can_publish = len(operations) > 0 and all(
            op.impact_level not in ["critical"] for op in operations
        )
        
        # Calculate estimated impact
        impact_levels = [op.impact_level for op in operations]
        if "critical" in impact_levels:
            estimated_impact = "critical"
        elif "high" in impact_levels:
            estimated_impact = "high"
        elif "medium" in impact_levels:
            estimated_impact = "medium"
        else:
            estimated_impact = "low"
        
        # Generate warnings
        warnings = []
        if len(operations) > 10:
            warnings.append("Large number of operations may take time to apply")
        if any(op.impact_level == "high" for op in operations):
            warnings.append("High impact operations detected")
        
        return DiffPlan(
            draft_id=draft["id"],
            parent_id=parent_id,
            operations=operations,
            summary=summary,
            validation_issues=[],
            estimated_impact=estimated_impact,
            can_publish=can_publish,
            warnings=warnings
        )
    
    def _calculate_enhanced_operations(
        self,
        current: List[Dict[str, Any]],
        target: List[Dict[str, Any]]
    ) -> List[DiffOperation]:
        """Calculate enhanced operations with detailed impact analysis."""
        operations = []
        
        # Create maps for easier lookup
        current_by_id = {child["id"]: child for child in current}
        target_by_id = {child["id"]: child for child in target}
        
        # Find deletions
        for child in current:
            if child["id"] not in target_by_id:
                operations.append(DiffOperation(
                    type=VMOperationType.DELETE,
                    node_id=child["id"],
                    old_data=child,
                    new_data=None,
                    impact_level="high",
                    description=f"Delete node '{child['label']}' from slot {child['slot']}",
                    affected_children=[]
                ))
        
        # Find updates and moves
        for child in target:
            if child["id"] in current_by_id:
                current_child = current_by_id[child["id"]]
                changes = []
                impact_level = "low"
                
                if current_child["label"] != child["label"]:
                    changes.append(f"label: '{current_child['label']}' → '{child['label']}'")
                    impact_level = "medium"
                
                if current_child["slot"] != child["slot"]:
                    changes.append(f"slot: {current_child['slot']} → {child['slot']}")
                    impact_level = "high"
                
                if current_child["is_leaf"] != child["is_leaf"]:
                    changes.append(f"is_leaf: {current_child['is_leaf']} → {child['is_leaf']}")
                    impact_level = "high"
                
                if changes:
                    operations.append(DiffOperation(
                        type=VMOperationType.UPDATE,
                        node_id=child["id"],
                        old_data=current_child,
                        new_data=child,
                        impact_level=impact_level,
                        description=f"Update node: {', '.join(changes)}",
                        affected_children=[]
                    ))
        
        # Find creations
        for child in target:
            if child["id"] not in current_by_id:
                operations.append(DiffOperation(
                    type=VMOperationType.CREATE,
                    node_id=child["id"],
                    old_data=None,
                    new_data=child,
                    impact_level="medium",
                    description=f"Create node '{child['label']}' in slot {child['slot']}",
                    affected_children=[]
                ))
        
        return operations
    
    def _validate_draft_plan(self, draft: Dict[str, Any], diff_plan: DiffPlan) -> List[ValidationIssue]:
        """Validate a draft plan and return issues."""
        issues = []
        
        # Check for empty operations
        if not diff_plan.operations:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="No changes to apply",
                code="no_changes"
            ))
        
        # Check for critical operations
        critical_ops = [op for op in diff_plan.operations if op.impact_level == "critical"]
        if critical_ops:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"{len(critical_ops)} critical operations detected",
                code="critical_operations"
            ))
        
        # Check for slot conflicts
        slots_used = set()
        for op in diff_plan.operations:
            if op.type in [VMOperationType.CREATE, VMOperationType.UPDATE] and op.new_data:
                slot = op.new_data.get("slot")
                if slot in slots_used:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Slot {slot} is used multiple times",
                        field="slot",
                        code="slot_conflict"
                    ))
                slots_used.add(slot)
        
        # Check for label conflicts
        labels_used = set()
        for op in diff_plan.operations:
            if op.type in [VMOperationType.CREATE, VMOperationType.UPDATE] and op.new_data:
                label = op.new_data.get("label", "").strip()
                if label and label in labels_used:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Label '{label}' is used multiple times",
                        field="label",
                        code="label_duplicate"
                    ))
                labels_used.add(label)
        
        return issues
    
    def _apply_enhanced_operation(self, operation: DiffOperation, parent_id: int):
        """Apply an enhanced operation to the database."""
        cursor = self.conn.cursor()
        op_type = operation.type
        
        if op_type == VMOperationType.CREATE:
            cursor.execute("""
                INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                operation.node_id,
                parent_id,
                operation.new_data["label"],
                operation.new_data["slot"],
                operation.new_data["is_leaf"],
                operation.new_data["depth"]
            ))
        
        elif op_type == VMOperationType.UPDATE:
            cursor.execute("""
                UPDATE nodes
                SET label = ?, slot = ?, is_leaf = ?
                WHERE id = ?
            """, (
                operation.new_data["label"],
                operation.new_data["slot"],
                operation.new_data["is_leaf"],
                operation.node_id
            ))
        
        elif op_type == VMOperationType.DELETE:
            cursor.execute("DELETE FROM nodes WHERE id = ?", (operation.node_id,))
    
    def _get_current_children(self, parent_id: int) -> List[Dict[str, Any]]:
        """Get current children for a parent node."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, label, slot, is_leaf, depth
            FROM nodes
            WHERE parent_id = ?
            ORDER BY slot
        """, (parent_id,))
        
        children = []
        for row in cursor.fetchall():
            children.append({
                "id": row[0],
                "label": row[1],
                "slot": row[2],
                "is_leaf": bool(row[3]),
                "depth": row[4]
            })
        
        return children
    
    def _summarize_operations(self, operations: List[DiffOperation]) -> Dict[str, int]:
        """Summarize operations by type."""
        summary = {
            "create": 0,
            "update": 0,
            "delete": 0,
            "move": 0,
            "total": len(operations)
        }
        
        for op in operations:
            op_type = op.type.value
            if op_type in summary:
                summary[op_type] += 1
        
        return summary
    
    def _log_audit_action(
        self,
        draft_id: str,
        action: str,
        actor: str,
        before_state: Optional[Dict[str, Any]],
        after_state: Optional[Dict[str, Any]],
        success: bool,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log an audit action."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO vm_builder_audit 
            (draft_id, action, actor, before_state, after_state, success, message, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            draft_id,
            action,
            actor,
            json.dumps(before_state) if before_state else None,
            json.dumps(after_state) if after_state else None,
            success,
            message,
            json.dumps(metadata) if metadata else None
        ))
        self.conn.commit()
    
    def list_drafts(self, parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """List enhanced VM Builder drafts."""
        cursor = self.conn.cursor()
        
        if parent_id:
            cursor.execute("""
                SELECT id, created_at, updated_at, parent_id, status
                FROM vm_drafts_enhanced
                WHERE parent_id = ?
                ORDER BY updated_at DESC
            """, (parent_id,))
        else:
            cursor.execute("""
                SELECT id, created_at, updated_at, parent_id, status
                FROM vm_drafts_enhanced
                ORDER BY updated_at DESC
            """)
        
        rows = cursor.fetchall()
        drafts = []
        
        for row in rows:
            drafts.append({
                "id": row[0],
                "created_at": row[1],
                "updated_at": row[2],
                "parent_id": row[3],
                "status": row[4]
            })
        
        return drafts

    def get_draft_stats(self) -> Dict[str, Any]:
        """Get enhanced VM Builder statistics."""
        cursor = self.conn.cursor()
        
        # Total drafts
        cursor.execute("SELECT COUNT(*) FROM vm_drafts_enhanced")
        total_drafts = cursor.fetchone()[0]
        
        # Drafts by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM vm_drafts_enhanced
            GROUP BY status
        """)
        status_counts = dict(cursor.fetchall())
        
        # Recent drafts
        cursor.execute("""
            SELECT COUNT(*) FROM vm_drafts_enhanced
            WHERE created_at > datetime('now', '-7 days')
        """)
        recent_drafts = cursor.fetchone()[0]
        
        # Published drafts
        cursor.execute("""
            SELECT COUNT(*) FROM vm_drafts_enhanced
            WHERE status = 'published'
        """)
        published_drafts = cursor.fetchone()[0]
        
        return {
            "total_drafts": total_drafts,
            "status_counts": status_counts,
            "recent_drafts": recent_drafts,
            "published_drafts": published_drafts
        }
