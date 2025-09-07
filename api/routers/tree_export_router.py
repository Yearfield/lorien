from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from api.db import get_conn, ensure_schema
from api.repositories.tree_repo import export_rows

router = APIRouter()

@router.get("/tree/export-json")
def tree_export(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
    conn = get_conn()
    ensure_schema(conn)
    payload = export_rows(conn, limit=limit, offset=offset)
    return JSONResponse(payload)
