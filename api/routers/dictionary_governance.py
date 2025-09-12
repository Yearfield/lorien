"""
Dictionary Governance API endpoints.

Provides comprehensive governance features for dictionary terms including
approval workflows, status management, and audit trails.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timezone

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository
from ..core.dictionary_governance import (
    DictionaryGovernanceManager,
    DictionaryStatus,
    DictionaryAction,
    ApprovalLevel,
    DictionaryTerm,
    DictionaryChange
)

router = APIRouter(prefix="/dictionary/governance", tags=["dictionary-governance"])

# Request/Response Models
class TermCreateRequest(BaseModel):
    type: str = Field(..., description="Term type")
    term: str = Field(..., min_length=1, max_length=64, description="Term text")
    hints: Optional[str] = Field(None, max_length=256, description="Term hints")
    tags: Optional[List[str]] = Field(None, description="Term tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Term metadata")

class TermUpdateRequest(BaseModel):
    term: Optional[str] = Field(None, min_length=1, max_length=64, description="Term text")
    hints: Optional[str] = Field(None, max_length=256, description="Term hints")
    tags: Optional[List[str]] = Field(None, description="Term tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Term metadata")
    reason: Optional[str] = Field(None, description="Reason for update")

class ApprovalRequest(BaseModel):
    reason: Optional[str] = Field(None, description="Approval reason")

class RejectionRequest(BaseModel):
    reason: str = Field(..., min_length=1, description="Rejection reason")

class BulkApprovalRequest(BaseModel):
    term_ids: List[int] = Field(..., min_items=1, description="Term IDs to approve")
    reason: Optional[str] = Field(None, description="Approval reason")

class BulkRejectionRequest(BaseModel):
    term_ids: List[int] = Field(..., min_items=1, description="Term IDs to reject")
    reason: str = Field(..., min_length=1, description="Rejection reason")

class TermResponse(BaseModel):
    id: int
    type: str
    term: str
    normalized: str
    hints: Optional[str]
    status: str
    version: int
    created_by: Optional[str]
    created_at: Optional[str]
    updated_by: Optional[str]
    updated_at: Optional[str]
    approved_by: Optional[str]
    approved_at: Optional[str]
    rejection_reason: Optional[str]
    approval_level: str
    tags: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]

class ChangeResponse(BaseModel):
    id: int
    term_id: int
    action: str
    actor: str
    timestamp: str
    before_state: Optional[Dict[str, Any]]
    after_state: Optional[Dict[str, Any]]
    reason: Optional[str]
    metadata: Optional[Dict[str, Any]]

class TermsListResponse(BaseModel):
    items: List[TermResponse]
    total: int
    limit: int
    offset: int

class ChangesListResponse(BaseModel):
    items: List[ChangeResponse]
    total: int
    limit: int
    offset: int

class GovernanceStatsResponse(BaseModel):
    status_counts: Dict[str, int]
    type_counts: Dict[str, int]
    pending_by_type: Dict[str, int]
    recent_changes_7d: int
    approval_rate_30d: float
    total_terms: int
    pending_approvals: int

@router.get("/terms", response_model=TermsListResponse)
async def get_terms(
    type: Optional[str] = Query(None, description="Filter by term type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    search: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(50, ge=1, le=1000, description="Number of terms to return"),
    offset: int = Query(0, ge=0, description="Number of terms to skip"),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get dictionary terms with governance filtering."""
    try:
        with repo._get_connection() as conn:
            manager = DictionaryGovernanceManager(conn)
            
            # Parse status filter
            status_filter = None
            if status:
                try:
                    status_filter = DictionaryStatus(status)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "invalid_status",
                            "message": f"Invalid status: {status}",
                            "valid_statuses": [s.value for s in DictionaryStatus]
                        }
                    )
            
            terms = manager.get_terms(
                type=type,
                status=status_filter,
                created_by=created_by,
                limit=limit,
                offset=offset,
                search_query=search
            )
            
            # Convert to response format
            items = []
            for term in terms:
                items.append(TermResponse(
                    id=term.id,
                    type=term.type,
                    term=term.term,
                    normalized=term.normalized,
                    hints=term.hints,
                    status=term.status.value,
                    version=term.version,
                    created_by=term.created_by,
                    created_at=term.created_at.isoformat() if term.created_at else None,
                    updated_by=term.updated_by,
                    updated_at=term.updated_at.isoformat() if term.updated_at else None,
                    approved_by=term.approved_by,
                    approved_at=term.approved_at.isoformat() if term.approved_at else None,
                    rejection_reason=term.rejection_reason,
                    approval_level=term.approval_level.value,
                    tags=term.tags,
                    metadata=term.metadata
                ))
            
            return TermsListResponse(
                items=items,
                total=len(items),  # This should be the actual total count
                limit=limit,
                offset=offset
            )
    
    except Exception as e:
        logging.error(f"Error getting dictionary terms: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get dictionary terms",
                "message": str(e)
            }
        )

