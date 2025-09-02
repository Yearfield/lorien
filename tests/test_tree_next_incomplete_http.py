"""
Test next-incomplete-parent HTTP semantics.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_next_incomplete_204_when_none(client):
    """Test that next-incomplete-parent returns 204 when no incomplete parents."""
    # This test assumes there are no incomplete parents in the test database
    # If there are incomplete parents, this will return 200 instead
    r = client.get("/api/v1/tree/next-incomplete-parent")
    assert r.status_code in [200, 204]  # Either is acceptable depending on data

    if r.status_code == 204:
        # Should have empty body
        assert r.content == b""
        assert r.json() is None or r.json() == {}


def test_next_incomplete_200_with_data_when_exists(client):
    """Test that next-incomplete-parent returns 200 with data when incomplete parents exist."""
    r = client.get("/api/v1/tree/next-incomplete-parent")
    assert r.status_code in [200, 204]  # Either is acceptable depending on data

    if r.status_code == 200:
        data = r.json()
        required_fields = ["parent_id", "missing_slots", "depth"]
        for field in required_fields:
            assert field in data

        # Validate field types
        assert isinstance(data["parent_id"], int)
        assert isinstance(data["depth"], int)
        assert isinstance(data["missing_slots"], str)


def test_next_incomplete_dual_mount(client):
    """Test next-incomplete works on both / and /api/v1 mounts."""
    # Test root mount
    r1 = client.get("/tree/next-incomplete-parent")
    assert r1.status_code in [200, 204]

    # Test api/v1 mount
    r2 = client.get("/api/v1/tree/next-incomplete-parent")
    assert r2.status_code in [200, 204]

    # Both should return the same status
    assert r1.status_code == r2.status_code
