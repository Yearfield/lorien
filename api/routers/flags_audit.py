"""
Red Flag Audit router for tracking flag assignments and removals.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository

router = APIRouter(prefix="/flags/audit", tags=["flags-audit"])


class RedFlagAuditRecord(BaseModel):
    id: int
    node_id: int
    flag_id: int
    action: str
    user: Optional[str] = None
    ts: str


class RedFlagAuditCreate(BaseModel):
    node_id: int = Field(..., ge=1)
    flag_id: int = Field(..., ge=1)
    action: str = Field(..., pattern="^(assign|remove)$")
    user: Optional[str] = None


@router.get("/", response_model=List[RedFlagAuditRecord])
async def get_audit(
    node_id: Optional[int] = Query(None, ge=1),
    flag_id: Optional[int] = Query(None, ge=1),
    user: Optional[str] = Query(None),
    branch: bool = Query(False, description="Include descendants when node_id is specified"),
    limit: int = Query(100, ge=1, le=1000),
    repo: SQLiteRepository = Depends(get_repository)
):
    """List audit records with optional filtering."""
    try:
        if branch and node_id is not None:
            # Use the new method that supports branch scope
            records = repo.get_red_flag_audit_with_branch(
                node_id=node_id,
                flag_id=flag_id,
                user=user,
                branch=True,
                limit=limit
            )
        else:
            # Use the original method for non-branch queries
            records = repo.get_red_flag_audit(
                node_id=node_id,
                flag_id=flag_id,
                user=user,
                limit=limit
            )
        return records
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve audit records: {str(e)}"
        )


@router.post("/", response_model=RedFlagAuditRecord, status_code=201)
async def create_audit(
    record: RedFlagAuditCreate,
    repo: SQLiteRepository = Depends(get_repository)
):
    """Insert new audit record (used internally after flag operations)."""
    try:
        # Validate that node and flag exist
        node = repo.get_node(record.node_id)
        if not node:
            raise HTTPException(
                status_code=404,
                detail=f"Node with ID {record.node_id} not found"
            )
        
        flag = repo.get_red_flag(record.flag_id)
        if not flag:
            raise HTTPException(
                status_code=404,
                detail=f"Red flag with ID {record.flag_id} not found"
            )
        
        # Create audit record
        audit_id = repo.create_red_flag_audit(
            node_id=record.node_id,
            flag_id=record.flag_id,
            action=record.action,
            user=record.user
        )
        
        # Return the created record
        audit_record = repo.get_red_flag_audit_by_id(audit_id)
        if not audit_record:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve created audit record"
            )
        
        return audit_record
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create audit record: {str(e)}"
        )
