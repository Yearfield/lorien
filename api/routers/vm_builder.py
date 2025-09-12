"""
VM Builder endpoints for draft management and publishing.

Provides endpoints for creating, managing, and publishing VM Builder drafts
with diff preview capabilities.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict, Any
import logging

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository
from ..repositories.vm_builder import VMBuilderManager

router = APIRouter(tags=["vm-builder"])

@router.post("/tree/vm/draft")
async def create_draft(
    parent_id: int,
    draft_data: Dict[str, Any],
    actor: str = "admin",
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Create a new VM Builder draft.
    
    Args:
        parent_id: Parent node ID for the draft
        draft_data: Draft configuration data
        actor: Who is creating the draft
        
    Returns:
        Created draft information
    """
    try:
        with repo._get_connection() as conn:
            manager = VMBuilderManager(conn)
            
            # Validate parent exists
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM nodes WHERE id = ?", (parent_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "parent_not_found",
                        "message": f"Parent node {parent_id} not found"
                    }
                )
            
            draft_id = manager.create_draft(parent_id, draft_data, actor)
            
            return {
                "success": True,
                "message": "Draft created successfully",
                "draft_id": draft_id,
                "parent_id": parent_id,
                "actor": actor
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating draft: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to create draft",
                "message": str(e)
            }
        )

@router.get("/tree/vm/draft/{draft_id}")
async def get_draft(
    draft_id: str,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get a VM Builder draft.
    
    Args:
        draft_id: Draft ID
        
    Returns:
        Draft data
    """
    try:
        with repo._get_connection() as conn:
            manager = VMBuilderManager(conn)
            
            draft = manager.get_draft(draft_id)
            if not draft:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "draft_not_found",
                        "message": f"Draft {draft_id} not found"
                    }
                )
            
            return {
                "draft": draft,
                "status": "success"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting draft: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get draft",
                "message": str(e)
            }
        )

@router.put("/tree/vm/draft/{draft_id}")
async def update_draft(
    draft_id: str,
    draft_data: Dict[str, Any],
    actor: str = "admin",
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Update a VM Builder draft.
    
    Args:
        draft_id: Draft ID
        draft_data: Updated draft data
        actor: Who is updating the draft
        
    Returns:
        Update result
    """
    try:
        with repo._get_connection() as conn:
            manager = VMBuilderManager(conn)
            
            success = manager.update_draft(draft_id, draft_data, actor)
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "draft_not_found_or_published",
                        "message": f"Draft {draft_id} not found or already published"
                    }
                )
            
            return {
                "success": True,
                "message": "Draft updated successfully",
                "draft_id": draft_id,
                "actor": actor
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating draft: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to update draft",
                "message": str(e)
            }
        )

@router.delete("/tree/vm/draft/{draft_id}")
async def delete_draft(
    draft_id: str,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Delete a VM Builder draft.
    
    Args:
        draft_id: Draft ID
        
    Returns:
        Delete result
    """
    try:
        with repo._get_connection() as conn:
            manager = VMBuilderManager(conn)
            
            success = manager.delete_draft(draft_id)
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "draft_not_found_or_published",
                        "message": f"Draft {draft_id} not found or already published"
                    }
                )
            
            return {
                "success": True,
                "message": "Draft deleted successfully",
                "draft_id": draft_id
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting draft: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to delete draft",
                "message": str(e)
            }
        )

@router.get("/tree/vm/drafts")
async def list_drafts(
    parent_id: Optional[int] = Query(None),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    List VM Builder drafts.
    
    Args:
        parent_id: Filter by parent ID (optional)
        
    Returns:
        List of draft summaries
    """
    try:
        with repo._get_connection() as conn:
            manager = VMBuilderManager(conn)
            
            drafts = manager.list_drafts(parent_id)
            
            return {
                "drafts": drafts,
                "count": len(drafts),
                "parent_id": parent_id
            }
    
    except Exception as e:
        logging.error(f"Error listing drafts: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to list drafts",
                "message": str(e)
            }
        )

@router.post("/tree/vm/draft/{draft_id}/plan")
async def plan_draft(
    draft_id: str,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Calculate diff plan for a VM Builder draft.
    
    Args:
        draft_id: Draft ID
        
    Returns:
        Diff plan with operations
    """
    try:
        with repo._get_connection() as conn:
            manager = VMBuilderManager(conn)
            
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
            
            if draft["status"] != "draft":
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "draft_not_draft",
                        "message": f"Draft {draft_id} is not in draft status"
                    }
                )
            
            diff = manager.calculate_diff(draft_id)
            
            return {
                "success": True,
                "message": "Diff plan calculated successfully",
                "diff": diff
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error planning draft: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to plan draft",
                "message": str(e)
            }
        )

@router.post("/tree/vm/draft/{draft_id}/publish")
async def publish_draft(
    draft_id: str,
    actor: str = "admin",
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Publish a VM Builder draft.
    
    Args:
        draft_id: Draft ID
        actor: Who is publishing the draft
        
    Returns:
        Publish result with audit information
    """
    try:
        with repo._get_connection() as conn:
            manager = VMBuilderManager(conn)
            
            result = manager.publish_draft(draft_id, actor)
            
            return {
                "success": True,
                "message": "Draft published successfully",
                "result": result
            }
    
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_draft",
                "message": str(e)
            }
        )
    except Exception as e:
        logging.error(f"Error publishing draft: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to publish draft",
                "message": str(e)
            }
        )

@router.get("/tree/vm/stats")
async def get_vm_stats(
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get VM Builder statistics.
    
    Returns:
        VM Builder statistics
    """
    try:
        with repo._get_connection() as conn:
            manager = VMBuilderManager(conn)
            
            stats = manager.get_draft_stats()
            
            return {
                "stats": stats,
                "status": "healthy"
            }
    
    except Exception as e:
        logging.error(f"Error getting VM stats: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get VM stats",
                "message": str(e)
            }
        )
