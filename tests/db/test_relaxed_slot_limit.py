"""
Test relaxed slot limit - can store more than 5 children under one parent.
"""

import sqlite3
import os
import pytest
from api.db.migrate import apply_migrations


def test_can_store_more_than_five_children(tmp_path, monkeypatch):
    """Test that we can store 6+ children under one parent after migration 011."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))  # should apply through 011

    conn = sqlite3.connect(str(db))
    cur = conn.cursor()

    # root
    cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (NULL,0,NULL,'Root')")
    root_id = cur.lastrowid
    # parent at depth=1
    cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,?,?,?)", (root_id,1,1,'Alpha'))
    parent_id = cur.lastrowid

    # 6 children (slots 1..6)
    for i, lab in enumerate(["A","B","C","D","E","F"], start=1):
        cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,?,?,?)",
                    (parent_id, 2, i, lab))
    conn.commit()

    # verify we actually stored 6 and slots are 1..6
    cur.execute("SELECT slot, label FROM nodes WHERE parent_id=? ORDER BY slot ASC", (parent_id,))
    rows = cur.fetchall()
    conn.close()

    assert len(rows) == 6
    assert [r[0] for r in rows] == [1,2,3,4,5,6]
    assert [r[1] for r in rows] == ["A","B","C","D","E","F"]


def test_slot_uniqueness_per_parent_still_enforced(tmp_path, monkeypatch):
    """Test that (parent_id, slot) uniqueness is still enforced."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))

    conn = sqlite3.connect(str(db))
    cur = conn.cursor()

    # root
    cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (NULL,0,NULL,'Root')")
    root_id = cur.lastrowid
    # parent at depth=1
    cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,?,?,?)", (root_id,1,1,'Alpha'))
    parent_id = cur.lastrowid

    # Insert first child with slot 1
    cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,?,?,?)",
                (parent_id, 2, 1, "A"))
    
    # Try to insert second child with same slot 1 - should fail
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,?,?,?)",
                    (parent_id, 2, 1, "B"))
    
    conn.close()


def test_root_nodes_still_have_null_slots(tmp_path, monkeypatch):
    """Test that root nodes still have NULL slots as required."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))

    conn = sqlite3.connect(str(db))
    cur = conn.cursor()

    # Root with NULL slot should work
    cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (NULL,0,NULL,'Root')")
    
    # Root with non-NULL slot should fail
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (NULL,0,1,'BadRoot')")
    
    conn.close()


def test_non_root_nodes_must_have_slot_ge_1(tmp_path, monkeypatch):
    """Test that non-root nodes must have slot >= 1."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))

    conn = sqlite3.connect(str(db))
    cur = conn.cursor()

    # root
    cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (NULL,0,NULL,'Root')")
    root_id = cur.lastrowid

    # Child with slot 1 should work
    cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,?,?,?)",
                (root_id, 1, 1, "Child1"))
    
    # Child with slot 0 should fail
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,?,?,?)",
                    (root_id, 1, 0, "BadChild"))
    
    # Child with slot NULL should fail
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,?,?,?)",
                    (root_id, 1, None, "BadChild2"))
    
    conn.close()
