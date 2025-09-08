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
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "stats.db"))
    from api.app import app
    return TestClient(app)

def test_stats_root_labels_vs_nodes(client):
    # Import data with same root label appearing multiple times
    df = pd.DataFrame([
        ["BP","High","A","","","","X","A"],
        ["BP","Low","B","","","","Y","B"]
    ], columns=CANON)
    r = client.post("/api/v1/import?mode=replace", files={"file": ("ok.xlsx", _xlsx(df),
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200
    
    # Check stats
    s = client.get("/api/v1/tree/stats").json()
    assert s["root_labels"] == 1  # Only "BP" as distinct label
    assert s["root_nodes"] >= 1   # At least one root node
    assert s["roots"] == s["root_nodes"]  # Backward compatibility

def test_stats_empty_database(client):
    # Check stats on empty database
    s = client.get("/api/v1/tree/stats").json()
    assert s["root_labels"] == 0
    assert s["root_nodes"] == 0
    assert s["roots"] == 0
    assert s["nodes"] == 0
