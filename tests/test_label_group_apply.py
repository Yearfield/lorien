import io
import pandas as pd
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
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "label_apply.db"))
    from api.app import app
    return TestClient(app)

def test_group_and_apply_defaults(client):
    df = pd.DataFrame([
        ["BP","High","Headache","","","","Emergent","A"],
        ["BP","High","Vomiting","","","","Routine","B"],
        ["BP","High","Neck Stiffness","","","","Urgent","C"],
        ["Pulse","High","Fever","","","","Routine","D"],
        ["Pulse","High","Vomiting","","","","Routine","E"],
    ], columns=CANON)
    r = client.post("/api/v1/import", files={"file": ("d.xlsx", _xlsx(df), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200

    labels = client.get("/api/v1/tree/labels?limit=50&offset=0").json()
    assert any(x["label"] == "High" for x in labels["items"])

    agg = client.get("/api/v1/tree/labels/High/aggregate").json()
    union_labels = [u["label"] for u in agg["union"]]
    assert "Headache" in union_labels and "Vomiting" in union_labels

    chosen = ["Headache","Vomiting","Fever","Neck Stiffness","Other"]
    r2 = client.post("/api/v1/tree/labels/High/apply-default", json={"chosen": chosen})
    assert r2.status_code == 200

    # verify each parent with label 'High' now has these exact 5
    db = os.environ["LORIEN_DB"]
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    pids = [r["id"] for r in conn.execute("SELECT id FROM nodes WHERE label='High'").fetchall()]
    for pid in pids:
        ch = [r["label"] for r in conn.execute("SELECT label FROM nodes WHERE parent_id=? ORDER BY slot", (pid,)).fetchall()]
        assert ch == chosen

def test_dual_mounting(client):
    # Test that endpoints are available at both /api/v1/... and /...
    r1 = client.get("/api/v1/tree/labels?limit=10&offset=0")
    r2 = client.get("/tree/labels?limit=10&offset=0")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json() == r2.json()

def test_validation_errors(client):
    # Test 422 for invalid chosen list
    r = client.post("/api/v1/tree/labels/Test/apply-default", json={"chosen": ["A", "B"]})  # Only 2 items
    assert r.status_code == 422
    detail = r.json()["detail"]
    # Check for any validation error message
    assert len(detail) > 0
    assert any("chosen" in str(d.get("loc", [])) for d in detail)

def test_empty_label_aggregate(client):
    # Test aggregate for non-existent label
    r = client.get("/api/v1/tree/labels/NonExistent/aggregate")
    assert r.status_code == 200
    result = r.json()
    assert result["label"] == "NonExistent"
    assert result["occurrences"] == 0
    assert result["union"] == []
    assert result["by_parent"] == []
