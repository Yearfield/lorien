"""
Test conflicts list filtering functionality.
"""
import pytest
import sqlite3
from api.repositories.tree_repo import detect_conflicts


@pytest.fixture
def conn():
    """Create a test database connection."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access
    conn.execute("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER,
            label TEXT NOT NULL,
            depth INTEGER NOT NULL,
            slot INTEGER,
            FOREIGN KEY (parent_id) REFERENCES nodes(id)
        )
    """)
    conn.execute("""
        CREATE TABLE outcomes (
            node_id INTEGER PRIMARY KEY,
            diagnostic_triage TEXT,
            actions TEXT,
            FOREIGN KEY (node_id) REFERENCES nodes(id)
        )
    """)
    return conn


def test_conflicts_list_default_filters(conn):
    """Test that default filters only show true merge conflicts (exactly 5 children, duplicate parents)."""
    # Create test data: parent with exactly 5 children and duplicate parents
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, NULL, 'Root', 0, NULL)")
    
    # Create duplicate parent nodes (same parent_id and label)
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Parent1', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 1, 'Parent1', 1, 2)")  # Duplicate parent
    
    # Add 5 children to the first parent
    for i in range(5):
        conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (?, 2, ?, 2, ?)", 
                    (4 + i, f'Child{i + 1}', i + 1))
    
    # Create underfilled parent (should be filtered out)
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (9, 1, 'Parent2', 1, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (10, 9, 'Child6', 2, 1)")
    
    # Create overfilled parent (should be filtered out)
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (11, 1, 'Parent3', 1, 4)")
    for i in range(6):  # 6 children (overfilled)
        conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (?, 11, ?, 2, ?)", 
                    (12 + i, f'Child{7 + i}', i + 1))
    
    conn.commit()
    
    # Test with default filters (only_exact_five=True, only_duplicate_parents=True)
    result = detect_conflicts(conn, limit=50, offset=0, only_exact_five=True, only_duplicate_parents=True)
    
    # Should only return the parent with exactly 5 children and duplicate parents
    assert len(result['items']) == 1
    item = result['items'][0]
    assert item['parent_id'] == 2  # Parent1
    assert item['child_count'] == 5
    assert item['duplicate_parents'] > 0


def test_conflicts_list_no_filters(conn):
    """Test that disabling filters shows all conflicts."""
    # Create test data
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, NULL, 'Root', 0, NULL)")
    
    # Underfilled parent
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Underfilled', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 2, 'Child1', 2, 1)")
    
    # Overfilled parent
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (4, 1, 'Overfilled', 1, 2)")
    for i in range(6):  # 6 children
        conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (?, 4, ?, 2, ?)", 
                    (5 + i, f'Child{i + 1}', i + 1))
    
    conn.commit()
    
    # Test with no filters
    result = detect_conflicts(conn, limit=50, offset=0, only_exact_five=False, only_duplicate_parents=False)
    
    # Should return underfilled and overfilled parents (and root with children)
    assert len(result['items']) >= 2
    parent_ids = [item['parent_id'] for item in result['items']]
    assert 2 in parent_ids  # Underfilled
    assert 4 in parent_ids  # Overfilled


def test_conflicts_list_only_exact_five(conn):
    """Test filtering by only_exact_five=True."""
    # Create test data
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, NULL, 'Root', 0, NULL)")
    
    # Parent with exactly 5 children (no duplicates)
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'ExactFive', 1, 1)")
    for i in range(5):
        conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (?, 2, ?, 2, ?)", 
                    (3 + i, f'Child{i + 1}', i + 1))
    
    # Underfilled parent
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (8, 1, 'Underfilled', 1, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (9, 8, 'Child6', 2, 1)")
    
    conn.commit()
    
    # Test with only_exact_five=True
    result = detect_conflicts(conn, limit=50, offset=0, only_exact_five=True, only_duplicate_parents=False)
    
    # Should only return the parent with exactly 5 children
    assert len(result['items']) == 1
    item = result['items'][0]
    assert item['parent_id'] == 2
    assert item['child_count'] == 5


def test_conflicts_list_only_duplicate_parents(conn):
    """Test filtering by only_duplicate_parents=True."""
    # Create test data
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, NULL, 'Root', 0, NULL)")
    
    # Parent with duplicate parents but not exactly 5 children
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Duplicate', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 1, 'Duplicate', 1, 2)")  # Duplicate parent
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (4, 2, 'Child1', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (5, 2, 'Child2', 2, 2)")
    
    # Parent with exactly 5 children but no duplicates
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (6, 1, 'NoDuplicate', 1, 3)")
    for i in range(5):
        conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (?, 6, ?, 2, ?)", 
                    (7 + i, f'Child{i + 3}', i + 1))
    
    conn.commit()
    
    # Test with only_duplicate_parents=True
    result = detect_conflicts(conn, limit=50, offset=0, only_exact_five=False, only_duplicate_parents=True)
    
    # Should only return the parent with duplicate parents
    assert len(result['items']) == 1
    item = result['items'][0]
    assert item['parent_id'] == 2
    assert item['duplicate_parents'] > 0


def test_conflicts_list_empty_result(conn):
    """Test that filtering returns empty result when no conflicts match criteria."""
    # Create test data with no conflicts (no duplicate parents)
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, NULL, 'Root', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Parent', 1, 1)")
    for i in range(5):
        conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (?, 2, ?, 2, ?)", 
                    (3 + i, f'Child{i + 1}', i + 1))
    
    conn.commit()
    
    # Test with strict filters
    result = detect_conflicts(conn, limit=50, offset=0, only_exact_five=True, only_duplicate_parents=True)
    
    # Should return empty result (no duplicate parents)
    assert len(result['items']) == 0
    assert result['total'] == 0
