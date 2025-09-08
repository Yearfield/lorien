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
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "preview.db"))
    from api.app import app
    return TestClient(app)

def test_preview_detects_single_root(client):
    df = pd.DataFrame([["BP","High","A","","","","X","A"]], columns=CANON)
    r = client.post("/api/v1/import/preview", files={"file": ("ok.xlsx", _xlsx(df),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    j = r.json()
    assert j["ok"] is True
    assert j["roots_detected"] == ["BP"]
    assert j["roots_count"] == 1

def test_preview_detects_multiple_roots(client):
    df = pd.DataFrame([
        ["BP","High","A","","","","X","A"],
        ["Pulse","Low","B","","","","Y","B"],
        ["BP","Normal","C","","","","Z","C"],
    ], columns=CANON)
    r = client.post("/api/v1/import/preview", files={"file": ("ok.xlsx", _xlsx(df),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    j = r.json()
    assert j["ok"] is True
    assert j["roots_detected"] == ["BP", "Pulse"]
    assert j["roots_count"] == 2

def test_preview_validates_headers(client):
    df = pd.DataFrame([["Wrong","Header","A","","","","X","A"]], columns=["Wrong","Header","A","","","","X","A"])
    r = client.post("/api/v1/import/preview", files={"file": ("bad.xlsx", _xlsx(df),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 422
    j = r.json()
    assert "detail" in j
    assert j["detail"][0]["loc"] == ["header"]
