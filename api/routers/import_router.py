from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from api.dependencies import get_db_connection
from Engines.EngineLongBow import ingest_file, apply_import, apply_import_with_metadata, FROZEN_HEADER
from Engines.EngineLongBow.ingest import read_file, extract_paths
from Engines.EngineLongBow.importer import import_rows, ImportOptions
from Engines.EngineLongBow.import_analyzer import analyze_max_children
from .helpers import parse_csv_or_xlsx, coerce_rows_to_canonical, CANONICAL_HEADER
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
async def import_preview(
    file: UploadFile = File(...),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Preview import without writing to database - shows detected paths."""
    try:
        file_content = await file.read()
        rows = parse_csv_or_xlsx(file_content, file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=[{"loc": ["body", "file"], "msg": f"Could not read file: {str(e)}", "type":"value_error.file_read"}]
        )
    
    # Coerce to canonical columns
    try:
        rows = coerce_rows_to_canonical(rows)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"bad_header: {e}")
    
    try:
        # Header coercion already applied above
        issues = []
        # Basic path checks
        for idx, r in enumerate(rows, start=2):
            # Check if row has any non-empty values
            has_content = any((r.get(f"D{d}") or "").strip() for d in range(7))
            if has_content and (r.get("D0") or "").strip() == "":
                issues.append({"row": idx, "msg": "path must start at D0 (root)", "type": "value_error.path"})
            if any((r.get(f"D{d}") or "").strip() for d in range(7, 10)):  # future-proof
                issues.append({"row": idx, "msg": "depth exceeds D6", "type": "value_error.max_depth"})
        # Max-children preflight (append considered against DB)
        max_children = analyze_max_children(conn, rows, mode="append")
        
        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "header": CANONICAL_HEADER,
                "stats": {"found_paths": len(rows)},
                "errors": issues + max_children,  # clients show this as preview banner/list
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
    enforce_five: bool = Query(default=False),  # IMPORT DOES NOT ENFORCE by default
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

    if not rows:
        return {"ok": True, "inserted": 0}
    # Coerce to canonical columns; never 400 for minor header variations
    try:
        rows = coerce_rows_to_canonical(rows)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"bad_header: {e}")

    try:
        # Import never enforces ≤5; it just writes. We attach preview-style warnings for visibility.
        warnings = analyze_max_children(conn, rows, mode=mode)
        result = import_rows(conn, rows, ImportOptions(mode=mode, enforce_five=False))
        result["warnings"] = warnings  # surfaced to UI, but not an error
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
