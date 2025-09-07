import io
import pandas as pd
import pytest
from fastapi.testclient import TestClient

CANON = ["Vital Measurement","Node 1","Node 2","Node 3","Node 4","Node 5","Diagnostic Triage","Actions"]

def _xlsx_bytes(df: pd.DataFrame):
    import io
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    buf.seek(0)
    return buf

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "nav.db"))
    from api.app import app
    return TestClient(app)

def test_navigate_flow(client):
    df = pd.DataFrame([
        ["BP","High","Headache","","","","Emergent","IV labetalol"],
        ["BP","Low","","","","","Routine","Salt"],
    ], columns=CANON)
    buf = _xlsx_bytes(df)
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200

    roots = client.get("/api/v1/tree/root-options").json()["items"]
    assert "BP" in roots

    step1 = client.get("/api/v1/tree/navigate", params={"root":"BP"}).json()
    labs1 = [o["label"] for o in step1["options"]]
    assert "High" in labs1 or "Low" in labs1

    step2 = client.get("/api/v1/tree/navigate", params={"root":"BP","n1":"High"}).json()
    # may or may not have outcome/options depending on data
    assert "options" in step2 and "outcome" in step2
