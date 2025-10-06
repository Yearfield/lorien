import os
import json
import pytest
from fastapi.testclient import TestClient
from api.app import app  # or api.app_vm_core: adjust if needed
from api.db.migrate import apply_migrations

def _children_from_response(data):
    """
    Accept either a raw list of children or an object containing 'children'.
    Each child should have at least: id (or node_id), label, slot (optional).
    """
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "children" in data and isinstance(data["children"], list):
            return data["children"]
        # Some implementations might use 'items'
        if "items" in data and isinstance(data["items"], list):
            return data["items"]
    raise AssertionError(f"Unrecognized children payload shape: {data}")

def _get_child_id_by_label(client: TestClient, parent_id: int, label: str) -> int:
    r = client.get("/api/v1/tree/children", params={"parent_id": parent_id})
    assert r.status_code == 200, r.text
    kids = _children_from_response(r.json())
    for k in kids:
        lab = (k.get("label") or k.get("name") or "").strip().lower()
        if lab == label.lower():
            return k.get("id") or k.get("node_id")
    raise AssertionError(f"Child with label '{label}' not found under parent {parent_id}. Got: {kids}")

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    os.environ["LORIEN_DB_PATH"] = str(db_path)
    apply_migrations(str(db_path))
    yield str(db_path)

@pytest.fixture
def test_data(temp_db):
    """
    Create 3 different roots, each with a depth-1 parent labeled 'hypertension',
    but with divergent children so the conflicts scan detects a conflict.
    """
    client = TestClient(app)

    # Root 1
    r = client.post("/api/v1/tree/roots", json={"label": "Vital Measurement A"})
    assert r.status_code == 201, r.text
    root1 = r.json()["id"]
    # add 'hypertension' under root1
    r = client.put("/api/v1/tree/children", json={
        "parent_id": root1,
        "children": [{"label": "hypertension"}]
    })
    assert r.status_code == 200, r.text
    parent1 = _get_child_id_by_label(client, root1, "hypertension")
    # children: [headache, nausea, vomiting]
    r = client.put("/api/v1/tree/children", json={
        "parent_id": parent1,
        "children": [{"label": "headache"}, {"label": "nausea"}, {"label": "vomiting"}]
    })
    assert r.status_code == 200, r.text

    # Root 2
    r = client.post("/api/v1/tree/roots", json={"label": "Vital Measurement B"})
    assert r.status_code == 201, r.text
    root2 = r.json()["id"]
    r = client.put("/api/v1/tree/children", json={
        "parent_id": root2,
        "children": [{"label": "hypertension"}]
    })
    assert r.status_code == 200, r.text
    parent2 = _get_child_id_by_label(client, root2, "hypertension")
    # children: [headache, chest pain, myalgia]
    r = client.put("/api/v1/tree/children", json={
        "parent_id": parent2,
        "children": [{"label": "headache"}, {"label": "chest pain"}, {"label": "myalgia"}]
    })
    assert r.status_code == 200, r.text

    # Root 3
    r = client.post("/api/v1/tree/roots", json={"label": "Vital Measurement C"})
    assert r.status_code == 201, r.text
    root3 = r.json()["id"]
    r = client.put("/api/v1/tree/children", json={
        "parent_id": root3,
        "children": [{"label": "hypertension"}]
    })
    assert r.status_code == 200, r.text
    parent3 = _get_child_id_by_label(client, root3, "hypertension")
    # children: [dizziness, nausea, vomiting]
    r = client.put("/api/v1/tree/children", json={
        "parent_id": parent3,
        "children": [{"label": "dizziness"}, {"label": "nausea"}, {"label": "vomiting"}]
    })
    assert r.status_code == 200, r.text

    # Root 4 with a deep hypertension parent at depth 6 (max depth)
    r = client.post("/api/v1/tree/roots", json={"label": "Vital Measurement D"})
    assert r.status_code == 201, r.text
    root4 = r.json()["id"]
    current_parent = root4
    for label in ["level1", "level2", "level3", "level4", "level5"]:
        r = client.put("/api/v1/tree/children", json={
            "parent_id": current_parent,
            "children": [{"label": label}]
        })
        assert r.status_code == 200, r.text
        current_parent = _get_child_id_by_label(client, current_parent, label)

    r = client.put("/api/v1/tree/children", json={
        "parent_id": current_parent,
        "children": [{"label": "hypertension"}]
    })
    assert r.status_code == 200, r.text
    deep_parent = _get_child_id_by_label(client, current_parent, "hypertension")

    return {
        "client": client,
        "parents": [parent1, parent2, parent3],
        "deep_parent": deep_parent,
    }

