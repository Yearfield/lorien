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
        triage_style = request.get("triage_style", "diagnosis-only")
        actions_style = request.get("actions_style", "referral-only")
        apply = request.get("apply", False)
        
        if not root_label or len(nodes) != 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid path context: root and exactly 5 nodes required"
            )
        
        # Validate style values
        valid_triage_styles = ["diagnosis-only", "referral-only"]
        valid_actions_styles = ["diagnosis-only", "referral-only"]
        
        if triage_style not in valid_triage_styles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid triage_style. Must be one of: {valid_triage_styles}"
            )
        
        if actions_style not in valid_actions_styles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid actions_style. Must be one of: {valid_actions_styles}"
            )
        
        # Mock LLM response for now (in real implementation, call actual LLM)
        # This is guidance-only and will be reviewed by user
        raw_diagnostic_triage = f"Based on the path {root_label} → {' → '.join(nodes)}, consider {triage_style} assessment."
        raw_actions = f"Recommended {actions_style} actions for this clinical scenario."
        
        # Use new text utilities for word limits and validation
        from core.text_utils import truncate_to_words, enforce_phrase_rules
        
        TRIAGE_MAX_WORDS = 7
        ACTIONS_MAX_WORDS = 7
        
        # Truncate to word limits
        diagnostic_triage = truncate_to_words(raw_diagnostic_triage, TRIAGE_MAX_WORDS)
        actions = truncate_to_words(raw_actions, ACTIONS_MAX_WORDS)
        
        # Validate and clean using phrase rules
        try:
            diagnostic_triage = enforce_phrase_rules(diagnostic_triage, TRIAGE_MAX_WORDS)
            actions = enforce_phrase_rules(actions, ACTIONS_MAX_WORDS)
        except ValueError as e:
            # If phrase rules fail, truncate and continue (guidance-only)
            diagnostic_triage = truncate_to_words(diagnostic_triage, TRIAGE_MAX_WORDS)
            actions = truncate_to_words(actions, ACTIONS_MAX_WORDS)
        
        # If apply is requested, enforce leaf-only upsert
        if apply:
            # PM contract: 422 with suggestions at TOP-LEVEL + error string
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=422,
                content={
                    "error": "Cannot apply triage/actions to non-leaf node",
                    "diagnostic_triage": diagnostic_triage,
                    "actions": actions,
                },
            )
        
        return {
            "diagnostic_triage": diagnostic_triage,
            "actions": actions
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


@router.post("/backup")
async def create_backup(
    repo: SQLiteRepository = Depends(get_repository)
):
    """Create a backup of the database."""
    try:
        import subprocess
        import os
        from datetime import datetime
        
        # Get database path from repository
        db_path = repo._db_path
        if not os.path.exists(db_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Database file not found"
            )
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(os.path.dirname(db_path), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"lorien_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy database file
        import shutil
        shutil.copy2(db_path, backup_path)
        
        # Run integrity check
        integrity_result = repo.check_integrity()
        
        return {
            "ok": True,
            "path": backup_path,
            "integrity": integrity_result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create backup: {str(e)}"
        )


@router.post("/restore")
async def restore_backup(
    repo: SQLiteRepository = Depends(get_repository)
):
    """Restore from the latest backup."""
    try:
        import subprocess
        import os
        from datetime import datetime
        
        # Get database path from repository
        db_path = repo._db_path
        backup_dir = os.path.join(os.path.dirname(db_path), "backups")
        
        if not os.path.exists(backup_dir):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No backup directory found"
            )
        
        # Find latest backup file
        backup_files = []
        for file in os.listdir(backup_dir):
            if file.startswith("lorien_backup_") and file.endswith(".db"):
                backup_files.append(file)
        
        if not backup_files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No backup files found"
            )
        
        # Sort by timestamp and get latest
        backup_files.sort(reverse=True)
        latest_backup = backup_files[0]
        backup_path = os.path.join(backup_dir, latest_backup)
        
        # Create a backup of current database before restore
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_backup = f"lorien_pre_restore_{timestamp}.db"
        current_backup_path = os.path.join(backup_dir, current_backup)
        
        import shutil
        shutil.copy2(db_path, current_backup_path)
        
        # Restore from backup
        shutil.copy2(backup_path, db_path)
        
        # Run integrity check
        integrity_result = repo.check_integrity()
        
        return {
            "ok": True,
            "path": backup_path,
            "pre_restore_backup": current_backup_path,
            "integrity": integrity_result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restore backup: {str(e)}"
        )


@router.get("/backup/status")
async def get_backup_status(
    repo: SQLiteRepository = Depends(get_repository)
):
    """Get backup status and available backups."""
    try:
        import os
        
        # Get database path from repository
        db_path = repo._db_path
        backup_dir = os.path.join(os.path.dirname(db_path), "backups")
        
        if not os.path.exists(backup_dir):
            return {
                "backup_directory": backup_dir,
                "exists": False,
                "backups": []
            }
        
        # List available backups
        backup_files = []
        for file in os.listdir(backup_dir):
            if file.startswith("lorien_backup_") and file.endswith(".db"):
                file_path = os.path.join(backup_dir, file)
                stat = os.stat(file_path)
                backup_files.append({
                    "filename": file,
                    "path": file_path,
                    "size_bytes": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Sort by creation time (newest first)
        backup_files.sort(key=lambda x: x["created"], reverse=True)
        
        return {
            "backup_directory": backup_dir,
            "exists": True,
            "backups": backup_files,
            "total_backups": len(backup_files)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get backup status: {str(e)}"
        )


@router.get("/flags/preview-assign")
async def preview_flag_assignment(
    node_id: int = Query(..., description="Node ID to assign flag to"),
    flag_id: int = Query(..., description="Red flag ID to assign"),
    cascade: bool = Query(False, description="Whether to cascade to descendants"),
    repo: SQLiteRepository = Depends(get_repository)
):
    """Preview the effect of assigning a red flag to a node."""
    try:
        # Validate that the node exists
        node = repo.get_node(node_id)
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Node with ID {node_id} not found"
            )
        
        # Validate that the flag exists
        flags = repo.search_red_flags_by_id(flag_id)
        if not flags:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Red flag with ID {flag_id} not found"
            )
        
        flag = flags[0]
        
        # Calculate affected nodes
        if cascade:
            # Get all descendants using recursive CTE
            descendants = repo.get_descendant_nodes(node_id)
            nodes_to_process = [node_id] + descendants
        else:
            nodes_to_process = [node_id]
        
        # Return preview (truncate to first 200 for UI)
        preview_nodes = nodes_to_process[:200]
        
        return {
            "flag_name": flag.name,
            "node_id": node_id,
            "cascade": cascade,
            "count": len(nodes_to_process),
            "nodes": preview_nodes if len(nodes_to_process) <= 200 else None,
            "truncated": len(nodes_to_process) > 200
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview flag assignment: {str(e)}"
        )
