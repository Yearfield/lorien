from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from api.db import get_conn, ensure_schema, tx

router = APIRouter()

@router.post("/admin/sanitize-labels")
def sanitize_labels(dry_run: bool = Query(True)):
    """
    Deletes nodes whose label is NULL/blank/'nan' (case-insensitive).
    Returns counts; dry_run default True.
    """
    conn = get_conn()
    ensure_schema(conn)
    sel = """
      SELECT id FROM nodes
      WHERE label IS NULL OR TRIM(label)='' OR LOWER(label)='nan'
    """
    ids = [r[0] for r in conn.execute(sel).fetchall()]
    deleted = 0
    if not dry_run and ids:
        with tx(conn):
            for nid in ids:
                conn.execute("DELETE FROM nodes WHERE id=?", (nid,))
                deleted += 1
    return JSONResponse({"ok": True, "candidate_ids": ids, "deleted": deleted, "dry_run": dry_run})
