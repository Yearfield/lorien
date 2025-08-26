"""
Route handlers for the decision tree API.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
import io
import sqlite3
from datetime import datetime

from storage.sqlite import SQLiteRepository
from core.models import Node, Triaging, RedFlag
from core.engine import DecisionTreeEngine

from .models import (
    ChildSlot, ChildrenUpsert, TriageDTO, IncompleteParentDTO,
    RedFlagAssignment, HealthResponse
)
from .dependencies import (
    get_repository, validate_parent_exists, validate_node_exists,
    validate_triage_exists
)
from .utils import normalize_label, validate_unique_slots, format_csv_export, get_missing_slots
from .exceptions import TooManyChildrenError, ConflictError

router = APIRouter()


# Health endpoint is now handled by the health router
# This endpoint is kept for backward compatibility but delegates to the new implementation


@router.get("/tree/next-incomplete-parent", response_model=IncompleteParentDTO)
async def get_next_incomplete_parent(repo: SQLiteRepository = Depends(get_repository)):
    """Get the next incomplete parent for the 'Skip to next incomplete parent' feature."""
    incomplete = repo.get_next_incomplete_parent()
    
    if not incomplete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No incomplete parents found"
        )
    
    # Parse missing slots from the view data
    missing_slots_str = incomplete["missing_slots"]
    missing_slots = [int(slot) for slot in missing_slots_str.split(",")] if missing_slots_str else []
    
    return IncompleteParentDTO(
        parent_id=incomplete["parent_id"],
        missing_slots=missing_slots
    )


@router.get("/tree/{parent_id}/children")
async def get_children(
    parent_id: int,
    parent: Node = Depends(validate_parent_exists),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get all children of a parent node."""
    children = repo.get_children(parent_id)
    
    return {
        "parent_id": parent_id,
        "children": [
            {
                "id": child.id,
                "slot": child.slot,
                "label": child.label,
                "depth": child.depth,
                "is_leaf": child.is_leaf
            }
            for child in children
        ]
    }


@router.post("/tree/{parent_id}/children")
async def upsert_children(
    parent_id: int,
    request: ChildrenUpsert,
    parent: Node = Depends(validate_parent_exists),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Atomic upsert of multiple children slots (1-5)."""
    # Validate request
    if len(request.children) > 5:
        raise TooManyChildrenError("Cannot have more than 5 children")
    
    # Validate unique slots
    slots = [child.slot for child in request.children]
    if len(slots) != len(set(slots)):
        raise ConflictError("Duplicate slots are not allowed")
    
    # Normalize labels
    normalized_children = []
    for child in request.children:
        try:
            normalized_label = normalize_label(child.label)
            normalized_children.append({
                "slot": child.slot,
                "label": normalized_label
            })
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid label for slot {child.slot}: {str(e)}"
            )
    
    # Use atomic upsert method
    try:
        result = repo.upsert_children_atomic(parent_id, normalized_children)
        
        # Check for errors
        if result["errors"]:
            error_details = "; ".join(result["errors"])
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Upsert conflicts: {error_details}"
            )
        
        return {
            "message": f"Successfully upserted {result['children_processed']} children",
            "details": {
                "created": result["children_created"],
                "updated": result["children_updated"],
                "processed": result["children_processed"]
            }
        }
        
    except sqlite3.IntegrityError as e:
        # Handle UNIQUE constraint violations
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Slot conflict: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database integrity error: {str(e)}"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upsert children: {str(e)}"
        )


@router.post("/tree/{parent_id}/child")
async def insert_child(
    parent_id: int,
    child: ChildSlot,
    parent: Node = Depends(validate_parent_exists),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Insert or replace a single child slot."""
    # Validate slot
    if child.slot < 1 or child.slot > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slot must be between 1 and 5"
        )
    
    # Normalize label
    try:
        normalized_label = normalize_label(child.label)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid label: {str(e)}"
        )
    
    # Check if slot already exists
    existing_children = repo.get_children(parent_id)
    existing_child = next((c for c in existing_children if c.slot == child.slot), None)
    
    try:
        if existing_child:
            # Update existing child
            existing_child.label = normalized_label
            repo.update_node(existing_child)
            return {"message": f"Updated child in slot {child.slot}"}
        else:
            # Create new child
            new_child = Node(
                parent_id=parent_id,
                depth=parent.depth + 1,
                slot=child.slot,
                label=normalized_label,
                is_leaf=(parent.depth + 1 == 5)
            )
            child_id = repo.create_node(new_child)
            return {"message": f"Created child in slot {child.slot}", "child_id": child_id}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to insert child: {str(e)}"
        )


