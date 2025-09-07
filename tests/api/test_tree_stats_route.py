"""
Test tree stats route precedence and contract.

Route precedence bug: /api/v1/tree/stats should return stats, not 422
due to /tree/{parent_id} route taking precedence.
"""

import pytest
import requests
import sqlite3
from typing import Dict, Any


@pytest.fixture
def base_url():
    return "http://127.0.0.1:8000/api/v1"


@pytest.fixture
def temp_db():
    """Create a temporary database with test data."""
    db_path = "/tmp/lorien_stats_test.db"

    # Clean up any existing database
    import os
    if os.path.exists(db_path):
        os.remove(db_path)

    # Create fresh database
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
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert test data: 1 root, 2 children
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, depth, slot, label)
        VALUES (1, NULL, 0, NULL, 'Root Node')
    """)
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, depth, slot, label)
        VALUES (2, 1, 1, 1, 'Child 1')
    """)
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, depth, slot, label)
        VALUES (3, 1, 1, 2, 'Child 2')
    """)

    conn.commit()
    conn.close()

    # Set environment variable for this test
    import os
    os.environ['LORIEN_DB_PATH'] = db_path

    yield db_path

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


def test_tree_stats_route_returns_stats_not_422(base_url, temp_db):
    """Test that /tree/stats returns stats object, not 422 due to route precedence."""

    # Test /api/v1/tree/stats (should work)
    response = requests.get(f"{base_url}/tree/stats")

    # This should return 200 with stats, but may currently return 422
    # due to /tree/{parent_id} route taking precedence
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

    # Expected behavior: should return 200 with stats
    if response.status_code == 422:
        pytest.fail(
            "Route precedence bug: /tree/stats returns 422 instead of stats. "
            "The /tree/{parent_id} route is taking precedence over /tree/stats."
        )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)

    # Should contain expected stats keys
    expected_keys = {'nodes', 'roots', 'leaves', 'complete_paths', 'incomplete_parents'}
    assert set(data.keys()) == expected_keys

    # Verify counts based on our test data
    assert data['nodes'] >= 3  # At least our 3 test nodes
    assert data['roots'] >= 1  # At least our root
    assert data['leaves'] >= 0  # Leaves can be 0 if no complete paths exist


def test_tree_stats_dual_mount_compatibility(base_url, temp_db):
    """Test that both /tree/stats and /api/v1/tree/stats work identically."""

    # Test both routes
    api_response = requests.get(f"{base_url}/tree/stats")
    root_response = requests.get("http://127.0.0.1:8000/tree/stats")

    # Both should return the same status
    assert api_response.status_code == root_response.status_code

    if api_response.status_code == 200:
        # Both should return the same data structure
        api_data = api_response.json()
        root_data = root_response.json()
        assert api_data == root_data


def test_tree_stats_contract_when_working(base_url):
    """Test the full contract of tree stats when the route works."""

    response = requests.get(f"{base_url}/tree/stats")
    assert response.status_code == 200

    data = response.json()

    # Verify data types
    assert isinstance(data['nodes'], int)
    assert isinstance(data['roots'], int)
    assert isinstance(data['leaves'], int)
    assert isinstance(data['complete_paths'], int)
    assert isinstance(data['incomplete_parents'], int)

    # Verify non-negative counts
    assert data['nodes'] >= 0
    assert data['roots'] >= 0
    assert data['leaves'] >= 0
    assert data['complete_paths'] >= 0
    assert data['incomplete_parents'] >= 0
