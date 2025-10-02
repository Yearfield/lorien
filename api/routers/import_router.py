from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from api.dependencies import get_db_connection
from Engines.EngineLongBow import ingest_file, apply_import, apply_import_with_metadata, FROZEN_HEADER
from Engines.EngineLongBow.ingest import read_file, extract_paths
from Engines.EngineLongBow.importer import import_rows, ImportOptions, CANONICAL_HEADER
from .helpers import parse_csv_or_xlsx
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
        rows = parse_csv_or_xlsx(file_content, file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=[{"loc": ["body", "file"], "msg": f"Could not read file: {str(e)}", "type":"value_error.file_read"}]
        )
    
    try:
        issues: List[Dict[str, Any]] = []
        # Shallow pass: check that each row starts at D0 and depth never exceeds 6
        for idx, r in enumerate(rows, start=2):
            path = [ (i, (r.get(h) or "").strip()) for i, h in enumerate(CANONICAL_HEADER[:7]) ]
            nonempty = [(d, v) for (d, v) in path if v]
            if not nonempty:
                continue
            # Ensure first is D0
            if nonempty[0][0] != 0:
                issues.append({"row": idx, "msg": "path must start at D0 (root)", "type": "value_error.path"})
            # Ensure no D7+
            if any(d > 6 for (d, _) in nonempty):
                issues.append({"row": idx, "msg": "depth exceeds D6", "type": "value_error.max_depth"})
        
        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "header": CANONICAL_HEADER,
                "stats": {"found_paths": len(rows)},
                "errors": issues,  # clients show this as preview banner/list
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
        rows = parse_csv_or_xlsx(blob, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"parse_error: {e}")

    # Light header sanity (tolerate case/spacing but require D0..D6 present)
    if not rows:
        return {"ok": True, "inserted": 0}
    first = rows[0]
    missing = [h for h in CANONICAL_HEADER[:7] if h not in first]
    if missing:
        raise HTTPException(status_code=400, detail=f"bad_header: missing {missing}")

    try:
        result = import_rows(conn, rows, ImportOptions(mode=mode, enforce_five=enforce_five))
        return result
    except RuntimeError as e:
        # Known validation issue (≤5, malformed path, etc.)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # Surface sqlite constraint in a readable way
        msg = str(e)
        if "CHECK constraint failed" in msg:
            raise HTTPException(status_code=422, detail=f"constraint_error: {msg}")
        raise HTTPException(status_code=500, detail=f"import_error: {msg}")
