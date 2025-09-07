"""
Tree conflicts router for detecting various data integrity issues.
"""

from fastapi import APIRouter, Query, Depends, Path, Body, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, conlist, constr
from typing import List, Optional
import sqlite3
import logging

from ..dependencies import get_db_connection
from api.db import get_conn, ensure_schema
from api.repositories.tree_repo import detect_conflicts, normalize_parent, merge_duplicate_parents, get_conflict_group, resolve_conflict_group

router = APIRouter(prefix="/tree/conflicts", tags=["tree-conflicts"])
logger = logging.getLogger(__name__)


class DuplicateLabelItem(BaseModel):
    parent_id: int
    parent_label: str
    depth: int
    label: str
    count: int
    slots: List[int]


class DuplicateLabelsResponse(BaseModel):
    items: List[DuplicateLabelItem]
    total: int
    limit: int
    offset: int


class OrphanItem(BaseModel):
    node_id: int
    label: str
    depth: int
    parent_id: Optional[int] = None


class OrphansResponse(BaseModel):
    items: List[OrphanItem]
    total: int
    limit: int
    offset: int


class DepthAnomalyItem(BaseModel):
    node_id: int
    label: str
    expected_depth: int
    actual_depth: int
    parent_id: Optional[int]


class DepthAnomaliesResponse(BaseModel):
    items: List[DepthAnomalyItem]
    total: int
    limit: int
    offset: int


