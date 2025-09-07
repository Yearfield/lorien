from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from api.db import get_conn, ensure_schema

router = APIRouter()

@router.get("/admin/roots/suspect")
def suspect_roots(prefix: str = Query("sheet", description="case-insensitive contains match"), limit:int=Query(50,ge=1,le=500)):
    """
    Heuristic: list root labels that look like sheet names (e.g., 'Sheet1', 'Sheet 2', 'sheet-...').
    Use this to inspect and manually delete via DELETE /tree/{id} which you already have.
    """
    conn = get_conn()
    ensure_schema(conn)
    cur = conn.execute(
        "SELECT id,label FROM nodes WHERE parent_id IS NULL AND LOWER(label) LIKE ? ORDER BY id DESC LIMIT ?",
        (f"%{prefix.lower()}%", limit)
    )
    return JSONResponse({"items":[{"id":r["id"],"label":r["label"]} for r in cur.fetchall()]})
