"""
Test group endpoint coherence with variant sets.
"""
import pytest
import sqlite3
from api.repositories.tree_repo import get_conflict_group


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


def test_group_endpoint_returns_union_of_children(conn):
    """Test that group endpoint returns union of children from all parents in group."""
    # Create test data: two parents with different child sets
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
    
    # Test group endpoint for parent 1
    result = get_conflict_group(conn, parent_id=2, label="Hypertension")
    
    # Should return group with both parents
    assert len(result['group']) == 2
    group_ids = [item['id'] for item in result['group']]
    assert 2 in group_ids
    assert 8 in group_ids
    
    # Should return union of children (all unique children from both parents)
    children_labels = [child['label'] for child in result['children']]
    unique_labels = set(children_labels)
    
    # Should have 6 unique children: 5 from parent 1 + 1 unique from parent 2
    assert len(unique_labels) == 6
    assert 'Headache' in unique_labels
    assert 'Nausea' in unique_labels
    assert 'Dizziness' in unique_labels
    assert 'Chest Pain' in unique_labels
    assert 'Shortness of Breath' in unique_labels
    assert 'Fatigue' in unique_labels
    
    # Summary should reflect the union
    assert result['summary']['unique_children'] == 6
    assert result['summary']['total_children'] == 10  # 5 + 5


def test_group_endpoint_single_parent(conn):
    """Test group endpoint with single parent (no duplicates)."""
    # Create test data: single parent
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, NULL, 'Root', 0, NULL)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Single', 1, 1)")
    for i in range(5):
        conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (?, 2, ?, 2, ?)", 
                    (3 + i, f'Child{i + 1}', i + 1))
    
    conn.commit()
    
    # Test group endpoint
    result = get_conflict_group(conn, parent_id=2, label="Single")
    
    # Should return group with single parent
    assert len(result['group']) == 1
    assert result['group'][0]['id'] == 2
    
    # Should return children from single parent
    assert len(result['children']) == 5
    children_labels = [child['label'] for child in result['children']]
    assert set(children_labels) == {'Child1', 'Child2', 'Child3', 'Child4', 'Child5'}
    
    # Summary should reflect single parent
    assert result['summary']['unique_children'] == 5
    assert result['summary']['total_children'] == 5


def test_group_endpoint_identical_sets(conn):
    """Test group endpoint with identical child sets."""
    # Create test data: two parents with identical sets
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, NULL, 'Root', 0, NULL)")
    
    # Parent 1
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Identical', 1, 1)")
    for i in range(5):
        conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (?, 2, ?, 2, ?)", 
                    (3 + i, f'Child{i + 1}', i + 1))
    
    # Parent 2 with identical set
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (8, 1, 'Identical', 1, 2)")
    for i in range(5):
        conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (?, 8, ?, 2, ?)", 
                    (9 + i, f'Child{i + 1}', i + 1))
    
    conn.commit()
    
    # Test group endpoint
    result = get_conflict_group(conn, parent_id=2, label="Identical")
    
    # Should return group with both parents
    assert len(result['group']) == 2
    group_ids = [item['id'] for item in result['group']]
    assert 2 in group_ids
    assert 8 in group_ids
    
    # Should return union of children (but they're identical, so same 5 children)
    children_labels = [child['label'] for child in result['children']]
    unique_labels = set(children_labels)
    
    # Should have 5 unique children (duplicates are deduplicated)
    assert len(unique_labels) == 5
    assert unique_labels == {'Child1', 'Child2', 'Child3', 'Child4', 'Child5'}
    
    # Summary should reflect the union
    assert result['summary']['unique_children'] == 5
    assert result['summary']['total_children'] == 10  # 5 + 5, but unique is 5


def test_group_endpoint_multiple_variants(conn):
    """Test group endpoint with multiple variant sets."""
    # Create test data: 3 parents with different sets
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, NULL, 'Root', 0, NULL)")
    
    # Parent 1: Set A
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Fever', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 2, 'High Temp', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (4, 2, 'Chills', 2, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (5, 2, 'Sweating', 2, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (6, 2, 'Headache', 2, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (7, 2, 'Fatigue', 2, 5)")
    
    # Parent 2: Set B
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (8, 1, 'Fever', 1, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (9, 8, 'High Temp', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (10, 8, 'Chills', 2, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (11, 8, 'Sweating', 2, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (12, 8, 'Headache', 2, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (13, 8, 'Nausea', 2, 5)")
    
    # Parent 3: Set C
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (14, 1, 'Fever', 1, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (15, 14, 'High Temp', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (16, 14, 'Chills', 2, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (17, 14, 'Sweating', 2, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (18, 14, 'Headache', 2, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (19, 14, 'Dizziness', 2, 5)")
    
    conn.commit()
    
    # Test group endpoint for parent 1
    result = get_conflict_group(conn, parent_id=2, label="Fever")
    
    # Should return group with all 3 parents
    assert len(result['group']) == 3
    group_ids = [item['id'] for item in result['group']]
    assert 2 in group_ids
    assert 8 in group_ids
    assert 14 in group_ids
    
    # Should return union of children from all 3 parents
    children_labels = [child['label'] for child in result['children']]
    unique_labels = set(children_labels)
    
    # Should have 7 unique children: 4 common + 3 unique
    assert len(unique_labels) == 7
    assert 'High Temp' in unique_labels
    assert 'Chills' in unique_labels
    assert 'Sweating' in unique_labels
    assert 'Headache' in unique_labels
    assert 'Fatigue' in unique_labels  # From parent 1
    assert 'Nausea' in unique_labels   # From parent 2
    assert 'Dizziness' in unique_labels  # From parent 3
    
    # Summary should reflect the union
    assert result['summary']['unique_children'] == 7
    assert result['summary']['total_children'] == 15  # 5 + 5 + 5
