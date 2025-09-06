"""
Tree router for navigation and path operations.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Response, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import logging
import time

from ..dependencies import get_db_connection

router = APIRouter(prefix="/tree", tags=["tree"])
logger = logging.getLogger(__name__)


class ParentInfo(BaseModel):
    id: int
    label: str
    depth: int
    parent_id: Optional[int]


class ChildInfo(BaseModel):
    id: int
    label: str
    slot: int
    depth: int
    is_leaf: bool


class MissingSlotsItem(BaseModel):
    parent_id: int
    label: str
    depth: int
    missing_slots: str  # e.g., "2,4"
    updated_at: str


class MissingSlotsResponse(BaseModel):
    items: List[MissingSlotsItem]
    total: int
    limit: int
    offset: int


class NextIncompleteResponse(BaseModel):
    parent_id: int
    label: str
    missing_slots: List[int]  # e.g., [2,4]
    depth: int


class PathResponse(BaseModel):
    node_id: int
    is_leaf: bool
    depth: int
    vital_measurement: str
    nodes: List[str]  # Always length 5, padded with ""
    csv_header: List[str]


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
        with conn as db_conn:
            cursor = db_conn.cursor()

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
                # Get all children of the current parent to build the full 5-slot row
                if current_parent_id is not None:
                    cursor.execute("""
                        SELECT label, slot
                        FROM nodes
                        WHERE parent_id = ?
                        ORDER BY slot
                    """, (current_parent_id,))
                    siblings = cursor.fetchall()

                    # Build 5-slot array
                    row = [""] * 5
                    for sibling_label, sibling_slot in siblings:
                        if 1 <= sibling_slot <= 5:
                            row[sibling_slot - 1] = sibling_label or ""
                    path_nodes.insert(0, row)
                else:
                    # Root node - get its children
                    cursor.execute("""
                        SELECT label, slot
                        FROM nodes
                        WHERE parent_id = ?
                        ORDER BY slot
                    """, (current_id,))
                    children = cursor.fetchall()

                    # Build 5-slot array for root
                    row = [""] * 5
                    for child_label, child_slot in children:
                        if 1 <= child_slot <= 5:
                            row[child_slot - 1] = child_label or ""
                    path_nodes.insert(0, row)

                # Move up to parent
                if current_parent_id is not None:
                    cursor.execute("SELECT parent_id FROM nodes WHERE id = ?", (current_parent_id,))
                    parent_row = cursor.fetchone()
                    current_id = current_parent_id
                    current_parent_id = parent_row[0] if parent_row else None
                else:
                    break

            # Get vital measurement (root label)
            cursor.execute("SELECT label FROM nodes WHERE parent_id IS NULL LIMIT 1")
            root_row = cursor.fetchone()
            vital_measurement = root_row[0] if root_row else "Unknown"

            # CSV header
            csv_header = [
                "Vital Measurement",
                "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
                "Diagnostic Triage",
                "Actions"
            ]

            # Performance check
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            if duration_ms > 50:
                logger.warning(f"Path query took {duration_ms:.1f}ms (target: <50ms)")

            return PathResponse(
                node_id=node_id,
                is_leaf=bool(is_leaf),
                depth=depth,
                vital_measurement=vital_measurement,
                nodes=path_nodes[0] if path_nodes else ["", "", "", "", ""],
                csv_header=csv_header
            )

    except Exception as e:
        logger.exception("Error getting node path")
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/{parent_id}", response_model=ParentInfo)
def get_parent_info(
    parent_id: int = Path(..., ge=1),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Get basic information about a parent node.

    Returns parent_id, label, depth, and parent_id.
    """
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, label, depth, parent_id
        FROM nodes
        WHERE id = ?
    """, (parent_id,))

    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Parent {parent_id} not found")

    return ParentInfo(
        id=row[0],
        label=row[1],
        depth=row[2],
        parent_id=row[3]
    )


@router.get("/{parent_id}/children", response_model=List[ChildInfo])
def get_parent_children(
    parent_id: int = Path(..., ge=1),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Get all children of a parent node (max 5).

    Returns list of child nodes with id, label, slot, depth, is_leaf.
    """
    cursor = conn.cursor()

    # Validate parent exists
    cursor.execute("SELECT id FROM nodes WHERE id = ?", (parent_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Parent {parent_id} not found")

    # Get children
    cursor.execute("""
        SELECT id, label, slot, depth, is_leaf
        FROM nodes
        WHERE parent_id = ?
        ORDER BY slot
    """, (parent_id,))

    children = [
        ChildInfo(
            id=row[0],
            label=row[1],
            slot=row[2],
            depth=row[3],
            is_leaf=bool(row[4])
        )
        for row in cursor.fetchall()
    ]

    return children


@router.get("/missing-slots", response_model=MissingSlotsResponse)
def get_missing_slots(
    q: str = Query("", description="Search query for parent labels"),
    depth: Optional[int] = Query(None, ge=0, le=4, description="Filter by depth"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Get parents with missing children slots.

    Returns paginated list of parents with their missing slots.
    """
    cursor = conn.cursor()

    # Build query parameters
    params = []
    where_clauses = ["p.depth BETWEEN 0 AND 4"]  # Only non-leaf nodes can be incomplete

    if q.strip():
        query_param = f"%{q.strip().lower()}%"
        where_clauses.append("LOWER(p.label) LIKE ?")
        params.append(query_param)

    if depth is not None:
        where_clauses.append("p.depth = ?")
        params.append(depth)

    where_sql = " AND ".join(where_clauses)

    # Get items with missing slots
    items_query = f"""
        WITH slots(slot) AS (VALUES (1),(2),(3),(4),(5)),
             parent_missing AS (
               SELECT p.id AS parent_id,
                      p.label,
                      p.depth,
                      p.updated_at,
                      GROUP_CONCAT(CASE WHEN c.id IS NULL THEN s.slot ELSE NULL END) AS missing_slots,
                      SUM(CASE WHEN c.id IS NULL THEN 1 ELSE 0 END) AS missing_count
               FROM nodes p
               CROSS JOIN slots s
               LEFT JOIN nodes c ON c.parent_id = p.id AND c.slot = s.slot
               WHERE {where_sql}
               GROUP BY p.id, p.label, p.depth, p.updated_at
               HAVING missing_count > 0
             )
        SELECT parent_id, label, depth, COALESCE(missing_slots, '') AS missing_slots, updated_at
        FROM parent_missing
        ORDER BY depth ASC, parent_id ASC
        LIMIT ? OFFSET ?
    """

    cursor.execute(items_query, (*params, limit, offset))
    rows = cursor.fetchall()

    # Get total count
    count_query = f"""
        WITH slots(slot) AS (VALUES (1),(2),(3),(4),(5)),
             parent_missing AS (
               SELECT p.id AS parent_id
               FROM nodes p
               CROSS JOIN slots s
               LEFT JOIN nodes c ON c.parent_id = p.id AND c.slot = s.slot
               WHERE {where_sql}
               GROUP BY p.id
               HAVING SUM(CASE WHEN c.id IS NULL THEN 1 ELSE 0 END) > 0
             )
        SELECT COUNT(*) FROM parent_missing
    """

    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]

    items = [
        MissingSlotsItem(
            parent_id=row[0],
            label=row[1],
            depth=row[2],
            missing_slots=row[3],
            updated_at=row[4]
        )
        for row in rows
    ]

    return MissingSlotsResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/next-incomplete-parent", responses={204: {"description": "No incomplete parent"}})
def get_next_incomplete_parent(conn: sqlite3.Connection = Depends(get_db_connection)):
    """
    Find the next incomplete parent node (earliest by ID).

    Returns 204 if no incomplete parents exist.
    Performance target: <100 ms.
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
            logger.warning(f"next-incomplete-parent query took {elapsed:.3f}s")

        return NextIncompleteResponse(
            parent_id=parent_id,
            label=label,
            missing_slots=missing_slots,
            depth=depth
        )

    except Exception as e:
        logger.exception("Error finding next incomplete parent")
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/roots")
def get_roots():
    """
    Get all root nodes (vital measurements).

    Returns a list of unique vital measurement names.
    """
    try:
        from ..dependencies import get_db_connection
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Simple test query first
            cursor.execute("SELECT COUNT(*) FROM nodes WHERE depth = 0")
            count = cursor.fetchone()[0]

            # Get all unique vital measurements from root nodes (depth 0)
            cursor.execute("""
                SELECT DISTINCT label
                FROM nodes
                WHERE depth = 0
                ORDER BY label
            """)

            roots = [row[0] for row in cursor.fetchall()]
            return {"count": count, "roots": roots}

    except Exception as e:
        logger.exception("Error getting roots")
        return {"error": str(e)}


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


