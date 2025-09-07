from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr
from typing import Optional, List, Dict, Any
from api.db import get_conn, ensure_schema
from api.repositories.tree_repo import create_root_if_missing, sanitize_label

router = APIRouter()

class VMReq(BaseModel):
    label: constr(strip_whitespace=True, min_length=1)

@router.post("/tree/vm")
def create_vm(req: VMReq):
    conn = get_conn()
    ensure_schema(conn)
    lab = sanitize_label(req.label)
    if not lab:
        raise HTTPException(status_code=422, detail=[{"loc":["body","label"],"msg":"empty VM label","type":"value_error"}])
    rid = create_root_if_missing(conn, lab)
    # Return basic node
    row = conn.execute("SELECT id,label,depth FROM nodes WHERE id=?", (rid,)).fetchone()
    return JSONResponse({"id": int(row["id"]), "label": row["label"], "depth": int(row["depth"])})

@router.get("/tree/suggest/labels")
def suggest_labels(q: Optional[str] = Query(None), limit:int = Query(25, ge=1, le=200)):
    """Return distinct non-empty labels (excluding roots) ordered by frequency desc."""
    conn = get_conn()
    ensure_schema(conn)
    params: List[Any] = []
    where = "WHERE label IS NOT NULL AND TRIM(label)<>'' AND LOWER(label)<>'nan'"
    if q:
        where += " AND LOWER(label) LIKE ?"
        params.append(f"%{q.lower()}%")
    sql = f"""
      SELECT label, COUNT(*) as freq
      FROM nodes
      {where}
      GROUP BY label
      ORDER BY freq DESC, label ASC
      LIMIT ?
    """
    rows = conn.execute(sql, params + [limit]).fetchall()
    return JSONResponse({"items":[{"label":r["label"], "freq": int(r["freq"])} for r in rows]})

@router.get("/tree/children")
def list_children(parent_id: int = Query(..., ge=1)):
    """List children of a parent for builder UI to navigate."""
    conn = get_conn()
    ensure_schema(conn)
    cur = conn.execute("SELECT id,label,slot,depth FROM nodes WHERE parent_id=? ORDER BY slot, id", (parent_id,))
    items = [{"id": r["id"], "label": r["label"], "slot": r["slot"], "depth": r["depth"]} for r in cur.fetchall()]
    return JSONResponse({"items": items})
