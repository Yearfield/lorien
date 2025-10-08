import re
import sqlite3
from collections import defaultdict
from collections.abc import Iterable
from typing import Any, Literal

import anyio
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse

from api.dependencies import get_db_connection
from api.observability import get_logger
from api.observability.metrics import increment_counter, record_timer
from Engines.EngineLongBow import apply_import_with_metadata
from Engines.EngineLongBow.import_analyzer import analyze_max_children

from .helpers import CANONICAL_HEADER, coerce_rows_to_canonical, parse_csv_or_xlsx

logger = get_logger(__name__)

router = APIRouter()

_DEPTH_PATTERN = re.compile(r"D(\d+)$")
DEPTH_COLUMNS = sorted(
    [column for column in CANONICAL_HEADER if _DEPTH_PATTERN.fullmatch(column)],
    key=lambda column: int(_DEPTH_PATTERN.fullmatch(column).group(1)),
)
MAX_DEPTH_INDEX = int(_DEPTH_PATTERN.fullmatch(DEPTH_COLUMNS[-1]).group(1)) if DEPTH_COLUMNS else 0
MAX_DEPTH_LABEL = DEPTH_COLUMNS[-1] if DEPTH_COLUMNS else "D0"


def _group_overfive_within_file(paths: list[list[str]], limit: int = 5) -> list[dict[str, Any]]:
    """
    Heuristic preview-only check: within the uploaded file, if any parent path
    (D0..Dk) produces >limit distinct child labels at Dk+1, flag rows.
    Returns a list of error dicts with row numbers (1-based including header).
    """
    # Build mapping: parent_tuple -> set(child_labels) and rows exceeding limit
    parent_children = defaultdict(set)
    violations: list[dict[str, Any]] = []
    reported_rows = set()
    for row_number, path in enumerate(paths, start=2):  # row 1 = header
        cleaned = [(segment or "").strip() for segment in path]
        parent_candidates = [idx for idx, value in enumerate(cleaned[:-1]) if value]
        if not parent_candidates:
            continue
        last_parent_idx = parent_candidates[-1]
        if last_parent_idx + 1 >= len(cleaned):
            continue
        child_label = cleaned[last_parent_idx + 1]
        if not child_label:
            continue
        parent_key = tuple(cleaned[: last_parent_idx + 1])
        pc = parent_children[parent_key]
        pc.add(child_label.lower())
        if len(pc) > limit and row_number not in reported_rows:
            parent_display = " > ".join(parent_key)
            violations.append(
                {
                    "row": row_number,
                    "msg": f"parent '{parent_display}' would exceed {limit} children with '{child_label}' (preview)",
                    "type": "value_error.max_children",
                }
            )
            reported_rows.add(row_number)
    return violations


def _canonical_paths(rows: Iterable[dict[str, Any]]) -> list[list[str]]:
    """Return canonical depth-only slices for downstream heuristics."""
    return [[(row.get(column) or "").strip() for column in DEPTH_COLUMNS] for row in rows]


def _row_exceeds_depth(row: dict[str, Any]) -> bool:
    if not DEPTH_COLUMNS:
        return False
    for key, value in row.items():
        match = _DEPTH_PATTERN.fullmatch(key)
        if not match or not (value or "").strip():
            continue
        if int(match.group(1)) > MAX_DEPTH_INDEX:
            return True
    return False


