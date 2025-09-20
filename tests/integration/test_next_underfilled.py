from api.app import app
from starlette.testclient import TestClient
from api.db.migrate import apply_migrations
import os

def test_next_underfilled_parent(tmp_path, monkeypatch):
    """Test finding the next parent with fewer than 5 children."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Create a tree with parents having different numbers of children
    csv = """D0,D1,D2,D3,D4,D5,D6,Notes
Root1,Child1,,,,,,
Root1,Child2,,,,,,
Root1,Child3,,,,,,
Root1,Child4,,,,,,
Root1,Child5,,,,,,
Root2,ChildA,,,,,,
Root2,ChildB,,,,,,
Root3,ChildX,,,,,,"""
    
    r = c.post("/api/v1/import?mode=replace", files={"file": ("tree.csv", csv, "text/csv")})
    assert r.status_code in (200, 201)

    # Get the actual IDs of the roots
    r = c.get("/api/v1/tree/roots")
    assert r.status_code == 200
    roots = r.json()["items"]
    root_ids = {root["label"].lower(): root["id"] for root in roots}
    
    # Root1 has 5 children (full), Root2 has 2 children, Root3 has 1 child
    # Next underfilled should be Root2 (first with <5)
    r = c.get("/api/v1/tree/next-underfilled")
    assert r.status_code == 200
    data = r.json()
    assert data["label"].lower() == "root2"
    assert data["child_count"] == 2

    # Test with after_id parameter (after Root1)
    root1_id = root_ids["root1"]
    r = c.get(f"/api/v1/tree/next-underfilled?after_id={root1_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["label"].lower() == "root2"
    assert data["child_count"] == 2

    # After Root2, should find Root3
    root2_id = root_ids["root2"]
    r = c.get(f"/api/v1/tree/next-underfilled?after_id={root2_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["label"].lower() == "root3"
    assert data["child_count"] == 1

    # After Root3, should return 204 (no more underfilled)
    root3_id = root_ids["root3"]
    r = c.get(f"/api/v1/tree/next-underfilled?after_id={root3_id}")
    assert r.status_code == 204

def test_next_underfilled_all_full(tmp_path, monkeypatch):
    """Test when all parents have 5 children."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Create a tree where all parents have exactly 5 children
    csv = """D0,D1,D2,D3,D4,D5,D6,Notes
Root1,Child1,,,,,,
Root1,Child2,,,,,,
Root1,Child3,,,,,,
Root1,Child4,,,,,,
Root1,Child5,,,,,,
Root2,ChildA,,,,,,
Root2,ChildB,,,,,,
Root2,ChildC,,,,,,
Root2,ChildD,,,,,,
Root2,ChildE,,,,,,"""
    
    r = c.post("/api/v1/import?mode=replace", files={"file": ("tree.csv", csv, "text/csv")})
    assert r.status_code in (200, 201)

    # All parents are full, should return 204
    r = c.get("/api/v1/tree/next-underfilled")
    assert r.status_code == 204
