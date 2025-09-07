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
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "labels.db"))
    from api.app import app
    return TestClient(app)

def test_group_labels_filter_on_aggregate(client):
    # High under two different roots; one complete (5), one incomplete (3)
    # Each row creates a separate tree path
    rows = [
        ["BP","High","A","B","C","D","E","X"],  # BP->High->A->B->C->D->E (deep path)
        ["Pulse","High","A","B","C","","","Y"],  # Pulse->High->A->B->C (shorter path)
    ]
    df = pd.DataFrame(rows, columns=CANON)
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", _xlsx(df), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200

    g = client.get("/api/v1/tree/labels?limit=50&offset=0").json()
    item = next(it for it in g["items"] if it["label"] == "High")
    # Both High parents should be incomplete because they don't have exactly 5 children at depth 2
    assert item["occurrences"] == 2
    assert item["incomplete_count"] == 2  # Both are incomplete