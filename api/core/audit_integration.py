"""
Audit integration helpers for easy addition of audit logging to existing operations.

This module provides decorators and context managers for seamless audit integration.
"""

import functools
import logging
from typing import Dict, Any, Optional, Callable, Union
from datetime import datetime, timezone
from contextlib import contextmanager

from .audit_expansion import (
    EnhancedAuditManager, 
    ExpandedAuditOperation, 
    AuditContext
)

logger = logging.getLogger(__name__)

class AuditIntegration:
    """Helper class for integrating audit logging into existing operations."""
    
    def __init__(self, audit_manager: EnhancedAuditManager):
        self.audit_manager = audit_manager
        self._operation_groups = {}
    
    @contextmanager
    def operation_group(self, group_id: str, name: str, description: Optional[str] = None):
        """Context manager for grouping related audit operations."""
        try:
            # Create operation group
            self.audit_manager.create_operation_group(
                group_id=group_id,
                name=name,
                description=description
            )
            self._operation_groups[group_id] = {
                "name": name,
                "description": description,
                "operations": []
            }
            
            yield group_id
            
        finally:
            # Complete operation group
            self.audit_manager.complete_operation_group(group_id)
            if group_id in self._operation_groups:
                del self._operation_groups[group_id]
    
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
        tags: Optional[list] = None
    ) -> int:
        """Log an audit operation with enhanced capabilities."""
        return self.audit_manager.log_operation(
            operation=operation,
            target_id=target_id,
            target_type=target_type,
            actor=actor,
            context=context,
            payload=payload,
            undo_data=undo_data,
            operation_group_id=operation_group_id,
            severity=severity,
            tags=tags
        )
    
    def log_node_operation(
        self,
        operation: ExpandedAuditOperation,
        node_id: int,
        actor: str = "system",
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        context: Optional[AuditContext] = None,
        operation_group_id: Optional[str] = None
    ) -> int:
        """Log a node-related operation with automatic undo data."""
        undo_data = None
        if before_state and operation in [
            ExpandedAuditOperation.NODE_UPDATE,
            ExpandedAuditOperation.NODE_CREATE
        ]:
            undo_data = {
                "before_state": before_state,
                "after_state": after_state,
                "operation": operation.value
            }
        
        return self.log_operation(
            operation=operation,
            target_id=node_id,
            target_type="node",
            actor=actor,
            context=context,
            payload=after_state,
            undo_data=undo_data,
            operation_group_id=operation_group_id
        )
    
    def log_flag_operation(
        self,
        operation: ExpandedAuditOperation,
        node_id: int,
        flag_id: int,
        actor: str = "system",
        before_state: Optional[Dict[str, Any]] = None,
        context: Optional[AuditContext] = None,
        operation_group_id: Optional[str] = None
    ) -> int:
        """Log a flag-related operation with automatic undo data."""
        undo_data = {
            "node_id": node_id,
            "flag_id": flag_id,
            "before_state": before_state,
            "operation": operation.value
        }
        
        return self.log_operation(
            operation=operation,
            target_id=node_id,
            target_type="node_flag",
            actor=actor,
            context=context,
            payload={"flag_id": flag_id, "node_id": node_id},
            undo_data=undo_data,
            operation_group_id=operation_group_id
        )
    
    def log_bulk_operation(
        self,
        operation: ExpandedAuditOperation,
        operations: list,
        actor: str = "system",
        context: Optional[AuditContext] = None,
        operation_group_id: Optional[str] = None
    ) -> int:
        """Log a bulk operation with all sub-operations."""
        undo_data = {
            "operations": operations,
            "operation": operation.value,
            "count": len(operations)
        }
        
        return self.log_operation(
            operation=operation,
            target_id=operations[0].get("target_id") if operations else None,
            target_type="bulk",
            actor=actor,
            context=context,
            payload={"operations": operations, "count": len(operations)},
            undo_data=undo_data,
            operation_group_id=operation_group_id,
            severity="info",
            tags=["bulk"]
        )

