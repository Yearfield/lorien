from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi.responses import JSONResponse
from Engines.EngineLongBow import export_paths, ExportEngine, ExportOptions
from api.dependencies import get_db_connection
import sqlite3
from typing import Optional, Set, Tuple

router = APIRouter(tags=["export"])

def _ensure_xlsx_support() -> None:
    """Raise a helpful error when xlsx export is requested without xlsxwriter."""
    try:
        import xlsxwriter  # noqa: F401
    except ImportError as exc:  # pragma: no cover - exercised in prod when dependency missing
        raise HTTPException(
            status_code=500,
            detail="XLSX export requires 'xlsxwriter'. Please install it on the server.",
        ) from exc


def _parse_root_filters(raw_ids: Optional[str], raw_labels: Optional[str]) -> Tuple[Optional[Set[int]], Optional[Set[str]]]:
    """Parse comma-separated root id/label filters while keeping backward compatibility."""
    root_id_set: Optional[Set[int]] = None
    if raw_ids:
        try:
            root_id_set = {int(x.strip()) for x in raw_ids.split(",") if x.strip()}
        except ValueError:
            # Preserve legacy behaviour: ignore malformed values instead of hard failing
            root_id_set = None

    root_label_set = None
    if raw_labels:
        root_label_set = {x.strip() for x in raw_labels.split(",") if x.strip()}

    return root_id_set, root_label_set


def _perform_export(
    fmt: str,
    max_depth: Optional[int],
    root_ids: Optional[str],
    root_labels: Optional[str],
    only_red: bool,
    include_meta: bool,
    filename: Optional[str],
    conn: sqlite3.Connection,
):
    fmt_normalized = fmt.lower()
    if fmt_normalized not in {"csv", "xlsx"}:
        raise HTTPException(status_code=400, detail=f"Unsupported export format: {fmt}")

    if fmt_normalized == "xlsx":
        _ensure_xlsx_support()

    root_id_set, root_label_set = _parse_root_filters(root_ids, root_labels)

    opts = ExportOptions(
        fmt=fmt_normalized,
        max_depth=max_depth if max_depth and max_depth > 0 else None,
        root_ids=root_id_set,
        root_labels=root_label_set,
        only_red=only_red,
        include_meta=include_meta,
        filename=filename,
    )

    engine = ExportEngine(conn, opts)
    return engine.export()

@router.get("/tree/export-json")
def tree_export(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), conn: sqlite3.Connection = Depends(get_db_connection)):
    # Use EngineLongBow to export paths with provided connection
    paths = list(export_paths(limit=limit, offset=offset, conn=conn))
    
    # Convert paths to the expected format
    items = []
    for path in paths:
        # Convert path to dict format expected by existing clients
        item = {}
        for i, col in enumerate(["D0", "D1", "D2", "D3", "D4", "D5", "D6"]):
            if i < len(path):
                item[col] = path[i]
            else:
                item[col] = ""
        item["Notes"] = ""  # Always empty for now
        items.append(item)
    
    return JSONResponse({
        "items": items,
        "total": len(items),  # This is approximate for now
        "limit": limit,
        "offset": offset
    })

# ---- CANONICAL ROUTES ----
@router.get("/tree/export", name="tree_export_csv")
@router.head("/tree/export")
def export_csv(
    format: str = Query("csv", description="Export format: csv or xlsx"),
    max_depth: Optional[int] = Query(None, description="Maximum depth to export"),
    root_ids: Optional[str] = Query(None, description="Comma-separated root IDs to filter"),
    root_labels: Optional[str] = Query(None, description="Comma-separated root labels to filter"),
    only_red: bool = Query(False, description="Only export red-flagged paths"),
    include_meta: bool = Query(False, description="Include metadata columns"),
    filename: Optional[str] = Query(None, description="Custom filename for download"),
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    return _perform_export(
        fmt=format,
        max_depth=max_depth,
        root_ids=root_ids,
        root_labels=root_labels,
        only_red=only_red,
        include_meta=include_meta,
        filename=filename,
        conn=conn,
    )

@router.get("/tree/export.xlsx", name="tree_export_xlsx")
@router.head("/tree/export.xlsx")
def export_xlsx(conn: sqlite3.Connection = Depends(get_db_connection)):
    return _perform_export(
        fmt="xlsx",
        max_depth=None,
        root_ids=None,
        root_labels=None,
        only_red=False,
        include_meta=False,
        filename=None,
        conn=conn,
    )

# ---- Backward-compat ALIASES (keep until all clients updated) ----
@router.get("/export/csv", name="export_csv_alias")
@router.head("/export/csv")
def export_csv_alias(
    max_depth: Optional[int] = Query(None, description="Maximum depth to export"),
    root_ids: Optional[str] = Query(None, description="Comma-separated root IDs to filter"),
    root_labels: Optional[str] = Query(None, description="Comma-separated root labels to filter"),
    only_red: bool = Query(False, description="Only export red-flagged paths"),
    include_meta: bool = Query(False, description="Include metadata columns"),
    filename: Optional[str] = Query(None, description="Custom filename for download"),
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    # Keep legacy semantics: aliases are always CSV format.
    return _perform_export(
        fmt="csv",
        max_depth=max_depth,
        root_ids=root_ids,
        root_labels=root_labels,
        only_red=only_red,
        include_meta=include_meta,
        filename=filename,
        conn=conn,
    )

@router.get("/export.xlsx", name="export_xlsx_alias")
@router.head("/export.xlsx")
def export_xlsx_alias(
    max_depth: Optional[int] = Query(None, description="Maximum depth to export"),
    root_ids: Optional[str] = Query(None, description="Comma-separated root IDs to filter"),
    root_labels: Optional[str] = Query(None, description="Comma-separated root labels to filter"),
    only_red: bool = Query(False, description="Only export red-flagged paths"),
    include_meta: bool = Query(False, description="Include metadata columns"),
    filename: Optional[str] = Query(None, description="Custom filename for download"),
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    return _perform_export(
        fmt="xlsx",
        max_depth=max_depth,
        root_ids=root_ids,
        root_labels=root_labels,
        only_red=only_red,
        include_meta=include_meta,
        filename=filename,
        conn=conn,
    )
