"""
Integration tests for root CRUD operations.
"""

from starlette.testclient import TestClient

from api.db.migrate import apply_migrations
from api.main import app


def test_create_and_delete_root(tmp_path, monkeypatch):
    """Test creating and deleting a root node."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))

    client = TestClient(app)

    # Create a root
    r = client.post("/api/v1/tree/roots", json={"label": "root-one"})
    assert r.status_code == 201
    root = r.json()
    rid = root["id"]
    assert root["label"] == "root-one"
    assert root["depth"] == 0

    # List shows it
    r = client.get("/api/v1/tree/roots")
    assert r.status_code == 200
    roots = r.json().get("items", [])
    assert any(it["id"] == rid for it in roots)

    # Delete the root
    r = client.delete(f"/api/v1/tree/roots/{rid}")
    assert r.status_code == 204

    # Root is gone from list
    r = client.get("/api/v1/tree/roots")
    assert r.status_code == 200
    roots = r.json().get("items", [])
    assert not any(it["id"] == rid for it in roots)


def test_delete_nonexistent_root(tmp_path, monkeypatch):
    """Test deleting a non-existent root returns 404."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))

    client = TestClient(app)

    # Try to delete non-existent root
    r = client.delete("/api/v1/tree/roots/999")
    assert r.status_code == 404


def test_delete_non_root_node(tmp_path, monkeypatch):
    """Test deleting a non-root node returns 422."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))

    client = TestClient(app)

    # Create a root and add a child
    r = client.post("/api/v1/tree/roots", json={"label": "parent"})
    assert r.status_code == 201
    root_id = r.json()["id"]

    # Add a child
    r = client.put(
        "/api/v1/tree/children", json={"parent_id": root_id, "children": [{"label": "child"}]}
    )
    assert r.status_code == 200

    # Get the child ID
    r = client.get(f"/api/v1/tree/children?parent_id={root_id}")
    assert r.status_code == 200
    child_id = r.json()["items"][0]["id"]

    # Try to delete the child as if it were a root
    r = client.delete(f"/api/v1/tree/roots/{child_id}")
    assert r.status_code == 422


def test_create_root_empty_label(tmp_path, monkeypatch):
    """Test creating a root with empty label returns 422."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))

    client = TestClient(app)

    # Try to create root with empty label
    r = client.post("/api/v1/tree/roots", json={"label": ""})
    assert r.status_code == 422

    # Try to create root with whitespace-only label
    r = client.post("/api/v1/tree/roots", json={"label": "   "})
    assert r.status_code == 422


def test_export_csv_with_root_id(tmp_path, monkeypatch):
    """Test CSV export with root_id parameter."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))

    client = TestClient(app)

    # Create a root
    r = client.post("/api/v1/tree/roots", json={"label": "export-test"})
    assert r.status_code == 201
    root_id = r.json()["id"]

    # Export CSV for this root
    r = client.get(f"/api/v1/tree/export?format=csv&root_id={root_id}")
    assert r.status_code == 200
    assert r.headers["content-type"] == "text/csv; charset=utf-8"

    # Check CSV content has header
    csv_content = r.text
    assert "D0,D1,D2,D3,D4,D5,D6,Notes" in csv_content
    assert "export-test" in csv_content


def test_cascade_delete_removes_children(tmp_path, monkeypatch):
    """Test that deleting a root cascades to remove all children."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))

    client = TestClient(app)

    # Create a root and add children
    r = client.post("/api/v1/tree/roots", json={"label": "parent-with-children"})
    assert r.status_code == 201
    root_id = r.json()["id"]

    # Add children
    r = client.put(
        "/api/v1/tree/children",
        json={"parent_id": root_id, "children": [{"label": "child1"}, {"label": "child2"}]},
    )
    assert r.status_code == 200

    # Verify children exist
    r = client.get(f"/api/v1/tree/children?parent_id={root_id}")
    assert r.status_code == 200
    children = r.json()["items"]
    assert len(children) == 2

    # Delete the root
    r = client.delete(f"/api/v1/tree/roots/{root_id}")
    assert r.status_code == 204

    # Verify children are gone (they should be cascade deleted)
    r = client.get(f"/api/v1/tree/children?parent_id={root_id}")
    assert r.status_code == 200
    children = r.json()["items"]
    assert len(children) == 0
