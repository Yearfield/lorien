from starlette.testclient import TestClient

from api.app import app
from api.db.migrate import apply_migrations


def test_clone_candidates(tmp_path, monkeypatch):
    """Test finding clone candidates by label."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Create a tree with some nodes that have children
    csv = """D0,D1,D2,D3,D4,D5,D6,Notes
Root1,Headache,Type1,,,,,
Root1,Headache,Type2,,,,,
Root2,Fever,High,,,,,
Root2,Fever,Low,,,,,"""

    r = c.post("/api/v1/import?mode=replace", files={"file": ("tree.csv", csv, "text/csv")})
    assert r.status_code in (200, 201)

    # Find clone candidates for "Headache" (should find the one under Root1)
    r = c.get("/api/v1/tree/clone/candidates?label=Headache")
    assert r.status_code == 200
    candidates = r.json()["items"]
    assert len(candidates) == 1
    assert candidates[0]["label"].lower() == "headache"
    assert candidates[0]["child_count"] == 2  # Has Type1 and Type2 children

    # Find clone candidates for "Fever"
    r = c.get("/api/v1/tree/clone/candidates?label=Fever")
    assert r.status_code == 200
    candidates = r.json()["items"]
    assert len(candidates) == 1
    assert candidates[0]["label"].lower() == "fever"
    assert candidates[0]["child_count"] == 2  # Has High and Low children

    # Find clone candidates for non-existent label
    r = c.get("/api/v1/tree/clone/candidates?label=NonExistent")
    assert r.status_code == 200
    candidates = r.json()["items"]
    assert len(candidates) == 0


def test_clone_subtree(tmp_path, monkeypatch):
    """Test cloning a subtree from one location to another."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Create a source tree with a subtree to clone
    csv = """D0,D1,D2,D3,D4,D5,D6,Notes
Root1,Headache,Type1,Severe,,,,,
Root1,Headache,Type1,Mild,,,,,
Root1,Headache,Type2,Chronic,,,,,
Root2,Fever,,,,,,"""

    r = c.post("/api/v1/import?mode=replace", files={"file": ("tree.csv", csv, "text/csv")})
    assert r.status_code in (200, 201)

    # Get the source and destination IDs
    roots = c.get("/api/v1/tree/roots").json()["items"]
    root1_id = roots[0]["id"]
    root2_id = roots[1]["id"]

    # Find the Headache node under Root1 (source)
    children = c.get(f"/api/v1/tree/children?parent_id={root1_id}").json()["items"]
    headache_id = None
    for child in children:
        if child["label"].lower() == "headache":
            headache_id = child["id"]
            break
    assert headache_id is not None

    # Clone the Headache subtree to Root2
    r = c.post("/api/v1/tree/clone", json={"source_id": headache_id, "dest_parent_id": root2_id})
    assert r.status_code == 200
    result = r.json()
    assert result["ok"] is True
    assert result["created"] == 6  # Headache + Type1 + Type2 + Severe + Mild + Chronic (6 nodes)

    # Verify the clone was successful
    # Root2 should now have both Fever (original) and Headache (cloned)
    children = c.get(f"/api/v1/tree/children?parent_id={root2_id}").json()["items"]
    assert len(children) == 2

    # Find the cloned Headache child
    cloned_headache_id = None
    for child in children:
        if child["label"].lower() == "headache":
            cloned_headache_id = child["id"]
            break
    assert cloned_headache_id is not None, "Cloned Headache child not found"
    sub_children = c.get(f"/api/v1/tree/children?parent_id={cloned_headache_id}").json()["items"]
    assert len(sub_children) == 2
    labels = [child["label"].lower() for child in sub_children]
    assert "type1" in labels
    assert "type2" in labels

    # Type1 should have Severe and Mild children
    type1_child = next(child for child in sub_children if child["label"].lower() == "type1")
    type1_children = c.get(f"/api/v1/tree/children?parent_id={type1_child['id']}").json()["items"]
    assert len(type1_children) == 2
    type1_labels = [child["label"].lower() for child in type1_children]
    assert "severe" in type1_labels
    assert "mild" in type1_labels


def test_clone_subtree_not_found(tmp_path, monkeypatch):
    """Test cloning a non-existent subtree."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Create a simple tree
    csv = """D0,D1,D2,D3,D4,D5,D6,Notes
Root,Child,,,,,,"""

    r = c.post("/api/v1/import?mode=replace", files={"file": ("tree.csv", csv, "text/csv")})
    assert r.status_code in (200, 201)

    # Try to clone a non-existent node
    r = c.post(
        "/api/v1/tree/clone",
        json={"source_id": 999, "dest_parent_id": 1},  # Non-existent ID
    )
    assert r.status_code == 404
