"""
Orphan Repair API endpoints.

Provides comprehensive repair functionality for orphaned nodes in the decision tree.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository
from ..core.orphan_repair import (
    OrphanRepairManager,
    OrphanType,
    RepairAction,
    OrphanNode,
    RepairResult
)

router = APIRouter(prefix="/admin/data-quality/orphan-repair", tags=["orphan-repair"])

# Request/Response Models
class OrphanNodeResponse(BaseModel):
    id: int
    label: str
    depth: int
    parent_id: Optional[int]
    slot: Optional[int]
    orphan_type: str
    severity: str
    suggested_actions: List[str]
    repair_impact: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class RepairRequest(BaseModel):
    action: str = Field(..., description="Repair action to perform")
    new_parent_id: Optional[int] = Field(None, description="New parent ID for reassignment")
    new_slot: Optional[int] = Field(None, description="New slot number for slot fixes")
    sibling_id: Optional[int] = Field(None, description="Sibling ID for merge operations")
    reason: Optional[str] = Field(None, description="Reason for repair")

class RepairResponse(BaseModel):
    success: bool
    action: str
    orphan_id: int
    message: str
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    warnings: Optional[List[str]] = None

class OrphanSummaryResponse(BaseModel):
    total_orphans: int
    type_counts: Dict[str, int]
    severity_counts: Dict[str, int]
    status: str

class OrphanListResponse(BaseModel):
    items: List[OrphanNodeResponse]
    total: int
    limit: int
    offset: int

class RepairHistoryResponse(BaseModel):
    items: List[Dict[str, Any]]
    total: int
    limit: int
    offset: int

@router.get("/summary", response_model=OrphanSummaryResponse)
async def get_orphan_summary(
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get summary of orphan issues."""
    try:
        with repo._get_connection() as conn:
            manager = OrphanRepairManager(conn)
            summary = manager.get_orphan_summary()
            
            return OrphanSummaryResponse(
                total_orphans=summary["total_orphans"],
                type_counts=summary["type_counts"],
                severity_counts=summary["severity_counts"],
                status=summary["status"]
            )
    
    except Exception as e:
        logging.error(f"Error getting orphan summary: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get orphan summary",
                "message": str(e)
            }
        )

