from fastapi import APIRouter, Query, Path
from fastapi.responses import JSONResponse
from typing import Optional
from api.db import get_conn, ensure_schema
from api.repositories.tree_repo import list_parents, list_children

router = APIRouter()

@router.get("/tree/parents")
def get_parents(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    incomplete_only: bool = Query(True),
    depth: Optional[int] = Query(None, ge=0, le=5),
    q: Optional[str] = Query(None)
):
    conn = get_conn()
    ensure_schema(conn)
    return JSONResponse(list_parents(conn, limit, offset, incomplete_only, depth, q))

@router.get("/tree/children/{parent_id}")
def get_children(parent_id: int = Path(..., ge=1)):
    conn = get_conn()
    ensure_schema(conn)
    return JSONResponse(list_children(conn, parent_id))
