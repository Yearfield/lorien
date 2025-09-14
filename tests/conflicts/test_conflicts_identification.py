"""
Test conflicts identification with variant sets.
"""
import pytest
import sqlite3
from api.repositories.tree_repo import detect_conflicts, children_signature


@pytest.fixture
def conn():
    """Create a test database connection."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
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


def test_children_signature():
    """Test children signature computation."""
    # Test basic functionality
    assert children_signature(["A", "B", "C", "D", "E"]) == "a|b|c|d|e"
    
    # Test order independence
    assert children_signature(["E", "D", "C", "B", "A"]) == "a|b|c|d|e"
    
    # Test duplicate handling
    assert children_signature(["A", "A", "B", "C", "D"]) == "a|b|c|d"
    
    # Test whitespace handling
    assert children_signature([" A ", " B ", " C ", " D ", " E "]) == "a|b|c|d|e"
    
    # Test empty/null handling
    assert children_signature(["A", "", "B", None, "C"]) == "a|b|c"


def test_conflicts_with_variant_sets(conn):
    """Test that conflicts with different child sets are included."""
    # Create test data: two parents with different 5-child sets
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, NULL, 'Root', 0, NULL)")
    
    # Parent 1 with set A
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Hypertension', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 2, 'Headache', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (4, 2, 'Nausea', 2, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (5, 2, 'Dizziness', 2, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (6, 2, 'Chest Pain', 2, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (7, 2, 'Shortness of Breath', 2, 5)")
    
    # Parent 2 with set B (different from A)
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (8, 1, 'Hypertension', 1, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (9, 8, 'Headache', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (10, 8, 'Nausea', 2, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (11, 8, 'Dizziness', 2, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (12, 8, 'Chest Pain', 2, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (13, 8, 'Fatigue', 2, 5)")  # Different from set A
    
    conn.commit()
    
    # Test with variant sets required
    result = detect_conflicts(conn, limit=50, offset=0, require_variant_sets=True)
    
    # Should return conflicts with variant sets
    assert len(result['items']) >= 1
    for item in result['items']:
        assert item['child_count'] == 5
        assert item['duplicate_parents'] > 0
        assert item['variant_sets'] >= 2


def test_conflicts_with_identical_sets_excluded(conn):
    """Test that duplicate parents with identical 5-sets are excluded."""
    # Create test data: two parents with identical 5-child sets
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, NULL, 'Root', 0, NULL)")
    
    # Parent 1 with set A
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Diabetes', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 2, 'Thirst', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (4, 2, 'Hunger', 2, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (5, 2, 'Fatigue', 2, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (6, 2, 'Blurred Vision', 2, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (7, 2, 'Slow Healing', 2, 5)")
    
    # Parent 2 with identical set A
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (8, 1, 'Diabetes', 1, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (9, 8, 'Thirst', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (10, 8, 'Hunger', 2, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (11, 8, 'Fatigue', 2, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (12, 8, 'Blurred Vision', 2, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (13, 8, 'Slow Healing', 2, 5)")
    
    conn.commit()
    
    # Test with variant sets required
    result = detect_conflicts(conn, limit=50, offset=0, require_variant_sets=True)
    
    # Should exclude identical sets
    assert len(result['items']) == 0


def test_underfilled_parents_excluded(conn):
    """Test that under-filled parents are excluded."""
    # Create test data: under-filled parent
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, NULL, 'Root', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Underfilled', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 2, 'Child1', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (4, 2, 'Child2', 2, 2)")
    # Only 2 children, not 5
    
    conn.commit()
    
    # Test with variant sets required
    result = detect_conflicts(conn, limit=50, offset=0, require_variant_sets=True)
    
    # Should exclude under-filled parents
    assert len(result['items']) == 0


def test_singleton_parents_excluded(conn):
    """Test that singleton parents (no duplicates) are excluded."""
    # Create test data: single parent with 5 children
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, NULL, 'Root', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Singleton', 1, 1)")
    for i in range(5):
        conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (?, 2, ?, 2, ?)", 
                    (3 + i, f'Child{i + 1}', i + 1))
    
    conn.commit()
    
    # Test with variant sets required
    result = detect_conflicts(conn, limit=50, offset=0, require_variant_sets=True)
    
    # Should exclude singleton parents
    assert len(result['items']) == 0


def test_complex_variant_scenario(conn):
    """Test complex scenario with multiple variant sets."""
    # Create test data: 3 parents with different sets
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, NULL, 'Root', 0, NULL)")
    
    # Parent 1: Set A
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Fever', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 2, 'High Temp', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (4, 2, 'Chills', 2, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (5, 2, 'Sweating', 2, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (6, 2, 'Headache', 2, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (7, 2, 'Fatigue', 2, 5)")
    
    # Parent 2: Set B (different from A)
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (8, 1, 'Fever', 1, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (9, 8, 'High Temp', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (10, 8, 'Chills', 2, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (11, 8, 'Sweating', 2, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (12, 8, 'Headache', 2, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (13, 8, 'Nausea', 2, 5)")  # Different
    
    # Parent 3: Set C (different from A and B)
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (14, 1, 'Fever', 1, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (15, 14, 'High Temp', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (16, 14, 'Chills', 2, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (17, 14, 'Sweating', 2, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (18, 14, 'Headache', 2, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (19, 14, 'Dizziness', 2, 5)")  # Different
    
    conn.commit()
    
    # Test with variant sets required
    result = detect_conflicts(conn, limit=50, offset=0, require_variant_sets=True)
    
    # Should return conflicts with 3 variant sets
    assert len(result['items']) >= 1
    for item in result['items']:
        assert item['child_count'] == 5
        assert item['duplicate_parents'] > 0
        assert item['variant_sets'] >= 3  # A, B, C are all different


def test_no_variant_sets_parameter_disabled(conn):
    """Test that disabling require_variant_sets shows all conflicts."""
    # Create test data with identical sets
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, NULL, 'Root', 0, NULL)")
    
    # Two parents with identical sets
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Identical', 1, 1)")
    for i in range(5):
        conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (?, 2, ?, 2, ?)", 
                    (3 + i, f'Child{i + 1}', i + 1))
    
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (8, 1, 'Identical', 1, 2)")
    for i in range(5):
        conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (?, 8, ?, 2, ?)", 
                    (9 + i, f'Child{i + 1}', i + 1))
    
    conn.commit()
    
    # Test with variant sets NOT required
    result = detect_conflicts(conn, limit=50, offset=0, require_variant_sets=False)
    
    # Should include identical sets when variant requirement is disabled
    assert len(result['items']) >= 1
    # Filter to only parent nodes (those with child_count > 0)
    parent_items = [item for item in result['items'] if item['child_count'] > 0]
    assert len(parent_items) >= 1
    for item in parent_items:
        assert item['child_count'] == 5
        assert item['duplicate_parents'] > 0
