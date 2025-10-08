import os

import pytest
from fastapi.testclient import TestClient

from api.app import app
from api.db.migrate import apply_migrations


@pytest.fixture
def client(tmp_path):
    db = tmp_path / "undo.db"
    os.environ["LORIEN_DB_PATH"] = str(db)
    apply_migrations(str(db))
    return TestClient(app)


def test_delete_and_undo(client: TestClient):
    # create root and child
    r = client.post("/api/v1/tree/roots", json={"label": "Root A"})
    assert r.status_code == 201
    rid = r.json()["id"]
    put = client.put(
        "/api/v1/tree/children",
        json={"parent_id": rid, "children": [{"label": "x"}, {"label": "y"}]},
    )
    assert put.status_code == 200
    kids = client.get(f"/api/v1/tree/children?parent_id={rid}").json()["items"]
    kid_id = kids[0]["id"]
    # dry-run + delete
    dry = client.delete(f"/api/v1/tree/node/{kid_id}?dry_run=true")
    assert dry.status_code == 200
    snap = dry.json()["snapshot"]
    do = client.delete(f"/api/v1/tree/node/{kid_id}?dry_run=false")
    assert do.status_code == 200
    # verify gone
    kids2 = client.get(f"/api/v1/tree/children?parent_id={rid}").json()["items"]
    assert len(kids2) == 1
    # restore
    res = client.post("/api/v1/tree/subtree/restore", json={"snapshot": snap})
    assert res.status_code == 200
    kids3 = client.get(f"/api/v1/tree/children?parent_id={rid}").json()["items"]
    assert len(kids3) == 2


def test_delete_nonexistent_node(client: TestClient):
    # Try to delete a node that doesn't exist
    dry = client.delete("/api/v1/tree/node/999?dry_run=true")
    assert dry.status_code == 404


def test_restore_with_invalid_snapshot(client: TestClient):
    # Try to restore with invalid snapshot
    res = client.post("/api/v1/tree/subtree/restore", json={"snapshot": {"invalid": "data"}})
    assert res.status_code == 400


def test_restore_with_missing_parent(client: TestClient):
    # Create a snapshot with a parent that doesn't exist
    snap = {
        "origin": {"id": 1, "parent_id": 999, "depth": 1, "slot": 1, "label": "test"},
        "nodes": [{"id": 1, "parent_id": 999, "depth": 1, "slot": 1, "label": "test"}],
    }
    res = client.post("/api/v1/tree/subtree/restore", json={"snapshot": snap})
    assert res.status_code == 404


def test_restore_violates_five_children_limit(client: TestClient):
    # Create root and 5 children
    r = client.post("/api/v1/tree/roots", json={"label": "Root A"})
    assert r.status_code == 201
    rid = r.json()["id"]
    put = client.put(
        "/api/v1/tree/children",
        json={
            "parent_id": rid,
            "children": [
                {"label": "x1"},
                {"label": "x2"},
                {"label": "x3"},
                {"label": "x4"},
                {"label": "x5"},
            ],
        },
    )
    assert put.status_code == 200

    # Create another root with a child to delete
    r2 = client.post("/api/v1/tree/roots", json={"label": "Root B"})
    assert r2.status_code == 201
    rid2 = r2.json()["id"]
    put2 = client.put(
        "/api/v1/tree/children", json={"parent_id": rid2, "children": [{"label": "y"}]}
    )
    assert put2.status_code == 200

    # Get the child from root B
    kids = client.get(f"/api/v1/tree/children?parent_id={rid2}").json()["items"]
    kid_id = kids[0]["id"]

    # Delete the child and get snapshot
    dry = client.delete(f"/api/v1/tree/node/{kid_id}?dry_run=true")
    assert dry.status_code == 200
    snap = dry.json()["snapshot"]
    do = client.delete(f"/api/v1/tree/node/{kid_id}?dry_run=false")
    assert do.status_code == 200

    # Modify the snapshot to try to restore under root A (which already has 5 children)
    # We need to change the parent_id in the snapshot to point to root A
    snap["origin"]["parent_id"] = rid
    res = client.post("/api/v1/tree/subtree/restore", json={"snapshot": snap})
    assert res.status_code == 422