@router.get("/terms/pending", response_model=TermsListResponse)
async def get_pending_approvals(
    type: Optional[str] = Query(None, description="Filter by term type"),
    limit: int = Query(50, ge=1, le=1000, description="Number of terms to return"),
    offset: int = Query(0, ge=0, description="Number of terms to skip"),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get terms pending approval."""
    try:
        with repo._get_connection() as conn:
            manager = DictionaryGovernanceManager(conn)
            
            terms = manager.get_pending_approvals(
                type=type,
                limit=limit,
                offset=offset
            )
            
            # Convert to response format
            items = []
            for term in terms:
                items.append(TermResponse(
                    id=term.id,
                    type=term.type,
                    term=term.term,
                    normalized=term.normalized,
                    hints=term.hints,
                    status=term.status.value,
                    version=term.version,
                    created_by=term.created_by,
                    created_at=term.created_at.isoformat() if term.created_at else None,
                    updated_by=term.updated_by,
                    updated_at=term.updated_at.isoformat() if term.updated_at else None,
                    approved_by=term.approved_by,
                    approved_at=term.approved_at.isoformat() if term.approved_at else None,
                    rejection_reason=term.rejection_reason,
                    approval_level=term.approval_level.value,
                    tags=term.tags,
                    metadata=term.metadata
                ))
            
            return TermsListResponse(
                items=items,
                total=len(items),
                limit=limit,
                offset=offset
            )
    
    except Exception as e:
        logging.error(f"Error getting pending approvals: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get pending approvals",
                "message": str(e)
            }
        )

@router.post("/terms", response_model=TermResponse, status_code=201)
async def create_term(
    request: TermCreateRequest,
    created_by: str = "system",
    repo: SQLiteRepository = Depends(get_repository)
):
    """Create a new dictionary term with governance."""
    try:
        with repo._get_connection() as conn:
            manager = DictionaryGovernanceManager(conn)
            
            # Normalize term
            normalized = request.term.lower().strip()
            
            term_id = manager.create_term(
                type=request.type,
                term=request.term,
                normalized=normalized,
                hints=request.hints,
                created_by=created_by,
                tags=request.tags,
                metadata=request.metadata
            )
            
            # Get created term
            terms = manager.get_terms(limit=1, offset=0)
            if not terms or terms[0].id != term_id:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve created term"
                )
            
            term = terms[0]
            return TermResponse(
                id=term.id,
                type=term.type,
                term=term.term,
                normalized=term.normalized,
                hints=term.hints,
                status=term.status.value,
                version=term.version,
                created_by=term.created_by,
                created_at=term.created_at.isoformat() if term.created_at else None,
                updated_by=term.updated_by,
                updated_at=term.updated_at.isoformat() if term.updated_at else None,
                approved_by=term.approved_by,
                approved_at=term.approved_at.isoformat() if term.approved_at else None,
                rejection_reason=term.rejection_reason,
                approval_level=term.approval_level.value,
                tags=term.tags,
                metadata=term.metadata
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating dictionary term: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to create dictionary term",
                "message": str(e)
            }
        )

@router.put("/terms/{term_id}", response_model=TermResponse)
async def update_term(
    term_id: int,
    request: TermUpdateRequest,
    updated_by: str = "system",
    repo: SQLiteRepository = Depends(get_repository)
):
    """Update a dictionary term with governance."""
    try:
        with repo._get_connection() as conn:
            manager = DictionaryGovernanceManager(conn)
            
            # Normalize term if provided
            normalized = None
            if request.term:
                normalized = request.term.lower().strip()
            
            success = manager.update_term(
                term_id=term_id,
                term=request.term,
                normalized=normalized,
                hints=request.hints,
                updated_by=updated_by,
                reason=request.reason,
                tags=request.tags,
                metadata=request.metadata
            )
            
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail="Term not found"
                )
            
            # Get updated term
            terms = manager.get_terms(limit=1, offset=0)
            updated_term = None
            for term in terms:
                if term.id == term_id:
                    updated_term = term
                    break
            
            if not updated_term:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve updated term"
                )
            
            return TermResponse(
                id=updated_term.id,
                type=updated_term.type,
                term=updated_term.term,
                normalized=updated_term.normalized,
                hints=updated_term.hints,
                status=updated_term.status.value,
                version=updated_term.version,
                created_by=updated_term.created_by,
                created_at=updated_term.created_at.isoformat() if updated_term.created_at else None,
                updated_by=updated_term.updated_by,
                updated_at=updated_term.updated_at.isoformat() if updated_term.updated_at else None,
                approved_by=updated_term.approved_by,
                approved_at=updated_term.approved_at.isoformat() if updated_term.approved_at else None,
                rejection_reason=updated_term.rejection_reason,
                approval_level=updated_term.approval_level.value,
                tags=updated_term.tags,
                metadata=updated_term.metadata
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating dictionary term: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to update dictionary term",
                "message": str(e)
            }
        )

@router.post("/terms/{term_id}/approve", response_model=Dict[str, str])
async def approve_term(
    term_id: int,
    request: ApprovalRequest,
    approver: str = "admin",
    repo: SQLiteRepository = Depends(get_repository)
):
    """Approve a dictionary term."""
    try:
        with repo._get_connection() as conn:
            manager = DictionaryGovernanceManager(conn)
            
            success = manager.approve_term(
                term_id=term_id,
                approver=approver,
                reason=request.reason
            )
            
            if not success:
                raise HTTPException(
                    status_code=400,
                    detail="Term not found or not pending approval"
                )
            
            return {
                "message": "Term approved successfully",
                "term_id": str(term_id),
                "approver": approver
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error approving term {term_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to approve term",
                "message": str(e)
            }
        )

@router.post("/terms/{term_id}/reject", response_model=Dict[str, str])
async def reject_term(
    term_id: int,
    request: RejectionRequest,
    approver: str = "admin",
    repo: SQLiteRepository = Depends(get_repository)
):
    """Reject a dictionary term."""
    try:
        with repo._get_connection() as conn:
            manager = DictionaryGovernanceManager(conn)
            
            success = manager.reject_term(
                term_id=term_id,
                approver=approver,
                reason=request.reason
            )
            
            if not success:
                raise HTTPException(
                    status_code=400,
                    detail="Term not found or not pending approval"
                )
            
            return {
                "message": "Term rejected successfully",
                "term_id": str(term_id),
                "approver": approver,
                "reason": request.reason
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error rejecting term {term_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to reject term",
                "message": str(e)
            }
        )

@router.post("/terms/bulk-approve", response_model=Dict[str, Any])
async def bulk_approve_terms(
    request: BulkApprovalRequest,
    approver: str = "admin",
    repo: SQLiteRepository = Depends(get_repository)
):
    """Bulk approve multiple terms."""
    try:
        with repo._get_connection() as conn:
            manager = DictionaryGovernanceManager(conn)
            
            results = manager.bulk_approve(
                term_ids=request.term_ids,
                approver=approver,
                reason=request.reason
            )
            
            return {
                "message": "Bulk approval completed",
                "results": results,
                "approver": approver
            }
    
    except Exception as e:
        logging.error(f"Error bulk approving terms: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to bulk approve terms",
                "message": str(e)
            }
        )

@router.post("/terms/bulk-reject", response_model=Dict[str, Any])
async def bulk_reject_terms(
    request: BulkRejectionRequest,
    approver: str = "admin",
    repo: SQLiteRepository = Depends(get_repository)
):
    """Bulk reject multiple terms."""
    try:
        with repo._get_connection() as conn:
            manager = DictionaryGovernanceManager(conn)
            
            results = manager.bulk_reject(
                term_ids=request.term_ids,
                approver=approver,
                reason=request.reason
            )
            
            return {
                "message": "Bulk rejection completed",
                "results": results,
                "approver": approver
            }
    
    except Exception as e:
        logging.error(f"Error bulk rejecting terms: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to bulk reject terms",
                "message": str(e)
            }
        )

@router.get("/terms/{term_id}/changes", response_model=ChangesListResponse)
async def get_term_changes(
    term_id: int,
    limit: int = Query(50, ge=1, le=1000, description="Number of changes to return"),
    offset: int = Query(0, ge=0, description="Number of changes to skip"),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get change history for a term."""
    try:
        with repo._get_connection() as conn:
            manager = DictionaryGovernanceManager(conn)
            
            changes = manager.get_term_changes(
                term_id=term_id,
                limit=limit,
                offset=offset
            )
            
            # Convert to response format
            items = []
            for change in changes:
                items.append(ChangeResponse(
                    id=change.id,
                    term_id=change.term_id,
                    action=change.action.value,
                    actor=change.actor,
                    timestamp=change.timestamp.isoformat(),
                    before_state=change.before_state,
                    after_state=change.after_state,
                    reason=change.reason,
                    metadata=change.metadata
                ))
            
            return ChangesListResponse(
                items=items,
                total=len(items),
                limit=limit,
                offset=offset
            )
    
    except Exception as e:
        logging.error(f"Error getting term changes: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get term changes",
                "message": str(e)
            }
        )

