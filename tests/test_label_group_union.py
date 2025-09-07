import io
import pandas as pd
import pytest
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
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "union.db"))
    from api.app import app
    return TestClient(app)

def test_union_contains_children_from_all_occurrences(client):
    df = pd.DataFrame([
        ["BP","High","Headache","","","","X","A"],
        ["Pulse","High","Vomiting","","","","Y","A"],
    ], columns=CANON)
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", _xlsx(df), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200

    agg = client.get("/api/v1/tree/labels/High/aggregate").json()
    union = [u["label"] for u in agg["union"]]
    assert "Headache" in union
    assert "Vomiting" in union
