from starlette.testclient import TestClient

from api.app import app
from api.db.migrate import apply_migrations


def test_roots_children_put(tmp_path, monkeypatch):
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Create a root via import (simplest)
    csv = "D0,D1,D2,D3,D4,D5,D6,Notes\nRootX,,,,,,,\n"
    r = c.post("/api/v1/import?mode=replace", files={"file": ("r.csv", csv, "text/csv")})
    assert r.status_code in (200, 201)

    r = c.get("/api/v1/tree/roots")
    root_id = r.json()["items"][0]["id"]

    # No children yet
    rc = c.get(f"/api/v1/tree/children?parent_id={root_id}")
    assert rc.json()["total"] == 0

    # Add 3 children
    rput = c.put(
        "/api/v1/tree/children",
        json={"parent_id": root_id, "children": [{"label": "A"}, {"label": "B"}, {"label": "C"}]},
    )
    assert rput.status_code == 200

    rc2 = c.get(f"/api/v1/tree/children?parent_id={root_id}")
    labels = [x["label"] for x in rc2.json()["items"]]
    assert labels == ["A", "B", "C"]


def test_delete_root_cascades(tmp_path, monkeypatch):
    from starlette.testclient import TestClient

    from api.db.migrate import apply_migrations
    from api.main import app

    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # seed one root + child through API
    csv = "D0,D1,D2,D3,D4,D5,D6,Notes\nRootX,ChildA,,,,,,\n"
    r = c.post("/api/v1/import?mode=replace", files={"file": ("r.csv", csv, "text/csv")})
    assert r.status_code in (200, 201)

    roots = c.get("/api/v1/tree/roots").json()["items"]
    root_id = roots[0]["id"]

    # verify child exists
    children = c.get(f"/api/v1/tree/children?parent_id={root_id}").json()["items"]
    assert children and children[0]["label"].lower() == "childa"

    # delete root
    d = c.delete(f"/api/v1/tree/root?root_id={root_id}")
    assert d.status_code == 200 and d.json()["ok"] is True

    # root gone, subtree gone
    roots_after = c.get("/api/v1/tree/roots").json()["items"]
    assert roots_after == []


def test_search_by_label_endpoint(tmp_path, monkeypatch):
    """Test search by label endpoint"""
    from starlette.testclient import TestClient

    from api.db.migrate import apply_migrations
    from api.main import app

    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Test search for non-existent label
    search_r = c.get("/api/v1/tree/search-by-label?label=NonExistent")
    assert search_r.status_code == 200
    assert search_r.json()["total"] == 0


def test_rename_endpoint(tmp_path, monkeypatch):
    """Test rename endpoint"""
    from starlette.testclient import TestClient

    from api.db.migrate import apply_migrations
    from api.main import app

    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Test rename non-existent node
    rename_r = c.put("/api/v1/tree/node/999/rename", json={"label": "NewName"})
    assert rename_r.status_code == 404


def test_merge_validation_errors(tmp_path, monkeypatch):
    """Test merge endpoint validation and error handling"""
    from starlette.testclient import TestClient

    from api.db.migrate import apply_migrations
    from api.main import app

    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Test merge with non-existent parents
    merge_r = c.post(
        "/api/v1/tree/merge-parents",
        json={
            "current_parent_id": 999,
            "existing_parent_id": 998,
            "selected_children": ["Child1", "Child2"],
        },
    )
    assert merge_r.status_code == 404

    # Test merge with too many children
    merge_r = c.post(
        "/api/v1/tree/merge-parents",
        json={
            "current_parent_id": 1,
            "existing_parent_id": 2,
            "selected_children": ["Child1", "Child2", "Child3", "Child4", "Child5", "Child6"],
        },
    )
    assert merge_r.status_code == 422
