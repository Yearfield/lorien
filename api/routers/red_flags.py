"""
Red flags router for bulk operations and audit.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/red-flags", tags=["red-flags"])


class BulkAttachRequest(BaseModel):
    node_id: int
    red_flag_ids: List[int]


class BulkDetachRequest(BaseModel):
    node_id: int
    red_flag_ids: List[int]


class RedFlagAuditResponse(BaseModel):
    id: int
    node_id: int
    red_flag_id: int
    action: str
    ts: str
    red_flag_name: Optional[str] = None


@router.post("/bulk-attach")
async def bulk_attach(
    request: BulkAttachRequest,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Bulk attach red flags to a node.
    
    Args:
        request: Node ID and list of red flag IDs to attach
        repo: Database repository
        
    Returns:
        Success message with count of flags attached
    """
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            # Begin transaction
            cursor.execute("BEGIN TRANSACTION")
            
            attached_count = 0
            for flag_id in request.red_flag_ids:
                try:
                    # Check if flag exists
                    cursor.execute("SELECT id FROM red_flags WHERE id = ?", (flag_id,))
                    if not cursor.fetchone():
                        logger.warning(f"Red flag {flag_id} not found, skipping")
                        continue
                    
                    # Check if already attached
                    cursor.execute(
                        "SELECT 1 FROM node_red_flags WHERE node_id = ? AND red_flag_id = ?",
                        (request.node_id, flag_id)
                    )
                    if cursor.fetchone():
                        logger.info(f"Red flag {flag_id} already attached to node {request.node_id}")
                        continue
                    
                    # Attach flag
                    cursor.execute(
                        "INSERT INTO node_red_flags (node_id, red_flag_id, created_at) VALUES (?, ?, datetime('now'))",
                        (request.node_id, flag_id)
                    )
                    
                    # Audit the attachment
                    cursor.execute(
                        "INSERT INTO red_flag_audit (node_id, red_flag_id, action, ts) VALUES (?, ?, 'attach', datetime('now'))",
                        (request.node_id, flag_id)
                    )
                    
                    attached_count += 1
                    
                except Exception as e:
                    logger.error(f"Error attaching red flag {flag_id}: {e}")
                    continue
            
            # Commit transaction
            conn.commit()
            
            logger.info(f"Bulk attach completed: {attached_count} flags attached to node {request.node_id}")
            return {
                "message": f"Successfully attached {attached_count} red flags",
                "node_id": request.node_id,
                "attached_count": attached_count,
                "total_requested": len(request.red_flag_ids)
            }
            
    except Exception as e:
        logger.error(f"Bulk attach failed: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk attach failed: {str(e)}")


@router.post("/bulk-detach")
async def bulk_detach(
    request: BulkDetachRequest,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Bulk detach red flags from a node.
    
    Args:
        request: Node ID and list of red flag IDs to detach
        repo: Database repository
        
    Returns:
        Success message with count of flags detached
    """
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            # Begin transaction
            cursor.execute("BEGIN TRANSACTION")
            
            detached_count = 0
            for flag_id in request.red_flag_ids:
                try:
                    # Check if currently attached
                    cursor.execute(
                        "SELECT 1 FROM node_red_flags WHERE node_id = ? AND red_flag_id = ?",
                        (request.node_id, flag_id)
                    )
                    if not cursor.fetchone():
                        logger.info(f"Red flag {flag_id} not attached to node {request.node_id}")
                        continue
                    
                    # Detach flag
                    cursor.execute(
                        "DELETE FROM node_red_flags WHERE node_id = ? AND red_flag_id = ?",
                        (request.node_id, flag_id)
                    )
                    
                    # Audit the detachment
                    cursor.execute(
                        "INSERT INTO red_flag_audit (node_id, red_flag_id, action, ts) VALUES (?, ?, 'detach', datetime('now'))",
                        (request.node_id, flag_id)
                    )
                    
                    detached_count += 1
                    
                except Exception as e:
                    logger.error(f"Error detaching red flag {flag_id}: {e}")
                    continue
            
            # Commit transaction
            conn.commit()
            
            logger.info(f"Bulk detach completed: {detached_count} flags detached from node {request.node_id}")
            return {
                "message": f"Successfully detached {detached_count} red flags",
                "node_id": request.node_id,
                "detached_count": detached_count,
                "total_requested": len(request.red_flag_ids)
            }
            
    except Exception as e:
        logger.error(f"Bulk detach failed: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk detach failed: {str(e)}")


@router.get("/audit", response_model=List[RedFlagAuditResponse])
async def get_audit(
    node_id: Optional[int] = None,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get red flag audit records.
    
    Args:
        node_id: Optional node ID to filter by
        repo: Database repository
        
    Returns:
        List of audit records
    """
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            if node_id:
                # Get audit for specific node
                cursor.execute("""
                    SELECT rfa.id, rfa.node_id, rfa.red_flag_id, rfa.action, rfa.ts, rf.name
                    FROM red_flag_audit rfa
                    LEFT JOIN red_flags rf ON rfa.red_flag_id = rf.id
                    WHERE rfa.node_id = ?
                    ORDER BY rfa.ts DESC
                """, (node_id,))
            else:
                # Get all audit records
                cursor.execute("""
                    SELECT rfa.id, rfa.node_id, rfa.red_flag_id, rfa.action, rfa.ts, rf.name
                    FROM red_flag_audit rfa
                    LEFT JOIN red_flags rf ON rfa.red_flag_id = rf.id
                    ORDER BY rfa.ts DESC
                    LIMIT 1000
                """)
            
            records = []
            for row in cursor.fetchall():
                records.append(RedFlagAuditResponse(
                    id=row[0],
                    node_id=row[1],
                    red_flag_id=row[2],
                    action=row[3],
                    ts=row[4],
                    red_flag_name=row[5]
                ))
            
            return records
            
    except Exception as e:
        logger.error(f"Failed to get audit records: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get audit records: {str(e)}")
