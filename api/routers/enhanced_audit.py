"""
Enhanced audit router with expanded operation types and undo capabilities.

Provides comprehensive audit logging, advanced undo operations, and audit trail management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime, timezone

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository
from ..core.audit_expansion import (
    EnhancedAuditManager, 
    ExpandedAuditOperation, 
    AuditContext,
    UndoCapability
)

router = APIRouter(tags=["enhanced-audit"])

@router.get("/admin/audit/enhanced")
async def get_enhanced_audit_log(
    limit: int = Query(50, ge=1, le=1000),
    after_id: Optional[int] = Query(None),
    operation: Optional[str] = Query(None),
    actor: Optional[str] = Query(None),
    target_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    undoable_only: bool = Query(False),
    group_id: Optional[str] = Query(None),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get enhanced audit log entries with advanced filtering.
    
    Args:
        limit: Maximum number of entries to return (1-1000)
        after_id: Return entries after this ID
        operation: Filter by operation type
        actor: Filter by actor
        target_type: Filter by target type
        severity: Filter by severity level
        tag: Filter by tag
        undoable_only: Only return undoable entries
        group_id: Filter by operation group ID
        
    Returns:
        Paginated list of enhanced audit log entries
    """
    try:
        with repo._get_connection() as conn:
            manager = EnhancedAuditManager(conn)
            
            # Parse operation filter
            operation_filter = None
            if operation:
                try:
                    operation_filter = ExpandedAuditOperation(operation)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "invalid_operation",
                            "message": f"Invalid operation type: {operation}",
                            "valid_operations": [op.value for op in ExpandedAuditOperation]
                        }
                    )
            
            entries = manager.get_enhanced_audit_entries(
                limit=limit,
                after_id=after_id,
                operation_filter=operation_filter,
                actor_filter=actor,
                target_type_filter=target_type,
                severity_filter=severity,
                tag_filter=tag,
                undoable_only=undoable_only,
                group_id=group_id
            )
            
            return {
                "entries": entries,
                "count": len(entries),
                "limit": limit,
                "filters": {
                    "after_id": after_id,
                    "operation": operation,
                    "actor": actor,
                    "target_type": target_type,
                    "severity": severity,
                    "tag": tag,
                    "undoable_only": undoable_only,
                    "group_id": group_id
                }
            }
    
    except Exception as e:
        logging.error(f"Error getting enhanced audit log: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get enhanced audit log",
                "message": str(e)
            }
        )

@router.get("/admin/audit/enhanced/undoable")
async def get_undoable_entries(
    limit: int = Query(100, ge=1, le=1000),
    include_expired: bool = Query(False),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get all undoable audit entries.
    
    Args:
        limit: Maximum number of entries to return
        include_expired: Include entries that have exceeded their undo timeout
        
    Returns:
        List of undoable audit entries
    """
    try:
        with repo._get_connection() as conn:
            manager = EnhancedAuditManager(conn)
            entries = manager.get_undoable_entries(
                limit=limit,
                include_expired=include_expired
            )
            
            return {
                "entries": entries,
                "count": len(entries),
                "include_expired": include_expired,
                "message": "Only operations within their undo timeout are shown by default"
            }
    
    except Exception as e:
        logging.error(f"Error getting undoable entries: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get undoable entries",
                "message": str(e)
            }
        )

@router.post("/admin/audit/enhanced/{audit_id}/undo")
async def undo_enhanced_operation(
    audit_id: int,
    reason: Optional[str] = Body(None, embed=True),
    actor: str = "admin",
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Undo an enhanced operation if possible.
    
    Args:
        audit_id: Audit log entry ID to undo
        reason: Reason for undoing the operation
        actor: Who is performing the undo
        
    Returns:
        Undo operation result
    """
    try:
        with repo._get_connection() as conn:
            manager = EnhancedAuditManager(conn)
            
            result = manager.undo_operation(
                audit_id=audit_id,
                actor=actor,
                reason=reason
            )
            
            if result["success"]:
                return result
            else:
                raise HTTPException(
                    status_code=400,
                    detail=result
                )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error undoing enhanced operation {audit_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to undo operation",
                "message": str(e)
            }
        )