@router.get("/stats", response_model=GovernanceStatsResponse)
async def get_governance_stats(
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get dictionary governance statistics."""
    try:
        with repo._get_connection() as conn:
            manager = DictionaryGovernanceManager(conn)
            
            stats = manager.get_governance_stats()
            
            return GovernanceStatsResponse(
                status_counts=stats["status_counts"],
                type_counts=stats["type_counts"],
                pending_by_type=stats["pending_by_type"],
                recent_changes_7d=stats["recent_changes_7d"],
                approval_rate_30d=stats["approval_rate_30d"],
                total_terms=stats["total_terms"],
                pending_approvals=stats["pending_approvals"]
            )
    
    except Exception as e:
        logging.error(f"Error getting governance stats: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get governance stats",
                "message": str(e)
            }
        )

@router.get("/workflows")
async def get_workflows():
    """Get available dictionary workflows."""
    return {
        "workflows": [
            {
                "type": "vital_measurement",
                "approval_level": "medical_review",
                "requires_medical_review": True,
                "auto_approve_editors": False,
                "max_versions": 5,
                "retention_days": 730
            },
            {
                "type": "node_label",
                "approval_level": "editor",
                "requires_medical_review": False,
                "auto_approve_editors": True,
                "max_versions": 10,
                "retention_days": 365
            },
            {
                "type": "outcome_template",
                "approval_level": "medical_review",
                "requires_medical_review": True,
                "auto_approve_editors": False,
                "max_versions": 3,
                "retention_days": 1095
            }
        ]
    }