@router.get("/orphans", response_model=OrphanListResponse)
async def get_orphans(
    limit: int = Query(50, ge=1, le=200, description="Number of orphans to return"),
    offset: int = Query(0, ge=0, description="Number of orphans to skip"),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get list of orphaned nodes with repair suggestions."""
    try:
        with repo._get_connection() as conn:
            manager = OrphanRepairManager(conn)
            orphans = manager.detect_orphans(limit=limit, offset=offset)
            
            # Convert to response format
            items = []
            for orphan in orphans:
                items.append(OrphanNodeResponse(
                    id=orphan.id,
                    label=orphan.label,
                    depth=orphan.depth,
                    parent_id=orphan.parent_id,
                    slot=orphan.slot,
                    orphan_type=orphan.orphan_type.value,
                    severity=orphan.severity,
                    suggested_actions=[action.value for action in orphan.suggested_actions],
                    repair_impact=orphan.repair_impact,
                    created_at=orphan.created_at.isoformat() if orphan.created_at else None,
                    updated_at=orphan.updated_at.isoformat() if orphan.updated_at else None
                ))
            
            return OrphanListResponse(
                items=items,
                total=len(items),  # This should be the actual total count
                limit=limit,
                offset=offset
            )
    
    except Exception as e:
        logging.error(f"Error getting orphans: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get orphans",
                "message": str(e)
            }
        )

@router.post("/repair/{orphan_id}", response_model=RepairResponse)
async def repair_orphan(
    orphan_id: int,
    request: RepairRequest,
    actor: str = "admin",
    repo: SQLiteRepository = Depends(get_repository)
):
    """Repair a specific orphan node."""
    try:
        with repo._get_connection() as conn:
            manager = OrphanRepairManager(conn)
            
            # Parse action
            try:
                action = RepairAction(request.action)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "invalid_action",
                        "message": f"Invalid repair action: {request.action}",
                        "valid_actions": [action.value for action in RepairAction]
                    }
                )
            
            # Prepare kwargs based on action
            kwargs = {}
            if action == RepairAction.REASSIGN_PARENT and request.new_parent_id:
                kwargs["new_parent_id"] = request.new_parent_id
            elif action == RepairAction.FIX_SLOT and request.new_slot:
                kwargs["new_slot"] = request.new_slot
            elif action == RepairAction.MERGE_WITH_SIBLING and request.sibling_id:
                kwargs["sibling_id"] = request.sibling_id
            
            # Perform repair
            result = manager.repair_orphan(
                orphan_id=orphan_id,
                action=action,
                actor=actor,
                **kwargs
            )
            
            return RepairResponse(
                success=result.success,
                action=result.action.value,
                orphan_id=result.orphan_id,
                message=result.message,
                before_state=result.before_state,
                after_state=result.after_state,
                warnings=result.warnings
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error repairing orphan {orphan_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to repair orphan",
                "message": str(e)
            }
        )

@router.post("/repair/bulk", response_model=Dict[str, Any])
async def bulk_repair_orphans(
    orphan_ids: List[int] = Body(..., description="List of orphan IDs to repair"),
    action: str = Body(..., description="Repair action to perform"),
    actor: str = "admin",
    repo: SQLiteRepository = Depends(get_repository)
):
    """Bulk repair multiple orphan nodes."""
    try:
        with repo._get_connection() as conn:
            manager = OrphanRepairManager(conn)
            
            # Parse action
            try:
                repair_action = RepairAction(action)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "invalid_action",
                        "message": f"Invalid repair action: {action}",
                        "valid_actions": [action.value for action in RepairAction]
                    }
                )
            
            results = {
                "successful": [],
                "failed": [],
                "total_processed": len(orphan_ids)
            }
            
            for orphan_id in orphan_ids:
                try:
                    result = manager.repair_orphan(
                        orphan_id=orphan_id,
                        action=repair_action,
                        actor=actor
                    )
                    
                    if result.success:
                        results["successful"].append({
                            "orphan_id": orphan_id,
                            "message": result.message
                        })
                    else:
                        results["failed"].append({
                            "orphan_id": orphan_id,
                            "error": result.message
                        })
                
                except Exception as e:
                    results["failed"].append({
                        "orphan_id": orphan_id,
                        "error": str(e)
                    })
            
            return {
                "message": f"Bulk repair completed: {len(results['successful'])} successful, {len(results['failed'])} failed",
                "results": results
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error bulk repairing orphans: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to bulk repair orphans",
                "message": str(e)
            }
        )

@router.get("/repair/history", response_model=RepairHistoryResponse)
async def get_repair_history(
    orphan_id: Optional[int] = Query(None, description="Filter by specific orphan ID"),
    limit: int = Query(50, ge=1, le=200, description="Number of history items to return"),
    offset: int = Query(0, ge=0, description="Number of history items to skip"),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get repair history."""
    try:
        with repo._get_connection() as conn:
            manager = OrphanRepairManager(conn)
            history = manager.get_repair_history(
                orphan_id=orphan_id,
                limit=limit,
                offset=offset
            )
            
            return RepairHistoryResponse(
                items=history,
                total=len(history),
                limit=limit,
                offset=offset
            )
    
    except Exception as e:
        logging.error(f"Error getting repair history: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get repair history",
                "message": str(e)
            }
        )

@router.get("/repair/actions")
async def get_repair_actions():
    """Get available repair actions and their descriptions."""
    return {
        "actions": [
            {
                "action": "delete_orphan",
                "description": "Delete the orphaned node (only if it has no children)",
                "severity": "high",
                "irreversible": True
            },
            {
                "action": "reassign_parent",
                "description": "Reassign orphan to a new parent node",
                "severity": "medium",
                "irreversible": False,
                "requires": ["new_parent_id"]
            },
            {
                "action": "fix_depth",
                "description": "Fix depth to match parent depth + 1",
                "severity": "low",
                "irreversible": False
            },
            {
                "action": "fix_slot",
                "description": "Assign a valid slot number (1-5)",
                "severity": "medium",
                "irreversible": False,
                "optional": ["new_slot"]
            },
            {
                "action": "convert_to_root",
                "description": "Convert orphan to a root node",
                "severity": "high",
                "irreversible": True
            },
            {
                "action": "merge_with_sibling",
                "description": "Merge orphan with a sibling node",
                "severity": "high",
                "irreversible": True,
                "requires": ["sibling_id"]
            }
        ]
    }

@router.get("/orphan-types")
async def get_orphan_types():
    """Get available orphan types and their descriptions."""
    return {
        "types": [
            {
                "type": "missing_parent",
                "description": "Node references a non-existent parent",
                "severity": "high",
                "common_causes": ["Data corruption", "Incomplete migration", "Manual deletion"]
            },
            {
                "type": "invalid_depth",
                "description": "Node depth doesn't match parent depth + 1",
                "severity": "medium",
                "common_causes": ["Manual data modification", "Migration errors"]
            },
            {
                "type": "invalid_slot",
                "description": "Node slot is outside valid range (1-5) or null",
                "severity": "medium",
                "common_causes": ["Data corruption", "Manual modification"]
            },
            {
                "type": "duplicate_slot",
                "description": "Multiple children have the same slot number",
                "severity": "high",
                "common_causes": ["Concurrent modifications", "Data corruption"]
            }
        ]
    }
