"""
Orphan Node Repair System

Provides comprehensive repair functionality for orphaned nodes in the decision tree.
Handles various types of orphan scenarios and provides safe repair options.
"""

import sqlite3
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class OrphanType(Enum):
    """Types of orphan nodes."""
    MISSING_PARENT = "missing_parent"  # parent_id references non-existent node
    INVALID_DEPTH = "invalid_depth"    # depth doesn't match parent depth + 1
    CIRCULAR_REFERENCE = "circular_reference"  # node references itself or creates cycle
    INVALID_SLOT = "invalid_slot"      # slot is outside valid range (1-5)
    DUPLICATE_SLOT = "duplicate_slot"  # multiple children with same slot

class RepairAction(Enum):
    """Available repair actions."""
    DELETE_ORPHAN = "delete_orphan"
    REASSIGN_PARENT = "reassign_parent"
    FIX_DEPTH = "fix_depth"
    FIX_SLOT = "fix_slot"
    CONVERT_TO_ROOT = "convert_to_root"
    MERGE_WITH_SIBLING = "merge_with_sibling"

@dataclass
class OrphanNode:
    """Represents an orphaned node with repair information."""
    id: int
    label: str
    depth: int
    parent_id: Optional[int]
    slot: Optional[int]
    orphan_type: OrphanType
    severity: str  # "low", "medium", "high", "critical"
    suggested_actions: List[RepairAction]
    repair_impact: str  # Description of what the repair will do
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class RepairResult:
    """Result of a repair operation."""
    success: bool
    action: RepairAction
    orphan_id: int
    message: str
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    warnings: List[str] = None

