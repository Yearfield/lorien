#!/usr/bin/env python3
"""Test stats lists functionality."""

import pytest
import sqlite3
from api.db import get_conn, ensure_schema


def test_list_roots():
    """Test listing root nodes."""
    conn = get_conn()
    ensure_schema(conn)
    
    # Clean slate
    conn.execute("DELETE FROM nodes")
    
    # Create test data: multiple roots
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, 0, 'Root1', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 0, 'Root2', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 0, 'Root3', 0, NULL)")
    
    # Create some children (should not appear in roots)
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (4, 1, 'Child1', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (5, 2, 'Child2', 1, 1)")
    
    # Test listing roots
    roots = conn.execute("SELECT id, label, depth FROM nodes WHERE parent_id = 0 ORDER BY id").fetchall()
    
    assert len(roots) == 3
    assert roots[0] == (1, 'Root1', 0)
    assert roots[1] == (2, 'Root2', 0)
    assert roots[2] == (3, 'Root3', 0)


def test_list_leaves():
    """Test listing leaf nodes."""
    conn = get_conn()
    ensure_schema(conn)
    
    # Clean slate
    conn.execute("DELETE FROM nodes")
    
    # Create test data: tree structure
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, 0, 'Root', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Child1', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 1, 'Child2', 1, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (4, 2, 'Grandchild1', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (5, 2, 'Grandchild2', 2, 2)")
    
    # Test listing leaves (nodes with no children)
    leaves = conn.execute("""
        SELECT n.id, n.label, n.depth 
        FROM nodes n 
        LEFT JOIN nodes c ON c.parent_id = n.id 
        WHERE c.id IS NULL 
        ORDER BY n.id
    """).fetchall()
    
    assert len(leaves) == 3  # Child2, Grandchild1, Grandchild2
    assert (3, 'Child2', 1) in leaves
    assert (4, 'Grandchild1', 2) in leaves
    assert (5, 'Grandchild2', 2) in leaves


def test_list_complete_paths():
    """Test listing complete paths (depth 5)."""
    conn = get_conn()
    ensure_schema(conn)
    
    # Clean slate
    conn.execute("DELETE FROM nodes")
    
    # Create test data: complete path (depth 5)
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, 0, 'Root', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Level1', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 2, 'Level2', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (4, 3, 'Level3', 3, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (5, 4, 'Level4', 4, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (6, 5, 'Level5', 5, 1)")
    
    # Create incomplete path (depth 3)
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (7, 0, 'Root2', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (8, 7, 'Level1', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (9, 8, 'Level2', 2, 1)")
    
    # Test listing complete paths
    complete_paths = conn.execute("SELECT id, label, depth FROM nodes WHERE depth = 5 ORDER BY id").fetchall()
    
    assert len(complete_paths) == 1
    assert complete_paths[0] == (6, 'Level5', 5)


def test_list_incomplete_parents():
    """Test listing incomplete parents."""
    conn = get_conn()
    ensure_schema(conn)
    
    # Clean slate
    conn.execute("DELETE FROM nodes")
    
    # Create test data: complete parent (5 children)
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, 0, 'Complete', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Child1', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 1, 'Child2', 1, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (4, 1, 'Child3', 1, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (5, 1, 'Child4', 1, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (6, 1, 'Child5', 1, 5)")
    
    # Create incomplete parent (3 children)
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (7, 0, 'Incomplete', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (8, 7, 'Child1', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (9, 7, 'Child2', 1, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (10, 7, 'Child3', 1, 3)")
    
    # Test listing incomplete parents
    incomplete_parents = conn.execute("""
        SELECT n.id, n.label, n.depth, COUNT(c.id) as child_count
        FROM nodes n
        LEFT JOIN nodes c ON c.parent_id = n.id
        WHERE n.depth < 5
        GROUP BY n.id, n.label, n.depth
        HAVING COUNT(c.id) < 5
        ORDER BY n.id
    """).fetchall()
    
    assert len(incomplete_parents) == 1
    assert incomplete_parents[0] == (7, 'Incomplete', 0, 3)


def test_stats_lists_pagination():
    """Test pagination for stats lists."""
    conn = get_conn()
    ensure_schema(conn)
    
    # Clean slate
    conn.execute("DELETE FROM nodes")
    
    # Create many root nodes
    for i in range(25):
        conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (?, 0, ?, 0, NULL)", 
                    (i + 1, f'Root{i + 1}'))
    
    # Test pagination: first page
    page1 = conn.execute("SELECT id, label FROM nodes WHERE parent_id = 0 ORDER BY id LIMIT 10 OFFSET 0").fetchall()
    assert len(page1) == 10
    assert page1[0] == (1, 'Root1')
    assert page1[9] == (10, 'Root10')
    
    # Test pagination: second page
    page2 = conn.execute("SELECT id, label FROM nodes WHERE parent_id = 0 ORDER BY id LIMIT 10 OFFSET 10").fetchall()
    assert len(page2) == 10
    assert page2[0] == (11, 'Root11')
    assert page2[9] == (20, 'Root20')
    
    # Test pagination: last page
    page3 = conn.execute("SELECT id, label FROM nodes WHERE parent_id = 0 ORDER BY id LIMIT 10 OFFSET 20").fetchall()
    assert len(page3) == 5
    assert page3[0] == (21, 'Root21')
    assert page3[4] == (25, 'Root25')


def test_stats_lists_search():
    """Test search functionality for stats lists."""
    conn = get_conn()
    ensure_schema(conn)
    
    # Clean slate
    conn.execute("DELETE FROM nodes")
    
    # Create test data with searchable labels
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, 0, 'Apple Root', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 0, 'Banana Root', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 0, 'Apple Tree', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (4, 0, 'Orange Root', 0, NULL)")
    
    # Test search for "Apple"
    apple_results = conn.execute("""
        SELECT id, label FROM nodes 
        WHERE parent_id = 0 AND label LIKE ? 
        ORDER BY id
    """, ('%Apple%',)).fetchall()
    
    assert len(apple_results) == 2
    assert apple_results[0] == (1, 'Apple Root')
    assert apple_results[1] == (3, 'Apple Tree')
    
    # Test search for "Root"
    root_results = conn.execute("""
        SELECT id, label FROM nodes 
        WHERE parent_id = 0 AND label LIKE ? 
        ORDER BY id
    """, ('%Root%',)).fetchall()
    
    assert len(root_results) == 3
    assert root_results[0] == (1, 'Apple Root')
    assert root_results[1] == (2, 'Banana Root')
    assert root_results[2] == (4, 'Orange Root')


if __name__ == '__main__':
    pytest.main([__file__])
