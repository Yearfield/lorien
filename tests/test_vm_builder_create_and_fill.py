import io
import pandas as pd
import pytest
import sqlite3
import os
import json
from fastapi.testclient import TestClient

CANON = ["Vital Measurement","Node 1","Node 2","Node 3","Node 4","Node 5","Diagnostic Triage","Actions"]

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "vmbuilder.db"))
    from api.app import app
    return TestClient(app)

def test_vm_builder_create_and_fill(client):
    # seed some labels so suggestions exist
    df = pd.DataFrame([
        ["Pulse","High","Headache","","","","X","A"],
        ["Pulse","High","Vomiting","","","","Y","A"],
    ], columns=CANON)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    buf.seek(0)
    client.post("/api/v1/import", files={"file": ("seed.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})

    # create VM
    r = client.post("/api/v1/tree/vm", json={"label": "NewVM"})
    assert r.status_code == 200
    rid = r.json()["id"]

    # fill slot 1 with an existing label
    r2 = client.put(f"/api/v1/tree/{rid}/slot/1", json={"label":"High"})
    assert r2.status_code == 200

    # verify as child
    db = os.environ["LORIEN_DB"]
    con = sqlite3.connect(db)
    ch = [row[0] for row in con.execute("SELECT label FROM nodes WHERE parent_id=? ORDER BY slot", (rid,)).fetchall()]
    assert ch and ch[0] == "High"
