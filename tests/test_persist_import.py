import io, os, pandas as pd
from fastapi.testclient import TestClient

CANON = [
    "Vital Measurement","Node 1","Node 2","Node 3","Node 4","Node 5","Diagnostic Triage","Actions"
]

def _xlsx_bytes(df: pd.DataFrame) -> io.BytesIO:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    buf.seek(0)
    return buf

def test_import_persists_and_stats_increase(tmp_path, monkeypatch):
    # Use isolated DB per test
    db_path = tmp_path / "persist.db"
    monkeypatch.setenv("LORIEN_DB", str(db_path))

    # Late import so app sees env var
    from api.app import app  # noqa: E402
    client = TestClient(app)

    # Build a tiny canonical sheet
    df = pd.DataFrame([
        ["BP","High","Headache","Severe","","","Emergent","IV labetalol"],
        ["BP","High","Blurred vision","","","","Urgent","Oral antihypertensive"],
    ], columns=CANON)

    # XLSX upload
    buf = _xlsx_bytes(df)
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["rows"] == 2
    assert "result" in body
    assert body["result"]["status"] == "success"

    # Check that we have some nodes created
    r1 = client.get("/api/v1/tree/stats")
    assert r1.status_code == 200
    stats = r1.json()
    assert stats["nodes"] > 0  # tree has nodes
    assert stats["roots"] >= 1  # at least one root for 'BP'
    assert stats["leaves"] >= 1  # at least one leaf
