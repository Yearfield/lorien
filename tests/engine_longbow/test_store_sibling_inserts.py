import os
import sqlite3
import pytest
from api.db.migrate import apply_migrations
from Engines.EngineLongBow.store import _get_or_create_node


def test_siblings_under_same_parent_are_all_inserted(tmp_path, monkeypatch):
    """Test that multiple siblings under the same parent are all inserted correctly."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))

    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")

    try:
        # Build: RootX -> ParentA -> G1..G7
        root = _get_or_create_node(conn, None, 0, "RootX")
        parent = _get_or_create_node(conn, root, 1, "ParentA")
        for i in range(1, 8):
            _get_or_create_node(conn, parent, 2, f"G{i}")

        cur = conn.execute("SELECT slot, label FROM nodes WHERE parent_id=? ORDER BY slot", (parent,))
        rows = cur.fetchall()

        assert len(rows) == 7
        assert [r[0] for r in rows] == [1, 2, 3, 4, 5, 6, 7]
        assert [r[1] for r in rows] == ["G1", "G2", "G3", "G4", "G5", "G6", "G7"]
    finally:
        conn.close()


def test_siblings_with_different_cases_are_deduplicated(tmp_path, monkeypatch):
    """Test that siblings with different cases are deduplicated by normalization."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))

    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")

    try:
        # Build: RootX -> ParentA -> "Alpha", "alpha", "ALPHA"
        root = _get_or_create_node(conn, None, 0, "RootX")
        parent = _get_or_create_node(conn, root, 1, "ParentA")
        
        # These should all be treated as the same node due to normalization
        node1 = _get_or_create_node(conn, parent, 2, "Alpha")
        node2 = _get_or_create_node(conn, parent, 2, "alpha")
        node3 = _get_or_create_node(conn, parent, 2, "ALPHA")

        # All should return the same node ID
        assert node1 == node2 == node3

        cur = conn.execute("SELECT COUNT(*) FROM nodes WHERE parent_id=? AND depth=2", (parent,))
        count = cur.fetchone()[0]

        # Should only have one child due to deduplication
        assert count == 1
    finally:
        conn.close()


def test_siblings_with_whitespace_differences_are_deduplicated(tmp_path, monkeypatch):
    """Test that siblings with different whitespace are deduplicated by normalization."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))

    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")

    try:
        # Build: RootX -> ParentA -> "Beta", " Beta ", "  Beta  "
        root = _get_or_create_node(conn, None, 0, "RootX")
        parent = _get_or_create_node(conn, root, 1, "ParentA")
        
        # These should all be treated as the same node due to normalization
        node1 = _get_or_create_node(conn, parent, 2, "Beta")
        node2 = _get_or_create_node(conn, parent, 2, " Beta ")
        node3 = _get_or_create_node(conn, parent, 2, "  Beta  ")

        # All should return the same node ID
        assert node1 == node2 == node3

        cur = conn.execute("SELECT COUNT(*) FROM nodes WHERE parent_id=? AND depth=2", (parent,))
        count = cur.fetchone()[0]

        # Should only have one child due to deduplication
        assert count == 1
    finally:
        conn.close()
