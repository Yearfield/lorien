import sqlite3

import anyio
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from api.core.validators import validate_child_labels_and_limit
from api.dependencies import get_db_connection, get_repository
from api.repositories.tree_repo import TreeRepository

router = APIRouter(prefix="/api/v1/tree", tags=["tree"])


class Child(BaseModel):
    label: str = Field(min_length=1, max_length=256)
    slot: int | None = None  # optional on input; server will assign sequentially


class PutChildrenRequest(BaseModel):
    parent_id: int
    children: list[Child] = Field(default_factory=list)


class AddChildRequest(BaseModel):
    parent_id: int
    label: str = Field(min_length=1, max_length=256)


class CreateRootBody(BaseModel):
    label: str


@router.get("/roots")
async def list_roots(conn: sqlite3.Connection = Depends(get_db_connection)):
    cur = await anyio.to_thread.run_sync(
        conn.execute, "SELECT id, label FROM nodes WHERE depth=0 ORDER BY id"
    )
    rows = await anyio.to_thread.run_sync(cur.fetchall)
    data = []
    for r in rows:
        raw_label = r[1] or ""
        data.append(
            {
                "id": r[0],
                "label": raw_label,
                "display_label": raw_label,
            }
        )
    return {"items": data, "total": len(data)}


@router.post("/roots", status_code=201)
async def create_root(body: CreateRootBody, conn: sqlite3.Connection = Depends(get_db_connection)):
    lab = body.label.strip()
    if not lab:
        raise HTTPException(status_code=422, detail="empty label")
    cur = await anyio.to_thread.run_sync(
        conn.execute,
        "INSERT INTO nodes (label, depth, parent_id, slot) VALUES (?, 0, NULL, NULL) RETURNING id, label, depth",
        (lab,),
    )
    row = await anyio.to_thread.run_sync(cur.fetchone)
    return {"id": row[0], "label": row[1], "depth": row[2]}


@router.get("/children")
async def list_children(
    parent_id: int,
    only_red: bool = Query(default=False),
    repo: TreeRepository = Depends(get_repository),
):
    items = await repo.list_children(parent_id, only_red)
    return {"items": items, "total": len(items)}


@router.put("/children")
async def put_children(
    payload: PutChildrenRequest, conn: sqlite3.Connection = Depends(get_db_connection)
):
    # Atomic replace children for a given parent (simple version).
    parent_id = payload.parent_id
    # Service-level guard for ≤5 rule + duplicates
    labels = validate_child_labels_and_limit(payload.children, limit=5)

    try:
        cur = await anyio.to_thread.run_sync(
            conn.execute, "SELECT depth FROM nodes WHERE id=?", (parent_id,)
        )
        parent_row = await anyio.to_thread.run_sync(cur.fetchone)
        if not parent_row:
            raise HTTPException(status_code=404, detail="parent not found")
        parent_depth = parent_row[0]
        if parent_depth >= 6:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[
                    {
                        "loc": ["parent_id"],
                        "msg": "cannot add children beyond depth 6",
                        "type": "value_error.max_depth",
                    }
                ],
            )

        # Remove current children
        await anyio.to_thread.run_sync(
            conn.execute, "DELETE FROM nodes WHERE parent_id=?", (parent_id,)
        )

        # Insert new children with sequential slots starting at 1
        assigned_slot = 1
        for lab in labels:
            depth = parent_depth + 1
            try:
                await anyio.to_thread.run_sync(
                    conn.execute,
                    "INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,?,?,?)",
                    (parent_id, depth, assigned_slot, lab),
                )
            except sqlite3.IntegrityError as e:
                # Map unique slot conflicts to 409 for better client handling
                msg = str(e).lower()
                if "unique" in msg and (
                    "nodes(parent_id, slot)" in msg or "idx_parent_slot_unique" in msg
                ):
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "error": "slot_conflict",
                            "slot": assigned_slot,
                            "parent_id": parent_id,
                            "hint": "Concurrent edit detected. Slot already occupied.",
                        },
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


