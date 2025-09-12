"""
Enhanced VM Builder API endpoints with advanced planning and publishing features.

Provides sophisticated draft management, diff visualization, validation,
and publishing capabilities for the Vital Measurement Builder.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository
from ..core.vm_builder_enhanced import (
    EnhancedVMBuilderManager,
    VMBuilderStatus,
    ValidationSeverity,
    DiffOperation,
    DiffPlan,
    ValidationIssue
)

router = APIRouter(prefix="/vm-builder", tags=["vm-builder-enhanced"])

# Request/Response Models
class CreateDraftRequest(BaseModel):
    parent_id: int = Field(..., description="Parent node ID for the draft")
    draft_data: Dict[str, Any] = Field(..., description="Draft configuration data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class UpdateDraftRequest(BaseModel):
    draft_data: Dict[str, Any] = Field(..., description="Updated draft data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")

class PlanDraftResponse(BaseModel):
    success: bool
    message: str
    plan: Dict[str, Any]
    can_publish: bool
    validation_issues: List[Dict[str, Any]]
    warnings: List[str]

class PublishDraftRequest(BaseModel):
    force: bool = Field(False, description="Force publish even with validation issues")
    reason: Optional[str] = Field(None, description="Reason for publishing")

class PublishDraftResponse(BaseModel):
    success: bool
    message: str
    operations_applied: int
    audit_id: Optional[int]
    summary: Dict[str, int]

class DraftResponse(BaseModel):
    id: str
    created_at: str
    updated_at: str
    parent_id: int
    status: str
    published_at: Optional[str] = None
    published_by: Optional[str] = None
    plan_data: Optional[Dict[str, Any]] = None
    validation_data: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = {}

class DraftListResponse(BaseModel):
    drafts: List[DraftResponse]
    total: int
    status_filter: Optional[str] = None

class ValidationIssueResponse(BaseModel):
    severity: str
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None
    code: Optional[str] = None

class DiffOperationResponse(BaseModel):
    type: str
    node_id: Optional[int] = None
    old_data: Optional[Dict[str, Any]] = None
    new_data: Optional[Dict[str, Any]] = None
    impact_level: str
    description: str
    affected_children: List[int] = []

class DiffPlanResponse(BaseModel):
    draft_id: str
    parent_id: int
    operations: List[DiffOperationResponse]
    summary: Dict[str, int]
    validation_issues: List[ValidationIssueResponse]
    estimated_impact: str
    can_publish: bool
    warnings: List[str]

@router.post("/drafts", response_model=DraftResponse)
async def create_enhanced_draft(
    request: CreateDraftRequest,
    actor: str = "admin",
    repo: SQLiteRepository = Depends(get_repository)
):
    """Create a new enhanced VM Builder draft."""
    try:
        with repo._get_connection() as conn:
            manager = EnhancedVMBuilderManager(conn)
            
            # Validate parent exists
            cursor = conn.cursor()
            cursor.execute("SELECT id, label FROM nodes WHERE id = ?", (request.parent_id,))
            parent_row = cursor.fetchone()
            if not parent_row:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "parent_not_found",
                        "message": f"Parent node {request.parent_id} not found"
                    }
                )
            
            draft_id = manager.create_draft(
                parent_id=request.parent_id,
                draft_data=request.draft_data,
                actor=actor,
                metadata=request.metadata
            )
            
            # Get created draft
            draft = manager.get_draft(draft_id)
            
            return DraftResponse(
                id=draft["id"],
                created_at=draft["created_at"],
                updated_at=draft["updated_at"],
                parent_id=draft["parent_id"],
                status=draft["status"],
                published_at=draft["published_at"],
                published_by=draft["published_by"],
                plan_data=draft["plan_data"],
                validation_data=draft["validation_data"],
                metadata=draft["metadata"]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating enhanced draft: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to create draft",
                "message": str(e)
            }
        )

@router.get("/drafts/{draft_id}", response_model=DraftResponse)
async def get_enhanced_draft(
    draft_id: str,
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get an enhanced VM Builder draft."""
    try:
        with repo._get_connection() as conn:
            manager = EnhancedVMBuilderManager(conn)
            
            draft = manager.get_draft(draft_id)
            if not draft:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "draft_not_found",
                        "message": f"Draft {draft_id} not found"
                    }
                )
            
            return DraftResponse(
                id=draft["id"],
                created_at=draft["created_at"],
                updated_at=draft["updated_at"],
                parent_id=draft["parent_id"],
                status=draft["status"],
                published_at=draft["published_at"],
                published_by=draft["published_by"],
                plan_data=draft["plan_data"],
                validation_data=draft["validation_data"],
                metadata=draft["metadata"]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting enhanced draft: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get draft",
                "message": str(e)
            }
        )

