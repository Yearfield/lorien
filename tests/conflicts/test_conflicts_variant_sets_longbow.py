"""
Conflicts tests for variant sets in EngineLongBow.
"""

import os
import sqlite3
import pytest
from api.db.migrate import apply_migrations
from api.main import app
from fastapi.testclient import TestClient


def test_variant_sets_across_duplicate_parents(tmp_path, monkeypatch):
    """Test that conflicts are detected for duplicate parents with variant 5-sets"""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    
    # Build two different parents with same depth+label via contextual parentage
    # Root1 -> Alpha -> (A,B,C,D,E)
    # Root2 -> Alpha -> (A,B,C,D,X)
    cur = conn.cursor()
    cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (NULL,0,NULL,'Root1')")
    r1 = cur.lastrowid
    cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (NULL,0,NULL,'Root2')")
    r2 = cur.lastrowid
    
    def mk(parent, labs):
        cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,1,NULL,'Alpha')", (parent,))
        p = cur.lastrowid
        slot = 0
        for lab in labs:
            slot += 1
            cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,2,?,?)", (p, slot, lab))
        return p
    
    p1 = mk(r1, ["A","B","C","D","E"])
    p2 = mk(r2, ["A","B","C","D","X"])
    conn.commit()
    conn.close()

    client = TestClient(app)
    resp = client.get("/api/v1/tree/conflicts/conflicts?limit=50")
    assert resp.status_code == 200, resp.text
    
    items = resp.json()["items"]
    labels = [(it["label"], it["variant_sets"], it["duplicate_parents"]) for it in items]
    
    # Should find Alpha with variant_sets >= 2 and duplicate_parents >= 2
    assert any(lbl == "Alpha" and vs >= 2 and dp >= 2 for (lbl, vs, dp) in labels), f"Alpha conflict not found: {labels}"


def test_no_conflict_identical_sets(tmp_path, monkeypatch):
    """Test that identical 5-sets don't create conflicts"""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    
    # Build two parents with identical 5-sets
    # Root1 -> Beta -> (K,L,M,N,O)
    # Root2 -> Beta -> (K,L,M,N,O)
    cur = conn.cursor()
    cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (NULL,0,NULL,'Root1')")
    r1 = cur.lastrowid
    cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (NULL,0,NULL,'Root2')")
    r2 = cur.lastrowid
    
    def mk(parent, labs):
        cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,1,NULL,'Beta')", (parent,))
        p = cur.lastrowid
        slot = 0
        for lab in labs:
            slot += 1
            cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,2,?,?)", (p, slot, lab))
        return p
    
    p1 = mk(r1, ["K","L","M","N","O"])
    p2 = mk(r2, ["K","L","M","N","O"])
    conn.commit()
    conn.close()

    client = TestClient(app)
    resp = client.get("/api/v1/tree/conflicts/conflicts?limit=50")
    assert resp.status_code == 200, resp.text
    
    items = resp.json()["items"]
    labels = [it["label"] for it in items]
    
    # Should NOT find Beta (identical sets)
    assert "Beta" not in labels, f"Beta should not be flagged as conflict: {labels}"


def test_conflict_group_endpoint(tmp_path, monkeypatch):
    """Test that conflict group endpoint returns correct data"""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    
    # Build conflict scenario
    cur = conn.cursor()
    cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (NULL,0,NULL,'Root1')")
    r1 = cur.lastrowid
    cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (NULL,0,NULL,'Root2')")
    r2 = cur.lastrowid
    
    def mk(parent, labs):
        cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,1,NULL,'Alpha')", (parent,))
        p = cur.lastrowid
        slot = 0
        for lab in labs:
            slot += 1
            cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,2,?,?)", (p, slot, lab))
        return p
    
    p1 = mk(r1, ["A","B","C","D","E"])
    p2 = mk(r2, ["A","B","C","D","X"])
    conn.commit()
    conn.close()

    client = TestClient(app)
    
    # Get group for one of the Alpha nodes
    resp = client.get(f"/api/v1/tree/conflicts/group?node_id={p1}")
    assert resp.status_code == 200, resp.text
    
    group_data = resp.json()
    
    # Should have 2 parents in group
    assert len(group_data["group"]) == 2, f"Expected 2 parents in group, got {len(group_data['group'])}"
    
    # Should have children from both parents
    children = group_data["children"]
    assert len(children) == 10, f"Expected 10 children total, got {len(children)}"
    
    # Should have unique children count
    unique_children = group_data["summary"]["unique_children"]
    assert unique_children > 0, "Should have unique children"


def test_normalization_in_conflicts(tmp_path, monkeypatch):
    """Test that normalization works correctly in conflicts detection"""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    
    # Build parents with normalized labels that should be treated as same
    cur = conn.cursor()
    cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (NULL,0,NULL,'Root1')")
    r1 = cur.lastrowid
    cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (NULL,0,NULL,'Root2')")
    r2 = cur.lastrowid
    
    def mk(parent, label, labs):
        cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,1,NULL,?)", (parent, label))
        p = cur.lastrowid
        slot = 0
        for lab in labs:
            slot += 1
            cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,2,?,?)", (p, slot, lab))
        return p
    
    # Create parents with different case/whitespace that should normalize to same
    p1 = mk(r1, "Alpha", ["A","B","C","D","E"])
    p2 = mk(r2, "ALPHA", ["A","B","C","D","X"])  # Different case
    
    conn.commit()
    conn.close()

    client = TestClient(app)
    resp = client.get("/api/v1/tree/conflicts/conflicts?limit=50")
    assert resp.status_code == 200, resp.text
    
    items = resp.json()["items"]
    labels = [(it["label"], it["variant_sets"], it["duplicate_parents"]) for it in items]
    
    # Should find conflict despite different case (normalization)
    assert any(lbl in ["Alpha", "ALPHA"] and vs >= 2 and dp >= 2 for (lbl, vs, dp) in labels), f"Normalized conflict not found: {labels}"
