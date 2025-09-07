import io, pandas as pd
import pytest
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

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "complete.db"))
    from api.app import app  # late import to honor env
    return TestClient(app)

def _import_rows(client: TestClient, rows):
    df = pd.DataFrame(rows, columns=CANON)
    buf = _xlsx_bytes(df)
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200
    assert r.json()["ok"] is True

def test_stats_and_missing_slots(client):
    rows = [
        # Path: BP -> High -> Headache  (depth 2)
        ["BP","High","Headache","","","","Emergent","IV labetalol"],
        # Path: BP -> Low                (depth 1)
        ["BP","Low","","","","","Urgent","Oral saline"],
        # Path: Pulse -> Tachy           (depth 1)
        ["Pulse","Tachy","","","","","Routine","Hydration"],
    ]
    _import_rows(client, rows)

    # Stats present and sensible
    s = client.get("/api/v1/tree/stats").json()
    assert s["nodes"] >= 5
    assert s["roots"] >= 2
    assert s["leaves"] >= 3
    assert s["complete_paths"] >= 0
    assert s["incomplete_parents"] >= 1

    # Missing slots, first page
    ms = client.get("/api/v1/tree/missing-slots-json?limit=10&offset=0").json()
    assert "items" in ms and "total" in ms
    assert ms["limit"] == 10 and ms["offset"] == 0
    assert ms["total"] >= 3

    # Find BP parent row and ensure it lists some missing slots
    bp_rows = [it for it in ms["items"] if it["label"] == "BP" and it["depth"] == 0]
    assert len(bp_rows) >= 1
    assert isinstance(bp_rows[0]["missing_slots"], list)
    # BP has at most 2 children in our sample -> at least slots 3,4,5 are missing
    assert 3 in bp_rows[0]["missing_slots"]

    # Depth filter
    ms_d1 = client.get("/api/v1/tree/missing-slots-json?limit=10&offset=0&depth=1").json()
    assert all(it["depth"] == 1 for it in ms_d1["items"])

    # q filter
    ms_q = client.get("/api/v1/tree/missing-slots-json?q=high").json()
    assert any("High" == it["label"] for it in ms_q["items"])
