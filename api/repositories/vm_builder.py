"""
VM Builder functionality for safe authoring with diff preview.

Provides draft management, diff calculation, and publish capabilities
for the Vital Measurement Builder.
"""

import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class VMOperationType(Enum):
    """VM Builder operation types."""
    CREATE = "create"
    MOVE = "move"
    DELETE = "delete"
    UPDATE = "update"

class VMBuilderManager:
    """Manages VM Builder drafts, diffs, and publishing."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._ensure_vm_drafts_table()
    
    def _ensure_vm_drafts_table(self):
        """Ensure vm_drafts table exists."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vm_drafts (
                id TEXT PRIMARY KEY,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                parent_id INTEGER,
                draft_data TEXT,
                status TEXT DEFAULT 'draft',
                published_at DATETIME,
                published_by TEXT
            )
        """)
        self.conn.commit()
    
    def create_draft(
        self,
        parent_id: int,
        draft_data: Dict[str, Any],
        actor: str = "system"
    ) -> str:
        """
        Create a new VM Builder draft.
        
        Args:
            parent_id: Parent node ID for the draft
            draft_data: Draft configuration data
            actor: Who created the draft
            
        Returns:
            Draft ID
        """
        draft_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO vm_drafts (id, parent_id, draft_data, status)
            VALUES (?, ?, ?, ?)
        """, (
            draft_id,
            parent_id,
            json.dumps(draft_data),
            'draft'
        ))
        
        self.conn.commit()
        
        logger.info(f"VM draft created: {draft_id} for parent {parent_id} by {actor}")
        return draft_id
    
    def get_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a VM Builder draft.
        
        Args:
            draft_id: Draft ID
            
        Returns:
            Draft data or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, created_at, updated_at, parent_id, draft_data, status, published_at, published_by
            FROM vm_drafts
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
            "published_by": row[7]
        }
    
    def update_draft(
        self,
        draft_id: str,
        draft_data: Dict[str, Any],
        actor: str = "system"
    ) -> bool:
        """
        Update a VM Builder draft.
        
        Args:
            draft_id: Draft ID
            draft_data: Updated draft data
            actor: Who updated the draft
            
        Returns:
            True if successful
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            UPDATE vm_drafts
            SET draft_data = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'draft'
        """, (json.dumps(draft_data), draft_id))
        
        if cursor.rowcount == 0:
            return False
        
        self.conn.commit()
        
        logger.info(f"VM draft updated: {draft_id} by {actor}")
        return True
    
    def delete_draft(self, draft_id: str) -> bool:
        """
        Delete a VM Builder draft.
        
        Args:
            draft_id: Draft ID
            
        Returns:
            True if successful
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            DELETE FROM vm_drafts
            WHERE id = ? AND status = 'draft'
        """, (draft_id,))
        
        if cursor.rowcount == 0:
            return False
        
        self.conn.commit()
        
        logger.info(f"VM draft deleted: {draft_id}")
        return True
    
    def list_drafts(self, parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List VM Builder drafts.
        
        Args:
            parent_id: Filter by parent ID (optional)
            
        Returns:
            List of draft summaries
        """
        cursor = self.conn.cursor()
        
        if parent_id:
            cursor.execute("""
                SELECT id, created_at, updated_at, parent_id, status
                FROM vm_drafts
                WHERE parent_id = ?
                ORDER BY updated_at DESC
            """, (parent_id,))
        else:
            cursor.execute("""
                SELECT id, created_at, updated_at, parent_id, status
                FROM vm_drafts
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
    
    def calculate_diff(self, draft_id: str) -> Dict[str, Any]:
        """
        Calculate diff for a VM Builder draft.
        
        Args:
            draft_id: Draft ID
            
        Returns:
            Diff data with operations
        """
        draft = self.get_draft(draft_id)
        if not draft:
            raise ValueError(f"Draft {draft_id} not found")
        
        if draft["status"] != "draft":
            raise ValueError(f"Draft {draft_id} is not in draft status")
        
        parent_id = draft["parent_id"]
        draft_data = draft["draft_data"]
        
        # Get current state
        current_children = self._get_current_children(parent_id)
        
        # Get target state from draft
        target_children = draft_data.get("children", [])
        
        # Calculate operations
        operations = self._calculate_operations(current_children, target_children)
        
        return {
            "draft_id": draft_id,
            "parent_id": parent_id,
            "operations": operations,
            "summary": self._summarize_operations(operations),
            "current_state": current_children,
            "target_state": target_children
        }
    
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
    
    def _calculate_operations(
        self,
        current: List[Dict[str, Any]],
        target: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calculate operations needed to transform current to target state."""
        operations = []
        
        # Create maps for easier lookup
        current_by_id = {child["id"]: child for child in current}
        target_by_id = {child["id"]: child for child in target}
        
        # Find deletions (in current but not in target)
        for child in current:
            if child["id"] not in target_by_id:
                operations.append({
                    "type": VMOperationType.DELETE.value,
                    "node_id": child["id"],
                    "label": child["label"],
                    "slot": child["slot"]
                })
        
        # Find updates and moves (in both but different)
        for child in target:
            if child["id"] in current_by_id:
                current_child = current_by_id[child["id"]]
                if (current_child["label"] != child["label"] or 
                    current_child["slot"] != child["slot"] or
                    current_child["is_leaf"] != child["is_leaf"]):
                    operations.append({
                        "type": VMOperationType.UPDATE.value,
                        "node_id": child["id"],
                        "old_label": current_child["label"],
                        "new_label": child["label"],
                        "old_slot": current_child["slot"],
                        "new_slot": child["slot"],
                        "old_is_leaf": current_child["is_leaf"],
                        "new_is_leaf": child["is_leaf"]
                    })
        
        # Find creations (in target but not in current)
        for child in target:
            if child["id"] not in current_by_id:
                operations.append({
                    "type": VMOperationType.CREATE.value,
                    "node_id": child["id"],
                    "label": child["label"],
                    "slot": child["slot"],
                    "is_leaf": child["is_leaf"],
                    "depth": child["depth"]
                })
        
        return operations
    
    def _summarize_operations(self, operations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Summarize operations by type."""
        summary = {
            "create": 0,
            "update": 0,
            "delete": 0,
            "move": 0,
            "total": len(operations)
        }
        
        for op in operations:
            op_type = op["type"]
            if op_type in summary:
                summary[op_type] += 1
        
        return summary
    
    def publish_draft(
        self,
        draft_id: str,
        actor: str = "system"
    ) -> Dict[str, Any]:
        """
        Publish a VM Builder draft.
        
        Args:
            draft_id: Draft ID
            actor: Who is publishing the draft
            
        Returns:
            Publish result with audit information
        """
        draft = self.get_draft(draft_id)
        if not draft:
            raise ValueError(f"Draft {draft_id} not found")
        
        if draft["status"] != "draft":
            raise ValueError(f"Draft {draft_id} is not in draft status")
        
        # Calculate diff
        diff = self.calculate_diff(draft_id)
        operations = diff["operations"]
        
        if not operations:
            # No changes to apply
            return {
                "success": True,
                "message": "No changes to apply",
                "draft_id": draft_id,
                "operations_applied": 0
            }
        
        # Apply operations transactionally
        try:
            self.conn.execute("BEGIN TRANSACTION")
            
            # Apply each operation
            for operation in operations:
                self._apply_operation(operation, draft["parent_id"])
            
            # Mark draft as published
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE vm_drafts
                SET status = 'published', published_at = CURRENT_TIMESTAMP, published_by = ?
                WHERE id = ?
            """, (actor, draft_id))
            
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
                    "operations": operations,
                    "summary": diff["summary"]
                },
                is_undoable=False  # VM Builder operations are not undoable
            )
            
            logger.info(f"VM draft published: {draft_id} by {actor}")
            
            return {
                "success": True,
                "message": f"Successfully published {len(operations)} operations",
                "draft_id": draft_id,
                "operations_applied": len(operations),
                "audit_id": audit_id,
                "summary": diff["summary"]
            }
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error publishing draft {draft_id}: {e}")
            raise
    
    def _apply_operation(self, operation: Dict[str, Any], parent_id: int):
        """Apply a single operation to the database."""
        cursor = self.conn.cursor()
        op_type = operation["type"]
        
        if op_type == VMOperationType.CREATE.value:
            cursor.execute("""
                INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                operation["node_id"],
                parent_id,
                operation["label"],
                operation["slot"],
                operation["is_leaf"],
                operation["depth"]
            ))
        
        elif op_type == VMOperationType.UPDATE.value:
            cursor.execute("""
                UPDATE nodes
                SET label = ?, slot = ?, is_leaf = ?
                WHERE id = ?
            """, (
                operation["new_label"],
                operation["new_slot"],
                operation["new_is_leaf"],
                operation["node_id"]
            ))
        
        elif op_type == VMOperationType.DELETE.value:
            cursor.execute("DELETE FROM nodes WHERE id = ?", (operation["node_id"],))
    
    def get_draft_stats(self) -> Dict[str, Any]:
        """Get VM Builder draft statistics."""
        cursor = self.conn.cursor()
        
        # Total drafts
        cursor.execute("SELECT COUNT(*) FROM vm_drafts")
        total_drafts = cursor.fetchone()[0]
        
        # Drafts by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM vm_drafts
            GROUP BY status
        """)
        status_counts = dict(cursor.fetchall())
        
        # Recent drafts
        cursor.execute("""
            SELECT COUNT(*) FROM vm_drafts
            WHERE created_at > datetime('now', '-7 days')
        """)
        recent_drafts = cursor.fetchone()[0]
        
        return {
            "total_drafts": total_drafts,
            "status_counts": status_counts,
            "recent_drafts": recent_drafts
        }
