from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import pandas as pd
import io
import numpy as np

from api.db import get_conn, ensure_schema, tx
from api.repositories.tree_repo import import_dataframe, CANON_HEADERS, sanitize_label
from api.repositories.admin_repo import clear_nodes_only, hard_reset_nodes

router = APIRouter()

def _first_mismatch_index(expected, received):
    n = min(len(expected), len(received))
    for i in range(n):
        if expected[i] != received[i]:
            return i
    # if lengths differ and common prefix matches, mismatch is at n
    if len(expected) != len(received):
        return n
    return -1  # identical

def _read_table_like(file_obj, filename: str) -> pd.DataFrame:
    # Always read as object, turn off default NA parsing so "nan" stays a string we can clean.
    if filename.lower().endswith(".csv"):
        df = pd.read_csv(file_obj, dtype=object, keep_default_na=False)
    else:
        # XLSX: always use sheet 0; never read or rely on the sheet name itself.
        xls = pd.ExcelFile(file_obj, engine="openpyxl")
        df = pd.read_excel(xls, sheet_name=0, dtype=object, keep_default_na=False)
    
    # Sanitize data
    def _clean(v):
        if v is None: return None
        s = str(v).strip()
        if s == "" or s.lower() == "nan": return None
        return s
    
    for c in df.columns:
        df[c] = df[c].map(_clean)
    
    return df

@router.post("/import/preview")
async def import_preview(file: UploadFile = File(...)):
    """Preview import without writing to database - shows detected roots."""
    try:
        df = _read_table_like(file.file, file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", "file"], "msg": f"Could not parse file: {str(e)}", "type":"value_error.file_parse"}]
        )
    
    # Header validation
    _hdr = list(df.columns)
    if _hdr != CANON_HEADERS:
        return JSONResponse(status_code=422, content={
            "detail": [{"loc":["header"],"msg":"Frozen header mismatch", "type":"value_error.header",
                        "ctx":{"row":1,"col_index":None,"expected":CANON_HEADERS,"received":_hdr}}]
        })
    
    # Compute distinct roots as they would be imported
    roots = []
    for v in df["Vital Measurement"].dropna().tolist():
        lab = sanitize_label(v)
        if lab: roots.append(lab)
    uniq = sorted(set(roots))
    
    return JSONResponse({"ok": True, "rows": int(df.shape[0]), "roots_detected": uniq, "roots_count": len(uniq)})

@router.post("/import")
async def import_file(file: UploadFile = File(...), mode: str = Query("append", pattern="^(append|replace|hard_replace)$")):
    # Parse file into DataFrame
    try:
        df = _read_table_like(file.file, file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", "file"], "msg": f"Could not parse file: {str(e)}", "type":"value_error.file_parse"}]
        )

    # Normalize + trim
    def _clean(v):
        if v is None: return None
        s = str(v).strip()
        if s == "" or s.lower() == "nan": return None
        return s

    # Coerce every cell
    for c in df.columns:
        df[c] = df[c].map(_clean)

    # Strict header (exact order & size)
    received = list(df.columns)
    mismatch_index = _first_mismatch_index(CANON_HEADERS, received)
    if len(received) != len(CANON_HEADERS) or mismatch_index != -1:
        ctx = {"row": 1, "col_index": (mismatch_index if mismatch_index != -1 else 0), "expected": CANON_HEADERS, "received": received}
        raise HTTPException(status_code=422, detail=[{"loc":["header"], "msg":"Header mismatch", "type":"value_error.header_mismatch", "ctx": ctx}])

    # Persist transactionally
    conn = get_conn()
    ensure_schema(conn)
    # Normalize column order (in case DataFrame has extra hidden metadata)
    df = df[CANON_HEADERS].copy()
    
    if mode == "hard_replace":
        hard_reset_nodes(conn)  # drop and recreate tables
    elif mode == "replace":
        clear_nodes_only(conn)  # keep dictionary & schema intact
    result = import_dataframe(conn, df)

    return JSONResponse({"ok": True, "rows": int(len(df)), "mode": mode, "result": result})
