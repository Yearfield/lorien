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
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "hard.db"))
    from api.app import app
    return TestClient(app)

def test_hard_replace_removes_legacy_labels(client):
    # Import first dataset
    df1 = pd.DataFrame([["BP","High","A","","","","X","A"]], columns=CANON)
    client.post("/api/v1/import?mode=append", files={"file": ("a.xlsx", _xlsx(df1), "application/octet-stream")})
    r1 = client.get("/api/v1/tree/root-options").json()["items"]
    assert "BP" in r1

    # Hard replace with a different root
    df2 = pd.DataFrame([["Pulse","Low","B","","","","Y","B"]], columns=CANON)
    client.post("/api/v1/import?mode=hard_replace", files={"file": ("b.xlsx", _xlsx(df2), "application/octet-stream")})
    r2 = client.get("/api/v1/tree/root-options").json()["items"]
    assert r2 == ["Pulse"]