@router.get("/admin/audit/enhanced/stats")
async def get_enhanced_audit_stats(
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get enhanced audit log statistics.
    
    Returns:
        Enhanced audit log statistics and summary
    """
    try:
        with repo._get_connection() as conn:
            manager = EnhancedAuditManager(conn)
            stats = manager.get_enhanced_audit_stats()
            
            return {
                "stats": stats,
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    except Exception as e:
        logging.error(f"Error getting enhanced audit stats: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get enhanced audit stats",
                "message": str(e)
            }
        )

@router.get("/admin/audit/enhanced/operations")
async def get_available_enhanced_operations():
    """
    Get list of available enhanced audit operations with their capabilities.
    
    Returns:
        List of available operation types with undo capabilities
    """
    operations = []
    
    for operation in ExpandedAuditOperation:
        # Get undo capability (simplified for API response)
        is_undoable = operation in [
            ExpandedAuditOperation.APPLY_DEFAULT,
            ExpandedAuditOperation.NODE_CREATE,
            ExpandedAuditOperation.NODE_UPDATE,
            ExpandedAuditOperation.FLAG_ASSIGN,
            ExpandedAuditOperation.FLAG_REMOVE,
            ExpandedAuditOperation.BULK_FLAG_OPERATION,
            ExpandedAuditOperation.TRIAGE_UPDATE,
            ExpandedAuditOperation.DICTIONARY_UPDATE
        ]
        
        operations.append({
            "type": operation.value,
            "description": _get_operation_description(operation),
            "undoable": is_undoable,
            "category": _get_operation_category(operation)
        })
    
    return {
        "operations": operations,
        "total_count": len(operations),
        "undoable_count": sum(1 for op in operations if op["undoable"])
    }

@router.post("/admin/audit/enhanced/operation-groups")
async def create_operation_group(
    group_id: str = Body(..., embed=True),
    name: str = Body(..., embed=True),
    description: Optional[str] = Body(None, embed=True),
    total_operations: int = Body(0, embed=True),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Create an audit operation group for batch operations.
    
    Args:
        group_id: Unique identifier for the operation group
        name: Human-readable name for the group
        description: Optional description
        total_operations: Expected total number of operations
        
    Returns:
        Operation group creation result
    """
    try:
        with repo._get_connection() as conn:
            manager = EnhancedAuditManager(conn)
            
            success = manager.create_operation_group(
                group_id=group_id,
                name=name,
                description=description,
                total_operations=total_operations
            )
            
            if success:
                return {
                    "success": True,
                    "message": f"Operation group '{name}' created successfully",
                    "group_id": group_id
                }
            else:
                return {
                    "success": False,
                    "message": f"Operation group '{group_id}' already exists",
                    "group_id": group_id
                }
    
    except Exception as e:
        logging.error(f"Error creating operation group: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to create operation group",
                "message": str(e)
            }
        )

@router.put("/admin/audit/enhanced/operation-groups/{group_id}/complete")
async def complete_operation_group(
    group_id: str,
    status: str = Body("completed", embed=True),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Mark an audit operation group as completed.
    
    Args:
        group_id: Operation group ID
        status: Completion status (completed, failed, cancelled)
        
    Returns:
        Completion result
    """
    try:
        with repo._get_connection() as conn:
            manager = EnhancedAuditManager(conn)
            
            success = manager.complete_operation_group(
                group_id=group_id,
                status=status
            )
            
            if success:
                return {
                    "success": True,
                    "message": f"Operation group '{group_id}' marked as {status}",
                    "group_id": group_id,
                    "status": status
                }
            else:
                return {
                    "success": False,
                    "message": f"Operation group '{group_id}' not found",
                    "group_id": group_id
                }
    
    except Exception as e:
        logging.error(f"Error completing operation group: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to complete operation group",
                "message": str(e)
            }
        )

@router.get("/admin/audit/enhanced/operation-groups")
async def get_operation_groups(
    limit: int = Query(50, ge=1, le=1000),
    status: Optional[str] = Query(None),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get audit operation groups.
    
    Args:
        limit: Maximum number of groups to return
        status: Filter by status
        
    Returns:
        List of operation groups
    """
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM audit_operation_groups"
            params = []
            
            if status:
                query += " WHERE status = ?"
                params.append(status)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            groups = []
            for row in rows:
                groups.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "created_at": row[3],
                    "completed_at": row[4],
                    "status": row[5],
                    "total_operations": row[6],
                    "completed_operations": row[7],
                    "failed_operations": row[8]
                })
            
            return {
                "groups": groups,
                "count": len(groups),
                "limit": limit,
                "status_filter": status
            }
    
    except Exception as e:
        logging.error(f"Error getting operation groups: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get operation groups",
                "message": str(e)
            }
        )

