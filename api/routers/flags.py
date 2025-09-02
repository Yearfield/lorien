"""
Flags namespace router for flag management and audit.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
import logging
import sqlite3
from datetime import datetime

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/flags", tags=["flags"])


class FlagResponse(BaseModel):
    """Flag response model."""
    id: int
    label: str


class FlagsPage(BaseModel):
    """Paged flags response."""
    items: List[FlagResponse]
    total: int
    limit: int
    offset: int


class AssignPayload(BaseModel):
    """Flag assignment payload."""
    node_id: int
    flag_id: int
    cascade: bool = False


class AssignResponse(BaseModel):
    """Flag assignment response."""
    affected: int
    node_ids: List[int]


class FlagAuditResponse(BaseModel):
    """Flag audit response."""
    id: int
    node_id: int
    flag_id: int
    action: str
    user: Optional[str]
    ts: str


@router.get("/", response_model=FlagsPage)
async def list_flags(
    query: str = Query("", description="Search query for flag labels"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    List flags with paging and search.

    Args:
        query: Search query for flag labels (case-insensitive substring)
        limit: Maximum number of results
        offset: Number of results to skip
        repo: Database repository

    Returns:
        Paged response with items, total count, limit, and offset
    """
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()

            # Build items query with case-insensitive search and stable sort
            sql_items = "SELECT id, label FROM flags"
            params_items = []

            if query:
                sql_items += " WHERE LOWER(label) LIKE LOWER(?)"
                params_items.append(f"%{query}%")

            # Stable sort: updated_at DESC, id DESC for consistent ordering
            sql_items += " ORDER BY updated_at DESC, id DESC LIMIT ? OFFSET ?"
            params_items.extend([limit, offset])

            cursor.execute(sql_items, params_items)
            rows = cursor.fetchall()

            # Build total count query
            sql_total = "SELECT COUNT(*) FROM flags"
            params_total = []

            if query:
                sql_total += " WHERE LOWER(label) LIKE LOWER(?)"
                params_total.append(f"%{query}%")

            cursor.execute(sql_total, params_total)
            total = cursor.fetchone()[0]

            return FlagsPage(
                items=[
                    FlagResponse(id=row[0], label=row[1])
                    for row in rows
                ],
                total=total,
                limit=limit,
                offset=offset
            )

    except Exception as e:
        logger.error(f"Failed to list flags: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list flags: {str(e)}"
        )


