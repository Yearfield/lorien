"""
Tree router for navigation and path operations.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Response
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import logging
import time

from ..dependencies import get_db_connection

router = APIRouter(prefix="/tree", tags=["tree"])
logger = logging.getLogger(__name__)


class NextIncompleteResponse(BaseModel):
    parent_id: int
    label: str
    missing_slots: List[int]
    depth: int


class PathResponse(BaseModel):
    node_id: int
    is_leaf: bool
    depth: int
    vital_measurement: str
    nodes: List[str]  # Always length 5, padded with ""
    csv_header: List[str]


@router.get("/next-incomplete-parent", responses={204: {"description": "No incomplete parent"}})
def get_next_incomplete_parent(conn: sqlite3.Connection = Depends(get_db_connection)):
    """
    Find the next incomplete parent node (earliest by ID).

    Returns 204 if no incomplete parents exist.
    Performance target: <100 ms.

    Args:
        conn: Database connection

    Returns:
        NextIncompleteResponse or 204 No Content
    """
    start_time = time.time()

    try:
        cursor = conn.cursor()

        # Find parents with missing children slots
        cursor.execute("""
            WITH parent_slots AS (
                SELECT
                    n.id,
                    n.label,
                    n.depth,
                    COUNT(c.id) as children_count,
                    GROUP_CONCAT(c.slot) as filled_slots
                FROM nodes n
                LEFT JOIN nodes c ON c.parent_id = n.id
                WHERE n.is_leaf = 0
                GROUP BY n.id, n.label, n.depth
            ),
            missing_slots AS (
                SELECT
                    id,
                    label,
                    depth,
                    children_count,
                    -- Calculate missing slots (1-5 not in filled_slots)
                    CASE
                        WHEN filled_slots IS NULL THEN '1,2,3,4,5'
                        ELSE (
                            SELECT GROUP_CONCAT(slot)
                            FROM (
                                SELECT 1 as slot UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
                            ) all_slots
                            WHERE ',' || filled_slots || ',' NOT LIKE '%,' || slot || ',%'
                        )
                    END as missing
                FROM parent_slots
                WHERE children_count < 5
            )
            SELECT id, label, depth, missing
            FROM missing_slots
            ORDER BY id
            LIMIT 1
        """)

        row = cursor.fetchone()

        if not row:
            return Response(status_code=204)

        parent_id, label, depth, missing_str = row
        missing_slots = [int(x) for x in missing_str.split(',')] if missing_str else []

        # Performance check
        elapsed = time.time() - start_time
        if elapsed > 0.1:  # 100ms
            logger.warning(".2f")

        return NextIncompleteResponse(
            parent_id=parent_id,
            label=label,
            missing_slots=missing_slots,
            depth=depth
        )

    except Exception as e:
        logger.exception("Error finding next incomplete parent")
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/path", response_model=PathResponse)
def get_node_path(
    node_id: int = Query(..., ge=1, description="Node ID to get path for"),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Get the complete path from root to the specified node.

    Performance target: <50 ms.

    Args:
        node_id: The node ID to get the path for
        conn: Database connection

    Returns:
        PathResponse with breadcrumbs and CSV header
    """
    start_time = time.time()

    try:
        cursor = conn.cursor()

        # Validate node exists
        cursor.execute("SELECT id FROM nodes WHERE id = ?", (node_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")

        # Get node info
        cursor.execute("""
            SELECT n.id, n.is_leaf, n.depth, n.label, n.slot, n.parent_id
            FROM nodes n
            WHERE n.id = ?
        """, (node_id,))

        node_row = cursor.fetchone()
        if not node_row:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")

        node_id, is_leaf, depth, label, slot, parent_id = node_row

        # Build path by walking up the tree
        path_nodes = []
        current_id = node_id
        current_parent_id = parent_id

        # Collect all nodes in the path
        while current_id is not None:
            cursor.execute("""
                SELECT n.id, n.label, n.slot, n.parent_id
                FROM nodes n
                WHERE n.id = ?
            """, (current_id,))

            row = cursor.fetchone()
            if row:
                nid, nlabel, nslot, nparent_id = row
                path_nodes.append({
                    'id': nid,
                    'label': nlabel,
                    'slot': nslot
                })
                current_id = nparent_id
            else:
                break

        # Reverse to get root-first order
        path_nodes.reverse()

        # Extract vital measurement (root node label)
        vital_measurement = path_nodes[0]['label'] if path_nodes else ""

        # Build nodes array (slots 1-5, padded with empty strings)
        nodes = [""] * 5
        for node_info in path_nodes[1:]:  # Skip root
            if node_info['slot'] and 1 <= node_info['slot'] <= 5:
                nodes[node_info['slot'] - 1] = node_info['label']

        # CSV header (exact order/case)
        csv_header = [
            "Vital Measurement",
            "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
            "Diagnostic Triage", "Actions"
        ]

        # Performance check
        elapsed = time.time() - start_time
        if elapsed > 0.05:  # 50ms
            logger.warning(".2f")

        return PathResponse(
            node_id=node_id,
            is_leaf=bool(is_leaf),
            depth=depth,
            vital_measurement=vital_measurement,
            nodes=nodes,
            csv_header=csv_header
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting node path")
        raise HTTPException(status_code=500, detail="Database error")