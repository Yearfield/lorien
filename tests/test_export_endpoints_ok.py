import io, pandas as pd, pytest
from fastapi.testclient import TestClient

CAN = ["Vital Measurement","Node 1","Node 2","Node 3","Node 4","Node 5","Diagnostic Triage","Actions"]
def _xlsx(df):
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    bio.seek(0); return bio

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path/"exp.db"))
    from api.app import app
    return TestClient(app)

def test_export_csv_and_xlsx(client):
    df = pd.DataFrame([["VM","A","B","C","D","E","",""]], columns=CAN)
    client.post("/api/v1/import?mode=replace", files={"file": ("a.xlsx", _xlsx(df), "application/octet-stream")})
    r1 = client.get("/api/v1/tree/export")
    assert r1.status_code == 200
    assert r1.headers["content-type"].startswith("text/csv")
    r2 = client.get("/api/v1/tree/export.xlsx")
    assert r2.status_code == 200
    assert "officedocument.spreadsheetml.sheet" in r2.headers["content-type"]