@router.get("/duplicate-labels", response_model=DuplicateLabelsResponse)
def get_duplicate_labels(
    q: str = Query("", description="Search query for parent labels"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Find parents with duplicate child labels.

    Identifies parents where multiple children have the same label.
    Performance target: <200ms.
    """
    cursor = conn.cursor()

    # Build query parameters
    params = []
    where_clauses = []

    if q.strip():
        query_param = f"%{q.strip().lower()}%"
        where_clauses.append("LOWER(p.label) LIKE ?")
        params.append(query_param)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    # Get items with duplicate labels
    items_query = f"""
        WITH duplicate_labels AS (
            SELECT
                p.id AS parent_id,
                p.label AS parent_label,
                p.depth,
                c.label,
                COUNT(*) AS count,
                GROUP_CONCAT(c.slot) AS slots_str
            FROM nodes p
            JOIN nodes c ON c.parent_id = p.id
            WHERE {where_sql}
            GROUP BY p.id, p.label, p.depth, c.label
            HAVING COUNT(*) > 1
        )
        SELECT parent_id, parent_label, depth, label, count, slots_str
        FROM duplicate_labels
        ORDER BY parent_id ASC, label ASC
        LIMIT ? OFFSET ?
    """

    cursor.execute(items_query, (*params, limit, offset))
    rows = cursor.fetchall()

    # Get total count
    count_query = f"""
        WITH duplicate_labels AS (
            SELECT p.id AS parent_id
            FROM nodes p
            JOIN nodes c ON c.parent_id = p.id
            WHERE {where_sql}
            GROUP BY p.id, c.label
            HAVING COUNT(*) > 1
        )
        SELECT COUNT(DISTINCT parent_id) FROM duplicate_labels
    """

    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]

    items = []
    for row in rows:
        parent_id, parent_label, depth, label, count, slots_str = row
        slots = [int(s) for s in slots_str.split(',')] if slots_str else []

        items.append(DuplicateLabelItem(
            parent_id=parent_id,
            parent_label=parent_label,
            depth=depth,
            label=label,
            count=count,
            slots=slots
        ))

    return DuplicateLabelsResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/orphans", response_model=OrphansResponse)
def get_orphans(
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Find orphaned nodes (non-root nodes without valid parents).

    Identifies nodes that reference non-existent parents.
    Performance target: <100ms.
    """
    cursor = conn.cursor()

    # Get orphaned nodes
    items_query = """
        SELECT c.id, c.label, c.depth, c.parent_id
        FROM nodes c
        LEFT JOIN nodes p ON p.id = c.parent_id
        WHERE c.depth > 0 AND (p.id IS NULL OR p.depth >= c.depth)
        ORDER BY c.id ASC
        LIMIT ? OFFSET ?
    """

    cursor.execute(items_query, (limit, offset))
    rows = cursor.fetchall()

    # Get total count
    count_query = """
        SELECT COUNT(*)
        FROM nodes c
        LEFT JOIN nodes p ON p.id = c.parent_id
        WHERE c.depth > 0 AND (p.id IS NULL OR p.depth >= c.depth)
    """

    cursor.execute(count_query)
    total = cursor.fetchone()[0]

    items = [
        OrphanItem(
            node_id=row[0],
            label=row[1],
            depth=row[2],
            parent_id=row[3]
        )
        for row in rows
    ]

    return OrphansResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/depth-anomalies", response_model=DepthAnomaliesResponse)
def get_depth_anomalies(
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Find nodes with incorrect depth values.

    Identifies nodes where depth doesn't match parent.depth + 1.
    Performance target: <100ms.
    """
    cursor = conn.cursor()

    # Get nodes with depth anomalies
    items_query = """
        SELECT
            c.id,
            c.label,
            CASE WHEN p.depth IS NULL THEN 0 ELSE p.depth + 1 END AS expected_depth,
            c.depth AS actual_depth,
            c.parent_id
        FROM nodes c
        LEFT JOIN nodes p ON p.id = c.parent_id
        WHERE (p.depth IS NULL AND c.depth != 0)  -- Root should be depth 0
           OR (p.depth IS NOT NULL AND c.depth != p.depth + 1)  -- Children should be parent.depth + 1
        ORDER BY c.id ASC
        LIMIT ? OFFSET ?
    """

    cursor.execute(items_query, (limit, offset))
    rows = cursor.fetchall()

    # Get total count
    count_query = """
        SELECT COUNT(*)
        FROM nodes c
        LEFT JOIN nodes p ON p.id = c.parent_id
        WHERE (p.depth IS NULL AND c.depth != 0)
           OR (p.depth IS NOT NULL AND c.depth != p.depth + 1)
    """

    cursor.execute(count_query)
    total = cursor.fetchone()[0]

    items = [
        DepthAnomalyItem(
            node_id=row[0],
            label=row[1],
            expected_depth=row[2],
            actual_depth=row[3],
            parent_id=row[4]
        )
        for row in rows
    ]

    return DepthAnomaliesResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/conflicts")
def get_conflicts(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), q: Optional[str] = Query(None)):
    conn = get_conn()
    ensure_schema(conn)
    return JSONResponse(detect_conflicts(conn, limit, offset, q))


@router.post("/parent/{parent_id}/normalize")
def post_normalize(parent_id: int = Path(..., ge=1)):
    conn = get_conn()
    ensure_schema(conn)
    return JSONResponse(normalize_parent(conn, parent_id))


class MergeReq(BaseModel):
    label: str
    keep_id: int


@router.post("/parent/{parent_id}/merge-duplicates")
def post_merge_dupes(parent_id: int, req: MergeReq):
    conn = get_conn()
    ensure_schema(conn)
    try:
        res = merge_duplicate_parents(conn, parent_id, req.label, req.keep_id)
        return JSONResponse(res)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class ResolveReq(BaseModel):
    keep_id: int
    chosen: conlist(constr(strip_whitespace=True, min_length=1), min_length=5, max_length=5)


@router.get("/group")
def conflicts_group(
    node_id: Optional[int] = Query(None, ge=1),
    parent_id: Optional[int] = Query(None, ge=1),
    label: Optional[str] = Query(None),
):
    """
    Prefer node_id; fall back to (parent_id,label).
    node_id route ensures left list can pass what it has (the parent node's id).
    """
    conn = get_conn()
    ensure_schema(conn)
    
    # Resolve keys
    if node_id is not None:
        row = conn.execute("SELECT parent_id, label FROM nodes WHERE id=?", (node_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=422, detail=[{"loc":["query","node_id"],"msg":"Node not found","type":"value_error.node"}])
        parent_id = int(row["parent_id"]) if row["parent_id"] is not None else None
        label = str(row["label"])
        # If this is a root (parent_id is NULL), treat all roots with this label as a group (usually one)
        if parent_id is None:
            parent_id = -1  # sentinel; will not match; handle roots specially below
    if parent_id is None or label is None:
        raise HTTPException(status_code=422, detail=[{"loc":["query"],"msg":"Provide node_id or (parent_id & label)","type":"value_error.keys"}])

    # Standard duplicate-group case (same parent_id, label)
    try:
        out = get_conflict_group(conn, int(parent_id), str(label))
        # If group empty (shouldn't happen), return children of node_id itself as a fallback
        if not out["group"] and node_id is not None:
            from api.repositories.tree_repo import list_children
            lc = list_children(conn, node_id)
            kids = [{"child_id": c["id"], "from_id": node_id, "slot": c["slot"], "label": c["label"]} for c in lc["children"]]
            out = {"group":[{"id": node_id}], "children": kids, "summary":{"unique_children": len({k["label"] for k in kids}), "total_children": len(kids)}}
        return JSONResponse(out)
    except sqlite3.DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/group/resolve")
def conflicts_group_resolve(req: ResolveReq):
    conn = get_conn()
    ensure_schema(conn)
    try:
        # Get parent_id and label from keep_id
        parent_row = conn.execute("SELECT parent_id FROM nodes WHERE id=?", (req.keep_id,)).fetchone()
        label_row = conn.execute("SELECT label FROM nodes WHERE id=?", (req.keep_id,)).fetchone()
        if not parent_row or not label_row:
            raise HTTPException(status_code=422, detail=[{"loc":["body","keep_id"], "msg":"Keeper not found", "type":"value_error.keep_id"}])
        
        out = resolve_conflict_group(conn, parent_id=int(parent_row[0]), label=str(label_row[0]), keep_id=req.keep_id, chosen=req.chosen)
        return JSONResponse(out)
    except LookupError:
        raise HTTPException(status_code=422, detail=[{"loc":["body","keep_id"], "msg":"Keeper not part of duplicate group", "type":"value_error.keep_id"}])
    except ValueError as e:
        t = "value_error"
        if str(e) == "must_choose_five":
            t = "value_error.must_choose_five"
        if str(e) == "duplicate_labels":
            t = "value_error.duplicate_labels"
        raise HTTPException(status_code=422, detail=[{"loc":["body","chosen"], "msg":str(e), "type":t}])
    except Exception as e:
        raise HTTPException(status_code=409, detail=[{"loc":["body"], "msg":f"Conflict: {e}", "type":"conflict"}])


