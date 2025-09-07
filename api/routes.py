"""
Route handlers for the decision tree API.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, File, Query
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
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


@router.get("/tree/next-incomplete-parent")
async def get_next_incomplete_parent(repo: SQLiteRepository = Depends(get_repository)):
    """Get the next incomplete parent for the 'Skip to next incomplete parent' feature."""
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            # Use CTE to find next incomplete parent
            cursor.execute("""
                WITH parent_slots AS (
                    SELECT p.id AS parent_id, p.label, p.depth,
                           GROUP_CONCAT(s.slot) AS present
                    FROM nodes p
                    LEFT JOIN nodes s ON s.parent_id = p.id
                    GROUP BY p.id
                ),
                missing AS (
                    SELECT parent_id, label, depth,
                           CASE
                             WHEN COALESCE(present, '') LIKE '%1%' THEN '' ELSE '1,' END ||
                           CASE
                             WHEN COALESCE(present, '') LIKE '%2%' THEN '' ELSE '2,' END ||
                           CASE
                             WHEN COALESCE(present, '') LIKE '%3%' THEN '' ELSE '3,' END ||
                           CASE
                             WHEN COALESCE(present, '') LIKE '%4%' THEN '' ELSE '4,' END ||
                           CASE
                             WHEN COALESCE(present, '') LIKE '%5%' THEN '' ELSE '5' END
                           AS missing_slots_raw,
                           COALESCE(present, '') AS present_slots
                    FROM parent_slots
                ),
                cleaned AS (
                    SELECT parent_id, label, depth,
                           RTRIM(missing_slots_raw, ',') AS missing_slots
                    FROM missing
                )
                SELECT parent_id, label, depth, missing_slots
                FROM cleaned
                WHERE missing_slots <> ''
                ORDER BY depth ASC, parent_id ASC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            
            if not row:
                # No incomplete parents found - return 204
                return JSONResponse(status_code=204, content=None)

            return {
                "parent_id": row[0],
                "label": row[1],
                "depth": row[2],
                "missing_slots": row[3]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get next incomplete parent: {str(e)}"
        )


@router.get("/tree/{parent_id:int}/children")
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


