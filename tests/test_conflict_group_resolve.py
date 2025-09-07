#!/usr/bin/env python3
"""Test conflict group resolution functionality."""

import pytest
import sqlite3
from api.db import get_conn, ensure_schema, tx
from api.repositories.tree_repo import get_conflict_group, resolve_conflict_group
from api.repositories.validators import ensure_unique_5


def test_ensure_unique_5():
    """Test the ensure_unique_5 validator."""
    # Valid case
    result = ensure_unique_5(['a', 'b', 'c', 'd', 'e'])
    assert result == ['a', 'b', 'c', 'd', 'e']
    
    # Too few
    with pytest.raises(ValueError, match="must_choose_five"):
        ensure_unique_5(['a', 'b', 'c'])
    
    # Too many
    with pytest.raises(ValueError, match="must_choose_five"):
        ensure_unique_5(['a', 'b', 'c', 'd', 'e', 'f'])
    
    # Duplicates
    with pytest.raises(ValueError, match="duplicate_labels"):
        ensure_unique_5(['a', 'b', 'c', 'd', 'a'])
    
    # Empty strings filtered out
    with pytest.raises(ValueError, match="must_choose_five"):
        ensure_unique_5(['a', 'b', 'c', '', 'd'])
    
    # Whitespace trimmed
    result = ensure_unique_5([' a ', ' b ', ' c ', ' d ', ' e '])
    assert result == ['a', 'b', 'c', 'd', 'e']


def test_get_conflict_group():
    """Test getting conflict group data."""
    conn = get_conn()
    ensure_schema(conn)
    
    # Clean slate
    conn.execute("DELETE FROM nodes")
    
    # Create test data: parent with duplicate children
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, 0, 'Root', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Child1', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 1, 'Child2', 1, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (4, 1, 'Child3', 1, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (5, 1, 'Child4', 1, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (6, 1, 'Child5', 1, 5)")
    
    # Create duplicate parent
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (7, 0, 'Root', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (8, 7, 'Child1', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (9, 7, 'Child2', 1, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (10, 7, 'Child3', 1, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (11, 7, 'Child4', 1, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (12, 7, 'Child5', 1, 5)")
    
    # Test getting conflict group
    result = get_conflict_group(conn, 0, 'Root')
    
    assert 'group' in result
    assert 'children' in result
    assert 'summary' in result
    
    # Should have 2 nodes in group
    assert len(result['group']) == 2
    assert result['group'][0]['id'] == 1
    assert result['group'][1]['id'] == 7
    
    # Should have 10 children total
    assert len(result['children']) == 10
    assert result['summary']['total_children'] == 10
    assert result['summary']['unique_children'] == 5  # 5 unique labels


def test_resolve_conflict_group():
    """Test resolving conflict group."""
    conn = get_conn()
    ensure_schema(conn)
    
    # Clean slate
    conn.execute("DELETE FROM nodes")
    
    # Create test data: parent with duplicate children
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, 0, 'Root', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Child1', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 1, 'Child2', 1, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (4, 1, 'Child3', 1, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (5, 1, 'Child4', 1, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (6, 1, 'Child5', 1, 5)")
    
    # Create duplicate parent
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (7, 0, 'Root', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (8, 7, 'Child1', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (9, 7, 'Child2', 1, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (10, 7, 'Child3', 1, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (11, 7, 'Child4', 1, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (12, 7, 'Child5', 1, 5)")
    
    # Resolve conflict group - keep node 1, choose 5 children
    result = resolve_conflict_group(conn, 0, 'Root', 1, ['Child1', 'Child2', 'Child3', 'Child4', 'Child5'])
    
    assert result['ok'] is True
    assert result['moved_duplicates'] == 1
    assert result['kept'] == 1
    assert result['chosen'] == ['Child1', 'Child2', 'Child3', 'Child4', 'Child5']
    
    # Verify node 7 is deleted
    assert conn.execute("SELECT COUNT(*) FROM nodes WHERE id = 7").fetchone()[0] == 0
    
    # Verify node 1 has exactly 5 children
    children = conn.execute("SELECT id, slot, label FROM nodes WHERE parent_id = 1 ORDER BY slot").fetchall()
    assert len(children) == 5
    assert [c[1] for c in children] == [1, 2, 3, 4, 5]
    assert [c[2] for c in children] == ['Child1', 'Child2', 'Child3', 'Child4', 'Child5']


def test_resolve_conflict_group_invalid_keep_id():
    """Test resolving conflict group with invalid keep_id."""
    conn = get_conn()
    ensure_schema(conn)
    
    # Clean slate
    conn.execute("DELETE FROM nodes")
    
    # Create test data
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, 0, 'Root', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Child1', 1, 1)")
    
    # Try to resolve with keep_id not in group
    with pytest.raises(LookupError, match="keep_id_not_in_group"):
        resolve_conflict_group(conn, 0, 'Root', 999, ['Child1', 'Child2', 'Child3', 'Child4', 'Child5'])


if __name__ == '__main__':
    pytest.main([__file__])