@router.put("/drafts/{draft_id}", response_model=DraftResponse)
async def update_enhanced_draft(
    draft_id: str,
    request: UpdateDraftRequest,
    actor: str = "admin",
    repo: SQLiteRepository = Depends(get_repository)
):
    """Update an enhanced VM Builder draft."""
    try:
        with repo._get_connection() as conn:
            manager = EnhancedVMBuilderManager(conn)
            
            success = manager.update_draft(
                draft_id=draft_id,
                draft_data=request.draft_data,
                actor=actor
            )
            
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "draft_not_found_or_locked",
                        "message": f"Draft {draft_id} not found or not in editable status"
                    }
                )
            
            # Get updated draft
            draft = manager.get_draft(draft_id)
            
            return DraftResponse(
                id=draft["id"],
                created_at=draft["created_at"],
                updated_at=draft["updated_at"],
                parent_id=draft["parent_id"],
                status=draft["status"],
                published_at=draft["published_at"],
                published_by=draft["published_by"],
                plan_data=draft["plan_data"],
                validation_data=draft["validation_data"],
                metadata=draft["metadata"]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating enhanced draft: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to update draft",
                "message": str(e)
            }
        )

@router.get("/drafts", response_model=DraftListResponse)
async def list_enhanced_drafts(
    status: Optional[str] = Query(None, description="Filter by status"),
    parent_id: Optional[int] = Query(None, description="Filter by parent ID"),
    limit: int = Query(50, ge=1, le=200, description="Number of drafts to return"),
    offset: int = Query(0, ge=0, description="Number of drafts to skip"),
    repo: SQLiteRepository = Depends(get_repository)
):
    """List enhanced VM Builder drafts."""
    try:
        with repo._get_connection() as conn:
            manager = EnhancedVMBuilderManager(conn)
            
            # Build query
            query = "SELECT id, created_at, updated_at, parent_id, status, published_at, published_by, metadata FROM vm_drafts_enhanced"
            params = []
            conditions = []
            
            if status:
                conditions.append("status = ?")
                params.append(status)
            
            if parent_id:
                conditions.append("parent_id = ?")
                params.append(parent_id)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            drafts = []
            for row in rows:
                drafts.append(DraftResponse(
                    id=row[0],
                    created_at=row[1],
                    updated_at=row[2],
                    parent_id=row[3],
                    status=row[4],
                    published_at=row[5],
                    published_by=row[6],
                    metadata=json.loads(row[7]) if row[7] else {}
                ))
            
            # Get total count
            count_query = "SELECT COUNT(*) FROM vm_drafts_enhanced"
            if conditions:
                count_query += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(count_query, params[:-2])  # Remove limit and offset
            total = cursor.fetchone()[0]
            
            return DraftListResponse(
                drafts=drafts,
                total=total,
                status_filter=status
            )
    
    except Exception as e:
        logging.error(f"Error listing enhanced drafts: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to list drafts",
                "message": str(e)
            }
        )

@router.post("/drafts/{draft_id}/plan", response_model=PlanDraftResponse)
async def plan_enhanced_draft(
    draft_id: str,
    actor: str = "admin",
    repo: SQLiteRepository = Depends(get_repository)
):
    """Create a detailed plan for an enhanced draft."""
    try:
        with repo._get_connection() as conn:
            manager = EnhancedVMBuilderManager(conn)
            
            # Check if draft exists
            draft = manager.get_draft(draft_id)
            if not draft:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "draft_not_found",
                        "message": f"Draft {draft_id} not found"
                    }
                )
            
            # Create plan
            diff_plan = manager.plan_draft(draft_id, actor)
            
            # Convert to response format
            operations = []
            for op in diff_plan.operations:
                operations.append(DiffOperationResponse(
                    type=op.type.value,
                    node_id=op.node_id,
                    old_data=op.old_data,
                    new_data=op.new_data,
                    impact_level=op.impact_level,
                    description=op.description,
                    affected_children=op.affected_children or []
                ))
            
            validation_issues = []
            for issue in diff_plan.validation_issues:
                validation_issues.append(ValidationIssueResponse(
                    severity=issue.severity.value,
                    message=issue.message,
                    field=issue.field,
                    suggestion=issue.suggestion,
                    code=issue.code
                ))
            
            return PlanDraftResponse(
                success=True,
                message="Plan created successfully",
                plan=DiffPlanResponse(
                    draft_id=diff_plan.draft_id,
                    parent_id=diff_plan.parent_id,
                    operations=operations,
                    summary=diff_plan.summary,
                    validation_issues=validation_issues,
                    estimated_impact=diff_plan.estimated_impact,
                    can_publish=diff_plan.can_publish,
                    warnings=diff_plan.warnings
                ).dict(),
                can_publish=diff_plan.can_publish,
                validation_issues=[issue.dict() for issue in validation_issues],
                warnings=diff_plan.warnings
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error planning enhanced draft: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to plan draft",
                "message": str(e)
            }
        )

