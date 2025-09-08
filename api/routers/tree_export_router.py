from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, StreamingResponse
from api.db import get_conn, ensure_schema
from api.repositories.tree_repo import export_rows, export_rows_csv, export_rows_xlsx
import datetime
import io

router = APIRouter()

@router.get("/tree/export-json")
def tree_export(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
    conn = get_conn()
    ensure_schema(conn)
    payload = export_rows(conn, limit=limit, offset=offset)
    return JSONResponse(payload)


@router.get("/tree/export")
def export_csv():
    conn = get_conn()
    ensure_schema(conn)
    data = export_rows_csv(conn)
    name = f"tree_export_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(io.BytesIO(data), media_type="text/csv",
                             headers={"Content-Disposition": f'attachment; filename="{name}"'})


@router.get("/tree/export.xlsx")
def export_xlsx():
    conn = get_conn()
    ensure_schema(conn)
    data = export_rows_xlsx(conn)
    name = f"tree_export_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(io.BytesIO(data),
                             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f'attachment; filename="{name}"'})
