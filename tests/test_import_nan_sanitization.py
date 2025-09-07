import io
import pandas as pd
import numpy as np
import pytest
import sqlite3
import os
from fastapi.testclient import TestClient

CANON = ["Vital Measurement","Node 1","Node 2","Node 3","Node 4","Node 5","Diagnostic Triage","Actions"]

def _xlsx(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    buf.seek(0)
    return buf

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "nanfix.db"))
    from api.app import app
    return TestClient(app)

def test_xlsx_sanitizes_nan(client):
    df = pd.DataFrame([[np.nan,"High","A","","","","Urgent","Act"]], columns=CANON)  # 8 values
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", _xlsx(df), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200
    db = os.environ["LORIEN_DB"]
    con = sqlite3.connect(db)
    # No 'nan' literal or NULL-labeled nodes should exist at depth=0 (root missing is skipped)
    bad = con.execute("SELECT COUNT(*) FROM nodes WHERE label IS NULL OR LOWER(label)='nan'").fetchone()[0]
    assert bad == 0

def test_csv_sanitizes_nan_string(client, tmp_path):
    csv = "Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions\n" \
          "BP,High,nan,,,,Emergent,Act\n"
    r = client.post("/api/v1/import", files={"file": ("ok.csv", io.BytesIO(csv.encode()), "text/csv")})
    assert r.status_code == 200
    db = os.environ["LORIEN_DB"]
    con = sqlite3.connect(db)
    # 'nan' in Node2 must not persist as a child
    rows = con.execute("SELECT COUNT(*) FROM nodes WHERE label='nan'").fetchone()[0]
    assert rows == 0