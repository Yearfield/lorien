"""
Additional route handlers for Phase 6B features.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
from datetime import datetime
import os

from storage.sqlite import SQLiteRepository
from .dependencies import get_repository

router = APIRouter()


# CreateRootRequest moved to api/routers/tree_vm_builder.py


# Tree export routes moved to tree_export_router.py to avoid route conflicts


# LEGACY — do not define /tree/roots here
# Route moved to api/routers/tree_vm_builder.py to avoid conflicts


# REMOVED: LLM fill-triage-actions endpoint moved to api/routers/llm.py
# This endpoint was conflicting with the new implementation


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
