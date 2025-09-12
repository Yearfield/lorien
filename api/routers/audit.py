"""
Audit log endpoints for safety and recoverability.

Provides endpoints for viewing audit logs, performing undo operations,
and managing audit trail data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository
from ..repositories.audit import AuditManager, AuditOperation

router = APIRouter(tags=["audit"])

@router.get("/admin/audit")
async def get_audit_log(
    limit: int = Query(50, ge=1, le=1000),
    after_id: Optional[int] = Query(None),
    operation: Optional[str] = Query(None),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get audit log entries with pagination and filtering.
    
    Args:
        limit: Maximum number of entries to return (1-1000)
        after_id: Return entries after this ID
        operation: Filter by operation type
        
    Returns:
        Paginated list of audit log entries
    """
    try:
        with repo._get_connection() as conn:
            manager = AuditManager(conn)
            
            # Parse operation filter
            operation_filter = None
            if operation:
                try:
                    operation_filter = AuditOperation(operation)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "invalid_operation",
                            "message": f"Invalid operation type: {operation}",
                            "valid_operations": [op.value for op in AuditOperation]
                        }
                    )
            
            entries = manager.get_audit_entries(
                limit=limit,
                after_id=after_id,
                operation_filter=operation_filter
            )
            
            return {
                "entries": entries,
                "count": len(entries),
                "limit": limit,
                "after_id": after_id,
                "operation_filter": operation
            }
    
    except Exception as e:
        logging.error(f"Error getting audit log: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get audit log",
                "message": str(e)
            }
        )

@router.get("/admin/audit/undoable")
async def get_undoable_entries(
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get all undoable audit entries.
    
    Returns:
        List of undoable audit entries
    """
    try:
        with repo._get_connection() as conn:
            manager = AuditManager(conn)
            entries = manager.get_undoable_entries()
            
            return {
                "entries": entries,
                "count": len(entries),
                "message": "Only apply-default operations are currently undoable"
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

@router.post("/admin/audit/{audit_id}/undo")
async def undo_operation(
    audit_id: int,
    actor: str = "admin",
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Undo an operation if possible.
    
    Args:
        audit_id: Audit log entry ID to undo
        actor: Who is performing the undo
        
    Returns:
        Undo operation result
    """
    try:
        with repo._get_connection() as conn:
            manager = AuditManager(conn)
            
            # Check if entry exists and is undoable
            entries = manager.get_audit_entries(limit=1, after_id=audit_id - 1)
            if not entries or entries[0]["id"] != audit_id:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "audit_entry_not_found",
                        "message": f"Audit entry {audit_id} not found"
                    }
                )
            
            entry = entries[0]
            if not entry["is_undoable"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "not_undoable",
                        "message": f"Operation {entry['operation']} is not undoable"
                    }
                )
            
            if entry["undone_by"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "already_undone",
                        "message": f"Operation was already undone at {entry['undone_at']}"
                    }
                )
            
            # Perform undo
            success = manager.undo_operation(audit_id, actor)
            
            if success:
                return {
                    "success": True,
                    "message": f"Operation {audit_id} successfully undone",
                    "audit_id": audit_id,
                    "actor": actor,
                    "undone_at": datetime.now().isoformat()
                }
            else:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "undo_failed",
                        "message": "Failed to undo operation"
                    }
                )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error undoing operation {audit_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to undo operation",
                "message": str(e)
            }
        )

@router.get("/admin/audit/stats")
async def get_audit_stats(
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get audit log statistics.
    
    Returns:
        Audit log statistics and summary
    """
    try:
        with repo._get_connection() as conn:
            manager = AuditManager(conn)
            stats = manager.get_audit_stats()
            
            return {
                "stats": stats,
                "status": "healthy"
            }
    
    except Exception as e:
        logging.error(f"Error getting audit stats: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get audit stats",
                "message": str(e)
            }
        )

@router.get("/admin/audit/operations")
async def get_available_operations():
    """
    Get list of available audit operations.
    
    Returns:
        List of available operation types
    """
    return {
        "operations": [
            {
                "type": op.value,
                "description": _get_operation_description(op),
                "undoable": op == AuditOperation.APPLY_DEFAULT
            }
            for op in AuditOperation
        ]
    }

def _get_operation_description(operation: AuditOperation) -> str:
    """Get human-readable description for an operation."""
    descriptions = {
        AuditOperation.CONFLICT_RESOLVE: "Conflict resolution between competing edits",
        AuditOperation.APPLY_DEFAULT: "Apply default children to a parent node",
        AuditOperation.DELETE_SUBTREE: "Delete an entire subtree of nodes",
        AuditOperation.DATA_QUALITY_REPAIR: "Data quality repair operation",
        AuditOperation.CHILDREN_UPDATE: "Update children for a parent node",
        AuditOperation.OUTCOME_UPDATE: "Update outcome for a leaf node"
    }
    return descriptions.get(operation, "Unknown operation")
