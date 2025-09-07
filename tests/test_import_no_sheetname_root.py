import io
import pandas as pd
import pytest
import sqlite3
import os
from fastapi.testclient import TestClient

CANON = ["Vital Measurement","Node 1","Node 2","Node 3","Node 4","Node 5","Diagnostic Triage","Actions"]

def _xlsx_with_sheetname(df, sheet_name="SheetWeIgnore"):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name=sheet_name)
    buf.seek(0)
    return buf

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "rootfix.db"))
    from api.app import app
    return TestClient(app)

def test_sheet_name_never_becomes_root(client):
    df = pd.DataFrame([["BP","High","","","","","X","A"]], columns=CANON)
    buf = _xlsx_with_sheetname(df, sheet_name="THIS_IS_NOT_A_ROOT")
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200
    db = os.environ["LORIEN_DB"]
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    roots = [row["label"] for row in con.execute("SELECT label FROM nodes WHERE parent_id IS NULL").fetchall()]
    assert "THIS_IS_NOT_A_ROOT" not in roots
    assert "BP" in roots