def audit_operation(
    operation: ExpandedAuditOperation,
    target_type: str = "node",
    capture_before: bool = True,
    capture_after: bool = True,
    operation_group_id: Optional[str] = None,
    severity: str = "info",
    tags: Optional[list] = None
):
    """
    Decorator for automatically auditing function calls.
    
    Args:
        operation: Type of audit operation
        target_type: Type of target entity
        capture_before: Whether to capture state before operation
        capture_after: Whether to capture state after operation
        operation_group_id: Optional operation group ID
        severity: Operation severity
        tags: Optional tags for categorization
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract target_id from function arguments
            target_id = None
            if 'node_id' in kwargs:
                target_id = kwargs['node_id']
            elif 'id' in kwargs:
                target_id = kwargs['id']
            elif len(args) > 0 and isinstance(args[0], int):
                target_id = args[0]
            
            # Extract actor from context
            actor = kwargs.get('actor', 'system')
            
            # Create audit context
            context = AuditContext(
                user_id=kwargs.get('user_id'),
                session_id=kwargs.get('session_id'),
                request_id=kwargs.get('request_id')
            )
            
            # Capture before state if needed
            before_state = None
            if capture_before and target_id:
                before_state = _capture_entity_state(target_id, target_type)
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Capture after state if needed
                after_state = None
                if capture_after and target_id:
                    after_state = _capture_entity_state(target_id, target_type)
                
                # Log the operation
                audit_manager = _get_audit_manager()
                if audit_manager:
                    audit_manager.log_operation(
                        operation=operation,
                        target_id=target_id,
                        target_type=target_type,
                        actor=actor,
                        context=context,
                        payload=after_state,
                        undo_data={
                            "before_state": before_state,
                            "after_state": after_state,
                            "operation": operation.value
                        } if before_state else None,
                        operation_group_id=operation_group_id,
                        severity=severity,
                        tags=tags
                    )
                
                return result
                
            except Exception as e:
                # Log failed operation
                audit_manager = _get_audit_manager()
                if audit_manager:
                    audit_manager.log_operation(
                        operation=operation,
                        target_id=target_id,
                        target_type=target_type,
                        actor=actor,
                        context=context,
                        payload={"error": str(e)},
                        operation_group_id=operation_group_id,
                        severity="error",
                        tags=(tags or []) + ["failed"]
                    )
                raise
        
        return wrapper
    return decorator

def audit_bulk_operation(
    operation: ExpandedAuditOperation,
    operation_group_id: str,
    severity: str = "info",
    tags: Optional[list] = None
):
    """
    Decorator for auditing bulk operations.
    
    Args:
        operation: Type of audit operation
        operation_group_id: Operation group ID for batching
        severity: Operation severity
        tags: Optional tags for categorization
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract operations list
            operations = kwargs.get('operations', [])
            actor = kwargs.get('actor', 'system')
            
            # Create audit context
            context = AuditContext(
                user_id=kwargs.get('user_id'),
                session_id=kwargs.get('session_id'),
                request_id=kwargs.get('request_id')
            )
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Log the bulk operation
                audit_manager = _get_audit_manager()
                if audit_manager:
                    audit_manager.log_bulk_operation(
                        operation=operation,
                        operations=operations,
                        actor=actor,
                        context=context,
                        operation_group_id=operation_group_id
                    )
                
                return result
                
            except Exception as e:
                # Log failed bulk operation
                audit_manager = _get_audit_manager()
                if audit_manager:
                    audit_manager.log_operation(
                        operation=operation,
                        target_id=operations[0].get("target_id") if operations else None,
                        target_type="bulk",
                        actor=actor,
                        context=context,
                        payload={"error": str(e), "operations": operations},
                        operation_group_id=operation_group_id,
                        severity="error",
                        tags=(tags or []) + ["failed"]
                    )
                raise
        
        return wrapper
    return decorator

