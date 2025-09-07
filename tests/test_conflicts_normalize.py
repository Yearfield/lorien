import sqlite3
import os
import io
import pandas as pd
import pytest
from fastapi.testclient import TestClient

CANON = ["Vital Measurement","Node 1","Node 2","Node 3","Node 4","Node 5","Diagnostic Triage","Actions"]

def _xlsx_bytes(df: pd.DataFrame) -> io.BytesIO:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    buf.seek(0)
    return buf

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "conflicts.db"))
    from api.app import app
    return TestClient(app)

def _seed(client):
    df = pd.DataFrame([
        ["BP","High","","","","","Urgent","Act"],
        ["BP","Low","","","","","Routine","Act2"],
    ], columns=CANON)
    buf = _xlsx_bytes(df)
    client.post("/api/v1/import", files={"file": ("ok.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})

def test_detect_and_normalize_overfilled(client):
    _seed(client)
    # Manually overfill with a null-slot child to simulate legacy issue
    db = os.environ["LORIEN_DB"]
    conn = sqlite3.connect(db)
    pid = conn.execute("SELECT id FROM nodes WHERE depth=0 AND label='BP'").fetchone()[0]
    # add children with NULL slot (bypasses unique)
    conn.execute("INSERT INTO nodes(parent_id,label,depth,slot) VALUES (?,?,?,NULL)", (pid,"Xtra",1))
    conn.commit()
    conn.close()

    conf = client.get("/api/v1/tree/conflicts/conflicts").json()
    assert any(it["parent_id"] == pid for it in conf["items"])

    res = client.post(f"/api/v1/tree/conflicts/parent/{pid}/normalize").json()
    assert "kept" in res and "excess_children" in res