def _get_operation_description(operation: ExpandedAuditOperation) -> str:
    """Get human-readable description for an operation."""
    descriptions = {
        ExpandedAuditOperation.CONFLICT_RESOLVE: "Conflict resolution between competing edits",
        ExpandedAuditOperation.APPLY_DEFAULT: "Apply default children to a parent node",
        ExpandedAuditOperation.DELETE_SUBTREE: "Delete an entire subtree of nodes",
        ExpandedAuditOperation.DATA_QUALITY_REPAIR: "Data quality repair operation",
        ExpandedAuditOperation.CHILDREN_UPDATE: "Update children for a parent node",
        ExpandedAuditOperation.OUTCOME_UPDATE: "Update outcome for a leaf node",
        ExpandedAuditOperation.NODE_CREATE: "Create a new node",
        ExpandedAuditOperation.NODE_UPDATE: "Update an existing node",
        ExpandedAuditOperation.NODE_DELETE: "Delete a node",
        ExpandedAuditOperation.FLAG_ASSIGN: "Assign a flag to a node",
        ExpandedAuditOperation.FLAG_REMOVE: "Remove a flag from a node",
        ExpandedAuditOperation.BULK_FLAG_OPERATION: "Bulk flag assignment/removal operation",
        ExpandedAuditOperation.IMPORT_OPERATION: "Data import operation",
        ExpandedAuditOperation.EXPORT_OPERATION: "Data export operation",
        ExpandedAuditOperation.BACKUP_OPERATION: "Database backup operation",
        ExpandedAuditOperation.RESTORE_OPERATION: "Database restore operation",
        ExpandedAuditOperation.USER_LOGIN: "User login",
        ExpandedAuditOperation.USER_LOGOUT: "User logout",
        ExpandedAuditOperation.PERMISSION_CHANGE: "User permission change",
        ExpandedAuditOperation.ROLE_ASSIGNMENT: "User role assignment",
        ExpandedAuditOperation.DICTIONARY_UPDATE: "Dictionary term update",
        ExpandedAuditOperation.VM_BUILDER_OPERATION: "VM Builder operation",
        ExpandedAuditOperation.TRIAGE_UPDATE: "Triage status update",
        ExpandedAuditOperation.BULK_OPERATION: "Bulk operation"
    }
    return descriptions.get(operation, "Unknown operation")

def _get_operation_category(operation: ExpandedAuditOperation) -> str:
    """Get category for an operation."""
    categories = {
        ExpandedAuditOperation.CONFLICT_RESOLVE: "conflict",
        ExpandedAuditOperation.APPLY_DEFAULT: "tree",
        ExpandedAuditOperation.DELETE_SUBTREE: "tree",
        ExpandedAuditOperation.DATA_QUALITY_REPAIR: "maintenance",
        ExpandedAuditOperation.CHILDREN_UPDATE: "tree",
        ExpandedAuditOperation.OUTCOME_UPDATE: "tree",
        ExpandedAuditOperation.NODE_CREATE: "tree",
        ExpandedAuditOperation.NODE_UPDATE: "tree",
        ExpandedAuditOperation.NODE_DELETE: "tree",
        ExpandedAuditOperation.FLAG_ASSIGN: "flags",
        ExpandedAuditOperation.FLAG_REMOVE: "flags",
        ExpandedAuditOperation.BULK_FLAG_OPERATION: "flags",
        ExpandedAuditOperation.IMPORT_OPERATION: "data",
        ExpandedAuditOperation.EXPORT_OPERATION: "data",
        ExpandedAuditOperation.BACKUP_OPERATION: "system",
        ExpandedAuditOperation.RESTORE_OPERATION: "system",
        ExpandedAuditOperation.USER_LOGIN: "auth",
        ExpandedAuditOperation.USER_LOGOUT: "auth",
        ExpandedAuditOperation.PERMISSION_CHANGE: "auth",
        ExpandedAuditOperation.ROLE_ASSIGNMENT: "auth",
        ExpandedAuditOperation.DICTIONARY_UPDATE: "dictionary",
        ExpandedAuditOperation.VM_BUILDER_OPERATION: "vm_builder",
        ExpandedAuditOperation.TRIAGE_UPDATE: "triage",
        ExpandedAuditOperation.BULK_OPERATION: "bulk"
    }
    return categories.get(operation, "other")
