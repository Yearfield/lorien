from fastapi import APIRouter, Depends, HTTPException, Query
import sqlite3
from pydantic import BaseModel, Field
from typing import List, Optional
from api.settings import get_db_path

router = APIRouter(prefix="/api/v1/tree", tags=["tree"])

def get_conn():
    return sqlite3.connect(get_db_path())

class Child(BaseModel):
    label: str = Field(min_length=1, max_length=256)
    slot: Optional[int] = None  # optional on input; server will assign sequentially

class PutChildrenRequest(BaseModel):
    parent_id: int
    children: List[Child] = Field(default_factory=list)

@router.get("/roots")
def list_roots():
    conn = get_conn()
    cur = conn.execute("SELECT id, label FROM nodes WHERE depth=0 ORDER BY id")
    data = [{"id": r[0], "label": r[1]} for r in cur.fetchall()]
    conn.close()
    return {"items": data, "total": len(data)}

@router.get("/children")
def list_children(parent_id: int):
    conn = get_conn()
    cur = conn.execute(
        "SELECT id, label, slot FROM nodes WHERE parent_id=? ORDER BY slot ASC", (parent_id,)
    )
    rows = [{"id": r[0], "label": r[1], "slot": r[2]} for r in cur.fetchall()]
    conn.close()
    return {"items": rows, "total": len(rows)}

@router.put("/children")
def put_children(payload: PutChildrenRequest):
    # Atomic replace children for a given parent (simple version).
    parent_id = payload.parent_id
    labels = [c.label.strip() for c in payload.children if c.label.strip()]
    # Basic validation
    if len(labels) != len(set([l.lower() for l in labels])):
        raise HTTPException(status_code=422, detail=[{"loc": ["children"], "msg": "duplicate labels"}])

    conn = get_conn()
    try:
        conn.execute("BEGIN")
        # Remove current children
        conn.execute("DELETE FROM nodes WHERE parent_id=?", (parent_id,))
        # Insert new children with sequential slots starting at 1
        slot = 1
        for lab in labels:
            # fetch parent depth
            cur = conn.execute("SELECT depth FROM nodes WHERE id=?", (parent_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="parent not found")
            depth = row[0] + 1
            conn.execute(
                "INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,?,?,?)",
                (parent_id, depth, slot, lab),
            )
            slot += 1
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return {"ok": True, "count": len(labels)}

@router.delete("/root")
def delete_root(root_id: int = Query(..., ge=1)):
    conn = get_conn()
    try:
        # verify depth==0
        cur = conn.execute("SELECT id FROM nodes WHERE id=? AND depth=0", (root_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="root not found")
        conn.execute("DELETE FROM nodes WHERE id=?", (root_id,))
        conn.commit()
        return {"ok": True, "deleted": root_id}
    finally:
        conn.close()

@router.get("/node")
def get_node(node_id: int):
    """Return node id,label,depth,parent_id for breadcrumbs/drilldown."""
    conn = get_conn()
    try:
        cur = conn.execute("SELECT id,label,depth,parent_id FROM nodes WHERE id=?", (node_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="not found")
        return {"id": row[0], "label": row[1], "depth": row[2], "parent_id": row[3]}
    finally:
        conn.close()