@router.post("/assign", response_model=AssignResponse)
async def assign_flag(
    payload: AssignPayload,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Assign a flag to a node, optionally cascading to descendants.
    
    Args:
        payload: Assignment payload with node_id, flag_id, and cascade flag
        repo: Database repository
        
    Returns:
        Assignment response with affected count and node IDs
    """
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            # Start transaction
            conn.execute("BEGIN IMMEDIATE")
            
            # Validate node exists
            cursor.execute("SELECT id FROM nodes WHERE id = ?", (payload.node_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Node {payload.node_id} not found")
            
            # Validate flag exists
            cursor.execute("SELECT id, label FROM flags WHERE id = ?", (payload.flag_id,))
            flag_row = cursor.fetchone()
            if not flag_row:
                raise HTTPException(status_code=404, detail=f"Flag {payload.flag_id} not found")
            
            flag_label = flag_row[1]
            
            # Get nodes to affect
            if payload.cascade:
                # Get descendants using recursive CTE
                cursor.execute("""
                    WITH RECURSIVE descendants AS (
                        SELECT ? as id
                        UNION ALL
                        SELECT n.id FROM nodes n
                        JOIN descendants d ON n.parent_id = d.id
                    )
                    SELECT id FROM descendants
                """, (payload.node_id,))
                node_ids = [row[0] for row in cursor.fetchall()]
            else:
                node_ids = [payload.node_id]
            
            affected_count = 0
            
            # Process each node
            for node_id in node_ids:
                # Check if already assigned (idempotent)
                cursor.execute("""
                    SELECT 1 FROM node_flags 
                    WHERE node_id = ? AND flag_id = ?
                """, (node_id, payload.flag_id))
                
                if not cursor.fetchone():
                    # Assign flag
                    cursor.execute("""
                        INSERT INTO node_flags (node_id, flag_id, created_at)
                        VALUES (?, ?, ?)
                    """, (node_id, payload.flag_id, datetime.now().isoformat()))
                    
                    # Create audit record
                    cursor.execute("""
                        INSERT INTO flag_audit (node_id, flag_id, action, ts)
                        VALUES (?, ?, 'assign', ?)
                    """, (node_id, payload.flag_id, datetime.now().isoformat()))
                    
                    affected_count += 1
            
            conn.commit()
            
            logger.info(f"Assigned flag '{flag_label}' to {affected_count} node(s)")
            
            return AssignResponse(
                affected=affected_count,
                node_ids=node_ids
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to assign flag: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to assign flag: {str(e)}"
        )


@router.post("/remove", response_model=AssignResponse)
async def remove_flag(
    payload: AssignPayload,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Remove a flag from a node, optionally cascading to descendants.
    
    Args:
        payload: Removal payload with node_id, flag_id, and cascade flag
        repo: Database repository
        
    Returns:
        Removal response with affected count and node IDs
    """
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            # Start transaction
            conn.execute("BEGIN IMMEDIATE")
            
            # Validate node exists
            cursor.execute("SELECT id FROM nodes WHERE id = ?", (payload.node_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Node {payload.node_id} not found")
            
            # Validate flag exists
            cursor.execute("SELECT id, label FROM flags WHERE id = ?", (payload.flag_id,))
            flag_row = cursor.fetchone()
            if not flag_row:
                raise HTTPException(status_code=404, detail=f"Flag {payload.flag_id} not found")
            
            flag_label = flag_row[1]
            
            # Get nodes to affect
            if payload.cascade:
                # Get descendants using recursive CTE
                cursor.execute("""
                    WITH RECURSIVE descendants AS (
                        SELECT ? as id
                        UNION ALL
                        SELECT n.id FROM nodes n
                        JOIN descendants d ON n.parent_id = d.id
                    )
                    SELECT id FROM descendants
                """, (payload.node_id,))
                node_ids = [row[0] for row in cursor.fetchall()]
            else:
                node_ids = [payload.node_id]
            
            affected_count = 0
            
            # Process each node
            for node_id in node_ids:
                # Check if assigned
                cursor.execute("""
                    SELECT 1 FROM node_flags 
                    WHERE node_id = ? AND flag_id = ?
                """, (node_id, payload.flag_id))
                
                if cursor.fetchone():
                    # Remove flag
                    cursor.execute("""
                        DELETE FROM node_flags 
                        WHERE node_id = ? AND flag_id = ?
                    """, (node_id, payload.flag_id))
                    
                    # Create audit record
                    cursor.execute("""
                        INSERT INTO flag_audit (node_id, flag_id, action, ts)
                        VALUES (?, ?, 'remove', ?)
                    """, (node_id, payload.flag_id, datetime.now().isoformat()))
                    
                    affected_count += 1
            
            conn.commit()
            
            logger.info(f"Removed flag '{flag_label}' from {affected_count} node(s)")
            
            return AssignResponse(
                affected=affected_count,
                node_ids=node_ids
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove flag: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to remove flag: {str(e)}"
        )


@router.get("/audit", response_model=List[FlagAuditResponse])
async def flags_audit(
    node_id: Optional[int] = Query(None, description="Filter by node ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get flag audit records with optional filtering.
    
    Args:
        node_id: Filter by node ID
        limit: Maximum number of results
        offset: Number of results to skip
        repo: Database repository
        
    Returns:
        List of flag audit records
    """
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            # Build query
            sql = """
                SELECT fa.id, fa.node_id, fa.flag_id, fa.action, fa.user, fa.ts
                FROM flag_audit fa
            """
            params = []
            
            if node_id is not None:
                sql += " WHERE fa.node_id = ?"
                params.append(node_id)
            
            sql += " ORDER BY fa.ts DESC, fa.id DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [
                FlagAuditResponse(
                    id=row[0],
                    node_id=row[1],
                    flag_id=row[2],
                    action=row[3],
                    user=row[4],
                    ts=row[5]
                )
                for row in rows
            ]
            
    except Exception as e:
        logger.error(f"Failed to get flag audit: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get flag audit: {str(e)}"
        )
