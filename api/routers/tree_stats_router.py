from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from typing import Optional
from api.db import get_conn, ensure_schema
from api.repositories.tree_repo import stats as repo_stats, missing_slots as repo_missing

router = APIRouter()

@router.get("/tree/stats")
def tree_stats():
    conn = get_conn()
    ensure_schema(conn)
    s = repo_stats(conn)
    return JSONResponse(s)

@router.get("/tree/missing-slots-json")
def tree_missing_slots(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    depth: Optional[int] = Query(None, ge=0, le=5),
    q: Optional[str] = Query(None)
):
    conn = get_conn()
    ensure_schema(conn)
    payload = repo_missing(conn, limit=limit, offset=offset, depth=depth, q=q)
    return JSONResponse(payload)
