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
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "replace.db"))
    from api.app import app
    return TestClient(app)

def test_import_replace_clears_previous(client):
    # First import
    df1 = pd.DataFrame([["Pulse","High","A","","","","X","A"]], columns=CANON)
    r1 = client.post("/api/v1/import?mode=append", files={"file": ("a.xlsx", _xlsx(df1),
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r1.status_code == 200
    
    # Verify first import worked
    roots1 = client.get("/api/v1/tree/root-options").json()["items"]
    assert "Pulse" in roots1
    
    # Second import with replace mode
    df2 = pd.DataFrame([["BP","Low","B","","","","Y","B"]], columns=CANON)
    r2 = client.post("/api/v1/import?mode=replace", files={"file": ("b.xlsx", _xlsx(df2),
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r2.status_code == 200
    
    # Verify only new data exists
    roots2 = client.get("/api/v1/tree/root-options").json()["items"]
    assert roots2 == ["BP"]  # old Pulse removed

def test_import_append_mode_preserves_existing(client):
    # First import
    df1 = pd.DataFrame([["Pulse","High","A","","","","X","A"]], columns=CANON)
    r1 = client.post("/api/v1/import?mode=append", files={"file": ("a.xlsx", _xlsx(df1),
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r1.status_code == 200
    
    # Second import with append mode
    df2 = pd.DataFrame([["BP","Low","B","","","","Y","B"]], columns=CANON)
    r2 = client.post("/api/v1/import?mode=append", files={"file": ("b.xlsx", _xlsx(df2),
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r2.status_code == 200
    
    # Verify both exist
    roots = client.get("/api/v1/tree/root-options").json()["items"]
    assert "Pulse" in roots
    assert "BP" in roots
