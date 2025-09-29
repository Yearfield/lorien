from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from api.dependencies import get_db_connection
from Engines.EngineLongBow import ingest_file, apply_import, apply_import_with_metadata, FROZEN_HEADER
from Engines.EngineLongBow.ingest import read_file, extract_paths
import sqlite3
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict

router = APIRouter()

def _group_overfive_within_file(paths: List[List[str]], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Heuristic preview-only check: within the uploaded file, if any parent path
    (D0..Dk) produces >limit distinct child labels at Dk+1, flag rows.
    Returns a list of error dicts with row numbers (1-based including header).
    """
    # Build mapping: parent_tuple -> set(child_labels) and rows exceeding limit
    parent_children = defaultdict(set)
    violations = []  # (row_idx, parent_key, child_label)
    for i, p in enumerate(paths, start=2):  # row 1 = header
        # p is like ["D0","D1",...,"D6"] (may contain None/"")
        last_parent_idx = max([idx for idx, val in enumerate(p[:-1]) if (val or "").strip()] or [-1])
        if last_parent_idx < 0:
            continue
        parent_key = tuple((p[j] or "").strip() for j in range(last_parent_idx + 1))
        child_label = (p[last_parent_idx + 1] or "").strip()
        if not child_label:
            continue
        pc = parent_children[parent_key]
        pc.add(child_label.lower())
        if len(pc) > limit:
            violations.append({"row": i, "msg": f"parent {parent_key} would exceed {limit} children (preview)", "type": "value_error.max_children"})
    return violations


@router.post("/import/preview")
async def import_preview(file: UploadFile = File(...)):
    """Preview import without writing to database - shows detected paths."""
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", "file"], "msg": f"Could not read file: {str(e)}", "type":"value_error.file_read"}]
        )
    
    try:
        # Read DataFrame and extract canonical paths (without DB writes)
        df = read_file(file_content, file.filename)
        paths = extract_paths(df)  # List[List[str]] length 7 for D0..D6

        # File-only guard: highlight parents that would exceed limit
        errors = _group_overfive_within_file(paths, limit=5)

        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "header": FROZEN_HEADER,
                "stats": {"found_paths": len(paths)},
                "errors": errors,  # clients show this as preview banner/list
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["body"], "msg": f"Import failed: {str(e)}", "type":"value_error.import_failed"}]
        )

@router.post("/import")
async def import_apply(
    mode: str = Query(default="append", regex="^(append|replace)$"),
    enforce_five: bool = Query(default=True),
    file: UploadFile = File(...),
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """
    Apply import transactionally. If enforce_five=True, the import is rolled back if any parent ends with >5 children.
    """
    try:
        blob = await file.read()
        # Begin explicit transaction
        conn.isolation_level = None
        conn.execute("BEGIN IMMEDIATE")
        result = apply_import_with_metadata(conn=conn, file_bytes=blob, mode=mode)

        if enforce_five:
            # Validate post-apply state
            over = conn.execute(
                """
                WITH c AS (
                  SELECT parent_id, COUNT(*) AS cnt
                  FROM nodes
                  WHERE parent_id IS NOT NULL
                  GROUP BY parent_id
                )
                SELECT c.parent_id, n.label, c.cnt
                FROM c
                JOIN nodes n ON n.id = c.parent_id
                WHERE c.cnt > 5
                ORDER BY c.cnt DESC, c.parent_id ASC
                """
            ).fetchall()
            if over:
                conn.execute("ROLLBACK")
                return JSONResponse(
                    status_code=422,
                    content={
                        "ok": False,
                        "error": "value_error.max_children",
                        "detail": [
                            {"parent_id": r[0], "parent_label": r[1], "count": r[2], "msg": "parent ends with >5 children"}
                            for r in over
                        ],
                    },
                )

        conn.execute("COMMIT")
        return {"ok": True, "result": getattr(result, "__dict__", {})}
    except HTTPException:
        try:
            conn.execute("ROLLBACK")
        except Exception:
            pass
        raise
    except Exception as e:
        try:
            conn.execute("ROLLBACK")
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=[{"loc": ["body"], "msg": str(e), "type": "runtime_error"}])