def _capture_entity_state(entity_id: int, entity_type: str) -> Optional[Dict[str, Any]]:
    """Capture the current state of an entity for audit purposes."""
    # This would need to be implemented based on the specific entity type
    # For now, return a placeholder
    return {
        "entity_id": entity_id,
        "entity_type": entity_type,
        "captured_at": datetime.now(timezone.utc).isoformat()
    }

def _get_audit_manager() -> Optional[EnhancedAuditManager]:
    """Get the current audit manager instance."""
    # This would need to be implemented based on your dependency injection system
    # For now, return None to avoid errors
    return None

# Convenience functions for common operations
def audit_node_create(func: Callable) -> Callable:
    """Decorator for auditing node creation operations."""
    return audit_operation(
        operation=ExpandedAuditOperation.NODE_CREATE,
        target_type="node",
        capture_before=False,
        capture_after=True
    )(func)

def audit_node_update(func: Callable) -> Callable:
    """Decorator for auditing node update operations."""
    return audit_operation(
        operation=ExpandedAuditOperation.NODE_UPDATE,
        target_type="node",
        capture_before=True,
        capture_after=True
    )(func)

def audit_node_delete(func: Callable) -> Callable:
    """Decorator for auditing node deletion operations."""
    return audit_operation(
        operation=ExpandedAuditOperation.NODE_DELETE,
        target_type="node",
        capture_before=True,
        capture_after=False
    )(func)

def audit_flag_assign(func: Callable) -> Callable:
    """Decorator for auditing flag assignment operations."""
    return audit_operation(
        operation=ExpandedAuditOperation.FLAG_ASSIGN,
        target_type="node_flag",
        capture_before=True,
        capture_after=True
    )(func)

def audit_flag_remove(func: Callable) -> Callable:
    """Decorator for auditing flag removal operations."""
    return audit_operation(
        operation=ExpandedAuditOperation.FLAG_REMOVE,
        target_type="node_flag",
        capture_before=True,
        capture_after=True
    )(func)

def audit_triage_update(func: Callable) -> Callable:
    """Decorator for auditing triage update operations."""
    return audit_operation(
        operation=ExpandedAuditOperation.TRIAGE_UPDATE,
        target_type="node",
        capture_before=True,
        capture_after=True
    )(func)

def audit_dictionary_update(func: Callable) -> Callable:
    """Decorator for auditing dictionary update operations."""
    return audit_operation(
        operation=ExpandedAuditOperation.DICTIONARY_UPDATE,
        target_type="dictionary",
        capture_before=True,
        capture_after=True
    )(func)

def audit_import_operation(func: Callable) -> Callable:
    """Decorator for auditing import operations."""
    return audit_operation(
        operation=ExpandedAuditOperation.IMPORT_OPERATION,
        target_type="import",
        capture_before=False,
        capture_after=True,
        severity="info",
        tags=["import"]
    )(func)

def audit_export_operation(func: Callable) -> Callable:
    """Decorator for auditing export operations."""
    return audit_operation(
        operation=ExpandedAuditOperation.EXPORT_OPERATION,
        target_type="export",
        capture_before=False,
        capture_after=True,
        severity="info",
        tags=["export"]
    )(func)

def audit_backup_operation(func: Callable) -> Callable:
    """Decorator for auditing backup operations."""
    return audit_operation(
        operation=ExpandedAuditOperation.BACKUP_OPERATION,
        target_type="backup",
        capture_before=False,
        capture_after=True,
        severity="info",
        tags=["backup", "system"]
    )(func)

def audit_restore_operation(func: Callable) -> Callable:
    """Decorator for auditing restore operations."""
    return audit_operation(
        operation=ExpandedAuditOperation.RESTORE_OPERATION,
        target_type="restore",
        capture_before=False,
        capture_after=True,
        severity="warning",
        tags=["restore", "system"]
    )(func)

def audit_user_operation(func: Callable) -> Callable:
    """Decorator for auditing user-related operations."""
    return audit_operation(
        operation=ExpandedAuditOperation.USER_LOGIN,
        target_type="user",
        capture_before=False,
        capture_after=True,
        severity="info",
        tags=["user", "auth"]
    )(func)
