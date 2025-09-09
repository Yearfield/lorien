from fastapi.testclient import TestClient
import io, pandas as pd, pytest

CAN = ["Vital Measurement","Node 1","Node 2","Node 3","Node 4","Node 5","Diagnostic Triage","Actions"]

def _xlsx(df):
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as w: df.to_excel(w, index=False)
    bio.seek(0); return bio

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path/"export_alias.db"))
    from api.app import app
    return TestClient(app)

def test_alias_routes(client):
    df = pd.DataFrame([["Pulse","Low","","","","","",""]], columns=CAN)
    r = client.post("/api/v1/import?mode=replace", files={"file":("a.xlsx", _xlsx(df), "application/octet-stream")})
    assert r.status_code == 200

    for p in ["/api/v1/export/csv", "/export/csv",
              "/api/v1/export.xlsx", "/export.xlsx"]:
        res = client.get(p); assert res.status_code == 200

def test_canonical_routes_still_work(client):
    df = pd.DataFrame([["BP","High","","","","","",""]], columns=CAN)
    r = client.post("/api/v1/import?mode=replace", files={"file":("b.xlsx", _xlsx(df), "application/octet-stream")})
    assert r.status_code == 200

    for p in ["/api/v1/tree/export", "/tree/export",
              "/api/v1/tree/export.xlsx", "/tree/export.xlsx"]:
        res = client.get(p); assert res.status_code == 200

def test_head_requests_work(client):
    for p in ["/api/v1/tree/export", "/api/v1/tree/export.xlsx",
              "/api/v1/export/csv", "/api/v1/export.xlsx",
              "/tree/export", "/tree/export.xlsx",
              "/export/csv", "/export.xlsx"]:
        res = client.head(p); assert res.status_code == 200