@router.post("/drafts/{draft_id}/publish", response_model=PublishDraftResponse)
async def publish_enhanced_draft(
    draft_id: str,
    request: PublishDraftRequest,
    actor: str = "admin",
    repo: SQLiteRepository = Depends(get_repository)
):
    """Publish an enhanced VM Builder draft."""
    try:
        with repo._get_connection() as conn:
            manager = EnhancedVMBuilderManager(conn)
            
            result = manager.publish_draft(
                draft_id=draft_id,
                actor=actor,
                force=request.force
            )
            
            return PublishDraftResponse(
                success=result["success"],
                message=result["message"],
                operations_applied=result["operations_applied"],
                audit_id=result.get("audit_id"),
                summary=result["summary"]
            )
    
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_draft",
                "message": str(e)
            }
        )
    except Exception as e:
        logging.error(f"Error publishing enhanced draft: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to publish draft",
                "message": str(e)
            }
        )

@router.delete("/drafts/{draft_id}")
async def delete_enhanced_draft(
    draft_id: str,
    actor: str = "admin",
    repo: SQLiteRepository = Depends(get_repository)
):
    """Delete an enhanced VM Builder draft."""
    try:
        with repo._get_connection() as conn:
            manager = EnhancedVMBuilderManager(conn)
            
            # Check if draft exists and is deletable
            draft = manager.get_draft(draft_id)
            if not draft:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "draft_not_found",
                        "message": f"Draft {draft_id} not found"
                    }
                )
            
            if draft["status"] in [VMBuilderStatus.PUBLISHED.value, VMBuilderStatus.PUBLISHING.value]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "draft_not_deletable",
                        "message": f"Draft {draft_id} cannot be deleted in {draft['status']} status"
                    }
                )
            
            # Delete draft
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vm_drafts_enhanced WHERE id = ?", (draft_id,))
            
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "draft_not_found",
                        "message": f"Draft {draft_id} not found"
                    }
                )
            
            conn.commit()
            
            # Log deletion
            manager._log_audit_action(
                draft_id, "delete_draft", actor,
                draft, None,
                True, "Draft deleted"
            )
            
            return {
                "success": True,
                "message": "Draft deleted successfully",
                "draft_id": draft_id
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting enhanced draft: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to delete draft",
                "message": str(e)
            }
        )

@router.get("/stats")
async def get_enhanced_vm_stats(
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get enhanced VM Builder statistics."""
    try:
        with repo._get_connection() as conn:
            manager = EnhancedVMBuilderManager(conn)
            
            stats = manager.get_draft_stats()
            
            return {
                "stats": stats,
                "status": "healthy"
            }
    
    except Exception as e:
        logging.error(f"Error getting enhanced VM stats: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get VM stats",
                "message": str(e)
            }
        )

@router.get("/drafts/{draft_id}/audit")
async def get_draft_audit_history(
    draft_id: str,
    limit: int = Query(50, ge=1, le=200, description="Number of audit entries to return"),
    offset: int = Query(0, ge=0, description="Number of audit entries to skip"),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get audit history for a draft."""
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if draft exists
            cursor.execute("SELECT id FROM vm_drafts_enhanced WHERE id = ?", (draft_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "draft_not_found",
                        "message": f"Draft {draft_id} not found"
                    }
                )
            
            # Get audit history
            cursor.execute("""
                SELECT id, action, actor, timestamp, before_state, after_state, 
                       success, message, metadata
                FROM vm_builder_audit
                WHERE draft_id = ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """, (draft_id, limit, offset))
            
            rows = cursor.fetchall()
            audit_entries = []
            
            for row in rows:
                audit_entries.append({
                    "id": row[0],
                    "action": row[1],
                    "actor": row[2],
                    "timestamp": row[3],
                    "before_state": json.loads(row[4]) if row[4] else None,
                    "after_state": json.loads(row[5]) if row[5] else None,
                    "success": bool(row[6]),
                    "message": row[7],
                    "metadata": json.loads(row[8]) if row[8] else None
                })
            
            return {
                "draft_id": draft_id,
                "audit_entries": audit_entries,
                "total": len(audit_entries),
                "limit": limit,
                "offset": offset
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting draft audit history: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get audit history",
                "message": str(e)
            }
        )
