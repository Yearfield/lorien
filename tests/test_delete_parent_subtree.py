#!/usr/bin/env python3
"""Test delete parent subtree functionality."""

import pytest
import sqlite3
from api.db import get_conn, ensure_schema, tx


def test_delete_parent_subtree():
    """Test deleting a parent and its subtree."""
    conn = get_conn()
    ensure_schema(conn)
    
    # Clean slate
    conn.execute("DELETE FROM nodes")
    
    # Create test data: parent with children
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, 0, 'Root', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Child1', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 1, 'Child2', 1, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (4, 1, 'Child3', 1, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (5, 1, 'Child4', 1, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (6, 1, 'Child5', 1, 5)")
    
    # Create grandchild
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (7, 2, 'Grandchild1', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (8, 2, 'Grandchild2', 2, 2)")
    
    # Verify initial state
    assert conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] == 8
    
    # Delete parent 1 (should delete entire subtree)
    with tx(conn):
        conn.execute("DELETE FROM nodes WHERE id = ?", (1,))
    
    # Verify parent and all children are deleted
    assert conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] == 0
    
    # Verify specific nodes are gone
    assert conn.execute("SELECT COUNT(*) FROM nodes WHERE id = 1").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM nodes WHERE id = 2").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM nodes WHERE id = 7").fetchone()[0] == 0


def test_delete_parent_subtree_with_foreign_keys():
    """Test deleting a parent with foreign key constraints."""
    conn = get_conn()
    ensure_schema(conn)
    
    # Clean slate
    conn.execute("DELETE FROM nodes")
    
    # Create test data: parent with children
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, 0, 'Root', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Child1', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 1, 'Child2', 1, 2)")
    
    # Verify foreign key constraints are enabled
    fk_check = conn.execute("PRAGMA foreign_keys").fetchone()[0]
    assert fk_check == 1
    
    # Delete parent 1 (should cascade delete children)
    with tx(conn):
        conn.execute("DELETE FROM nodes WHERE id = ?", (1,))
    
    # Verify parent and all children are deleted
    assert conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] == 0


def test_delete_nonexistent_parent():
    """Test deleting a nonexistent parent."""
    conn = get_conn()
    ensure_schema(conn)
    
    # Clean slate
    conn.execute("DELETE FROM nodes")
    
    # Try to delete nonexistent parent
    with tx(conn):
        conn.execute("DELETE FROM nodes WHERE id = ?", (999,))
    
    # Should not raise error, just delete nothing
    assert conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] == 0


def test_delete_parent_transaction_rollback():
    """Test that delete operation can be rolled back."""
    conn = get_conn()
    ensure_schema(conn)
    
    # Clean slate
    conn.execute("DELETE FROM nodes")
    
    # Create test data
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, 0, 'Root', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Child1', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 1, 'Child2', 1, 2)")
    
    # Verify initial state
    assert conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] == 3
    
    # Try to delete in transaction that fails
    try:
        with tx(conn):
            conn.execute("DELETE FROM nodes WHERE id = ?", (1,))
            # Simulate error
            raise Exception("Simulated error")
    except Exception:
        pass
    
    # Verify rollback - all nodes should still exist
    assert conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] == 3
    assert conn.execute("SELECT COUNT(*) FROM nodes WHERE id = 1").fetchone()[0] == 1


if __name__ == '__main__':
    pytest.main([__file__])