@router.post("/child")
async def add_child(
    payload: AddChildRequest, conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Safely add a single child to a parent without affecting existing children."""
    parent_id = payload.parent_id
    label = payload.label.strip()

    if not label:
        raise HTTPException(status_code=422, detail="empty label")

    try:
        # Verify parent exists and get its depth
        cur = await anyio.to_thread.run_sync(
            conn.execute, "SELECT depth FROM nodes WHERE id=?", (parent_id,)
        )
        parent_row = await anyio.to_thread.run_sync(cur.fetchone)
        if not parent_row:
            raise HTTPException(status_code=404, detail="parent not found")
        parent_depth = parent_row[0]

        if parent_depth >= 6:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[
                    {
                        "loc": ["parent_id"],
                        "msg": "cannot add children beyond depth 6",
                        "type": "value_error.max_depth",
                    }
                ],
            )

        # Check current children count
        cur = await anyio.to_thread.run_sync(
            conn.execute, "SELECT COUNT(*) FROM nodes WHERE parent_id=?", (parent_id,)
        )
        current_count = await anyio.to_thread.run_sync(cur.fetchone)
        if current_count[0] >= 5:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[
                    {
                        "loc": ["parent_id"],
                        "msg": "parent already has 5 children",
                        "type": "value_error.max_children",
                    }
                ],
            )

        # Find next available slot
        cur = await anyio.to_thread.run_sync(
            conn.execute, "SELECT MAX(slot) FROM nodes WHERE parent_id=?", (parent_id,)
        )
        max_slot = await anyio.to_thread.run_sync(cur.fetchone)
        next_slot = (max_slot[0] or 0) + 1

        # Insert new child
        depth = parent_depth + 1
        await anyio.to_thread.run_sync(
            conn.execute,
            "INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,?,?,?)",
            (parent_id, depth, next_slot, label),
        )

        return {"ok": True, "parent_id": parent_id, "label": label, "slot": next_slot}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add child: {str(e)}",
        )


@router.delete("/roots/{root_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_root(root_id: int, conn: sqlite3.Connection = Depends(get_db_connection)):
    """Delete a root node and all its descendants."""
    cur = await anyio.to_thread.run_sync(
        conn.execute, "SELECT id, depth, parent_id FROM nodes WHERE id = ?", (root_id,)
    )
    row = await anyio.to_thread.run_sync(cur.fetchone)
    if not row:
        raise HTTPException(status_code=404, detail="root not found")
    if row[1] != 0 or row[2] is not None:
        raise HTTPException(status_code=422, detail="not a root")
    await anyio.to_thread.run_sync(conn.execute, "DELETE FROM nodes WHERE id = ?", (root_id,))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/root")
async def delete_root_legacy(
    root_id: int = Query(..., alias="root_id"),
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Legacy delete endpoint accepting `root_id` as query param and returning json payload."""
    cur = await anyio.to_thread.run_sync(
        conn.execute, "SELECT id, depth, parent_id FROM nodes WHERE id = ?", (root_id,)
    )
    row = await anyio.to_thread.run_sync(cur.fetchone)
    if not row:
        raise HTTPException(status_code=404, detail="root not found")
    if row[1] != 0 or row[2] is not None:
        raise HTTPException(status_code=422, detail="not a root")
    await anyio.to_thread.run_sync(conn.execute, "DELETE FROM nodes WHERE id = ?", (root_id,))
    return {"ok": True, "root_id": root_id}


@router.get("/node")
async def get_node(node_id: int, conn: sqlite3.Connection = Depends(get_db_connection)):
    """Return node id,label,depth,parent_id for breadcrumbs/drilldown."""
    cur = await anyio.to_thread.run_sync(
        conn.execute, "SELECT id,label,depth,parent_id FROM nodes WHERE id=?", (node_id,)
    )
    row = await anyio.to_thread.run_sync(cur.fetchone)
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    return {"id": row[0], "label": row[1], "depth": row[2], "parent_id": row[3]}


@router.get("/search-by-label")
async def search_by_label(label: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    """Find parents with the given label."""
    cur = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT id, label, depth FROM nodes WHERE LOWER(TRIM(label)) = LOWER(TRIM(?)) ORDER BY depth, id",
        (label,),
    )
    rows = await anyio.to_thread.run_sync(cur.fetchall)
    items = [{"id": row[0], "label": row[1], "depth": row[2]} for row in rows]
    return {"items": items, "total": len(items)}


@router.put("/node/{node_id}/rename")
async def rename_node(
    node_id: int, body: dict, conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Rename a node by updating its label."""
    new_label = body.get("label", "").strip()
    if not new_label:
        raise HTTPException(status_code=422, detail="empty label")

    # Check if node exists
    cur = await anyio.to_thread.run_sync(
        conn.execute, "SELECT id FROM nodes WHERE id = ?", (node_id,)
    )
    if not await anyio.to_thread.run_sync(cur.fetchone):
        raise HTTPException(status_code=404, detail="node not found")

    # Update the label
    await anyio.to_thread.run_sync(
        conn.execute,
        "UPDATE nodes SET label = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id = ?",
        (new_label, node_id),
    )

    return {"ok": True, "node_id": node_id, "new_label": new_label}


class MergeParentsRequest(BaseModel):
    current_parent_id: int
    existing_parent_id: int
    selected_children: list[str]


@router.post("/merge-parents")
async def merge_parents(
    body: MergeParentsRequest, conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Merge two parents by combining their children and deleting the current parent."""
    current_id = body.current_parent_id
    existing_id = body.existing_parent_id
    selected_children = body.selected_children

    if len(selected_children) > 5:
        raise HTTPException(status_code=422, detail="cannot have more than 5 children")

    # Verify both parents exist and get their depths
    cur = await anyio.to_thread.run_sync(
        conn.execute, "SELECT id, depth FROM nodes WHERE id IN (?, ?)", (current_id, existing_id)
    )
    rows = await anyio.to_thread.run_sync(cur.fetchall)
    if len(rows) != 2:
        raise HTTPException(status_code=404, detail="one or both parents not found")

    # Get the depth of the existing parent (target parent)
    existing_depth = None
    for row in rows:
        if row[0] == existing_id:
            existing_depth = row[1]
            break

    if existing_depth is None:
        raise HTTPException(status_code=404, detail="existing parent not found")

    try:
        # Delete all children from existing parent first (we'll replace with selected ones)
        await anyio.to_thread.run_sync(
            conn.execute, "DELETE FROM nodes WHERE parent_id = ?", (existing_id,)
        )
        await anyio.to_thread.run_sync(conn.commit)

        # Add selected children to existing parent with correct depth
        for i, child_label in enumerate(selected_children, 1):
            child_depth = existing_depth + 1
            is_leaf = 1 if child_depth >= 5 else 0

            await anyio.to_thread.run_sync(
                conn.execute,
                """INSERT INTO nodes (parent_id, depth, slot, label, is_leaf, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ','now'), strftime('%Y-%m-%dT%H:%M:%fZ','now'))""",
                (existing_id, child_depth, i, child_label, is_leaf),
            )
        await anyio.to_thread.run_sync(conn.commit)

        # Delete the current parent and all its children (cascade delete will handle this)
        await anyio.to_thread.run_sync(
            conn.execute, "DELETE FROM nodes WHERE id = ?", (current_id,)
        )
        await anyio.to_thread.run_sync(conn.commit)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"merge failed: {str(e)}")

    return {"ok": True, "merged_parent_id": existing_id, "deleted_parent_id": current_id}


@router.get("/ancestors")
async def get_ancestors(node_id: int, repo: TreeRepository = Depends(get_repository)):
    """Get the ancestor chain from root to the given node."""
    items = await repo.get_ancestors(node_id)
    if not items:
        raise HTTPException(status_code=404, detail="node not found")
    return {"items": items, "total": len(items)}


@router.get("/next-underfilled")
async def next_underfilled(
    root_id: int | None = Query(default=None),
    after_id: int | None = Query(default=None),
    repo: TreeRepository = Depends(get_repository),
):
    """Find the next parent with fewer than 5 children.

    If root_id is provided, search is scoped to that root subtree; otherwise searches across all roots.
    """
    if root_id is None:
        res = await repo.next_underfilled_parent(after_id=after_id)
    else:
        res = await repo.next_underfilled_parent_scoped(root_id=root_id, after_id=after_id)
    if not res:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return res


@router.put("/edge/flag")
async def set_edge_flag(payload: dict, repo: TreeRepository = Depends(get_repository)):
    """Set or unset the red flag for a specific parent-child edge."""
    parent_id = int(payload.get("parent_id"))
    child_id = int(payload.get("child_id"))
    red_flag = bool(payload.get("red_flag"))
    await repo.set_edge_flag(parent_id, child_id, red_flag)
    return {"ok": True, "parent_id": parent_id, "child_id": child_id, "red_flag": red_flag}


@router.get("/clone/candidates")
async def clone_candidates(label: str = Query(...), repo: TreeRepository = Depends(get_repository)):
    """Find nodes with the given label that have children (potential clone sources)."""
    return {"items": await repo.find_clone_candidates_by_label(label)}


@router.post("/clone")
async def clone_subtree(
    source_id: int = Body(..., embed=True),
    dest_parent_id: int = Body(..., embed=True),
    repo: TreeRepository = Depends(get_repository),
):
    """Clone a subtree from source_id to dest_parent_id."""
    try:
        created = await repo.clone_subtree(source_id, dest_parent_id)
    except ValueError as exc:
        msg = str(exc)
        if msg == "dest_parent_not_found":
            raise HTTPException(status_code=404, detail="destination parent not found")
        if msg == "dest_parent_at_max_depth":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[
                    {
                        "loc": ["dest_parent_id"],
                        "msg": "destination parent cannot accept children at depth 6",
                        "type": "value_error.max_depth",
                    }
                ],
            )
        if msg == "depth_limit_exceeded":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[
                    {
                        "loc": ["source_id"],
                        "msg": "cloned subtree would exceed depth limit",
                        "type": "value_error.max_depth",
                    }
                ],
            )
        if msg == "max_children_exceeded":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[
                    {
                        "loc": ["dest_parent_id"],
                        "msg": "destination parent already has 5 children",
                        "type": "value_error.max_children",
                    }
                ],
            )
        raise
    if created == 0:
        raise HTTPException(status_code=404, detail="source not found")
    return {"ok": True, "created": created}
