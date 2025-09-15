"""
Unit tests for EngineLongBow contextual node creation.
"""

import os
import sqlite3
import pytest
from Engines.EngineLongBow.store import _get_or_create_node, apply_import
from api.db.migrate import apply_migrations


def test_contextual_nodes_are_distinct(tmp_path, monkeypatch):
    """Test that nodes with same label under different parents are distinct"""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    
    # Root A and root B at depth 0
    ra = _get_or_create_node(conn, None, 0, "RootA")
    rb = _get_or_create_node(conn, None, 0, "RootB")
    
    # Same label at depth 1 under different parents must be distinct nodes
    a1 = _get_or_create_node(conn, ra, 1, "Alpha")
    b1 = _get_or_create_node(conn, rb, 1, "Alpha")
    
    assert a1 != b1, "Nodes with same label under different parents should be distinct"
    
    # Verify they exist in database
    nodes = conn.execute("SELECT id, parent_id, label, depth FROM nodes WHERE label = 'Alpha'").fetchall()
    assert len(nodes) == 2, f"Expected 2 Alpha nodes, got {len(nodes)}"
    
    # Verify they have different parent_ids
    parent_ids = {node['parent_id'] for node in nodes}
    assert len(parent_ids) == 2, f"Expected 2 different parent_ids, got {parent_ids}"
    
    conn.close()


def test_contextual_deduplication_same_parent(tmp_path, monkeypatch):
    """Test that nodes with same label under same parent are deduplicated"""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    
    # Create root
    root = _get_or_create_node(conn, None, 0, "Root")
    
    # Create same label under same parent twice
    node1 = _get_or_create_node(conn, root, 1, "Alpha")
    node2 = _get_or_create_node(conn, root, 1, "Alpha")
    
    assert node1 == node2, "Same label under same parent should be deduplicated"
    
    # Verify only one node exists
    nodes = conn.execute("SELECT id, parent_id, label, depth FROM nodes WHERE label = 'Alpha'").fetchall()
    assert len(nodes) == 1, f"Expected 1 Alpha node, got {len(nodes)}"
    
    conn.close()


def test_slot_assignment_deterministic(tmp_path, monkeypatch):
    """Test that slots are assigned deterministically"""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    
    # Create root
    root = _get_or_create_node(conn, None, 0, "Root")
    
    # Create multiple children
    child1 = _get_or_create_node(conn, root, 1, "Child1")
    child2 = _get_or_create_node(conn, root, 1, "Child2")
    child3 = _get_or_create_node(conn, root, 1, "Child3")
    
    # Check slots are assigned in order
    nodes = conn.execute("SELECT id, label, slot FROM nodes WHERE parent_id = ? ORDER BY slot", (root,)).fetchall()
    assert len(nodes) == 3, f"Expected 3 children, got {len(nodes)}"
    
    slots = [node['slot'] for node in nodes]
    assert slots == [1, 2, 3], f"Expected slots [1, 2, 3], got {slots}"
    
    conn.close()


def test_apply_import_contextual_paths(tmp_path, monkeypatch):
    """Test that apply_import creates contextual nodes correctly"""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    
    # Create paths with two different contexts for same label
    paths = [
        ['Root1', 'Alpha', 'A'],
        ['Root1', 'Alpha', 'B'],
        ['Root2', 'Alpha', 'A'],
        ['Root2', 'Alpha', 'X'],  # Different from B
    ]
    
    # Import paths
    result = apply_import(paths, 'replace', str(db))
    
    # Check import result
    assert result.inserted_nodes > 0, "Should have inserted nodes"
    assert not result.preview, "Should not be preview mode"
    
    # Check database structure
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    
    # Should have 2 root nodes
    roots = conn.execute("SELECT id, label FROM nodes WHERE parent_id IS NULL").fetchall()
    assert len(roots) == 2, f"Expected 2 root nodes, got {len(roots)}"
    
    # Should have 2 Alpha nodes (one under each root)
    alpha_nodes = conn.execute("SELECT id, parent_id, label FROM nodes WHERE label = 'Alpha'").fetchall()
    assert len(alpha_nodes) == 2, f"Expected 2 Alpha nodes, got {len(alpha_nodes)}"
    
    # Should have different parent_ids for Alpha nodes
    alpha_parent_ids = {node['parent_id'] for node in alpha_nodes}
    assert len(alpha_parent_ids) == 2, f"Expected 2 different parent_ids for Alpha, got {alpha_parent_ids}"
    
    conn.close()


def test_normalization_contextual(tmp_path, monkeypatch):
    """Test that normalization works correctly in contextual node creation"""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    
    # Create root
    root = _get_or_create_node(conn, None, 0, "Root")
    
    # Create nodes with different case/whitespace that should normalize to same
    node1 = _get_or_create_node(conn, root, 1, "Alpha")
    node2 = _get_or_create_node(conn, root, 1, "ALPHA")
    node3 = _get_or_create_node(conn, root, 1, "  alpha  ")
    
    # All should be the same node (deduplicated by normalization)
    assert node1 == node2 == node3, "Normalized labels should be deduplicated"
    
    # Verify only one node exists
    nodes = conn.execute("SELECT id, label FROM nodes WHERE parent_id = ?", (root,)).fetchall()
    assert len(nodes) == 1, f"Expected 1 normalized node, got {len(nodes)}"
    assert nodes[0]['label'] == "Alpha", f"Expected label 'Alpha', got '{nodes[0]['label']}'"
    
    conn.close()
