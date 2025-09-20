from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from fastapi.responses import Response
import sqlite3
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from api.settings import get_db_path
from api.dependencies import get_db_connection, get_repository
from api.repositories.tree_repo import TreeRepository

router = APIRouter(prefix="/api/v1/tree", tags=["tree"])

class Child(BaseModel):
    label: str = Field(min_length=1, max_length=256)
    slot: Optional[int] = None  # optional on input; server will assign sequentially

class PutChildrenRequest(BaseModel):
    parent_id: int
    children: List[Child] = Field(default_factory=list)

@router.get("/roots")
def list_roots(conn: sqlite3.Connection = Depends(get_db_connection)):
    cur = conn.execute("SELECT id, label FROM nodes WHERE depth=0 ORDER BY id")
    data = [{"id": r[0], "label": r[1]} for r in cur.fetchall()]
    return {"items": data, "total": len(data)}

@router.get("/children")
def list_children(parent_id: int, only_red: bool = Query(default=False), repo: TreeRepository = Depends(get_repository)):
    items = repo.list_children(parent_id, only_red)
    return {"items": items, "total": len(items)}

@router.put("/children")
def put_children(payload: PutChildrenRequest, conn: sqlite3.Connection = Depends(get_db_connection)):
    # Atomic replace children for a given parent (simple version).
    parent_id = payload.parent_id
    labels = [c.label.strip() for c in payload.children if c.label.strip()]
    # Basic validation
    if len(labels) != len(set([l.lower() for l in labels])):
        raise HTTPException(status_code=422, detail=[{"loc": ["children"], "msg": "duplicate labels"}])

    try:
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
    except Exception:
        raise
    return {"ok": True, "count": len(labels)}

@router.delete("/root")
def delete_root(root_id: int = Query(..., ge=1), conn: sqlite3.Connection = Depends(get_db_connection)):
    # verify depth==0
    cur = conn.execute("SELECT id FROM nodes WHERE id=? AND depth=0", (root_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="root not found")
    conn.execute("DELETE FROM nodes WHERE id=?", (root_id,))
    return {"ok": True, "deleted": root_id}

@router.get("/node")
def get_node(node_id: int, conn: sqlite3.Connection = Depends(get_db_connection)):
    """Return node id,label,depth,parent_id for breadcrumbs/drilldown."""
    cur = conn.execute("SELECT id,label,depth,parent_id FROM nodes WHERE id=?", (node_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    return {"id": row[0], "label": row[1], "depth": row[2], "parent_id": row[3]}

@router.get("/next-underfilled")
def next_underfilled(
    root_id: int,
    after_id: Optional[int] = Query(default=None),
    repo: TreeRepository = Depends(get_repository)
):
    """Find the next parent with fewer than 5 children within the specified root subtree."""
    res = repo.next_underfilled_parent_scoped(root_id=root_id, after_id=after_id)
    if not res:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return res

@router.put("/edge/flag")
def set_edge_flag(payload: Dict, repo: TreeRepository = Depends(get_repository)):
    """Set or unset the red flag for a specific parent-child edge."""
    parent_id = int(payload.get("parent_id"))
    child_id = int(payload.get("child_id"))
    red_flag = bool(payload.get("red_flag"))
    repo.set_edge_flag(parent_id, child_id, red_flag)
    return {"ok": True, "parent_id": parent_id, "child_id": child_id, "red_flag": red_flag}

@router.get("/clone/candidates")
def clone_candidates(label: str = Query(...), repo: TreeRepository = Depends(get_repository)):
    """Find nodes with the given label that have children (potential clone sources)."""
    return {"items": repo.find_clone_candidates_by_label(label)}

@router.post("/clone")
def clone_subtree(source_id: int = Body(..., embed=True), dest_parent_id: int = Body(..., embed=True), repo: TreeRepository = Depends(get_repository)):
    """Clone a subtree from source_id to dest_parent_id."""
    created = repo.clone_subtree(source_id, dest_parent_id)
    if created == 0:
        raise HTTPException(status_code=404, detail="source not found")
    return {"ok": True, "created": created}
