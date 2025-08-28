"""
Additional route handlers for Phase 6B features.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
import io
from datetime import datetime
import os

from storage.sqlite import SQLiteRepository
from .dependencies import get_repository

router = APIRouter()


@router.get("/tree/export.xlsx")
async def export_tree_xlsx(
    repo: SQLiteRepository = Depends(get_repository)
):
    """Export tree data as Excel workbook."""
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
            df.to_excel(writer, index=False, sheet_name="TreeExport")
        bio.seek(0)
        
        # Return streaming response
        return StreamingResponse(
            io.BytesIO(bio.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=tree_export.xlsx",
                "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export Excel: {str(e)}"
        )


@router.get("/tree/stats")
async def get_tree_stats(
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get tree completeness statistics."""
    try:
        stats = repo.get_tree_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tree stats: {str(e)}"
        )


@router.post("/tree/roots")
async def create_root_with_children(
    request: dict,
    repo: SQLiteRepository = Depends(get_repository)
):
    """Create a new root (vital measurement) with 5 preseeded child slots."""
    try:
        label = request.get("label", "").strip()
        if not label:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Root label cannot be empty"
            )
        
        # Optional initial children (up to 5)
        initial_children = request.get("children", [])
        if len(initial_children) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot have more than 5 initial children"
            )
        
        # Create root node (depth=0, no parent, slot=0)
        root_id = repo.create_root_node(label)
        
        # Create 5 child slots
        children_created = []
        for slot in range(1, 6):
            child_label = initial_children[slot - 1] if slot <= len(initial_children) else ""
            child_id = repo.create_child_node(root_id, slot, child_label, depth=1)
            
            children_created.append({
                "id": child_id,
                "slot": slot,
                "label": child_label
            })
        
        return {
            "root_id": root_id,
            "children": children_created,
            "message": f"Created root '{label}' with 5 child slots"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create root: {str(e)}"
        )


@router.post("/llm/fill-triage-actions")
async def fill_triage_actions(
    request: dict,
    repo: SQLiteRepository = Depends(get_repository)
):
    """Fill triage actions using LLM (guidance only, no auto-apply)."""
    try:
        # Check if LLM is enabled
        llm_enabled = os.getenv("LLM_ENABLED", "false").lower() == "true"
        if not llm_enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM service is disabled"
            )
        
        # Extract path context
        root_label = request.get("root", "")
        nodes = request.get("nodes", [])
        triage_style = request.get("triage_style", "clinical")
        actions_style = request.get("actions_style", "practical")
        
        if not root_label or len(nodes) != 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid path context: root and exactly 5 nodes required"
            )
        
        # Mock LLM response for now (in real implementation, call actual LLM)
        # This is guidance-only and will be reviewed by user
        diagnostic_triage = f"Based on the path {root_label} → {' → '.join(nodes)}, consider {triage_style} assessment."
        actions = f"Recommended {actions_style} actions for this clinical scenario."
        
        return {
            "diagnostic_triage": diagnostic_triage,
            "actions": actions,
            "note": "AI suggestions are guidance-only; dosing and diagnosis are refused. Review before saving."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fill triage actions: {str(e)}"
        )


@router.get("/tree/conflicts/duplicate-labels")
async def get_duplicate_labels(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get nodes with duplicate labels under the same parent."""
    try:
        duplicates = repo.get_duplicate_labels(limit=limit, offset=offset)
        return duplicates
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get duplicate labels: {str(e)}"
        )


@router.get("/tree/conflicts/orphans")
async def get_orphan_nodes(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get orphan nodes with invalid parent_id references."""
    try:
        orphans = repo.get_orphan_nodes(limit=limit, offset=offset)
        return orphans
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get orphan nodes: {str(e)}"
        )


@router.get("/tree/conflicts/depth-anomalies")
async def get_depth_anomalies(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get nodes with invalid depth values."""
    try:
        anomalies = repo.get_depth_anomalies(limit=limit, offset=offset)
        return anomalies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get depth anomalies: {str(e)}"
        )
