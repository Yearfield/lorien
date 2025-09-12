"""
Concurrency control endpoints for optimistic concurrency.

Provides endpoints for version checking, conflict resolution,
and concurrent edit management.
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from typing import Optional, Dict, Any
import logging

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository
from ..repositories.concurrency import ConcurrencyManager

router = APIRouter(tags=["concurrency"])

@router.get("/concurrency/node/{node_id}/version")
async def get_node_version(
    node_id: int,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get version information for a node.
    
    Args:
        node_id: Node ID to get version for
        
    Returns:
        Version information including version number, timestamp, and ETag
    """
    try:
        with repo._get_connection() as conn:
            manager = ConcurrencyManager(conn)
            version_info = manager.get_node_version(node_id)
            
            if not version_info:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "node_not_found",
                        "message": f"Node {node_id} not found"
                    }
                )
            
            return {
                "node_id": node_id,
                "version": version_info["version"],
                "updated_at": version_info["updated_at"],
                "etag": manager.create_etag(version_info),
                "concurrency_enabled": True
            }
    
    except Exception as e:
        logging.error(f"Error getting node version: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get node version",
                "message": str(e)
            }
        )

@router.get("/concurrency/node/{node_id}/children-with-version")
async def get_children_with_version(
    node_id: int,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get children for a node with version information.
    
    Args:
        node_id: Parent node ID
        
    Returns:
        Children list with parent version information
    """
    try:
        with repo._get_connection() as conn:
            manager = ConcurrencyManager(conn)
            children, parent_version = manager.get_children_with_versions(node_id)
            
            if not parent_version:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "node_not_found",
                        "message": f"Node {node_id} not found"
                    }
                )
            
            return {
                "parent_id": node_id,
                "children": children,
                "parent_version": parent_version["version"],
                "parent_updated_at": parent_version["updated_at"],
                "etag": manager.create_etag(parent_version),
                "concurrency_enabled": True
            }
    
    except Exception as e:
        logging.error(f"Error getting children with version: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get children with version",
                "message": str(e)
            }
        )

@router.post("/concurrency/check-version")
async def check_version(
    request_data: dict,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Check if a node's version matches the expected version.
    
    Args:
        request_data: Dict with node_id and expected_version
        
    Returns:
        Version check result
    """
    try:
        node_id = request_data.get("node_id")
        expected_version = request_data.get("expected_version")
        
        if node_id is None or expected_version is None:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "missing_parameters",
                    "message": "node_id and expected_version are required"
                }
            )
        
        with repo._get_connection() as conn:
            manager = ConcurrencyManager(conn)
            is_match, current_version = manager.check_version_match(node_id, expected_version)
            
            if not current_version:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "node_not_found",
                        "message": f"Node {node_id} not found"
                    }
                )
            
            if not is_match:
                return {
                    "is_match": False,
                    "current_version": current_version["version"],
                    "expected_version": expected_version,
                    "conflict_info": manager.handle_version_conflict(
                        node_id, expected_version, current_version
                    )
                }
            
            return {
                "is_match": True,
                "current_version": current_version["version"],
                "expected_version": expected_version,
                "message": "Version match confirmed"
            }
    
    except Exception as e:
        logging.error(f"Error checking version: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to check version",
                "message": str(e)
            }
        )

@router.get("/concurrency/conflict-resolution-info")
async def get_conflict_resolution_info():
    """
    Get information about conflict resolution strategies.
    
    Returns:
        Conflict resolution information and guidance
    """
    return {
        "conflict_types": {
            "version_conflict": {
                "status_code": 412,
                "description": "Data has been modified by another user",
                "resolution": "Reload data and retry with current version"
            },
            "slot_conflict": {
                "status_code": 409,
                "description": "Slot is already occupied",
                "resolution": "Choose a different slot or resolve slot conflict"
            }
        },
        "headers": {
            "If-Match": "Use current version number for optimistic concurrency",
            "Authorization": "Bearer token for write operations (if enabled)"
        },
        "best_practices": [
            "Always check version before making changes",
            "Use If-Match header for write operations",
            "Handle 412 responses by reloading and retrying",
            "Handle 409 responses by choosing different slots"
        ]
    }

def validate_if_match_header(if_match: Optional[str] = Header(None)) -> Optional[int]:
    """
    Validate and extract version from If-Match header.
    
    Args:
        if_match: If-Match header value
        
    Returns:
        Version number if valid, None if not provided
        
    Raises:
        HTTPException: If If-Match header is malformed
    """
    if not if_match:
        return None
    
    try:
        # Support both "version:123" and "123" formats
        if ":" in if_match:
            version_str = if_match.split(":")[-1].strip()
        else:
            version_str = if_match.strip()
        
        return int(version_str)
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_if_match_header",
                "message": "If-Match header must be a valid version number",
                "expected_format": "version:123 or 123"
            }
        )

def check_concurrency_requirements(
    node_id: int,
    expected_version: Optional[int],
    repo: SQLiteRepository
) -> Dict[str, Any]:
    """
    Check concurrency requirements and return appropriate response.
    
    Args:
        node_id: Node ID to check
        expected_version: Expected version (from If-Match header)
        repo: Repository instance
        
    Returns:
        Concurrency check result
        
    Raises:
        HTTPException: If version mismatch (412) or other errors
    """
    try:
        with repo._get_connection() as conn:
            manager = ConcurrencyManager(conn)
            
            if expected_version is not None:
                is_match, current_version = manager.check_version_match(node_id, expected_version)
                
                if not current_version:
                    raise HTTPException(
                        status_code=404,
                        detail={
                            "error": "node_not_found",
                            "message": f"Node {node_id} not found"
                        }
                    )
                
                if not is_match:
                    conflict_info = manager.handle_version_conflict(
                        node_id, expected_version, current_version
                    )
                    raise HTTPException(
                        status_code=412,
                        detail=conflict_info
                    )
                
                return {
                    "version_checked": True,
                    "current_version": current_version["version"],
                    "etag": manager.create_etag(current_version)
                }
            
            return {"version_checked": False}
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error checking concurrency requirements: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to check concurrency requirements",
                "message": str(e)
            }
        )
