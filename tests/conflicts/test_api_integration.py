"""
Test API integration with the conflicts engine.
"""
import pytest
import sqlite3
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


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


def test_conflicts_endpoint_with_variant_sets(client, conn):
    """Test the conflicts endpoint with variant sets."""
    # Create test data with variant sets
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
    
    # Test the conflicts endpoint
    response = client.get("/api/v1/tree/conflicts/conflicts?limit=50")
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    
    # Should find conflicts with variant sets
    assert len(data["items"]) >= 1
    for item in data["items"]:
        assert item["child_count"] == 5
        assert item["duplicate_parents"] >= 2
        assert item["variant_sets"] >= 2
        assert "signatures" in item


def test_conflicts_endpoint_identical_sets_excluded(client, conn):
    """Test that identical sets are excluded."""
    # Create test data with identical sets
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
    
    # Test the conflicts endpoint
    response = client.get("/api/v1/tree/conflicts/conflicts?limit=50")
    assert response.status_code == 200
    
    data = response.json()
    # Should not find conflicts (identical sets)
    assert len(data["items"]) == 0


def test_group_endpoint_integration(client, conn):
    """Test the group endpoint integration."""
    # Create test data
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (1, NULL, 'Root', 0, NULL)")
    
    # Parent 1
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (2, 1, 'Hypertension', 1, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (3, 2, 'Headache', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (4, 2, 'Nausea', 2, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (5, 2, 'Dizziness', 2, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (6, 2, 'Chest Pain', 2, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (7, 2, 'Shortness of Breath', 2, 5)")
    
    # Parent 2 with different children
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (8, 1, 'Hypertension', 1, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (9, 8, 'Headache', 2, 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (10, 8, 'Nausea', 2, 2)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (11, 8, 'Dizziness', 2, 3)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (12, 8, 'Chest Pain', 2, 4)")
    conn.execute("INSERT INTO nodes (id, parent_id, label, depth, slot) VALUES (13, 8, 'Fatigue', 2, 5)")
    
    conn.commit()
    
    # Test the group endpoint
    response = client.get("/api/v1/tree/conflicts/group?node_id=2")
    assert response.status_code == 200
    
    data = response.json()
    assert "group" in data
    assert "children" in data
    assert "summary" in data
    
    # Should return group with both parents
    assert len(data["group"]) == 2
    group_ids = [item["id"] for item in data["group"]]
    assert 2 in group_ids
    assert 8 in group_ids
    
    # Should return all children from both parents
    assert len(data["children"]) == 10
    children_labels = [child["label"] for child in data["children"]]
    assert "Headache" in children_labels
    assert "Nausea" in children_labels
    assert "Dizziness" in children_labels
    assert "Chest Pain" in children_labels
    assert "Shortness of Breath" in children_labels
    assert "Fatigue" in children_labels
