"""
Flags router for red flag management.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlite3
import logging

from ..dependencies import get_db_connection

router = APIRouter(prefix="/flags", tags=["flags"])
logger = logging.getLogger(__name__)


class FlagResponse(BaseModel):
    id: int
    label: str


class AssignRequest(BaseModel):
    node_id: int = Field(..., ge=1)
    flag_id: int = Field(..., ge=1)
    cascade: bool = False


class AssignResponse(BaseModel):
    affected: int
    node_ids: List[int]


class RemoveRequest(BaseModel):
    node_id: int = Field(..., ge=1)
    flag_id: int = Field(..., ge=1)
    cascade: bool = False


class RemoveResponse(BaseModel):
    affected: int
    node_ids: List[int]


class AuditResponse(BaseModel):
    id: int
    node_id: int
    flag_id: int
    action: str  # 'assign' or 'remove'
    ts: str


@router.get("", response_model=List[FlagResponse])
def list_flags(
    query: Optional[str] = Query(None, description="Search query for flag labels"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    List flags with optional search and pagination.

    Args:
        query: Optional search string for flag labels
        limit: Maximum number of results (1-1000)
        offset: Pagination offset
        conn: Database connection

    Returns:
        List of flag objects
    """
    try:
        cursor = conn.cursor()

        # Build query
        sql = "SELECT id, label FROM red_flags"
        params = []

        if query:
            sql += " WHERE label LIKE ?"
            params.append(f"%{query}%")

        sql += " ORDER BY label LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        return [
            FlagResponse(id=row[0], label=row[1])
            for row in rows
        ]

    except Exception as e:
        logger.exception("Error listing flags")
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/assign", response_model=AssignResponse)
def assign_flag(
    request: AssignRequest,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Assign a flag to a node with optional cascade to descendants.

    Args:
        request: Assignment request with node_id, flag_id, and cascade flag
        conn: Database connection

    Returns:
        Response with count of affected nodes and their IDs
    """
    try:
        cursor = conn.cursor()

        # Validate flag exists
        cursor.execute("SELECT id FROM red_flags WHERE id = ?", (request.flag_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Flag {request.flag_id} not found")

        # Validate node exists
        cursor.execute("SELECT id FROM nodes WHERE id = ?", (request.node_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Node {request.node_id} not found")

        affected_nodes = []

        if request.cascade:
            # Get all descendant nodes including the target node
            cursor.execute("""
                WITH RECURSIVE descendants AS (
                    SELECT id FROM nodes WHERE id = ?
                    UNION ALL
                    SELECT n.id FROM nodes n
                    INNER JOIN descendants d ON n.parent_id = d.id
                )
                SELECT id FROM descendants
            """, (request.node_id,))

            descendant_ids = [row[0] for row in cursor.fetchall()]
        else:
            descendant_ids = [request.node_id]

        # Assign flag to all affected nodes (idempotent)
        for node_id in descendant_ids:
            # Check if already assigned
            cursor.execute(
                "SELECT 1 FROM node_red_flags WHERE node_id = ? AND red_flag_id = ?",
                (node_id, request.flag_id)
            )

            if not cursor.fetchone():
                # Not assigned, so assign it
                cursor.execute(
                    "INSERT INTO node_red_flags (node_id, red_flag_id) VALUES (?, ?)",
                    (node_id, request.flag_id)
                )

                # Audit the assignment
                cursor.execute(
                    "INSERT INTO red_flag_audit (node_id, red_flag_id, action) VALUES (?, ?, 'assign')",
                    (node_id, request.flag_id)
                )

                affected_nodes.append(node_id)

        conn.commit()

        return AssignResponse(
            affected=len(affected_nodes),
            node_ids=affected_nodes
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error assigning flag")
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/remove", response_model=RemoveResponse)
def remove_flag(
    request: RemoveRequest,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Remove a flag from a node with optional cascade to descendants.

    Args:
        request: Removal request with node_id, flag_id, and cascade flag
        conn: Database connection

    Returns:
        Response with count of affected nodes and their IDs
    """
    try:
        cursor = conn.cursor()

        affected_nodes = []

        if request.cascade:
            # Get all descendant nodes including the target node
            cursor.execute("""
                WITH RECURSIVE descendants AS (
                    SELECT id FROM nodes WHERE id = ?
                    UNION ALL
                    SELECT n.id FROM nodes n
                    INNER JOIN descendants d ON n.parent_id = d.id
                )
                SELECT id FROM descendants
            """, (request.node_id,))

            descendant_ids = [row[0] for row in cursor.fetchall()]
        else:
            descendant_ids = [request.node_id]

        # Remove flag from all affected nodes
        for node_id in descendant_ids:
            # Check if currently assigned
            cursor.execute(
                "SELECT 1 FROM node_red_flags WHERE node_id = ? AND red_flag_id = ?",
                (node_id, request.flag_id)
            )

            if cursor.fetchone():
                # Currently assigned, so remove it
                cursor.execute(
                    "DELETE FROM node_red_flags WHERE node_id = ? AND red_flag_id = ?",
                    (node_id, request.flag_id)
                )

                # Audit the removal
                cursor.execute(
                    "INSERT INTO red_flag_audit (node_id, red_flag_id, action) VALUES (?, ?, 'remove')",
                    (node_id, request.flag_id)
                )

                affected_nodes.append(node_id)

        conn.commit()

        return RemoveResponse(
            affected=len(affected_nodes),
            node_ids=affected_nodes
        )

    except Exception as e:
        logger.exception("Error removing flag")
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/audit", response_model=List[AuditResponse])
def get_audit(
    node_id: Optional[int] = Query(None, ge=1, description="Filter by node ID"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Get audit trail for flag assignments/removals.

    Args:
        node_id: Optional node ID to filter audit entries
        limit: Maximum number of results (1-1000)
        offset: Pagination offset
        conn: Database connection

    Returns:
        List of audit entries ordered by timestamp (newest first)
    """
    try:
        cursor = conn.cursor()

        # Build query
        sql = "SELECT id, node_id, red_flag_id, action, ts FROM red_flag_audit"
        params = []

        if node_id is not None:
            sql += " WHERE node_id = ?"
            params.append(node_id)

        sql += " ORDER BY ts DESC, id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        return [
            AuditResponse(
                id=row[0],
                node_id=row[1],
                flag_id=row[2],
                action=row[3],
                ts=row[4]
            )
            for row in rows
        ]

    except Exception as e:
        logger.exception("Error retrieving audit trail")
        raise HTTPException(status_code=500, detail="Database error")