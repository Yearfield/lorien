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
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "calc.db"))
    from api.app import app
    return TestClient(app)

def test_roots_and_navigate(client):
    df = pd.DataFrame([
        ["BP","High","Headache","","","","Emergent","Go ER"],
        ["BP","Low","Faint","","","","Routine","Hydrate"],
    ], columns=CANON)
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", _xlsx(df), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200

    roots = client.get("/api/v1/tree/root-options").json()["items"]
    assert "BP" in roots

    nav0 = client.get("/api/v1/tree/navigate", params={"root":"BP"}).json()
    labels = [o["label"] for o in nav0["options"]]
    assert "High" in labels and "Low" in labels

    nav1 = client.get("/api/v1/tree/navigate", params={"root":"BP","n1":"High"}).json()
    labels2 = [o["label"] for o in nav1["options"]]
    assert "Headache" in labels2 or nav1["outcome"] is not None

def test_navigate_with_search_filter(client):
    df = pd.DataFrame([
        ["Pulse","High","Headache","","","","X","A"],
        ["Pulse","High","Vomiting","","","","Y","B"],
        ["Pulse","High","Fever","","","","Y","C"],
    ], columns=CANON)
    client.post("/api/v1/import", files={"file": ("seed.xlsx", _xlsx(df), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})

    # Test without search filter first
    nav_no_filter = client.get("/api/v1/tree/navigate", params={"root":"Pulse","n1":"High"}).json()
    labels_no_filter = [o["label"] for o in nav_no_filter["options"]]
    assert len(labels_no_filter) == 3
    assert "Headache" in labels_no_filter and "Vomiting" in labels_no_filter and "Fever" in labels_no_filter

    # Test with search filter
    nav = client.get("/api/v1/tree/navigate", params={"root":"Pulse","n1":"High","q":"fev"}).json()
    labels = [o["label"] for o in nav["options"]]
    assert labels == ["Fever"]
