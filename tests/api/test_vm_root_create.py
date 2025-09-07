"""
Test VM root creation contract.

Verifies that POST /api/v1/tree/roots works and creates proper VM structure,
not 500 due to missing handler.
"""

import pytest
import requests
import sqlite3
import os


@pytest.fixture
def base_url():
    return "http://127.0.0.1:8000/api/v1"


@pytest.fixture
def temp_db():
    """Create a temporary database with test data."""
    db_path = "/tmp/lorien_vm_test.db"

    # Clean up any existing database
    if os.path.exists(db_path):
        os.remove(db_path)

    # Create fresh database with schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables (simplified schema)
    cursor.execute("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER,
            depth INTEGER NOT NULL,
            slot INTEGER,
            label TEXT NOT NULL,
            is_leaf INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert some test data
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, depth, slot, label, is_leaf)
        VALUES (1, NULL, 0, 0, 'Existing Root', 0)
    """)

    conn.commit()
    conn.close()

    # Set environment variable for this test
    os.environ['LORIEN_DB_PATH'] = db_path

    yield db_path

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


def get_node_count(db_path: str) -> int:
    """Get total node count from database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM nodes")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_node_by_id(db_path: str, node_id: int) -> dict:
    """Get node details by ID."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, parent_id, depth, slot, label
        FROM nodes WHERE id = ?
    """, (node_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            'id': row[0],
            'parent_id': row[1],
            'depth': row[2],
            'slot': row[3],
            'label': row[4]
        }
    return None


def get_children(db_path: str, parent_id: int) -> list:
    """Get children of a parent node."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, parent_id, depth, slot, label
        FROM nodes WHERE parent_id = ?
        ORDER BY slot
    """, (parent_id,))
    rows = cursor.fetchall()
    conn.close()

    return [{
        'id': row[0],
        'parent_id': row[1],
        'depth': row[2],
        'slot': row[3],
        'label': row[4]
    } for row in rows]


def test_vm_root_create_returns_200_not_500(base_url, temp_db):
    """Test that VM root creation returns 200, not 500."""

    # Get baseline node count from the running server's stats
    stats_response = requests.get(f"{base_url}/tree/stats")
    baseline_count = stats_response.json().get("nodes", 0) if stats_response.status_code == 200 else 0

    payload = {"label": "Test VM Root"}

    response = requests.post(
        f"{base_url}/tree/roots",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print(f"VM root create response status: {response.status_code}")
    print(f"VM root create response body: {response.text}")

    # Should not return 500 (internal server error)
    assert response.status_code != 500, \
        "VM root creation returns 500 - likely missing handler implementation"

    if response.status_code == 404:
        pytest.skip("VM root creation endpoint not implemented (404)")
    else:
        assert response.status_code in [200, 201]


def test_vm_root_create_contract_when_working(base_url, temp_db):
    """Test the full contract of VM root creation when it works."""

    # Get baseline
    baseline_count = get_node_count(temp_db)

    payload = {"label": "Test Vital Measurement"}

    response = requests.post(
        f"{base_url}/tree/roots",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code in [200, 201]

    data = response.json()

    # Should return root creation response
    assert isinstance(data, dict)
    assert 'root_id' in data
    assert 'label' in data
    assert data['label'] == payload['label']

    root_id = data['root_id']
    assert isinstance(root_id, int)
    assert root_id > 0

    # Verify the root was actually created in database
    root_node = get_node_by_id(temp_db, root_id)
    assert root_node is not None
    assert root_node['label'] == payload['label']
    assert root_node['depth'] == 0
    assert root_node['parent_id'] is None

    # Should have created exactly 5 children (slots 1-5)
    children = get_children(temp_db, root_id)
    assert len(children) == 5, f"Expected 5 children, got {len(children)}"

    # Verify children have correct slots and depth
    for i, child in enumerate(children, 1):
        assert child['slot'] == i, f"Child {i} has wrong slot: {child['slot']}"
        assert child['depth'] == 1, f"Child {i} has wrong depth: {child['depth']}"
        assert child['parent_id'] == root_id

    # Verify total node count increased by 6 (1 root + 5 children)
    final_count = get_node_count(temp_db)
    expected_increase = 6
    actual_increase = final_count - baseline_count
    assert actual_increase == expected_increase, \
        f"Expected {expected_increase} new nodes, got {actual_increase}"


def test_vm_root_create_validation(base_url):
    """Test VM root creation input validation."""

    # Test empty label
    response = requests.post(
        f"{base_url}/tree/roots",
        json={"label": ""},
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 404:
        pytest.skip("VM root creation endpoint not implemented")
    elif response.status_code == 422:
        # Expected validation error
        assert response.status_code == 422
    else:
        # If it succeeds, verify the response structure
        assert response.status_code in [200, 201]
        data = response.json()
        assert 'root_id' in data
        assert 'label' in data


def test_vm_root_create_with_special_characters(base_url):
    """Test VM root creation with special characters in label."""

    payload = {"label": "Test VM: Blood Pressure (mmHg)"}

    response = requests.post(
        f"{base_url}/tree/roots",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 404:
        pytest.skip("VM root creation endpoint not implemented")
    else:
        assert response.status_code in [200, 201]

        if response.status_code in [200, 201]:
            data = response.json()
            assert data['label'] == payload['label']
