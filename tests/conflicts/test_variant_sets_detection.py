"""
Test variant-sets detection using the conflicts engine.
"""
import pytest
import sqlite3
from api.core.conflicts_engine import norm, signature, find_variant_set_conflicts, get_conflict_group_data


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


def test_norm_function():
    """Test string normalization."""
    # Basic normalization
    assert norm("  Hello  World  ") == "hello world"
    assert norm("HELLO") == "hello"
    assert norm("") == ""
    assert norm(None) == ""
    
    # Unicode normalization
    assert norm("café") == "café"  # Should handle Unicode properly
    assert norm("  Multiple   Spaces  ") == "multiple spaces"
    
    # Case folding
    assert norm("Chest Pain") == "chest pain"
    assert norm("CHEST PAIN") == "chest pain"


def test_signature_function():
    """Test signature creation."""
    # Basic signature
    assert signature(["A", "B", "C", "D", "E"]) == "a|b|c|d|e"
    
    # Order independence
    assert signature(["E", "D", "C", "B", "A"]) == "a|b|c|d|e"
    
    # Duplicate handling
    assert signature(["A", "A", "B", "C", "D"]) == "a|b|c|d"
    
    # Empty/None handling
    assert signature(["A", "", "B", None, "C"]) == "a|b|c"
    
    # Whitespace handling
    assert signature(["  A  ", " B ", " C ", " D ", " E "]) == "a|b|c|d|e"


def test_find_variant_set_conflicts_basic(conn):
    """Test basic variant set detection."""
    # Create test data: two parents with different child sets
    parents = [
        {"id": 1, "depth": 0, "label": "Hypertension"},
        {"id": 2, "depth": 0, "label": "Hypertension"},
    ]
    
    children = [
        # Parent 1 children
        {"parent_id": 1, "slot": 1, "label": "Headache"},
        {"parent_id": 1, "slot": 2, "label": "Nausea"},
        {"parent_id": 1, "slot": 3, "label": "Dizziness"},
        {"parent_id": 1, "slot": 4, "label": "Chest Pain"},
        {"parent_id": 1, "slot": 5, "label": "Shortness of Breath"},
        
        # Parent 2 children (different from parent 1)
        {"parent_id": 2, "slot": 1, "label": "Headache"},
        {"parent_id": 2, "slot": 2, "label": "Nausea"},
        {"parent_id": 2, "slot": 3, "label": "Dizziness"},
        {"parent_id": 2, "slot": 4, "label": "Chest Pain"},
        {"parent_id": 2, "slot": 5, "label": "Fatigue"},  # Different from parent 1
    ]
    
    conflicts = find_variant_set_conflicts(parents, children)
    
    # Should find conflicts with variant sets
    assert len(conflicts) == 2  # Both parents should be returned
    for conflict in conflicts:
        assert conflict["child_count"] == 5
        assert conflict["duplicate_parents"] == 2
        assert conflict["variant_sets"] == 2
        assert "signatures" in conflict
        assert len(conflict["signatures"]) == 2


def test_find_variant_set_conflicts_identical_sets_excluded(conn):
    """Test that identical sets are excluded."""
    parents = [
        {"id": 1, "depth": 0, "label": "Diabetes"},
        {"id": 2, "depth": 0, "label": "Diabetes"},
    ]
    
    children = [
        # Both parents have identical children
        {"parent_id": 1, "slot": 1, "label": "Thirst"},
        {"parent_id": 1, "slot": 2, "label": "Hunger"},
        {"parent_id": 1, "slot": 3, "label": "Fatigue"},
        {"parent_id": 1, "slot": 4, "label": "Blurred Vision"},
        {"parent_id": 1, "slot": 5, "label": "Slow Healing"},
        
        {"parent_id": 2, "slot": 1, "label": "Thirst"},
        {"parent_id": 2, "slot": 2, "label": "Hunger"},
        {"parent_id": 2, "slot": 3, "label": "Fatigue"},
        {"parent_id": 2, "slot": 4, "label": "Blurred Vision"},
        {"parent_id": 2, "slot": 5, "label": "Slow Healing"},
    ]
    
    conflicts = find_variant_set_conflicts(parents, children)
    
    # Should not find conflicts (identical sets)
    assert len(conflicts) == 0


def test_find_variant_set_conflicts_underfilled_excluded(conn):
    """Test that under-filled parents are excluded."""
    parents = [
        {"id": 1, "depth": 0, "label": "Underfilled"},
    ]
    
    children = [
        # Only 3 children, not 5
        {"parent_id": 1, "slot": 1, "label": "Child1"},
        {"parent_id": 1, "slot": 2, "label": "Child2"},
        {"parent_id": 1, "slot": 3, "label": "Child3"},
    ]
    
    conflicts = find_variant_set_conflicts(parents, children)
    
    # Should not find conflicts (under-filled)
    assert len(conflicts) == 0


