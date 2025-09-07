from fastapi import APIRouter, Query, Body, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel, conlist, constr
from api.db import get_conn, ensure_schema
from api.repositories.tree_repo import (
    list_parent_labels, aggregate_children_for_label, apply_default_children_for_label
)

router = APIRouter()

@router.get("/tree/labels")
def get_labels(limit: int = Query(50, ge=1, le=500),
               offset: int = Query(0, ge=0),
               incomplete_only: bool = Query(True),
               depth: Optional[int] = Query(None, ge=0, le=5),
               q: Optional[str] = Query(None)):
    conn = get_conn()
    ensure_schema(conn)
    return JSONResponse(list_parent_labels(conn, limit, offset, incomplete_only, depth, q))

@router.get("/tree/labels/{label}/aggregate")
def get_label_aggregate(label: str):
    conn = get_conn()
    ensure_schema(conn)
    return JSONResponse(aggregate_children_for_label(conn, label))

class ApplyReq(BaseModel):
    chosen: conlist(constr(strip_whitespace=True, min_length=1), min_length=5, max_length=5)

@router.post("/tree/labels/{label}/apply-default")
def post_apply_default(label: str, req: ApplyReq):
    try:
        conn = get_conn()
        ensure_schema(conn)
        res = apply_default_children_for_label(conn, label, req.chosen)
        return JSONResponse(res)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=[{"loc": ["body", "chosen"], "msg": str(e), "type": "value_error"}])