def test_scan_conflicts(test_data):
    client = test_data["client"]
    r = client.get("/api/v1/conflicts/scan")
    assert r.status_code == 200, r.text
    items = r.json()
    # expect a single conflict group for 'hypertension' (no depth at top level)
    grp = next((g for g in items if g["label"] == "hypertension"), None)
    assert grp is not None, f"No conflict group found. Got: {items}"
    assert grp["occurrences"] >= 3
    assert len(grp["union_children"]) > 5  # union: headache, chest pain, myalgia, dizziness, nausea, vomiting = 6
    # ensure each occurrence captured with depth info
    assert len(grp["parents"]) >= 3
    for parent in grp["parents"]:
        assert "depth" in parent
        assert "parent_id" in parent
        assert "children" in parent
    assert "skipped_parents" in grp
    assert len(grp["skipped_parents"]) >= 1
    for skipped in grp["skipped_parents"]:
        assert skipped.get("reason") == "max_depth"

def test_resolve_conflict_dry_run(test_data):
    client = test_data["client"]
    payload = {
        "label": "hypertension",
        "selected_children": ["headache","chest pain","nausea","vomiting","myalgia"],
        "dry_run": True
    }
    r = client.post("/api/v1/conflicts/resolve", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["updated_parents"] >= 3
    assert body["children_per_parent"] == 5
    assert len(body.get("skipped_parents", [])) >= 1
    assert isinstance(body["parents"], list) and body["parents"]
    assert "skipped_parents" in body
    assert len(body["skipped_parents"]) >= 1
    for skipped in body["skipped_parents"]:
        assert skipped.get("reason") == "max_depth"

def test_resolve_conflict_too_many_children(test_data):
    client = test_data["client"]
    payload = {
        "label": "hypertension",
        "selected_children": ["a","b","c","d","e","f"],  # 6 -> should 422
        "dry_run": False
    }
    r = client.post("/api/v1/conflicts/resolve", json=payload)
    assert r.status_code == 422, r.text
    # body may be list(detail) or object; just check msg/type presence
    text = r.text.lower()
    assert "max_children" in text or "too many children" in text

def test_resolve_conflict_apply(test_data):
    client = test_data["client"]
    # Apply canonical set (≤5)
    payload = {
        "label": "hypertension",
        "selected_children": ["headache","chest pain","nausea","vomiting","myalgia"],
        "dry_run": False
    }
    r = client.post("/api/v1/conflicts/resolve", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["updated_parents"] >= 3
    assert len(body.get("skipped_parents", [])) >= 1
    # After apply, scan should show no conflict for this group
    r = client.get("/api/v1/conflicts/scan")
    assert r.status_code == 200
    items = r.json()
    grp = next((g for g in items if g["label"] == "hypertension"), None)
    assert grp is None, f"Conflict still present after apply: {items}"

def test_resolve_conflict_case_insensitive(test_data):
    client = test_data["client"]
    payload = {
        "label": "HyPerTension",
        "selected_children": ["HEADACHE","CHEST PAIN","NAUSEA","VOMITING","MYALGIA"],
        "dry_run": True
    }
    r = client.post("/api/v1/conflicts/resolve", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["updated_parents"] >= 3
    assert body["children_per_parent"] == 5
    assert len(body.get("skipped_parents", [])) >= 1


def test_resolve_conflict_all_parents_max_depth(temp_db):
    client = TestClient(app)

    r = client.post("/api/v1/tree/roots", json={"label": "Vital Measurement Z"})
    assert r.status_code == 201, r.text
    root = r.json()["id"]

    current_parent = root
    for label in ["d1", "d2", "d3", "d4", "d5"]:
        r = client.put("/api/v1/tree/children", json={
            "parent_id": current_parent,
            "children": [{"label": label}]
        })
        assert r.status_code == 200, r.text
        current_parent = _get_child_id_by_label(client, current_parent, label)

    max_depth_label = "Max Depth Only"
    r = client.put("/api/v1/tree/children", json={
        "parent_id": current_parent,
        "children": [{"label": max_depth_label}]
    })
    assert r.status_code == 200, r.text

    r = client.post("/api/v1/conflicts/resolve", json={
        "label": max_depth_label,
        "selected_children": ["new child"],
        "dry_run": False,
    })
    assert r.status_code == 422, r.text
    assert "all parents at max depth" in r.text
