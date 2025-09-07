from fastapi.testclient import TestClient
import sqlite3
import os
import pytest

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "sweep.db"))
    from api.app import app
    return TestClient(app)

def test_sanitize_labels_endpoint(client):
    # Seed a fake 'nan' label directly
    db = os.environ["LORIEN_DB"]
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE IF NOT EXISTS nodes(id INTEGER PRIMARY KEY, parent_id INTEGER, label TEXT, depth INTEGER, slot INTEGER)")
    con.execute("INSERT INTO nodes(label,depth) VALUES('nan',0)")
    con.execute("INSERT INTO nodes(label,depth) VALUES('',0)")
    con.execute("INSERT INTO nodes(label,depth) VALUES(NULL,0)")
    con.execute("INSERT INTO nodes(label,depth) VALUES('Valid',0)")
    con.commit()
    
    # Test dry-run first
    r = client.post("/api/v1/admin/sanitize-labels")  # dry-run
    assert r.status_code == 200
    result = r.json()
    assert result["dry_run"] == True
    assert len(result["candidate_ids"]) == 3  # nan, '', NULL
    assert result["deleted"] == 0
    
    # Test actual deletion
    r2 = client.post("/api/v1/admin/sanitize-labels?dry_run=false")
    assert r2.status_code == 200
    result2 = r2.json()
    assert result2["dry_run"] == False
    assert result2["deleted"] == 3
    
    # Verify only valid label remains
    remaining = con.execute("SELECT label FROM nodes").fetchall()
    assert len(remaining) == 1
    assert remaining[0][0] == "Valid"

def test_sanitize_dual_mounting(client):
    # Test that endpoint works at both /api/v1/... and /...
    r1 = client.post("/api/v1/admin/sanitize-labels")
    r2 = client.post("/admin/sanitize-labels")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json() == r2.json()
