"""
Audit log functionality for tracking high-impact operations.

Provides audit logging, undo capabilities, and audit trail management
for safety and recoverability.
"""

import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class AuditOperation(Enum):
    """Audit operation types."""
    CONFLICT_RESOLVE = "conflict_resolve"
    APPLY_DEFAULT = "apply_default"
    DELETE_SUBTREE = "delete_subtree"
    DATA_QUALITY_REPAIR = "data_quality_repair"
    CHILDREN_UPDATE = "children_update"
    OUTCOME_UPDATE = "outcome_update"

class AuditManager:
    """Manages audit logging and undo operations."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._ensure_audit_table()
    
    def _ensure_audit_table(self):
        """Ensure audit_log table exists."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                actor TEXT,
                operation TEXT NOT NULL,
                target_id INTEGER,
                payload_json TEXT,
                undo_data_json TEXT,
                is_undoable BOOLEAN DEFAULT 0,
                undone_by INTEGER,
                undone_at DATETIME
            )
        """)
        self.conn.commit()
    
    def log_operation(
        self,
        operation: AuditOperation,
        target_id: int,
        actor: str = "system",
        payload: Dict[str, Any] = None,
        undo_data: Dict[str, Any] = None,
        is_undoable: bool = False
    ) -> int:
        """
        Log an audit operation.
        
        Args:
            operation: Type of operation
            target_id: Target node/entity ID
            actor: Who performed the operation
            payload: Operation payload data
            undo_data: Data needed for undo (before state)
            is_undoable: Whether this operation can be undone
            
        Returns:
            Audit log entry ID
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_log (actor, operation, target_id, payload_json, undo_data_json, is_undoable)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            actor,
            operation.value,
            target_id,
            json.dumps(payload) if payload else None,
            json.dumps(undo_data) if undo_data else None,
            is_undoable
        ))
        
        audit_id = cursor.lastrowid
        self.conn.commit()
        
        logger.info(f"Audit logged: {operation.value} on {target_id} by {actor} (ID: {audit_id})")
        return audit_id
    
    def log_apply_default(
        self,
        parent_id: int,
        before_children: List[Dict[str, Any]],
        after_children: List[Dict[str, Any]],
        actor: str = "system"
    ) -> int:
        """
        Log an apply-default operation with undo data.
        
        Args:
            parent_id: Parent node ID
            before_children: Children before apply-default
            after_children: Children after apply-default
            actor: Who performed the operation
            
        Returns:
            Audit log entry ID
        """
        payload = {
            "parent_id": parent_id,
            "children_count": len(after_children),
            "operation": "apply_default"
        }
        
        undo_data = {
            "parent_id": parent_id,
            "before_children": before_children,
            "after_children": after_children,
            "operation": "apply_default"
        }
        
        return self.log_operation(
            operation=AuditOperation.APPLY_DEFAULT,
            target_id=parent_id,
            actor=actor,
            payload=payload,
            undo_data=undo_data,
            is_undoable=True
        )
    
    def log_conflict_resolve(
        self,
        conflict_id: int,
        resolution_data: Dict[str, Any],
        actor: str = "system"
    ) -> int:
        """
        Log a conflict resolution operation.
        
        Args:
            conflict_id: Conflict ID
            resolution_data: How the conflict was resolved
            actor: Who performed the operation
            
        Returns:
            Audit log entry ID
        """
        payload = {
            "conflict_id": conflict_id,
            "resolution": resolution_data,
            "operation": "conflict_resolve"
        }
        
        return self.log_operation(
            operation=AuditOperation.CONFLICT_RESOLVE,
            target_id=conflict_id,
            actor=actor,
            payload=payload,
            is_undoable=False
        )
    
    def log_delete_subtree(
        self,
        root_id: int,
        deleted_nodes: List[Dict[str, Any]],
        actor: str = "system"
    ) -> int:
        """
        Log a delete subtree operation.
        
        Args:
            root_id: Root node ID of deleted subtree
            deleted_nodes: List of deleted nodes
            actor: Who performed the operation
            
        Returns:
            Audit log entry ID
        """
        payload = {
            "root_id": root_id,
            "deleted_count": len(deleted_nodes),
            "deleted_nodes": deleted_nodes,
            "operation": "delete_subtree"
        }
        
        return self.log_operation(
            operation=AuditOperation.DELETE_SUBTREE,
            target_id=root_id,
            actor=actor,
            payload=payload,
            is_undoable=False  # Delete operations are not undoable
        )
    
    def log_data_quality_repair(
        self,
        repair_type: str,
        affected_nodes: List[int],
        repair_data: Dict[str, Any],
        actor: str = "system"
    ) -> int:
        """
        Log a data quality repair operation.
        
        Args:
            repair_type: Type of repair performed
            affected_nodes: List of affected node IDs
            repair_data: Repair details
            actor: Who performed the operation
            
        Returns:
            Audit log entry ID
        """
        payload = {
            "repair_type": repair_type,
            "affected_count": len(affected_nodes),
            "affected_nodes": affected_nodes,
            "repair_data": repair_data,
            "operation": "data_quality_repair"
        }
        
        return self.log_operation(
            operation=AuditOperation.DATA_QUALITY_REPAIR,
            target_id=affected_nodes[0] if affected_nodes else 0,
            actor=actor,
            payload=payload,
            is_undoable=False
        )
    
    def get_audit_entries(
        self,
        limit: int = 50,
        after_id: Optional[int] = None,
        operation_filter: Optional[AuditOperation] = None
    ) -> List[Dict[str, Any]]:
        """
        Get audit log entries with pagination.
        
        Args:
            limit: Maximum number of entries to return
            after_id: Return entries after this ID
            operation_filter: Filter by operation type
            
        Returns:
            List of audit log entries
        """
        cursor = self.conn.cursor()
        
        query = """
            SELECT id, timestamp, actor, operation, target_id, payload_json, 
                   undo_data_json, is_undoable, undone_by, undone_at
            FROM audit_log
        """
        params = []
        
        conditions = []
        if after_id:
            conditions.append("id > ?")
            params.append(after_id)
        
        if operation_filter:
            conditions.append("operation = ?")
            params.append(operation_filter.value)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        entries = []
        for row in rows:
            entry = {
                "id": row[0],
                "timestamp": row[1],
                "actor": row[2],
                "operation": row[3],
                "target_id": row[4],
                "payload": json.loads(row[5]) if row[5] else None,
                "undo_data": json.loads(row[6]) if row[6] else None,
                "is_undoable": bool(row[7]),
                "undone_by": row[8],
                "undone_at": row[9]
            }
            entries.append(entry)
        
        return entries
    
    def get_undoable_entries(self) -> List[Dict[str, Any]]:
        """Get all undoable audit entries."""
        return self.get_audit_entries(
            limit=1000,
            operation_filter=AuditOperation.APPLY_DEFAULT
        )
    
    def undo_operation(self, audit_id: int, actor: str = "system") -> bool:
        """
        Undo an operation if possible.
        
        Args:
            audit_id: Audit log entry ID to undo
            actor: Who is performing the undo
            
        Returns:
            True if undo was successful, False otherwise
        """
        cursor = self.conn.cursor()
        
        # Get the audit entry
        cursor.execute("""
            SELECT operation, target_id, undo_data_json, is_undoable, undone_by
            FROM audit_log
            WHERE id = ?
        """, (audit_id,))
        
        row = cursor.fetchone()
        if not row:
            return False
        
        operation, target_id, undo_data_json, is_undoable, undone_by = row
        
        # Check if already undone
        if undone_by:
            return False
        
        # Check if undoable
        if not is_undoable:
            return False
        
        # Only apply-default operations are undoable in this implementation
        if operation != AuditOperation.APPLY_DEFAULT.value:
            return False
        
        try:
            # Parse undo data
            undo_data = json.loads(undo_data_json) if undo_data_json else None
            if not undo_data:
                return False
            
            # Perform the undo operation
            success = self._undo_apply_default(target_id, undo_data)
            
            if success:
                # Mark as undone
                cursor.execute("""
                    UPDATE audit_log
                    SET undone_by = ?, undone_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (audit_id, audit_id))  # Self-reference for undo tracking
                
                self.conn.commit()
                logger.info(f"Undo successful for audit entry {audit_id}")
                return True
            
        except Exception as e:
            logger.error(f"Error undoing operation {audit_id}: {e}")
        
        return False
    
    def _undo_apply_default(self, parent_id: int, undo_data: Dict[str, Any]) -> bool:
        """
        Undo an apply-default operation.
        
        Args:
            parent_id: Parent node ID
            undo_data: Undo data containing before state
            
        Returns:
            True if successful
        """
        try:
            cursor = self.conn.cursor()
            
            # Get current children
            cursor.execute("""
                SELECT id, label, slot, is_leaf
                FROM nodes
                WHERE parent_id = ?
                ORDER BY slot
            """, (parent_id,))
            
            current_children = []
            for row in cursor.fetchall():
                current_children.append({
                    "id": row[0],
                    "label": row[1],
                    "slot": row[2],
                    "is_leaf": bool(row[3])
                })
            
            # Delete current children
            cursor.execute("DELETE FROM nodes WHERE parent_id = ?", (parent_id,))
            
            # Restore before state
            before_children = undo_data.get("before_children", [])
            for child in before_children:
                cursor.execute("""
                    INSERT INTO nodes (id, parent_id, label, slot, is_leaf, depth)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    child.get("id"),
                    parent_id,
                    child.get("label"),
                    child.get("slot"),
                    child.get("is_leaf", 0),
                    child.get("depth", 1)
                ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error undoing apply-default for parent {parent_id}: {e}")
            return False
    
    def get_audit_stats(self) -> Dict[str, Any]:
        """Get audit log statistics."""
        cursor = self.conn.cursor()
        
        # Total entries
        cursor.execute("SELECT COUNT(*) FROM audit_log")
        total_entries = cursor.fetchone()[0]
        
        # Undoable entries
        cursor.execute("SELECT COUNT(*) FROM audit_log WHERE is_undoable = 1 AND undone_by IS NULL")
        undoable_entries = cursor.fetchone()[0]
        
        # Undone entries
        cursor.execute("SELECT COUNT(*) FROM audit_log WHERE undone_by IS NOT NULL")
        undone_entries = cursor.fetchone()[0]
        
        # Operations breakdown
        cursor.execute("""
            SELECT operation, COUNT(*) as count
            FROM audit_log
            GROUP BY operation
            ORDER BY count DESC
        """)
        operations = dict(cursor.fetchall())
        
        return {
            "total_entries": total_entries,
            "undoable_entries": undoable_entries,
            "undone_entries": undone_entries,
            "operations": operations
        }
