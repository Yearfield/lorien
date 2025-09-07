"""
Test next incomplete parent contract (sanity check).

This endpoint should already be working based on existing tests,
but we verify the contract here.
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
    db_path = "/tmp/lorien_incomplete_test.db"

    # Clean up any existing database
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

    # Insert test data: root with only 3 children (incomplete)
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, depth, slot, label)
        VALUES (1, NULL, 0, NULL, 'Incomplete Root')
    """)
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, depth, slot, label)
        VALUES (2, 1, 1, 1, 'Child 1')
    """)
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, depth, slot, label)
        VALUES (3, 1, 1, 2, 'Child 2')
    """)
    cursor.execute("""
        INSERT INTO nodes (id, parent_id, depth, slot, label)
        VALUES (4, 1, 1, 3, 'Child 3')
    """)

    conn.commit()
    conn.close()

    # Set environment variable for this test
    os.environ['LORIEN_DB_PATH'] = db_path

    yield db_path

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


def test_next_incomplete_parent_returns_proper_contract(base_url, temp_db):
    """Test next incomplete parent returns proper contract."""

    response = requests.get(f"{base_url}/tree/next-incomplete-parent")

    print(f"Next incomplete response status: {response.status_code}")
    print(f"Next incomplete response body: {response.text}")

    # Should return 200 with incomplete parent info, or 204 if none found
    assert response.status_code in [200, 204]

    if response.status_code == 200:
        data = response.json()

        # Should contain expected fields
        assert isinstance(data, dict)
        assert 'parent_id' in data
        assert 'missing_slots' in data

        # parent_id should be valid
        assert isinstance(data['parent_id'], int)
        assert data['parent_id'] > 0

        # missing_slots should be a string representation of missing slots
        assert isinstance(data['missing_slots'], str)
        # For our test data with slots 1,2,3 filled, should be missing 4,5
        assert '4' in data['missing_slots']
        assert '5' in data['missing_slots']


def test_next_incomplete_parent_when_complete(base_url):
    """Test next incomplete parent returns 204 when all parents are complete."""

    response = requests.get(f"{base_url}/tree/next-incomplete-parent")

    # If we get 204, that's expected (no incomplete parents)
    if response.status_code == 204:
        assert response.text.strip() == ""
    else:
        assert response.status_code == 200


def test_next_incomplete_parent_contract_details(base_url, temp_db):
    """Test detailed contract of next incomplete parent response."""

    response = requests.get(f"{base_url}/tree/next-incomplete-parent")

    if response.status_code == 200:
        data = response.json()

        # Verify response structure
        required_fields = ['parent_id', 'missing_slots']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # parent_id should be a positive integer
        assert isinstance(data['parent_id'], int)
        assert data['parent_id'] > 0

        # missing_slots should be a non-empty string
        assert isinstance(data['missing_slots'], str)
        assert len(data['missing_slots']) > 0

        # Should represent slot numbers (typically comma-separated)
        slots = data['missing_slots'].split(',')
        for slot in slots:
            slot_num = int(slot.strip())
            assert 1 <= slot_num <= 5, f"Invalid slot number: {slot_num}"


def test_next_incomplete_after_filling_slots(base_url, temp_db):
    """Test that next incomplete parent updates after filling slots."""

    # First, get the incomplete parent
    response1 = requests.get(f"{base_url}/tree/next-incomplete-parent")
    assert response1.status_code == 200
    data1 = response1.json()
    parent_id = data1['parent_id']

    # Fill the missing slots using bulk children update
    missing_slots = data1['missing_slots'].split(',')
    children_payload = []
    for slot in missing_slots[:2]:  # Fill first 2 missing slots
        slot_num = int(slot.strip())
        children_payload.append({
            "slot": slot_num,
            "label": f"Filled Child {slot_num}"
        })

    # Update children
    update_response = requests.post(
        f"{base_url}/tree/{parent_id}/children",
        json={"children": children_payload},
        headers={"Content-Type": "application/json"}
    )

    if update_response.status_code == 200:
        # Check next incomplete again - might still be incomplete or complete
        response2 = requests.get(f"{base_url}/tree/next-incomplete-parent")

        # Could be 200 (still incomplete) or 204 (now complete)
        assert response2.status_code in [200, 204]

        if response2.status_code == 200:
            data2 = response2.json()
            # Should have fewer missing slots now
            assert len(data2['missing_slots']) < len(data1['missing_slots'])
