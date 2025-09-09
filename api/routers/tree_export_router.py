from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, StreamingResponse
from api.db import get_conn, ensure_schema
from api.repositories.tree_repo import export_rows, export_rows_csv, export_rows_xlsx
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
    conn = get_conn()
    ensure_schema(conn)
    payload = export_rows(conn, limit=limit, offset=offset)
    return JSONResponse(payload)

# ---- CANONICAL ROUTES ----
@router.get("/tree/export", name="tree_export_csv")
@router.head("/tree/export")
def export_csv():
    conn = get_conn()
    ensure_schema(conn)
    return _csv_response(export_rows_csv(conn))

@router.get("/tree/export.xlsx", name="tree_export_xlsx")
@router.head("/tree/export.xlsx")
def export_xlsx():
    conn = get_conn()
    ensure_schema(conn)
    return _xlsx_response(export_rows_xlsx(conn))

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