def test_find_variant_set_conflicts_case_insensitive(conn):
    """Test that case differences are normalized."""
    parents = [
        {"id": 1, "depth": 0, "label": "Chest Pain"},
        {"id": 2, "depth": 0, "label": "chest pain"},  # Different case
    ]
    
    children = [
        # Parent 1 children
        {"parent_id": 1, "slot": 1, "label": "Headache"},
        {"parent_id": 1, "slot": 2, "label": "Nausea"},
        {"parent_id": 1, "slot": 3, "label": "Dizziness"},
        {"parent_id": 1, "slot": 4, "label": "Chest Pain"},
        {"parent_id": 1, "slot": 5, "label": "Shortness of Breath"},
        
        # Parent 2 children (different from parent 1)
        {"parent_id": 2, "slot": 1, "label": "Headache"},
        {"parent_id": 2, "slot": 2, "label": "Nausea"},
        {"parent_id": 2, "slot": 3, "label": "Dizziness"},
        {"parent_id": 2, "slot": 4, "label": "Chest Pain"},
        {"parent_id": 2, "slot": 5, "label": "Fatigue"},  # Different from parent 1
    ]
    
    conflicts = find_variant_set_conflicts(parents, children)
    
    # Should find conflicts (same normalized label, different children)
    assert len(conflicts) == 2
    for conflict in conflicts:
        assert conflict["child_count"] == 5
        assert conflict["duplicate_parents"] == 2
        assert conflict["variant_sets"] == 2


def test_find_variant_set_conflicts_whitespace_normalization(conn):
    """Test that whitespace differences are normalized."""
    parents = [
        {"id": 1, "depth": 0, "label": "Abdominal Pain"},
        {"id": 2, "depth": 0, "label": "  Abdominal  Pain  "},  # Different whitespace
    ]
    
    children = [
        # Parent 1 children
        {"parent_id": 1, "slot": 1, "label": "Headache"},
        {"parent_id": 1, "slot": 2, "label": "Nausea"},
        {"parent_id": 1, "slot": 3, "label": "Dizziness"},
        {"parent_id": 1, "slot": 4, "label": "Chest Pain"},
        {"parent_id": 1, "slot": 5, "label": "Shortness of Breath"},
        
        # Parent 2 children (different from parent 1)
        {"parent_id": 2, "slot": 1, "label": "Headache"},
        {"parent_id": 2, "slot": 2, "label": "Nausea"},
        {"parent_id": 2, "slot": 3, "label": "Dizziness"},
        {"parent_id": 2, "slot": 4, "label": "Chest Pain"},
        {"parent_id": 2, "slot": 5, "label": "Fatigue"},  # Different from parent 1
    ]
    
    conflicts = find_variant_set_conflicts(parents, children)
    
    # Should find conflicts (same normalized label, different children)
    assert len(conflicts) == 2
    for conflict in conflicts:
        assert conflict["child_count"] == 5
        assert conflict["duplicate_parents"] == 2
        assert conflict["variant_sets"] == 2


def test_get_conflict_group_data(conn):
    """Test conflict group data retrieval."""
    parents = [
        {"id": 1, "depth": 0, "label": "Hypertension"},
        {"id": 2, "depth": 0, "label": "Hypertension"},
    ]
    
    children = [
        # Parent 1 children
        {"id": 10, "parent_id": 1, "slot": 1, "label": "Headache"},
        {"id": 11, "parent_id": 1, "slot": 2, "label": "Nausea"},
        {"id": 12, "parent_id": 1, "slot": 3, "label": "Dizziness"},
        {"id": 13, "parent_id": 1, "slot": 4, "label": "Chest Pain"},
        {"id": 14, "parent_id": 1, "slot": 5, "label": "Shortness of Breath"},
        
        # Parent 2 children
        {"id": 20, "parent_id": 2, "slot": 1, "label": "Headache"},
        {"id": 21, "parent_id": 2, "slot": 2, "label": "Nausea"},
        {"id": 22, "parent_id": 2, "slot": 3, "label": "Dizziness"},
        {"id": 23, "parent_id": 2, "slot": 4, "label": "Chest Pain"},
        {"id": 24, "parent_id": 2, "slot": 5, "label": "Fatigue"},
    ]
    
    group_data = get_conflict_group_data(parents, children, 1, "Hypertension")
    
    # Should return group with both parents
    assert len(group_data["group"]) == 2
    group_ids = [item["id"] for item in group_data["group"]]
    assert 1 in group_ids
    assert 2 in group_ids
    
    # Should return all children from both parents
    assert len(group_data["children"]) == 10
    children_labels = [child["label"] for child in group_data["children"]]
    assert "Headache" in children_labels
    assert "Nausea" in children_labels
    assert "Dizziness" in children_labels
    assert "Chest Pain" in children_labels
    assert "Shortness of Breath" in children_labels
    assert "Fatigue" in children_labels
    
    # Summary should reflect the union
    assert group_data["summary"]["unique_children"] == 6  # 5 common + 1 unique
    assert group_data["summary"]["total_children"] == 10  # 5 + 5
