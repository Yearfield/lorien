from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from fastapi.responses import Response
import sqlite3
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from api.settings import get_db_path
from api.dependencies import get_db_connection, get_repository
from api.repositories.tree_repo import TreeRepository
from api.core.validators import validate_child_labels_and_limit, coerce_assigned_slots

router = APIRouter(prefix="/api/v1/tree", tags=["tree"])

class Child(BaseModel):
    label: str = Field(min_length=1, max_length=256)
    slot: Optional[int] = None  # optional on input; server will assign sequentially

class PutChildrenRequest(BaseModel):
    parent_id: int
    children: List[Child] = Field(default_factory=list)

class CreateRootBody(BaseModel):
    label: str

@router.get("/roots")
def list_roots(conn: sqlite3.Connection = Depends(get_db_connection)):
    cur = conn.execute("SELECT id, label FROM nodes WHERE depth=0 ORDER BY id")
    data = []
    for r in cur.fetchall():
        raw_label = r[1] or ""
        data.append({
            "id": r[0],
            "label": raw_label.lower(),
            "display_label": raw_label,
        })
    return {"items": data, "total": len(data)}

@router.post("/roots", status_code=201)
def create_root(body: CreateRootBody, conn: sqlite3.Connection = Depends(get_db_connection)):
    lab = body.label.strip()
    if not lab:
        raise HTTPException(status_code=422, detail="empty label")
    cur = conn.execute("INSERT INTO nodes (label, depth, parent_id, slot) VALUES (?, 0, NULL, NULL) RETURNING id, label, depth", (lab,))
    row = cur.fetchone()
    return {"id": row[0], "label": row[1], "depth": row[2]}

@router.get("/children")
def list_children(parent_id: int, only_red: bool = Query(default=False), repo: TreeRepository = Depends(get_repository)):
    items = repo.list_children(parent_id, only_red)
    return {"items": items, "total": len(items)}

@router.put("/children")
def put_children(payload: PutChildrenRequest, conn: sqlite3.Connection = Depends(get_db_connection)):
    # Atomic replace children for a given parent (simple version).
    parent_id = payload.parent_id
    # Service-level guard for ≤5 rule + duplicates
    labels = validate_child_labels_and_limit(payload.children, limit=5)

    try:
        parent_row = conn.execute("SELECT depth FROM nodes WHERE id=?", (parent_id,)).fetchone()
        if not parent_row:
            raise HTTPException(status_code=404, detail="parent not found")
        parent_depth = parent_row[0]
        if parent_depth >= 5:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[{"loc": ["parent_id"], "msg": "cannot add children beyond depth 6", "type": "value_error.max_depth"}],
            )

        # Remove current children
        conn.execute("DELETE FROM nodes WHERE parent_id=?", (parent_id,))

        # Insert new children with sequential slots starting at 1
        assigned_slot = 1
        for lab in labels:
            depth = parent_depth + 1
            try:
                conn.execute(
                    "INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,?,?,?)",
                    (parent_id, depth, assigned_slot, lab),
                )
            except sqlite3.IntegrityError as e:
                # Map unique slot conflicts to 409 for better client handling
                msg = str(e).lower()
                if "unique" in msg and ("nodes(parent_id, slot)" in msg or "idx_parent_slot_unique" in msg):
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "error": "slot_conflict",
                            "slot": assigned_slot,
                            "parent_id": parent_id,
                            "hint": "Concurrent edit detected. Slot already occupied."
                        }
                    )
                # Re-raise non-slot integrity errors
                raise
            assigned_slot += 1
    except HTTPException:
        # Let FastAPI handle structured HTTP errors
        raise
    except Exception:
        # Preserve default error propagation for unexpected failures
        raise
    return {"ok": True, "count": len(labels)}

@router.delete("/roots/{root_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_root(root_id: int, conn: sqlite3.Connection = Depends(get_db_connection)):
    """Delete a root node and all its descendants."""
    row = conn.execute("SELECT id, depth, parent_id FROM nodes WHERE id = ?", (root_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="root not found")
    if row[1] != 0 or row[2] is not None:
        raise HTTPException(status_code=422, detail="not a root")
    conn.execute("DELETE FROM nodes WHERE id = ?", (root_id,))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/root")
def delete_root_legacy(root_id: int = Query(..., alias="root_id"), conn: sqlite3.Connection = Depends(get_db_connection)):
    """Legacy delete endpoint accepting `root_id` as query param and returning json payload."""
    row = conn.execute("SELECT id, depth, parent_id FROM nodes WHERE id = ?", (root_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="root not found")
    if row[1] != 0 or row[2] is not None:
        raise HTTPException(status_code=422, detail="not a root")
    conn.execute("DELETE FROM nodes WHERE id = ?", (root_id,))
    return {"ok": True, "root_id": root_id}

@router.get("/node")
def get_node(node_id: int, conn: sqlite3.Connection = Depends(get_db_connection)):
    """Return node id,label,depth,parent_id for breadcrumbs/drilldown."""
    cur = conn.execute("SELECT id,label,depth,parent_id FROM nodes WHERE id=?", (node_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    return {"id": row[0], "label": row[1], "depth": row[2], "parent_id": row[3]}

@router.get("/ancestors")
def get_ancestors(node_id: int, repo: TreeRepository = Depends(get_repository)):
    """Get the ancestor chain from root to the given node."""
    items = repo.get_ancestors(node_id)
    if not items:
        raise HTTPException(status_code=404, detail="node not found")
    return {"items": items, "total": len(items)}

@router.get("/next-underfilled")
def next_underfilled(
    root_id: Optional[int] = Query(default=None),
    after_id: Optional[int] = Query(default=None),
    repo: TreeRepository = Depends(get_repository)
):
    """Find the next parent with fewer than 5 children.

    If root_id is provided, search is scoped to that root subtree; otherwise searches across all roots.
    """
    if root_id is None:
        res = repo.next_underfilled_parent(after_id=after_id)
    else:
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
    try:
        created = repo.clone_subtree(source_id, dest_parent_id)
    except ValueError as exc:
        msg = str(exc)
        if msg == "dest_parent_not_found":
            raise HTTPException(status_code=404, detail="destination parent not found")
        if msg == "dest_parent_at_max_depth":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[{"loc": ["dest_parent_id"], "msg": "destination parent cannot accept children at depth 6", "type": "value_error.max_depth"}],
            )
        if msg == "depth_limit_exceeded":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[{"loc": ["source_id"], "msg": "cloned subtree would exceed depth limit", "type": "value_error.max_depth"}],
            )
        if msg == "max_children_exceeded":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[{"loc": ["dest_parent_id"], "msg": "destination parent already has 5 children", "type": "value_error.max_children"}],
            )
        raise
    if created == 0:
        raise HTTPException(status_code=404, detail="source not found")
    return {"ok": True, "created": created}
