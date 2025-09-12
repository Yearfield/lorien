"""
Enhanced audit system with expanded operation types and undo capabilities.

This module extends the existing audit system to support more operation types,
better undo capabilities, and enhanced audit trail management.
"""

import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, asdict
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class ExpandedAuditOperation(Enum):
    """Expanded audit operation types."""
    # Existing operations
    CONFLICT_RESOLVE = "conflict_resolve"
    APPLY_DEFAULT = "apply_default"
    DELETE_SUBTREE = "delete_subtree"
    DATA_QUALITY_REPAIR = "data_quality_repair"
    CHILDREN_UPDATE = "children_update"
    OUTCOME_UPDATE = "outcome_update"
    
    # New operations
    NODE_CREATE = "node_create"
    NODE_UPDATE = "node_update"
    NODE_DELETE = "node_delete"
    FLAG_ASSIGN = "flag_assign"
    FLAG_REMOVE = "flag_remove"
    BULK_FLAG_OPERATION = "bulk_flag_operation"
    IMPORT_OPERATION = "import_operation"
    EXPORT_OPERATION = "export_operation"
    BACKUP_OPERATION = "backup_operation"
    RESTORE_OPERATION = "restore_operation"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PERMISSION_CHANGE = "permission_change"
    ROLE_ASSIGNMENT = "role_assignment"
    DICTIONARY_UPDATE = "dictionary_update"
    VM_BUILDER_OPERATION = "vm_builder_operation"
    TRIAGE_UPDATE = "triage_update"
    BULK_OPERATION = "bulk_operation"

