import io, pandas as pd
from fastapi.testclient import TestClient
import pytest
import os

CANON = [
    "Vital Measurement","Node 1","Node 2","Node 3","Node 4","Node 5","Diagnostic Triage","Actions"
]

def _xlsx_bytes(df: pd.DataFrame) -> io.BytesIO:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    buf.seek(0)
    return buf

@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "export.db"
    monkeypatch.setenv("LORIEN_DB", str(db_path))
    from api.app import app  # late import so env is set
    return TestClient(app)

def _import_rows(client: TestClient, rows):
    df = pd.DataFrame(rows, columns=CANON)
    buf = _xlsx_bytes(df)
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200
    assert r.json()["ok"] is True

def test_export_shape_and_paging(client):
    rows = [
        ["BP","High","Headache","","","","Emergent","IV labetalol"],
        ["BP","High","Blurred vision","","","","Urgent","Oral antihypertensive"],
        ["Pulse","Tachy","","","","","Routine","Hydration"],
    ]
    _import_rows(client, rows)

    r = client.get("/api/v1/tree/export-json?limit=2&offset=0")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body and "total" in body
    assert body["limit"] == 2 and body["offset"] == 0
    assert body["total"] >= 3  # we imported 3 paths

    first = body["items"][0]
    # Verify canonical keys present
    for k in CANON:
        assert k in first

    # Page 2
    r2 = client.get("/api/v1/tree/export-json?limit=2&offset=2")
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["limit"] == 2 and body2["offset"] == 2
    assert isinstance(body2["items"], list)
