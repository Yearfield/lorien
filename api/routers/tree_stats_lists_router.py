from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from typing import Optional
from api.db import get_conn, ensure_schema

router = APIRouter()

@router.get("/tree/roots")
def list_roots(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), q: Optional[str] = Query(None)):
    conn = get_conn()
    ensure_schema(conn)
    params = []
    where = "WHERE depth=0"
    if q:
        where += " AND LOWER(label) LIKE ?"
        params.append(f"%{q.lower()}%")
    total = conn.execute(f"SELECT COUNT(*) FROM nodes {where}", params).fetchone()[0]
    cur = conn.execute(f"SELECT id,label FROM nodes {where} ORDER BY label LIMIT ? OFFSET ?", params + [limit, offset])
    items = [{"id": r["id"], "label": r["label"]} for r in cur.fetchall()]
    return JSONResponse({"items": items, "total": int(total), "limit": limit, "offset": offset})


@router.get("/tree/leaves")
def list_leaves(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), q: Optional[str] = Query(None)):
    conn = get_conn()
    ensure_schema(conn)
    where = "WHERE NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = n.id)"
    params = []
    if q:
        where += " AND LOWER(n.label) LIKE ?"
        params.append(f"%{q.lower()}%")
    total = conn.execute(f"SELECT COUNT(*) FROM nodes n {where}", params).fetchone()[0]
    cur = conn.execute(f"SELECT n.id, n.label, n.depth FROM nodes n {where} ORDER BY n.depth, n.label LIMIT ? OFFSET ?", params + [limit, offset])
    items = [{"id": r["id"], "label": r["label"], "depth": r["depth"]} for r in cur.fetchall()]
    return JSONResponse({"items": items, "total": int(total), "limit": limit, "offset": offset})
