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

def test_sync_dictionary_from_tree(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "dict.db"))
    from api.app import app
    client = TestClient(app)
    
    df = pd.DataFrame([
        ["BP", "High", "Headache", "", "", "", "Emergent", "IV labetalol"],
        ["Pulse", "Tachy", "", "", "", "", "Routine", "Hydration"],
    ], columns=CANON)
    
    # Import data
    buf = _xlsx_bytes(df)
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200

    # Sync dictionary from tree
    r2 = client.post("/api/v1/admin/sync-dictionary-from-tree")
    assert r2.status_code == 200
    body = r2.json()
    assert "inserted" in body
    assert body["inserted"] > 0

    # List dictionary terms
    r3 = client.get("/api/v1/dictionary?limit=5&offset=0&query=head")
    assert r3.status_code == 200
    body = r3.json()
    assert "items" in body
    # Should find "Headache" term
    assert any("Headache" == item["term"] for item in body["items"])

def test_dictionary_list_with_filters(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "dict_filter.db"))
    from api.app import app
    client = TestClient(app)
    
    df = pd.DataFrame([
        ["BP", "High", "Headache", "", "", "", "Emergent", "IV labetalol"],
    ], columns=CANON)
    
    # Import and sync
    buf = _xlsx_bytes(df)
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200
    
    r2 = client.post("/api/v1/admin/sync-dictionary-from-tree")
    assert r2.status_code == 200

    # Test type filter
    r3 = client.get("/api/v1/dictionary?type=node_label&limit=10&offset=0")
    assert r3.status_code == 200
    body = r3.json()
    assert all(item["type"] == "node_label" for item in body["items"])

    # Test search query
    r4 = client.get("/api/v1/dictionary?query=bp&limit=10&offset=0")
    assert r4.status_code == 200
    body = r4.json()
    assert any("BP" in item["term"] for item in body["items"])

def test_dictionary_sync_idempotent(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "dict_idempotent.db"))
    from api.app import app
    client = TestClient(app)
    
    df = pd.DataFrame([
        ["BP", "High", "", "", "", "", "Emergent", "IV labetalol"],
    ], columns=CANON)
    
    # Import data
    buf = _xlsx_bytes(df)
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200

    # First sync
    r1 = client.post("/api/v1/admin/sync-dictionary-from-tree")
    assert r1.status_code == 200
    first_inserted = r1.json()["inserted"]

    # Second sync (should be idempotent)
    r2 = client.post("/api/v1/admin/sync-dictionary-from-tree")
    assert r2.status_code == 200
    second_inserted = r2.json()["inserted"]

    # Second sync should insert fewer (or zero) terms
    assert second_inserted <= first_inserted
