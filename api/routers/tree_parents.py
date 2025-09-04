"""
Tree parents router for incomplete parents listing.
"""

from fastapi import APIRouter, Query
from typing import Optional
from ..dependencies import get_db_connection

router = APIRouter(prefix="/tree/parents", tags=["tree-parents"])

@router.get("/incomplete")
def list_incomplete_parents(
    query: str = "",
    depth: Optional[int] = Query(None, ge=0, le=5),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    List incomplete parents with pagination and filtering.

    Returns parents that have fewer than 5 children, with their missing slots.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Build query parameters
    params = []
    where_clauses = ["p.depth BETWEEN 0 AND 4"]  # Only non-leaf nodes can be incomplete

    if query.strip():
        q = f"%{query.strip().lower()}%"
        where_clauses.append("LOWER(p.label) LIKE ?")
        params.append(q)

    if depth is not None:
        where_clauses.append("p.depth = ?")
        params.append(depth)

    where_sql = " AND ".join(where_clauses)

    # Get items
    items_query = f"""
        WITH slots(slot) AS (VALUES (1),(2),(3),(4),(5)),
             parent_missing AS (
               SELECT p.id AS parent_id,
                      p.label,
                      p.depth,
                      GROUP_CONCAT(CASE WHEN c.id IS NULL THEN s.slot ELSE NULL END) AS missing_slots,
                      SUM(CASE WHEN c.id IS NULL THEN 1 ELSE 0 END) AS missing_count
               FROM nodes p
               CROSS JOIN slots s
               LEFT JOIN nodes c ON c.parent_id = p.id AND c.slot = s.slot
               WHERE {where_sql}
               GROUP BY p.id, p.label, p.depth
               HAVING missing_count > 0
             )
        SELECT parent_id, label, depth,
               COALESCE(missing_slots, '') AS missing_slots
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
        {
            "parent_id": r[0],
            "label": r[1],
            "depth": r[2],
            "missing_slots": r[3]
        }
        for r in rows
    ]

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset
    }
