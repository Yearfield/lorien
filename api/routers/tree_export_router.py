from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from Engines.EngineLongBow import export_paths, export_paths_to_csv, export_paths_to_xlsx, ExportEngine, ExportOptions
from api.dependencies import get_db_connection
import datetime
import io
import sqlite3
from typing import Optional, Set

router = APIRouter()

def _csv_response(data: bytes):
    fname = f"tree_export_{datetime.datetime.utcnow():%Y%m%d_%H%M%S}.csv"
    return StreamingResponse(io.BytesIO(data), media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'})

def _xlsx_response(data: bytes):
    fname = f"tree_export_{datetime.datetime.utcnow():%Y%m%d_%H%M%S}.xlsx"
    return StreamingResponse(io.BytesIO(data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'})

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
    # Parse root_ids and root_labels
    root_id_set = None
    if root_ids:
        try:
            root_id_set = {int(x.strip()) for x in root_ids.split(",") if x.strip()}
        except ValueError:
            # If parsing fails, ignore the parameter
            root_id_set = None
    
    root_label_set = None
    if root_labels:
        root_label_set = {x.strip() for x in root_labels.split(",") if x.strip()}
    
    # Check if xlsxwriter is available for XLSX exports
    if format == "xlsx":
        try:
            import xlsxwriter  # noqa:F401
        except ImportError:
            raise HTTPException(status_code=500, detail="XLSX export requires 'xlsxwriter'. Please install it on the server.")
    
    # Create export options
    opts = ExportOptions(
        fmt=format,
        max_depth=max_depth if max_depth and max_depth > 0 else None,
        root_ids=root_id_set,
        root_labels=root_label_set,
        only_red=only_red,
        include_meta=include_meta,
        filename=filename,
    )
    
    # Use ExportEngine for the export
    engine = ExportEngine(conn, opts)
    return engine.export()

@router.get("/tree/export.xlsx", name="tree_export_xlsx")
@router.head("/tree/export.xlsx")
def export_xlsx(conn: sqlite3.Connection = Depends(get_db_connection)):
    # Check if xlsxwriter is available for XLSX exports
    try:
        import xlsxwriter  # noqa:F401
    except ImportError:
        raise HTTPException(status_code=500, detail="XLSX export requires 'xlsxwriter'. Please install it on the server.")
    
    # Use ExportEngine for XLSX export with default options
    opts = ExportOptions(fmt="xlsx")
    engine = ExportEngine(conn, opts)
    return engine.export()

# ---- Backward-compat ALIASES (keep until all clients updated) ----
@router.get("/export/csv", name="export_csv_alias")
@router.head("/export/csv")
def export_csv_alias():
    # 307 here would also work; returning content avoids any client redirect issues
    return export_csv()

@router.get("/export.xlsx", name="export_xlsx_alias")
@router.head("/export.xlsx")
def export_xlsx_alias():
    return export_xlsx()
