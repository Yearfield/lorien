import sqlite3
from typing import Any

import anyio
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from api.dependencies import get_db_connection

router = APIRouter(prefix="/api/v1/tree", tags=["tree"])


async def _subtree_snapshot(conn: sqlite3.Connection, node_id: int) -> dict[str, Any]:
    # recursive CTE to fetch subtree with relative order
    sql = """
    WITH RECURSIVE sub(id, parent_id, depth, slot, label) AS (
      SELECT id, parent_id, depth, slot, label FROM nodes WHERE id = ?
      UNION ALL
      SELECT n.id, n.parent_id, n.depth, n.slot, n.label
      FROM nodes n JOIN sub s ON n.parent_id = s.id
    )
    SELECT id, parent_id, depth, slot, label FROM sub ORDER BY depth, parent_id, slot, id;
    """
    cursor = await anyio.to_thread.run_sync(conn.execute, sql, (node_id,))
    raw_rows = await anyio.to_thread.run_sync(cursor.fetchall)
    rows = [dict(id=r[0], parent_id=r[1], depth=r[2], slot=r[3], label=r[4]) for r in raw_rows]
    if not rows:
        raise HTTPException(status_code=404, detail="node_not_found")
    # origin is the root of that subtree
    origin = rows[0]
    # collect children grouped by parent
    return {
        "origin": origin,  # {id, parent_id, depth, slot, label}
        "nodes": rows,  # flat list to re-create shape
    }


@router.delete("/node/{node_id}")
async def delete_node(
    node_id: int = Path(..., ge=1),
    dry_run: bool = Query(default=False),
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    # Always return a snapshot so clients can undo
    snap = await _subtree_snapshot(conn, node_id)
    if dry_run:
        return {"dry_run": True, "snapshot": snap}
    try:
        await anyio.to_thread.run_sync(conn.execute, "DELETE FROM nodes WHERE id = ?", (node_id,))
        await anyio.to_thread.run_sync(conn.commit)
        return {"dry_run": False, "snapshot": snap}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"delete_failed: {e}")


@router.post("/subtree/restore")
async def restore_subtree(
    payload: dict[str, Any],
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """
    payload: {
      "snapshot": {"origin": {...}, "nodes":[...] }
    }
    Restores the snapshot below its original parent/slots.
    """
    snap = payload.get("snapshot")
    if not snap or "origin" not in snap or "nodes" not in snap:
        raise HTTPException(status_code=400, detail="bad_snapshot")
    origin = snap["origin"]
    nodes = snap["nodes"]
    # Figure original parent and target depth
    parent_id = origin.get("parent_id")
    parent_depth = None
    if parent_id is not None:
        cursor = await anyio.to_thread.run_sync(
            conn.execute, "SELECT depth FROM nodes WHERE id=?", (parent_id,)
        )
        row = await anyio.to_thread.run_sync(cursor.fetchone)
        if not row:
            raise HTTPException(status_code=404, detail="parent_missing_for_restore")
        parent_depth = int(row[0])
    base_depth = parent_depth if parent_depth is not None else -1
    # check Option-B ≤5 for the origin insertion only (immediate children count)
    if parent_id is not None:
        cursor = await anyio.to_thread.run_sync(
            conn.execute, "SELECT COUNT(*) FROM nodes WHERE parent_id=?", (parent_id,)
        )
        cnt = (await anyio.to_thread.run_sync(cursor.fetchone))[0]
        # if the origin was a sibling under parent, we are adding 1
        if cnt >= 5:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[
                    {"type": "value_error.max_children", "msg": "parent already has 5 children"}
                ],
            )
    # Recreate subtree: insert origin, then breadth-first children
    try:
        # Map old_id -> new_id to reconnect children
        idmap: dict[int, int] = {}
        # Insert origin
        new_origin_depth = base_depth + 1
        ins = await anyio.to_thread.run_sync(
            conn.execute,
            "INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,?,?,?)",
            (parent_id, new_origin_depth, origin.get("slot"), origin.get("label")),
        )
        new_origin_id = ins.lastrowid
        idmap[origin["id"]] = new_origin_id
        # Insert descendants in order; reconnect their parent using idmap
        origin_depth_value = origin.get("depth", 0)
        for n in nodes[1:]:
            old_pid = n.get("parent_id")
            if old_pid not in idmap:
                # parent in snapshot not restored yet (should not happen due to ordering)
                raise HTTPException(status_code=400, detail="bad_snapshot_order")
            new_pid = idmap[old_pid]
            # Calculate correct depth for child nodes
            child_depth = base_depth + 1 + (n.get("depth", 0) - origin_depth_value)
            ins2 = await anyio.to_thread.run_sync(
                conn.execute,
                "INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,?,?,?)",
                (new_pid, child_depth, n.get("slot"), n.get("label")),
            )
            idmap[n["id"]] = ins2.lastrowid
        return {"restored": True, "new_origin_id": new_origin_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"restore_failed: {e}")