class OrphanRepairManager:
    """Manages orphan node detection and repair operations."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._ensure_repair_tables()
    
    def _ensure_repair_tables(self):
        """Ensure repair audit tables exist."""
        cursor = self.conn.cursor()
        
        # Orphan repair audit table
        cursor.execute("""
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
        
        # Index for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orphan_repair_audit_orphan_id 
            ON orphan_repair_audit(orphan_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orphan_repair_audit_timestamp 
            ON orphan_repair_audit(timestamp)
        """)
        
        self.conn.commit()
    
    def detect_orphans(self, limit: int = 100, offset: int = 0) -> List[OrphanNode]:
        """Detect all types of orphan nodes."""
        cursor = self.conn.cursor()
        orphans = []
        
        # 1. Missing parent orphans
        cursor.execute("""
            SELECT n.id, n.label, n.depth, n.parent_id, n.slot, n.created_at, n.updated_at
            FROM nodes n
            LEFT JOIN nodes p ON p.id = n.parent_id
            WHERE n.parent_id IS NOT NULL AND p.id IS NULL
            ORDER BY n.id
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        for row in cursor.fetchall():
            node_id, label, depth, parent_id, slot, created_at, updated_at = row
            orphans.append(OrphanNode(
                id=node_id,
                label=label,
                depth=depth,
                parent_id=parent_id,
                slot=slot,
                orphan_type=OrphanType.MISSING_PARENT,
                severity="high",
                suggested_actions=[RepairAction.DELETE_ORPHAN, RepairAction.CONVERT_TO_ROOT],
                repair_impact="Delete orphaned node or convert to root node",
                created_at=datetime.fromisoformat(created_at.replace('Z', '+00:00')) if created_at else None,
                updated_at=datetime.fromisoformat(updated_at.replace('Z', '+00:00')) if updated_at else None
            ))
        
        # 2. Invalid depth orphans
        cursor.execute("""
            SELECT n.id, n.label, n.depth, n.parent_id, n.slot, n.created_at, n.updated_at
            FROM nodes n
            JOIN nodes p ON p.id = n.parent_id
            WHERE n.depth != p.depth + 1
            ORDER BY n.id
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        for row in cursor.fetchall():
            node_id, label, depth, parent_id, slot, created_at, updated_at = row
            orphans.append(OrphanNode(
                id=node_id,
                label=label,
                depth=depth,
                parent_id=parent_id,
                slot=slot,
                orphan_type=OrphanType.INVALID_DEPTH,
                severity="medium",
                suggested_actions=[RepairAction.FIX_DEPTH],
                repair_impact="Fix depth to match parent depth + 1",
                created_at=datetime.fromisoformat(created_at.replace('Z', '+00:00')) if created_at else None,
                updated_at=datetime.fromisoformat(updated_at.replace('Z', '+00:00')) if updated_at else None
            ))
        
        # 3. Invalid slot orphans
        cursor.execute("""
            SELECT n.id, n.label, n.depth, n.parent_id, n.slot, n.created_at, n.updated_at
            FROM nodes n
            WHERE n.parent_id IS NOT NULL 
            AND (n.slot IS NULL OR n.slot < 1 OR n.slot > 5)
            ORDER BY n.id
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        for row in cursor.fetchall():
            node_id, label, depth, parent_id, slot, created_at, updated_at = row
            orphans.append(OrphanNode(
                id=node_id,
                label=label,
                depth=depth,
                parent_id=parent_id,
                slot=slot,
                orphan_type=OrphanType.INVALID_SLOT,
                severity="medium",
                suggested_actions=[RepairAction.FIX_SLOT],
                repair_impact="Assign valid slot number (1-5)",
                created_at=datetime.fromisoformat(created_at.replace('Z', '+00:00')) if created_at else None,
                updated_at=datetime.fromisoformat(updated_at.replace('Z', '+00:00')) if updated_at else None
            ))
        
        # 4. Duplicate slot orphans
        cursor.execute("""
            SELECT n.id, n.label, n.depth, n.parent_id, n.slot, n.created_at, n.updated_at
            FROM nodes n
            WHERE n.parent_id IS NOT NULL
            AND n.slot IN (
                SELECT slot FROM nodes 
                WHERE parent_id = n.parent_id 
                AND slot = n.slot 
                AND id != n.id
            )
            ORDER BY n.id
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        for row in cursor.fetchall():
            node_id, label, depth, parent_id, slot, created_at, updated_at = row
            orphans.append(OrphanNode(
                id=node_id,
                label=label,
                depth=depth,
                parent_id=parent_id,
                slot=slot,
                orphan_type=OrphanType.DUPLICATE_SLOT,
                severity="high",
                suggested_actions=[RepairAction.FIX_SLOT, RepairAction.MERGE_WITH_SIBLING],
                repair_impact="Fix duplicate slot or merge with sibling",
                created_at=datetime.fromisoformat(created_at.replace('Z', '+00:00')) if created_at else None,
                updated_at=datetime.fromisoformat(updated_at.replace('Z', '+00:00')) if updated_at else None
            ))
        
        return orphans
    
    def get_orphan_summary(self) -> Dict[str, Any]:
        """Get summary of orphan issues."""
        cursor = self.conn.cursor()
        
        # Count by type
        cursor.execute("""
            SELECT 
                'missing_parent' as type,
                COUNT(*) as count
            FROM nodes n
            LEFT JOIN nodes p ON p.id = n.parent_id
            WHERE n.parent_id IS NOT NULL AND p.id IS NULL
            
            UNION ALL
            
            SELECT 
                'invalid_depth' as type,
                COUNT(*) as count
            FROM nodes n
            JOIN nodes p ON p.id = n.parent_id
            WHERE n.depth != p.depth + 1
            
            UNION ALL
            
            SELECT 
                'invalid_slot' as type,
                COUNT(*) as count
            FROM nodes n
            WHERE n.parent_id IS NOT NULL 
            AND (n.slot IS NULL OR n.slot < 1 OR n.slot > 5)
            
            UNION ALL
            
            SELECT 
                'duplicate_slot' as type,
                COUNT(*) as count
            FROM nodes n
            WHERE n.parent_id IS NOT NULL
            AND n.slot IN (
                SELECT slot FROM nodes 
                WHERE parent_id = n.parent_id 
                AND slot = n.slot 
                AND id != n.id
            )
        """)
        
        type_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Total orphan count
        total_orphans = sum(type_counts.values())
        
        # Severity breakdown
        severity_counts = {
            "critical": 0,
            "high": type_counts.get("missing_parent", 0) + type_counts.get("duplicate_slot", 0),
            "medium": type_counts.get("invalid_depth", 0) + type_counts.get("invalid_slot", 0),
            "low": 0
        }
        
        return {
            "total_orphans": total_orphans,
            "type_counts": type_counts,
            "severity_counts": severity_counts,
            "status": "healthy" if total_orphans == 0 else "issues_detected"
        }
    
    def repair_orphan(
        self,
        orphan_id: int,
        action: RepairAction,
        actor: str = "system",
        **kwargs
    ) -> RepairResult:
        """Repair a specific orphan node."""
        cursor = self.conn.cursor()
        
        # Get current state
        cursor.execute("""
            SELECT id, label, depth, parent_id, slot, created_at, updated_at
            FROM nodes WHERE id = ?
        """, (orphan_id,))
        
        row = cursor.fetchone()
        if not row:
            return RepairResult(
                success=False,
                action=action,
                orphan_id=orphan_id,
                message="Orphan node not found"
            )
        
        node_id, label, depth, parent_id, slot, created_at, updated_at = row
        before_state = {
            "id": node_id,
            "label": label,
            "depth": depth,
            "parent_id": parent_id,
            "slot": slot,
            "created_at": created_at,
            "updated_at": updated_at
        }
        
        try:
            cursor.execute("BEGIN TRANSACTION")
            
            if action == RepairAction.DELETE_ORPHAN:
                result = self._delete_orphan(cursor, orphan_id, **kwargs)
            elif action == RepairAction.REASSIGN_PARENT:
                result = self._reassign_parent(cursor, orphan_id, **kwargs)
            elif action == RepairAction.FIX_DEPTH:
                result = self._fix_depth(cursor, orphan_id, **kwargs)
            elif action == RepairAction.FIX_SLOT:
                result = self._fix_slot(cursor, orphan_id, **kwargs)
            elif action == RepairAction.CONVERT_TO_ROOT:
                result = self._convert_to_root(cursor, orphan_id, **kwargs)
            elif action == RepairAction.MERGE_WITH_SIBLING:
                result = self._merge_with_sibling(cursor, orphan_id, **kwargs)
            else:
                result = RepairResult(
                    success=False,
                    action=action,
                    orphan_id=orphan_id,
                    message="Unknown repair action"
                )
            
            if result.success:
                cursor.execute("COMMIT")
                
                # Get after state
                cursor.execute("""
                    SELECT id, label, depth, parent_id, slot, created_at, updated_at
                    FROM nodes WHERE id = ?
                """, (orphan_id,))
                
                after_row = cursor.fetchone()
                if after_row:
                    result.after_state = {
                        "id": after_row[0],
                        "label": after_row[1],
                        "depth": after_row[2],
                        "parent_id": after_row[3],
                        "slot": after_row[4],
                        "created_at": after_row[5],
                        "updated_at": after_row[6]
                    }
                
                # Log repair action
                self._log_repair_action(
                    cursor, orphan_id, action, actor, 
                    before_state, result.after_state, 
                    result.message, result.warnings or []
                )
            else:
                cursor.execute("ROLLBACK")
            
            return result
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            logger.error(f"Error repairing orphan {orphan_id}: {e}")
            return RepairResult(
                success=False,
                action=action,
                orphan_id=orphan_id,
                message=f"Repair failed: {str(e)}"
            )
    
    def _delete_orphan(self, cursor, orphan_id: int, **kwargs) -> RepairResult:
        """Delete an orphaned node."""
        # Check if node has children
        cursor.execute("SELECT COUNT(*) FROM nodes WHERE parent_id = ?", (orphan_id,))
        child_count = cursor.fetchone()[0]
        
        if child_count > 0:
            return RepairResult(
                success=False,
                action=RepairAction.DELETE_ORPHAN,
                orphan_id=orphan_id,
                message=f"Cannot delete orphan with {child_count} children",
                warnings=[f"Node has {child_count} children that would become orphaned"]
            )
        
        # Delete the orphan
        cursor.execute("DELETE FROM nodes WHERE id = ?", (orphan_id,))
        
        return RepairResult(
            success=True,
            action=RepairAction.DELETE_ORPHAN,
            orphan_id=orphan_id,
            message="Orphan node deleted successfully"
        )
    
    def _reassign_parent(self, cursor, orphan_id: int, new_parent_id: int, **kwargs) -> RepairResult:
        """Reassign orphan to a new parent."""
        # Validate new parent exists
        cursor.execute("SELECT id, depth FROM nodes WHERE id = ?", (new_parent_id,))
        parent_row = cursor.fetchone()
        
        if not parent_row:
            return RepairResult(
                success=False,
                action=RepairAction.REASSIGN_PARENT,
                orphan_id=orphan_id,
                message=f"New parent {new_parent_id} does not exist"
            )
        
        parent_id, parent_depth = parent_row
        
        # Check for circular reference
        if parent_id == orphan_id:
            return RepairResult(
                success=False,
                action=RepairAction.REASSIGN_PARENT,
                orphan_id=orphan_id,
                message="Cannot assign node as its own parent"
            )
        
        # Update parent and depth
        new_depth = parent_depth + 1
        cursor.execute("""
            UPDATE nodes 
            SET parent_id = ?, depth = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_parent_id, new_depth, orphan_id))
        
        return RepairResult(
            success=True,
            action=RepairAction.REASSIGN_PARENT,
            orphan_id=orphan_id,
            message=f"Orphan reassigned to parent {new_parent_id}"
        )
    
    def _fix_depth(self, cursor, orphan_id: int, **kwargs) -> RepairResult:
        """Fix depth of orphan node."""
        # Get parent depth
        cursor.execute("""
            SELECT p.depth FROM nodes n
            JOIN nodes p ON p.id = n.parent_id
            WHERE n.id = ?
        """, (orphan_id,))
        
        parent_row = cursor.fetchone()
        if not parent_row:
            return RepairResult(
                success=False,
                action=RepairAction.FIX_DEPTH,
                orphan_id=orphan_id,
                message="Parent not found for depth fix"
            )
        
        parent_depth = parent_row[0]
        correct_depth = parent_depth + 1
        
        # Update depth
        cursor.execute("""
            UPDATE nodes 
            SET depth = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (correct_depth, orphan_id))
        
        return RepairResult(
            success=True,
            action=RepairAction.FIX_DEPTH,
            orphan_id=orphan_id,
            message=f"Depth fixed to {correct_depth}"
        )
    
    def _fix_slot(self, cursor, orphan_id: int, new_slot: Optional[int] = None, **kwargs) -> RepairResult:
        """Fix slot of orphan node."""
        # Get parent
        cursor.execute("SELECT parent_id FROM nodes WHERE id = ?", (orphan_id,))
        parent_row = cursor.fetchone()
        
        if not parent_row:
            return RepairResult(
                success=False,
                action=RepairAction.FIX_SLOT,
                orphan_id=orphan_id,
                message="Parent not found for slot fix"
            )
        
        parent_id = parent_row[0]
        
        # Find available slot
        if new_slot is None:
            cursor.execute("""
                SELECT slot FROM nodes 
                WHERE parent_id = ? AND slot IS NOT NULL
                ORDER BY slot
            """, (parent_id,))
            
            used_slots = {row[0] for row in cursor.fetchall()}
            available_slots = set(range(1, 6)) - used_slots
            
            if not available_slots:
                return RepairResult(
                    success=False,
                    action=RepairAction.FIX_SLOT,
                    orphan_id=orphan_id,
                    message="No available slots for parent"
                )
            
            new_slot = min(available_slots)
        
        # Validate slot
        if new_slot < 1 or new_slot > 5:
            return RepairResult(
                success=False,
                action=RepairAction.FIX_SLOT,
                orphan_id=orphan_id,
                message="Invalid slot number (must be 1-5)"
            )
        
        # Update slot
        cursor.execute("""
            UPDATE nodes 
            SET slot = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_slot, orphan_id))
        
        return RepairResult(
            success=True,
            action=RepairAction.FIX_SLOT,
            orphan_id=orphan_id,
            message=f"Slot fixed to {new_slot}"
        )
    
    def _convert_to_root(self, cursor, orphan_id: int, **kwargs) -> RepairResult:
        """Convert orphan to root node."""
        # Check if there's already a root at this depth
        cursor.execute("SELECT depth FROM nodes WHERE id = ?", (orphan_id,))
        depth_row = cursor.fetchone()
        
        if not depth_row:
            return RepairResult(
                success=False,
                action=RepairAction.CONVERT_TO_ROOT,
                orphan_id=orphan_id,
                message="Node not found"
            )
        
        current_depth = depth_row[0]
        
        # Convert to root
        cursor.execute("""
            UPDATE nodes 
            SET parent_id = NULL, depth = 0, slot = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (orphan_id,))
        
        return RepairResult(
            success=True,
            action=RepairAction.CONVERT_TO_ROOT,
            orphan_id=orphan_id,
            message="Orphan converted to root node"
        )
    
    def _merge_with_sibling(self, cursor, orphan_id: int, sibling_id: int, **kwargs) -> RepairResult:
        """Merge orphan with a sibling node."""
        # Get both nodes
        cursor.execute("""
            SELECT id, label, parent_id, slot FROM nodes 
            WHERE id IN (?, ?)
        """, (orphan_id, sibling_id))
        
        nodes = cursor.fetchall()
        if len(nodes) != 2:
            return RepairResult(
                success=False,
                action=RepairAction.MERGE_WITH_SIBLING,
                orphan_id=orphan_id,
                message="One or both nodes not found"
            )
        
        # Find the sibling
        sibling = None
        orphan = None
        for node in nodes:
            if node[0] == sibling_id:
                sibling = node
            elif node[0] == orphan_id:
                orphan = node
        
        if not sibling or not orphan:
            return RepairResult(
                success=False,
                action=RepairAction.MERGE_WITH_SIBLING,
                orphan_id=orphan_id,
                message="Could not identify sibling and orphan nodes"
            )
        
        # Check if they have the same parent
        if sibling[2] != orphan[2]:
            return RepairResult(
                success=False,
                action=RepairAction.MERGE_WITH_SIBLING,
                orphan_id=orphan_id,
                message="Nodes do not have the same parent"
            )
        
        # Merge labels (combine them)
        combined_label = f"{sibling[1]} / {orphan[1]}"
        
        # Update sibling with combined label
        cursor.execute("""
            UPDATE nodes 
            SET label = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (combined_label, sibling_id))
        
        # Delete orphan
        cursor.execute("DELETE FROM nodes WHERE id = ?", (orphan_id,))
        
        return RepairResult(
            success=True,
            action=RepairAction.MERGE_WITH_SIBLING,
            orphan_id=orphan_id,
            message=f"Orphan merged with sibling {sibling_id}"
        )
    
    def _log_repair_action(
        self,
        cursor,
        orphan_id: int,
        action: RepairAction,
        actor: str,
        before_state: Dict[str, Any],
        after_state: Optional[Dict[str, Any]],
        message: str,
        warnings: List[str]
    ):
        """Log repair action to audit table."""
        cursor.execute("""
            INSERT INTO orphan_repair_audit 
            (orphan_id, action, actor, before_state, after_state, success, message, warnings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            orphan_id,
            action.value,
            actor,
            str(before_state),
            str(after_state) if after_state else None,
            True,
            message,
            str(warnings) if warnings else None
        ))
    
    def get_repair_history(
        self,
        orphan_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get repair history."""
        cursor = self.conn.cursor()
        
        query = """
            SELECT id, orphan_id, action, actor, timestamp, before_state, 
                   after_state, success, message, warnings
            FROM orphan_repair_audit
        """
        params = []
        
        if orphan_id:
            query += " WHERE orphan_id = ?"
            params.append(orphan_id)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            history.append({
                "id": row[0],
                "orphan_id": row[1],
                "action": row[2],
                "actor": row[3],
                "timestamp": row[4],
                "before_state": row[5],
                "after_state": row[6],
                "success": bool(row[7]),
                "message": row[8],
                "warnings": row[9]
            })
        
        return history