@router.post("/tree/{parent_id:int}/children")
async def upsert_children(
    parent_id: int,
    request: ChildrenUpsert,
    parent: Node = Depends(validate_parent_exists),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Atomic upsert of multiple children slots (1-5)."""
    # Pydantic model enforces exactly 5 children
    
    # Validate unique slots
    slots = [child.slot for child in request.children]
    if len(slots) != len(set(slots)):
        raise ConflictError("Duplicate slots are not allowed")
    
    # Normalize labels
    normalized_children = []
    for idx, child in enumerate(request.children):
        try:
            normalized_label = normalize_label(child.label)
            normalized_children.append({
                "slot": child.slot,
                "label": normalized_label
            })
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[{
                    "loc": ["body", "children", idx, "label"],
                    "msg": str(e),
                    "type": "value_error"
                }]
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


@router.post("/tree/{parent_id:int}/child")
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


@router.get("/triage/search")
async def search_triage(
    leaf_only: bool = Query(True, description="Only return leaf nodes"),
    query: Optional[str] = Query(None, description="Search in triage/actions"),
    vm: Optional[str] = Query(None, description="Filter by Vital Measurement"),
    sort: Optional[str] = Query("updated_at:desc", description="Sort order (e.g., updated_at:desc)"),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="Maximum number of results"),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Search triage records with optional filtering."""
    results = repo.search_triage_records(
        leaf_only=leaf_only, 
        query=query, 
        vm=vm,
        sort=sort,
        limit=limit
    )
    
    # Handle both list and dict responses from repository
    if isinstance(results, dict) and "results" in results:
        items = results["results"]
        total_count = results.get("total_count", len(items))
    else:
        items = results
        total_count = len(results)
    
    return {
        "items": items,
        "total_count": total_count,
        "leaf_only": leaf_only,
        "vm": vm,
        "sort": sort,
        "limit": limit
    }


@router.get("/triage/{node_id:int}")
async def get_triage(
    node_id: int,
    triage: Triaging = Depends(validate_triage_exists)
):
    """Get triage information for a node."""
    return TriageDTO(
        diagnostic_triage=triage.diagnostic_triage,
        actions=triage.actions
    )


@router.get("/tree/missing-slots")
async def get_missing_slots(
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get all parents with missing child slots."""
    missing_data = repo.get_parents_with_missing_slots()
    return {
        "parents_with_missing_slots": missing_data,
        "total_count": len(missing_data)
    }


from core.validation.outcomes import normalize_phrase, validate_phrase


class TriageUpdate(BaseModel):
    """Triage update model with manual validation."""
    diagnostic_triage: str
    actions: str


@router.put("/triage/{node_id:int}")
async def update_triage(
    node_id: int,
    update: TriageUpdate,
    repo: SQLiteRepository = Depends(get_repository)
):
    """Update triage for a node (leaf-only)."""
    # Validate node is a leaf
    node = repo.get_node(node_id)
    if not node or not node.is_leaf:
        raise HTTPException(
            status_code=422,
            detail="Triage can only be updated for leaf nodes"
        )

    # Normalize and validate
    triage = normalize_phrase(update.diagnostic_triage)
    actions = normalize_phrase(update.actions)
    validate_phrase("diagnostic_triage", triage)
    validate_phrase("actions", actions)

    # Update triage
    success = repo.update_triage(node_id, triage, actions)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to update triage"
        )

    return {
        "node_id": node_id,
        "diagnostic_triage": triage,
        "actions": actions,
        "is_leaf": True
    }


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
    repo: SQLiteRepository = Depends(get_repository)
):
    """Assign a red flag to a node, optionally cascading to descendants."""
    # Validate that the node exists
    node = repo.get_node(assignment.node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node with ID {assignment.node_id} not found"
        )
    
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
        affected_nodes = []
        
        if assignment.cascade:
            # Get all descendants using recursive CTE
            descendants = repo.get_descendant_nodes(assignment.node_id)
            nodes_to_process = [assignment.node_id] + descendants
        else:
            nodes_to_process = [assignment.node_id]
        
        # Process each node
        for node_id in nodes_to_process:
            # Assign the flag
            repo.assign_red_flag_to_node(node_id, flag.id)
            
            # Create audit record
            repo.create_red_flag_audit(
                node_id=node_id,
                flag_id=flag.id,
                action="assign",
                user=assignment.user
            )
            
            affected_nodes.append(node_id)
        
        return {
            "message": f"Assigned red flag '{flag.name}' to {len(affected_nodes)} node(s)",
            "affected_nodes": affected_nodes,
            "flag_id": flag.id,
            "cascade": assignment.cascade
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign red flag: {str(e)}"
        )


@router.post("/flags/remove")
async def remove_flag(
    assignment: RedFlagAssignment,
    repo: SQLiteRepository = Depends(get_repository)
):
    """Remove a red flag from a node, optionally cascading to descendants."""
    # Validate that the node exists
    node = repo.get_node(assignment.node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node with ID {assignment.node_id} not found"
        )
    
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
        affected_nodes = []
        
        if assignment.cascade:
            # Get all descendants using recursive CTE
            descendants = repo.get_descendant_nodes(assignment.node_id)
            nodes_to_process = [assignment.node_id] + descendants
        else:
            nodes_to_process = [assignment.node_id]
        
        # Process each node
        for node_id in nodes_to_process:
            # Remove the flag
            repo.remove_red_flag_from_node(node_id, flag.id)
            
            # Create audit record
            repo.create_red_flag_audit(
                node_id=node_id,
                flag_id=flag.id,
                action="remove",
                user=assignment.user
            )
            
            affected_nodes.append(node_id)
        
        return {
            "message": f"Removed red flag '{flag.name}' from {len(affected_nodes)} node(s)",
            "affected_nodes": affected_nodes,
            "flag_id": flag.id,
            "cascade": assignment.cascade
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove red flag: {str(e)}"
        )


# Import Excel endpoint moved to api/routers/import_jobs.py


@router.get("/calc/export")
async def export_calculator_csv(
    repo: SQLiteRepository = Depends(get_repository)
):
    """Export calculator CSV with streaming response."""
    try:
        # Get tree data from database with exactly 5 children per parent
        tree_data = repo.get_tree_data_for_csv()
        
        if not tree_data:
            # Return empty CSV with headers if no data
            csv_content = format_csv_export([])
        else:
            csv_content = format_csv_export(tree_data)
        
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


@router.get("/tree/export")
async def export_tree_csv(
    repo: SQLiteRepository = Depends(get_repository)
):
    """Export tree data to CSV with streaming response."""
    try:
        # Get tree data from database with exactly 5 children per parent
        tree_data = repo.get_tree_data_for_csv()
        
        if not tree_data:
            # Return empty CSV with headers if no data
            csv_content = format_csv_export([])
        else:
            csv_content = format_csv_export(tree_data)
        
        # Create streaming response
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=tree_export.csv",
                "Content-Type": "text/csv; charset=utf-8"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export CSV: {str(e)}"
        )


@router.get("/calc/export.xlsx")
async def export_calculator_xlsx(
    repo: SQLiteRepository = Depends(get_repository)
):
    """Export calculator data as Excel workbook."""
    try:
        import pandas as pd
        from io import BytesIO
        
        # Get tree data using the same logic as CSV export
        tree_data = repo.get_tree_data_for_csv()
        
        if not tree_data:
            # Create empty DataFrame with headers
            df = pd.DataFrame(columns=[
                "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5", 
                "Diagnostic Triage", "Actions"
            ])
        else:
            # Convert to DataFrame with exact column order
            df_data = []
            for row in tree_data:
                df_row = {
                    "Vital Measurement": row.get("Diagnosis", row.get("Vital Measurement", "")),
                    "Node 1": row.get("Node 1", ""),
                    "Node 2": row.get("Node 2", ""),
                    "Node 3": row.get("Node 3", ""),
                    "Node 4": row.get("Node 4", ""),
                    "Node 5": row.get("Node 5", ""),
                    "Diagnostic Triage": row.get("Diagnostic Triage", ""),
                    "Actions": row.get("Actions", "")
                }
                df_data.append(df_row)
            
            df = pd.DataFrame(df_data)
        
        # Create Excel file in memory
        bio = BytesIO()
        with pd.ExcelWriter(bio, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="CalculatorExport")
        bio.seek(0)
        
        # Return streaming response
        return StreamingResponse(
            io.BytesIO(bio.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=calculator_export.xlsx",
                "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export Excel: {str(e)}"
        )