@router.get("/triage/{node_id}")
async def get_triage(
    node_id: int,
    triage: Triaging = Depends(validate_triage_exists)
):
    """Get triage information for a node."""
    return TriageDTO(
        diagnostic_triage=triage.diagnostic_triage,
        actions=triage.actions
    )


@router.put("/triage/{node_id}")
async def update_triage(
    node_id: int,
    triage_data: TriageDTO,
    node: Node = Depends(validate_node_exists),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Update triage information for a node."""
    # Validate that at least one field is provided
    if triage_data.diagnostic_triage is None and triage_data.actions is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field (diagnostic_triage or actions) must be provided"
        )
    
    # Get existing triage or create new
    existing_triage = repo.get_triage(node_id)
    
    if existing_triage:
        # Update existing triage
        if triage_data.diagnostic_triage is not None:
            existing_triage.diagnostic_triage = triage_data.diagnostic_triage
        if triage_data.actions is not None:
            existing_triage.actions = triage_data.actions
        existing_triage.updated_at = datetime.now()
    else:
        # Create new triage
        existing_triage = Triaging(
            node_id=node_id,
            diagnostic_triage=triage_data.diagnostic_triage or "",
            actions=triage_data.actions or ""
        )
    
    try:
        repo.create_triage(existing_triage)
        return {"message": "Triage updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update triage: {str(e)}"
        )


@router.get("/flags/search")
async def search_flags(
    q: str,
    repo: SQLiteRepository = Depends(get_repository)
):
    """Search red flags by name."""
    if not q.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty"
        )
    
    flags = repo.search_red_flags(q.strip())
    
    return {
        "query": q,
        "flags": [
            {
                "id": flag.id,
                "name": flag.name,
                "description": flag.description,
                "severity": flag.severity
            }
            for flag in flags
        ]
    }


@router.post("/flags/assign")
async def assign_flag(
    assignment: RedFlagAssignment,
    node: Node = Depends(validate_node_exists),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Assign a red flag to a node."""
    # Search for the red flag
    flags = repo.search_red_flags(assignment.red_flag_name)
    
    if not flags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Red flag '{assignment.red_flag_name}' not found"
        )
    
    # Use the first matching flag (exact match preferred)
    flag = flags[0]
    
    try:
        repo.assign_red_flag_to_node(assignment.node_id, flag.id)
        return {"message": f"Assigned red flag '{flag.name}' to node {assignment.node_id}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign red flag: {str(e)}"
        )


@router.get("/calc/export")
async def export_calculator_csv(
    repo: SQLiteRepository = Depends(get_repository)
):
    """Export calculator CSV with streaming response."""
    try:
        # Get all nodes and build tree data
        # This is a simplified implementation - in practice, you'd want to
        # build the full tree structure from the database
        
        # For now, return a sample CSV structure
        sample_data = [
            {
                "Vital Measurement": "Hypertension",
                "Node 1": "Severe",
                "Node 2": "Emergency",
                "Node 3": "ICU",
                "Node 4": "Ventilator",
                "Node 5": "Critical"
            }
        ]
        
        csv_content = format_csv_export(sample_data)
        
        # Create streaming response
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=calculator_export.csv",
                "Content-Type": "text/csv; charset=utf-8"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export CSV: {str(e)}"
        )
