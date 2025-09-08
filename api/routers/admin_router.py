from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse

from api.db import get_conn, ensure_schema, tx
from api.repositories.admin_repo import clear_workspace, clear_nodes_only, hard_reset_nodes
from datetime import datetime, timezone
import re

router = APIRouter()

@router.post("/admin/clear")
def admin_clear(include_dictionary: bool = Query(False)):
    conn = get_conn()
    ensure_schema(conn)
    try:
        result = clear_workspace(conn, include_dictionary=include_dictionary)
        return JSONResponse(result)
    except RuntimeError as e:
        # integrity_check failure or other explicit runtime errors
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear failed: {e}")

@router.post("/admin/clear-nodes")
def clear_nodes_endpoint():
    """Clear nodes and outcomes only (keeps dictionary tables intact)."""
    conn = get_conn()
    ensure_schema(conn)
    try:
        clear_nodes_only(conn)
        return JSONResponse({"ok": True})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear nodes failed: {e}")


@router.post("/admin/hard-reset-nodes")
def hard_reset_nodes_endpoint():
    """Hard reset: drop and recreate nodes/outcomes tables to guarantee zero remnants."""
    conn = get_conn()
    ensure_schema(conn)
    try:
        hard_reset_nodes(conn)
        return JSONResponse({"ok": True, "reset": "nodes/outcomes dropped+recreated"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hard reset failed: {e}")


@router.get("/admin/search-test-labels")
def search_test_labels(q: str | None = None, limit: int = 50, offset: int = 0):
    """Search for suspect/test labels in the database."""
    conn = get_conn()
    ensure_schema(conn)
    patterns = ["test%", "%vm%", "bp", "pulse", "high", "low", "a"]  # broaden as needed
    rows = []
    if q:
        cur = conn.execute("SELECT id,label,depth FROM nodes WHERE LOWER(label) LIKE ? ORDER BY depth, label LIMIT ? OFFSET ?",
                           (f"%{q.lower()}%", limit, offset))
        rows = [dict(id=r[0], label=r[1], depth=r[2]) for r in cur.fetchall()]
    else:
        for pat in patterns:
            cur = conn.execute("SELECT id,label,depth FROM nodes WHERE LOWER(label) LIKE ? LIMIT 200", (pat.lower(),))
            rows += [dict(id=r[0], label=r[1], depth=r[2]) for r in cur.fetchall()]
    return JSONResponse({"items": rows[:limit], "total": len(rows), "limit": limit, "offset": offset})

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip()).lower()


@router.post("/admin/sync-dictionary-from-tree")
def sync_dictionary_from_tree():
    """
    Scan unique node labels and insert missing dictionary_terms.
    - depth 0 → type 'vital_measurement'
    - depth 1..5 → type 'node_label'
    Idempotent: existing (type, normalized) pairs are skipped.
    """
    conn = get_conn()
    ensure_schema(conn)
    try:
      cur = conn.cursor()
      # Collect distinct labels by depth bucket
      cur.execute("SELECT DISTINCT label, depth FROM nodes")
      rows = cur.fetchall()
      inserted = 0
      now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
      for r in rows:
          label = r[0]
          depth = int(r[1])
          dict_type = 'vital_measurement' if depth == 0 else 'node_label'
          norm = _normalize(label)
          # Skip if exists
          cur.execute(
              "SELECT 1 FROM dictionary_terms WHERE type = ? AND normalized = ? LIMIT 1",
              (dict_type, norm)
          )
          if cur.fetchone():
              continue
          # Insert new
          cur.execute(
              """
              INSERT INTO dictionary_terms (type, term, normalized, hints, red_flag, updated_at, created_at)
              VALUES (?, ?, ?, NULL, NULL, ?, ?)
              """,
              (dict_type, label, norm, now, now)
          )
          inserted += 1
      conn.commit()
      return JSONResponse({"inserted": inserted})
    except Exception as e:
      raise HTTPException(status_code=500, detail=f"Sync failed: {e}")
