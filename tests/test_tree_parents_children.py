import io
import pandas as pd
import pytest
from fastapi.testclient import TestClient

CANON = ["Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5", "Diagnostic Triage", "Actions"]

def _xlsx_bytes(df: pd.DataFrame) -> io.BytesIO:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    buf.seek(0)
    return buf

def test_parents_and_children_listing(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "parents.db"))
    from api.app import app
    client = TestClient(app)
    
    df = pd.DataFrame([
        ["BP", "High", "Headache", "", "", "", "Emergent", "IV labetalol"],
        ["BP", "Low", "", "", "", "", "Urgent", "Salt"],
        ["Pulse", "Tachy", "", "", "", "", "Routine", "Hydration"],
    ], columns=CANON)
    
    # Import
    buf = _xlsx_bytes(df)
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200

    # List parents (incomplete only default)
    p = client.get("/api/v1/tree/parents?limit=10&offset=0").json()
    assert "items" in p and isinstance(p["items"], list)
    assert p["total"] >= 2

    # Pick one parent and fetch children
    pid = p["items"][0]["parent_id"]
    kids = client.get(f"/api/v1/tree/children/{pid}").json()
    assert "children" in kids and isinstance(kids["children"], list)
    assert "parent" in kids and kids["parent"] is not None

def test_parents_filtering_and_pagination(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "filter.db"))
    from api.app import app
    client = TestClient(app)
    
    df = pd.DataFrame([
        ["BP", "High", "Headache", "", "", "", "Emergent", "IV labetalol"],
        ["HR", "Fast", "", "", "", "", "Urgent", "Monitor"],
    ], columns=CANON)
    
    # Import
    buf = _xlsx_bytes(df)
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200

    # Test depth filter
    p = client.get("/api/v1/tree/parents?depth=0").json()
    assert all(item["depth"] == 0 for item in p["items"])

    # Test search filter
    p = client.get("/api/v1/tree/parents?q=bp").json()
    assert any("BP" in item["label"] for item in p["items"])

    # Test incomplete_only filter
    p = client.get("/api/v1/tree/parents?incomplete_only=false").json()
    # Should include all parents, not just incomplete ones
    assert p["total"] >= 2

def test_children_endpoint_validation(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "children.db"))
    from api.app import app
    client = TestClient(app)
    
    # Test non-existent parent
    r = client.get("/api/v1/tree/children/99999")
    assert r.status_code == 200
    body = r.json()
    assert body["parent"] is None
    assert body["children"] == []
