import io
import pandas as pd
import pytest
import sqlite3
import os
from fastapi.testclient import TestClient

CANON = ["Vital Measurement","Node 1","Node 2","Node 3","Node 4","Node 5","Diagnostic Triage","Actions"]

def _xlsx(df: pd.DataFrame) -> io.BytesIO:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="SHEET_SHOULD_NOT_APPEAR")
    buf.seek(0)
    return buf

def test_sheet_name_not_imported(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "nosheet.db"))
    from api.app import app
    client = TestClient(app)
    
    df = pd.DataFrame([["BP","High","","","","","Urgent","Act"]], columns=CANON)
    buf = _xlsx(df)
    
    r = client.post("/api/v1/import", files={"file": ("x.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200

    # Ensure no node label equals the sheet name
    conn = sqlite3.connect(os.environ["LORIEN_DB"])
    bad = conn.execute("SELECT COUNT(*) FROM nodes WHERE label='SHEET_SHOULD_NOT_APPEAR'").fetchone()[0]
    assert bad == 0
    conn.close()
