from starlette.testclient import TestClient

from api.app import app
from api.db.migrate import apply_migrations


def test_edge_flag_toggle(tmp_path, monkeypatch):
    """Test setting and unsetting edge flags."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Create a simple tree with parent and child
    csv = """D0,D1,D2,D3,D4,D5,D6,Notes
Root,Child1,,,,,,
Root,Child2,,,,,,"""

    r = c.post("/api/v1/import?mode=replace", files={"file": ("tree.csv", csv, "text/csv")})
    assert r.status_code in (200, 201)

    # Get the root and children
    roots = c.get("/api/v1/tree/roots").json()["items"]
    root_id = roots[0]["id"]

    children = c.get(f"/api/v1/tree/children?parent_id={root_id}").json()["items"]
    assert len(children) == 2
    child1_id = children[0]["id"]
    child2_id = children[1]["id"]

    # Initially no flags should be set
    assert not children[0]["red_flag"]
    assert not children[1]["red_flag"]

    # Set flag for first child
    r = c.put(
        "/api/v1/tree/edge/flag",
        json={"parent_id": root_id, "child_id": child1_id, "red_flag": True},
    )
    assert r.status_code == 200
    assert r.json()["red_flag"] is True

    # Check that flag is now set
    children = c.get(f"/api/v1/tree/children?parent_id={root_id}").json()["items"]
    assert children[0]["red_flag"] is True
    assert children[1]["red_flag"] is False

    # Test filtering by red flag
    red_children = c.get(f"/api/v1/tree/children?parent_id={root_id}&only_red=true").json()["items"]
    assert len(red_children) == 1
    assert red_children[0]["id"] == child1_id

    # Unset the flag
    r = c.put(
        "/api/v1/tree/edge/flag",
        json={"parent_id": root_id, "child_id": child1_id, "red_flag": False},
    )
    assert r.status_code == 200
    assert r.json()["red_flag"] is False

    # Check that flag is now unset
    children = c.get(f"/api/v1/tree/children?parent_id={root_id}").json()["items"]
    assert not children[0]["red_flag"]
    assert not children[1]["red_flag"]

    # No red children should be found
    red_children = c.get(f"/api/v1/tree/children?parent_id={root_id}&only_red=true").json()["items"]
    assert len(red_children) == 0


def test_edge_flag_cascade_delete(tmp_path, monkeypatch):
    """Test that edge flags are deleted when parent or child is deleted."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Create a simple tree
    csv = """D0,D1,D2,D3,D4,D5,D6,Notes
Root,Child1,,,,,,"""

    r = c.post("/api/v1/import?mode=replace", files={"file": ("tree.csv", csv, "text/csv")})
    assert r.status_code in (200, 201)

    # Get IDs
    roots = c.get("/api/v1/tree/roots").json()["items"]
    root_id = roots[0]["id"]

    children = c.get(f"/api/v1/tree/children?parent_id={root_id}").json()["items"]
    child_id = children[0]["id"]

    # Set a flag
    r = c.put(
        "/api/v1/tree/edge/flag",
        json={"parent_id": root_id, "child_id": child_id, "red_flag": True},
    )
    assert r.status_code == 200

    # Delete the root (should cascade delete child and edge flag)
    r = c.delete(f"/api/v1/tree/root?root_id={root_id}")
    assert r.status_code == 200

    # Verify root is gone
    roots = c.get("/api/v1/tree/roots").json()["items"]
    assert len(roots) == 0
