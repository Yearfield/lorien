from starlette.testclient import TestClient

from api.app import app
from api.db.migrate import apply_migrations


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

    # Test with root_id parameter - scope to Root1 tree
    root1_id = root_ids["root1"]
    r = c.get(f"/api/v1/tree/next-underfilled?root_id={root1_id}")
    assert r.status_code == 204  # Root1 is full (5 children)

    # Test with root_id parameter - scope to Root2 tree
    root2_id = root_ids["root2"]
    r = c.get(f"/api/v1/tree/next-underfilled?root_id={root2_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["label"].lower() == "root2"
    assert data["child_count"] == 2

    # Test with root_id and after_id parameters (after Root1 in Root1's subtree)
    # Since Root1 is full, after Root1 should return 204 (no more underfilled in Root1's subtree)
    r = c.get(f"/api/v1/tree/next-underfilled?root_id={root1_id}&after_id={root1_id}")
    assert r.status_code == 204

    # Test Root2's subtree - should find Root2 itself (has 2 children < 5)
    r = c.get(f"/api/v1/tree/next-underfilled?root_id={root2_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["label"].lower() == "root2"
    assert data["child_count"] == 2

    # Test Root3's subtree - should find Root3 itself (has 1 child < 5)
    root3_id = root_ids["root3"]
    r = c.get(f"/api/v1/tree/next-underfilled?root_id={root3_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["label"].lower() == "root3"
    assert data["child_count"] == 1


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

    # Get the root IDs
    r = c.get("/api/v1/tree/roots")
    assert r.status_code == 200
    roots = r.json()["items"]
    root_ids = {root["label"].lower(): root["id"] for root in roots}

    # All parents are full, should return 204 for any root scope
    for root_id in root_ids.values():
        r = c.get(f"/api/v1/tree/next-underfilled?root_id={root_id}")
        assert r.status_code == 204
