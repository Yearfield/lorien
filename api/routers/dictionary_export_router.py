from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from api.db import get_conn
import io, csv, datetime

router = APIRouter()

# We'll be liberal about column names to handle schema drift across branches.
DICT_HEADERS = ["Term","Type","Normalized","Red Flag","Hints"]

def _fetch_dictionary_rows(conn):
    # Try common column names; fallback gracefully if some don't exist.
    # We'll introspect columns then map to our canonical DICT_HEADERS.
    cols = {r[1] for r in conn.execute("PRAGMA table_info(dictionary_terms)").fetchall()}
    # Map variants
    col_map = {
        "Term":       "label" if "label" in cols else ("term" if "term" in cols else None),
        "Type":       "type"  if "type"  in cols else ("kind" if "kind" in cols else None),
        "Normalized": "normalized" if "normalized" in cols else None,
        "Red Flag":   "red_flag" if "red_flag" in cols else ("is_red" if "is_red" in cols else None),
        "Hints":      "hints" if "hints" in cols else ("notes" if "notes" in cols else None),
    }
    select_cols = [c for c in col_map.values() if c]
    if not select_cols:
        return []
    rows = conn.execute(f"SELECT {', '.join(select_cols)} FROM dictionary_terms").fetchall()
    # Convert to dicts keyed by our DICT_HEADERS
    items = []
    for r in rows:
        d = {}
        i = 0
        for hdr in DICT_HEADERS:
            src = col_map[hdr]
            d[hdr] = (r[i] if src else "")
            if src: i += 1
        items.append(d)
    return items

@router.get("/dictionary/export", name="dictionary_export_csv")
def dictionary_export_csv():
    conn = get_conn()
    items = _fetch_dictionary_rows(conn)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(DICT_HEADERS)
    for it in items:
        w.writerow([it.get(h,"") or "" for h in DICT_HEADERS])
    name = f"dictionary_export_{datetime.datetime.utcnow():%Y%m%d_%H%M%S}.csv"
    return StreamingResponse(io.BytesIO(buf.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{name}"'})

@router.get("/dictionary/export.xlsx", name="dictionary_export_xlsx")
def dictionary_export_xlsx():
    try:
        import openpyxl
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="openpyxl not available")
    conn = get_conn()
    items = _fetch_dictionary_rows(conn)
    wb = openpyxl.Workbook(); ws = wb.active
    ws.append(DICT_HEADERS)
    for it in items:
        ws.append([it.get(h,"") or "" for h in DICT_HEADERS])
    out = io.BytesIO(); wb.save(out)
    name = f"dictionary_export_{datetime.datetime.utcnow():%Y%m%d_%H%M%S}.xlsx"
    return StreamingResponse(io.BytesIO(out.getvalue()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{name}"'})