@dataclass
class AuditContext:
    """Context information for audit operations."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    parent_operation_id: Optional[int] = None

@dataclass
class UndoCapability:
    """Defines undo capability for an operation."""
    is_undoable: bool
    undo_timeout_seconds: Optional[int] = None  # None = no timeout
    requires_confirmation: bool = False
    undo_description: Optional[str] = None

class EnhancedAuditManager:
    """Enhanced audit manager with expanded capabilities."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._ensure_enhanced_audit_tables()
        self._operation_undo_capabilities = self._initialize_undo_capabilities()
    
    def _ensure_enhanced_audit_tables(self):
        """Ensure enhanced audit tables exist."""
        cursor = self.conn.cursor()
        
        # Enhanced audit_log table
        cursor.execute("""
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
        
        # Audit operation groups for batch operations
        cursor.execute("""
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
        
        # Audit tags for categorization
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                color TEXT DEFAULT '#007bff',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_enhanced_audit_timestamp 
            ON enhanced_audit_log(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_enhanced_audit_operation 
            ON enhanced_audit_log(operation)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_enhanced_audit_target 
            ON enhanced_audit_log(target_id, target_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_enhanced_audit_actor 
            ON enhanced_audit_log(actor)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_enhanced_audit_undoable 
            ON enhanced_audit_log(is_undoable, undone_by)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_enhanced_audit_group 
            ON enhanced_audit_log(operation_group_id)
        """)
        
        self.conn.commit()
    
    def _initialize_undo_capabilities(self) -> Dict[ExpandedAuditOperation, UndoCapability]:
        """Initialize undo capabilities for different operations."""
        return {
            # Existing undoable operations
            ExpandedAuditOperation.APPLY_DEFAULT: UndoCapability(
                is_undoable=True,
                undo_timeout_seconds=3600,  # 1 hour
                requires_confirmation=False,
                undo_description="Restore previous children configuration"
            ),
            
            # New undoable operations
            ExpandedAuditOperation.NODE_CREATE: UndoCapability(
                is_undoable=True,
                undo_timeout_seconds=1800,  # 30 minutes
                requires_confirmation=True,
                undo_description="Delete the created node"
            ),
            ExpandedAuditOperation.NODE_UPDATE: UndoCapability(
                is_undoable=True,
                undo_timeout_seconds=3600,  # 1 hour
                requires_confirmation=False,
                undo_description="Restore previous node state"
            ),
            ExpandedAuditOperation.FLAG_ASSIGN: UndoCapability(
                is_undoable=True,
                undo_timeout_seconds=1800,  # 30 minutes
                requires_confirmation=False,
                undo_description="Remove the assigned flag"
            ),
            ExpandedAuditOperation.FLAG_REMOVE: UndoCapability(
                is_undoable=True,
                undo_timeout_seconds=1800,  # 30 minutes
                requires_confirmation=False,
                undo_description="Reassign the removed flag"
            ),
            ExpandedAuditOperation.BULK_FLAG_OPERATION: UndoCapability(
                is_undoable=True,
                undo_timeout_seconds=3600,  # 1 hour
                requires_confirmation=True,
                undo_description="Reverse all flag operations in this batch"
            ),
            ExpandedAuditOperation.TRIAGE_UPDATE: UndoCapability(
                is_undoable=True,
                undo_timeout_seconds=1800,  # 30 minutes
                requires_confirmation=False,
                undo_description="Restore previous triage state"
            ),
            ExpandedAuditOperation.DICTIONARY_UPDATE: UndoCapability(
                is_undoable=True,
                undo_timeout_seconds=7200,  # 2 hours
                requires_confirmation=True,
                undo_description="Restore previous dictionary state"
            ),
            
            # Non-undoable operations
            ExpandedAuditOperation.DELETE_SUBTREE: UndoCapability(
                is_undoable=False,
                undo_description="Cannot undo subtree deletion"
            ),
            ExpandedAuditOperation.IMPORT_OPERATION: UndoCapability(
                is_undoable=False,
                undo_description="Cannot undo import operations"
            ),
            ExpandedAuditOperation.EXPORT_OPERATION: UndoCapability(
                is_undoable=False,
                undo_description="Cannot undo export operations"
            ),
            ExpandedAuditOperation.BACKUP_OPERATION: UndoCapability(
                is_undoable=False,
                undo_description="Cannot undo backup operations"
            ),
            ExpandedAuditOperation.RESTORE_OPERATION: UndoCapability(
                is_undoable=False,
                undo_description="Cannot undo restore operations"
            ),
            ExpandedAuditOperation.USER_LOGIN: UndoCapability(
                is_undoable=False,
                undo_description="Cannot undo login operations"
            ),
            ExpandedAuditOperation.USER_LOGOUT: UndoCapability(
                is_undoable=False,
                undo_description="Cannot undo logout operations"
            ),
            ExpandedAuditOperation.CONFLICT_RESOLVE: UndoCapability(
                is_undoable=False,
                undo_description="Cannot undo conflict resolution"
            ),
            ExpandedAuditOperation.DATA_QUALITY_REPAIR: UndoCapability(
                is_undoable=False,
                undo_description="Cannot undo data quality repairs"
            ),
        }
    
    def log_operation(
        self,
        operation: ExpandedAuditOperation,
        target_id: Optional[int] = None,
        target_type: Optional[str] = None,
        actor: str = "system",
        context: Optional[AuditContext] = None,
        payload: Optional[Dict[str, Any]] = None,
        undo_data: Optional[Dict[str, Any]] = None,
        operation_group_id: Optional[str] = None,
        severity: str = "info",
        tags: Optional[List[str]] = None
    ) -> int:
        """
        Log an enhanced audit operation.
        
        Args:
            operation: Type of operation
            target_id: Target entity ID
            target_type: Type of target entity
            actor: Who performed the operation
            context: Additional context information
            payload: Operation payload data
            undo_data: Data needed for undo (before state)
            operation_group_id: ID for grouping related operations
            severity: Operation severity (info, warning, error, critical)
            tags: List of tags for categorization
            
        Returns:
            Audit log entry ID
        """
        cursor = self.conn.cursor()
        
        # Get undo capability
        undo_capability = self._operation_undo_capabilities.get(operation, UndoCapability(is_undoable=False))
        
        # Check if operation is within undo timeout
        is_undoable = undo_capability.is_undoable
        if is_undoable and undo_capability.undo_timeout_seconds:
            # Operations with timeout are only undoable within the timeout period
            pass  # Will be checked at undo time
        
        cursor.execute("""
            INSERT INTO enhanced_audit_log (
                operation, target_id, target_type, actor, context_json, payload_json, 
                undo_data_json, is_undoable, undo_timeout_seconds, requires_confirmation,
                parent_operation_id, operation_group_id, severity, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            operation.value,
            target_id,
            target_type,
            actor,
            json.dumps(asdict(context)) if context else None,
            json.dumps(payload) if payload else None,
            json.dumps(undo_data) if undo_data else None,
            is_undoable,
            undo_capability.undo_timeout_seconds,
            undo_capability.requires_confirmation,
            context.parent_operation_id if context else None,
            operation_group_id,
            severity,
            json.dumps(tags) if tags else None
        ))
        
        audit_id = cursor.lastrowid
        self.conn.commit()
        
        logger.info(f"Enhanced audit logged: {operation.value} on {target_type}:{target_id} by {actor} (ID: {audit_id})")
        return audit_id
    
    def create_operation_group(
        self,
        group_id: str,
        name: str,
        description: Optional[str] = None,
        total_operations: int = 0
    ) -> bool:
        """Create an audit operation group for batch operations."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO audit_operation_groups (id, name, description, total_operations)
                VALUES (?, ?, ?, ?)
            """, (group_id, name, description, total_operations))
            
            self.conn.commit()
            logger.info(f"Created audit operation group: {group_id} - {name}")
            return True
            
        except sqlite3.IntegrityError:
            logger.warning(f"Audit operation group {group_id} already exists")
            return False
    
    def complete_operation_group(
        self,
        group_id: str,
        status: str = "completed"
    ) -> bool:
        """Mark an audit operation group as completed."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            UPDATE audit_operation_groups
            SET status = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, group_id))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_enhanced_audit_entries(
        self,
        limit: int = 50,
        after_id: Optional[int] = None,
        operation_filter: Optional[ExpandedAuditOperation] = None,
        actor_filter: Optional[str] = None,
        target_type_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
        tag_filter: Optional[str] = None,
        undoable_only: bool = False,
        group_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get enhanced audit log entries with advanced filtering."""
        cursor = self.conn.cursor()
        
        query = """
            SELECT id, timestamp, operation, target_id, target_type, actor, 
                   context_json, payload_json, undo_data_json, is_undoable, 
                   undo_timeout_seconds, requires_confirmation, undone_by, 
                   undone_at, undo_reason, parent_operation_id, operation_group_id, 
                   severity, tags
            FROM enhanced_audit_log
        """
        params = []
        conditions = []
        
        if after_id:
            conditions.append("id > ?")
            params.append(after_id)
        
        if operation_filter:
            conditions.append("operation = ?")
            params.append(operation_filter.value)
        
        if actor_filter:
            conditions.append("actor = ?")
            params.append(actor_filter)
        
        if target_type_filter:
            conditions.append("target_type = ?")
            params.append(target_type_filter)
        
        if severity_filter:
            conditions.append("severity = ?")
            params.append(severity_filter)
        
        if tag_filter:
            conditions.append("tags LIKE ?")
            params.append(f"%{tag_filter}%")
        
        if undoable_only:
            conditions.append("is_undoable = 1 AND undone_by IS NULL")
        
        if group_id:
            conditions.append("operation_group_id = ?")
            params.append(group_id)
        
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
                "operation": row[2],
                "target_id": row[3],
                "target_type": row[4],
                "actor": row[5],
                "context": json.loads(row[6]) if row[6] else None,
                "payload": json.loads(row[7]) if row[7] else None,
                "undo_data": json.loads(row[8]) if row[8] else None,
                "is_undoable": bool(row[9]),
                "undo_timeout_seconds": row[10],
                "requires_confirmation": bool(row[11]),
                "undone_by": row[12],
                "undone_at": row[13],
                "undo_reason": row[14],
                "parent_operation_id": row[15],
                "operation_group_id": row[16],
                "severity": row[17],
                "tags": json.loads(row[18]) if row[18] else None
            }
            entries.append(entry)
        
        return entries
    
    def get_undoable_entries(
        self,
        limit: int = 100,
        include_expired: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all undoable audit entries, optionally including expired ones."""
        cursor = self.conn.cursor()
        
        query = """
            SELECT id, timestamp, operation, target_id, target_type, actor,
                   undo_timeout_seconds, requires_confirmation, undone_by
            FROM enhanced_audit_log
            WHERE is_undoable = 1 AND undone_by IS NULL
        """
        params = []
        
        if not include_expired:
            # Only include entries within their undo timeout
            query += " AND (undo_timeout_seconds IS NULL OR (julianday('now') - julianday(timestamp)) * 86400 < undo_timeout_seconds)"
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        entries = []
        for row in rows:
            entry = {
                "id": row[0],
                "timestamp": row[1],
                "operation": row[2],
                "target_id": row[3],
                "target_type": row[4],
                "actor": row[5],
                "undo_timeout_seconds": row[6],
                "requires_confirmation": bool(row[7]),
                "undone_by": row[8]
            }
            entries.append(entry)
        
        return entries
    
    def undo_operation(
        self,
        audit_id: int,
        actor: str = "system",
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Undo an operation if possible.
        
        Returns:
            Dictionary with undo result information
        """
        cursor = self.conn.cursor()
        
        # Get the audit entry
        cursor.execute("""
            SELECT operation, target_id, target_type, undo_data_json, is_undoable, 
                   undo_timeout_seconds, requires_confirmation, undone_by, timestamp
            FROM enhanced_audit_log
            WHERE id = ?
        """, (audit_id,))
        
        row = cursor.fetchone()
        if not row:
            return {
                "success": False,
                "error": "audit_entry_not_found",
                "message": f"Audit entry {audit_id} not found"
            }
        
        operation, target_id, target_type, undo_data_json, is_undoable, \
        undo_timeout_seconds, requires_confirmation, undone_by, timestamp = row
        
        # Check if already undone
        if undone_by:
            return {
                "success": False,
                "error": "already_undone",
                "message": f"Operation was already undone at {undone_by}"
            }
        
        # Check if undoable
        if not is_undoable:
            return {
                "success": False,
                "error": "not_undoable",
                "message": f"Operation {operation} is not undoable"
            }
        
        # Check timeout
        if undo_timeout_seconds:
            # Parse timestamp and ensure it's timezone-aware
            if timestamp.endswith('Z'):
                timestamp = timestamp[:-1] + '+00:00'
            elif '+' not in timestamp and '-' not in timestamp[-6:]:
                # Assume UTC if no timezone info
                timestamp = timestamp + '+00:00'
            
            timestamp_dt = datetime.fromisoformat(timestamp)
            time_diff = (datetime.now(timezone.utc) - timestamp_dt).total_seconds()
            if time_diff > undo_timeout_seconds:
                return {
                    "success": False,
                    "error": "undo_timeout_expired",
                    "message": f"Undo timeout expired. Operation is {time_diff:.0f}s old, timeout is {undo_timeout_seconds}s"
                }
        
        try:
            # Parse undo data
            undo_data = json.loads(undo_data_json) if undo_data_json else None
            if not undo_data:
                return {
                    "success": False,
                    "error": "no_undo_data",
                    "message": "No undo data available for this operation"
                }
            
            # Perform the undo operation
            undo_result = self._perform_undo(operation, target_id, target_type, undo_data)
            
            if undo_result["success"]:
                # Mark as undone
                cursor.execute("""
                    UPDATE enhanced_audit_log
                    SET undone_by = ?, undone_at = CURRENT_TIMESTAMP, undo_reason = ?
                    WHERE id = ?
                """, (audit_id, reason, audit_id))
                
                self.conn.commit()
                logger.info(f"Undo successful for audit entry {audit_id}")
                
                return {
                    "success": True,
                    "message": f"Operation {audit_id} successfully undone",
                    "audit_id": audit_id,
                    "actor": actor,
                    "undone_at": datetime.now(timezone.utc).isoformat(),
                    "undo_result": undo_result
                }
            else:
                return {
                    "success": False,
                    "error": "undo_failed",
                    "message": undo_result.get("message", "Failed to undo operation"),
                    "undo_result": undo_result
                }
            
        except Exception as e:
            logger.error(f"Error undoing operation {audit_id}: {e}")
            return {
                "success": False,
                "error": "undo_exception",
                "message": str(e)
            }
    
    def _perform_undo(
        self,
        operation: str,
        target_id: int,
        target_type: str,
        undo_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform the actual undo operation based on operation type."""
        try:
            if operation == ExpandedAuditOperation.APPLY_DEFAULT.value:
                return self._undo_apply_default(target_id, undo_data)
            elif operation == ExpandedAuditOperation.NODE_CREATE.value:
                return self._undo_node_create(target_id, undo_data)
            elif operation == ExpandedAuditOperation.NODE_UPDATE.value:
                return self._undo_node_update(target_id, undo_data)
            elif operation == ExpandedAuditOperation.FLAG_ASSIGN.value:
                return self._undo_flag_assign(target_id, undo_data)
            elif operation == ExpandedAuditOperation.FLAG_REMOVE.value:
                return self._undo_flag_remove(target_id, undo_data)
            elif operation == ExpandedAuditOperation.BULK_FLAG_OPERATION.value:
                return self._undo_bulk_flag_operation(target_id, undo_data)
            elif operation == ExpandedAuditOperation.TRIAGE_UPDATE.value:
                return self._undo_triage_update(target_id, undo_data)
            elif operation == ExpandedAuditOperation.DICTIONARY_UPDATE.value:
                return self._undo_dictionary_update(target_id, undo_data)
            else:
                return {
                    "success": False,
                    "message": f"Undo not implemented for operation {operation}"
                }
        except Exception as e:
            logger.error(f"Error performing undo for {operation}: {e}")
            return {
                "success": False,
                "message": f"Undo failed: {str(e)}"
            }
    
    def _undo_apply_default(self, parent_id: int, undo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Undo an apply-default operation."""
        # Implementation similar to existing _undo_apply_default
        # but with enhanced error handling and logging
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
            return {"success": True, "message": "Apply-default operation undone"}
            
        except Exception as e:
            logger.error(f"Error undoing apply-default for parent {parent_id}: {e}")
            return {"success": False, "message": str(e)}
    
    def _undo_node_create(self, node_id: int, undo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Undo a node creation operation."""
        try:
            cursor = self.conn.cursor()
            
            # Delete the created node
            cursor.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
            
            if cursor.rowcount > 0:
                self.conn.commit()
                return {"success": True, "message": "Node creation undone"}
            else:
                return {"success": False, "message": "Node not found"}
                
        except Exception as e:
            logger.error(f"Error undoing node creation for {node_id}: {e}")
            return {"success": False, "message": str(e)}
    
    def _undo_node_update(self, node_id: int, undo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Undo a node update operation."""
        try:
            cursor = self.conn.cursor()
            
            # Restore previous state
            before_state = undo_data.get("before_state", {})
            if before_state:
                cursor.execute("""
                    UPDATE nodes 
                    SET label = ?, slot = ?, is_leaf = ?, depth = ?
                    WHERE id = ?
                """, (
                    before_state.get("label"),
                    before_state.get("slot"),
                    before_state.get("is_leaf"),
                    before_state.get("depth"),
                    node_id
                ))
                
                self.conn.commit()
                return {"success": True, "message": "Node update undone"}
            else:
                return {"success": False, "message": "No before state available"}
                
        except Exception as e:
            logger.error(f"Error undoing node update for {node_id}: {e}")
            return {"success": False, "message": str(e)}
    
    def _undo_flag_assign(self, node_id: int, undo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Undo a flag assignment operation."""
        try:
            cursor = self.conn.cursor()
            
            flag_id = undo_data.get("flag_id")
            if flag_id:
                cursor.execute("""
                    DELETE FROM node_flags 
                    WHERE node_id = ? AND flag_id = ?
                """, (node_id, flag_id))
                
                self.conn.commit()
                return {"success": True, "message": "Flag assignment undone"}
            else:
                return {"success": False, "message": "No flag ID in undo data"}
                
        except Exception as e:
            logger.error(f"Error undoing flag assignment for node {node_id}: {e}")
            return {"success": False, "message": str(e)}
    
    def _undo_flag_remove(self, node_id: int, undo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Undo a flag removal operation."""
        try:
            cursor = self.conn.cursor()
            
            flag_id = undo_data.get("flag_id")
            if flag_id:
                cursor.execute("""
                    INSERT INTO node_flags (node_id, flag_id, created_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (node_id, flag_id))
                
                self.conn.commit()
                return {"success": True, "message": "Flag removal undone"}
            else:
                return {"success": False, "message": "No flag ID in undo data"}
                
        except Exception as e:
            logger.error(f"Error undoing flag removal for node {node_id}: {e}")
            return {"success": False, "message": str(e)}
    
    def _undo_bulk_flag_operation(self, operation_id: int, undo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Undo a bulk flag operation."""
        try:
            cursor = self.conn.cursor()
            
            # Get all operations in this bulk operation
            operations = undo_data.get("operations", [])
            success_count = 0
            
            for op in operations:
                try:
                    if op.get("action") == "assign":
                        # Undo assignment (remove the flag)
                        cursor.execute("""
                            DELETE FROM node_flags 
                            WHERE node_id = ? AND flag_id = ?
                        """, (op.get("node_id"), op.get("flag_id")))
                    elif op.get("action") == "remove":
                        # Undo removal (add the flag back, but only if it doesn't exist)
                        cursor.execute("""
                            INSERT OR IGNORE INTO node_flags (node_id, flag_id, created_at)
                            VALUES (?, ?, CURRENT_TIMESTAMP)
                        """, (op.get("node_id"), op.get("flag_id")))
                    
                    if cursor.rowcount > 0:
                        success_count += 1
                except sqlite3.IntegrityError:
                    # Skip operations that can't be undone due to constraints
                    continue
            
            self.conn.commit()
            return {
                "success": True, 
                "message": f"Bulk flag operation undone: {success_count}/{len(operations)} operations"
            }
                
        except Exception as e:
            logger.error(f"Error undoing bulk flag operation {operation_id}: {e}")
            return {"success": False, "message": str(e)}
    
    def _undo_triage_update(self, node_id: int, undo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Undo a triage update operation."""
        try:
            cursor = self.conn.cursor()
            
            # Restore previous triage state
            before_triage = undo_data.get("before_triage", {})
            if before_triage:
                cursor.execute("""
                    UPDATE nodes 
                    SET triage = ?, triage_updated_at = ?
                    WHERE id = ?
                """, (
                    before_triage.get("triage"),
                    before_triage.get("triage_updated_at"),
                    node_id
                ))
                
                self.conn.commit()
                return {"success": True, "message": "Triage update undone"}
            else:
                return {"success": False, "message": "No before triage state available"}
                
        except Exception as e:
            logger.error(f"Error undoing triage update for node {node_id}: {e}")
            return {"success": False, "message": str(e)}
    
    def _undo_dictionary_update(self, dictionary_id: int, undo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Undo a dictionary update operation."""
        try:
            cursor = self.conn.cursor()
            
            # Restore previous dictionary state
            before_state = undo_data.get("before_state", {})
            if before_state:
                cursor.execute("""
                    UPDATE dictionary 
                    SET term = ?, definition = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    before_state.get("term"),
                    before_state.get("definition"),
                    before_state.get("updated_at"),
                    dictionary_id
                ))
                
                self.conn.commit()
                return {"success": True, "message": "Dictionary update undone"}
            else:
                return {"success": False, "message": "No before dictionary state available"}
                
        except Exception as e:
            logger.error(f"Error undoing dictionary update for {dictionary_id}: {e}")
            return {"success": False, "message": str(e)}
    
    def get_enhanced_audit_stats(self) -> Dict[str, Any]:
        """Get enhanced audit log statistics."""
        cursor = self.conn.cursor()
        
        # Total entries
        cursor.execute("SELECT COUNT(*) FROM enhanced_audit_log")
        total_entries = cursor.fetchone()[0]
        
        # Undoable entries
        cursor.execute("SELECT COUNT(*) FROM enhanced_audit_log WHERE is_undoable = 1 AND undone_by IS NULL")
        undoable_entries = cursor.fetchone()[0]
        
        # Undone entries
        cursor.execute("SELECT COUNT(*) FROM enhanced_audit_log WHERE undone_by IS NOT NULL")
        undone_entries = cursor.fetchone()[0]
        
        # Operations breakdown
        cursor.execute("""
            SELECT operation, COUNT(*) as count
            FROM enhanced_audit_log
            GROUP BY operation
            ORDER BY count DESC
        """)
        operations = dict(cursor.fetchall())
        
        # Severity breakdown
        cursor.execute("""
            SELECT severity, COUNT(*) as count
            FROM enhanced_audit_log
            GROUP BY severity
            ORDER BY count DESC
        """)
        severities = dict(cursor.fetchall())
        
        # Recent activity (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) FROM enhanced_audit_log
            WHERE timestamp > datetime('now', '-1 day')
        """)
        recent_activity = cursor.fetchone()[0]
        
        return {
            "total_entries": total_entries,
            "undoable_entries": undoable_entries,
            "undone_entries": undone_entries,
            "operations": operations,
            "severities": severities,
            "recent_activity_24h": recent_activity,
            "undo_rate": (undone_entries / total_entries * 100) if total_entries > 0 else 0
        }
    
    @contextmanager
    def operation_group(self, group_id: str, name: str, description: Optional[str] = None):
        """Context manager for grouping related audit operations."""
        try:
            # Create operation group
            self.create_operation_group(
                group_id=group_id,
                name=name,
                description=description
            )
            
            yield group_id
            
        finally:
            # Complete operation group
            self.complete_operation_group(group_id)