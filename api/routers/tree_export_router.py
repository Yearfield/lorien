from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, StreamingResponse
from api.db import get_conn, ensure_schema
from api.repositories.tree_repo import export_rows, export_rows_csv, export_rows_xlsx
from Engines.EngineLongBow import export_paths, export_paths_to_csv, export_paths_to_xlsx
import datetime
import io

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
def tree_export(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
    # Get database path
    from api.settings import get_db_path
    db_path = get_db_path()
    
    # Use EngineLongBow to export paths
    paths = list(export_paths(limit=limit, offset=offset, db_path=db_path))
    
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
def export_csv():
    # Get database path
    from api.settings import get_db_path
    db_path = get_db_path()
    
    # Use EngineLongBow to export CSV
    csv_data = export_paths_to_csv(db_path=db_path)
    return _csv_response(csv_data.encode('utf-8'))

@router.get("/tree/export.xlsx", name="tree_export_xlsx")
@router.head("/tree/export.xlsx")
def export_xlsx():
    # Get database path
    from api.settings import get_db_path
    db_path = get_db_path()
    
    # Use EngineLongBow to export XLSX
    xlsx_data = export_paths_to_xlsx(db_path=db_path)
    return _xlsx_response(xlsx_data)

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