@router.post("/import/preview")
async def import_preview(
    file: UploadFile = File(...), conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Preview import without writing to database - shows detected paths."""
    try:
        file_content = await file.read()
        filename = file.filename or "upload.csv"
        _, rows = parse_csv_or_xlsx(file_content, filename)

        logger.info(
            "Import preview started",
            extra_fields={
                "filename": filename,
                "file_size_bytes": len(file_content),
                "rows_found": len(rows),
            },
        )
    except Exception as e:
        logger.error(
            "Import preview file read failed",
            extra_fields={
                "filename": file.filename or "unknown",
                "error": str(e),
            },
            exc_info=True,
        )
        increment_counter("imports.preview_parse_error")
        raise HTTPException(
            status_code=400,
            detail=[
                {
                    "loc": ["body", "file"],
                    "msg": f"Could not read file: {str(e)}",
                    "type": "value_error.file_read",
                }
            ],
        )

    # Coerce to canonical columns
    try:
        rows = coerce_rows_to_canonical(rows)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"bad_header: {e}")

    try:
        # Header coercion already applied above
        issues = []
        canonical_paths = _canonical_paths(rows)
        issues.extend(_group_overfive_within_file(canonical_paths))
        # Basic path checks
        for idx, r in enumerate(rows, start=2):
            # Check if row has any non-empty values
            has_content = any((r.get(column) or "").strip() for column in DEPTH_COLUMNS)
            if has_content and (r.get("D0") or "").strip() == "":
                issues.append(
                    {"row": idx, "msg": "path must start at D0 (root)", "type": "value_error.path"}
                )
            if _row_exceeds_depth(r):  # future-proof
                issues.append(
                    {
                        "row": idx,
                        "msg": f"depth exceeds {MAX_DEPTH_LABEL}",
                        "type": "value_error.max_depth",
                    }
                )
        # Max-children preflight (append considered against DB)
        max_children = await anyio.to_thread.run_sync(analyze_max_children, conn, rows, "append")

        logger.info(
            "Import preview completed",
            extra_fields={
                "found_paths": len(rows),
                "issues_count": len(issues),
                "max_children_warnings": len(max_children),
            },
        )

        increment_counter("imports.preview_success")

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
            detail=[
                {
                    "loc": ["body"],
                    "msg": f"Import failed: {str(e)}",
                    "type": "value_error.import_failed",
                }
            ],
        )


@router.post("/import")
async def import_apply(
    mode: Literal["append", "replace"] = Query(default="append"),
    enforce_five: bool = Query(default=False),  # IMPORT DOES NOT ENFORCE by default
    file: UploadFile = File(...),
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """
    Apply import transactionally. If enforce_five=True, the import is rolled back if any parent ends with >5 children.
    """
    import time

    start_time = time.time()

    try:
        blob = await file.read()
        filename = file.filename or "upload.csv"
        _, rows = parse_csv_or_xlsx(blob, filename)

        logger.info(
            "Import started",
            extra_fields={
                "filename": filename,
                "file_size_bytes": len(blob),
                "rows_found": len(rows),
                "mode": mode,
                "enforce_five": enforce_five,
            },
        )
    except Exception as e:
        logger.error(
            "Import file parse failed",
            extra_fields={
                "filename": file.filename or "unknown",
                "mode": mode,
                "error": str(e),
            },
            exc_info=True,
        )
        increment_counter("imports.parse_error", tags={"mode": mode})
        raise HTTPException(status_code=400, detail=f"parse_error: {e}")

    if not rows:
        return {"ok": True, "inserted": 0}
    # Coerce to canonical columns; never 400 for minor header variations
    try:
        rows = coerce_rows_to_canonical(rows)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"bad_header: {e}")

    try:
        # Import enforces ≤5 only when caller opts in; warnings always returned for visibility.
        canonical_paths = _canonical_paths(rows)
        warnings = _group_overfive_within_file(canonical_paths)
        db_warnings = await anyio.to_thread.run_sync(analyze_max_children, conn, rows, mode)
        warnings.extend(db_warnings)

        if enforce_five and any(w.get("type") == "value_error.max_children" for w in db_warnings):
            # Abort import and return structured 422 so clients can surface the issue
            return JSONResponse(
                status_code=422,
                content={
                    "ok": False,
                    "error": "value_error.max_children",
                    "detail": db_warnings,
                },
            )

        paths_with_meta = []
        for row in rows:
            path: list[str] = []
            for key in DEPTH_COLUMNS[:-1]:
                value = (row.get(key) or "").strip()
                if not value:
                    break
                path.append(value)
            if not path:
                continue
            d6_value = (row.get(DEPTH_COLUMNS[-1]) or "").strip() or None
            notes_value = (row.get("Notes") or "").strip() or None
            paths_with_meta.append(
                {
                    "path": path,
                    "metadata": {"d6": d6_value, "notes": notes_value},
                }
            )

        import_result = await anyio.to_thread.run_sync(
            apply_import_with_metadata, paths_with_meta, mode, conn
        )

        response = {
            "ok": True,
            "inserted": import_result.inserted_nodes,
            "parents_touched": import_result.parents_touched,
            "warnings": warnings,
        }

        # Provide root count for caller parity
        try:
            cursor = await anyio.to_thread.run_sync(
                conn.execute, "SELECT COUNT(*) FROM nodes WHERE depth=0"
            )
            root_count = (await anyio.to_thread.run_sync(cursor.fetchone))[0]
        except Exception:
            root_count = 0
        response["roots"] = int(root_count)

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "Import completed successfully",
            extra_fields={
                "filename": filename,
                "mode": mode,
                "inserted_nodes": import_result.inserted_nodes,
                "parents_touched": import_result.parents_touched,
                "warnings_count": len(warnings),
                "duration_ms": round(duration_ms, 2),
            },
        )

        increment_counter("imports.success", tags={"mode": mode})
        record_timer("imports.duration", duration_ms, tags={"mode": mode})

        return response
    except RuntimeError as e:
        # Known validation issue (≤5, malformed path, etc.)
        logger.warning(
            "Import validation failed",
            extra_fields={
                "filename": filename,
                "mode": mode,
                "error": str(e),
            },
        )
        increment_counter("imports.validation_error", tags={"mode": mode})
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # Surface sqlite constraint in a readable way
        msg = str(e)
        logger.error(
            "Import failed",
            extra_fields={
                "filename": filename,
                "mode": mode,
                "error": msg,
            },
            exc_info=True,
        )
        increment_counter("imports.error", tags={"mode": mode})
        if "CHECK constraint failed" in msg:
            raise HTTPException(status_code=422, detail=f"constraint_error: {msg}")
        raise HTTPException(status_code=500, detail=f"import_error: {msg}")
