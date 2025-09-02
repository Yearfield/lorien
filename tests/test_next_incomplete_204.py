"""
Test next-incomplete-parent endpoint with 204 semantics.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_next_incomplete_returns_204_when_none(monkeypatch):
    """Test that next-incomplete-parent returns 204 when no incomplete parents."""
    from api.routes import get_next_incomplete_parent

    # Mock the database query to return no results
    def mock_no_results():
        return None

    # Monkey patch the internal function
    import api.routes
    original_func = api.routes.repo.get_next_incomplete_parent
    api.routes.repo.get_next_incomplete_parent = mock_no_results

    try:
        r = client.get("/api/v1/tree/next-incomplete-parent")
        assert r.status_code == 204
        assert r.content == b""  # Empty response body
    finally:
        # Restore original function
        api.routes.repo.get_next_incomplete_parent = original_func


def test_next_incomplete_returns_200_with_data():
    """Test that next-incomplete-parent returns 200 with data when incomplete parents exist."""
    r = client.get("/api/v1/tree/next-incomplete-parent")

    # This will depend on the test database state
    # If there are incomplete parents, it should return 200 with data
    # If there are none, it should return 204
    assert r.status_code in [200, 204]

    if r.status_code == 200:
        body = r.json()
        assert "parent_id" in body
        assert "missing_slots" in body
        assert "depth" in body


def test_next_incomplete_dual_mount():
    """Test next-incomplete works on both root and /api/v1 mounts."""
    # Test root mount
    r1 = client.get("/tree/next-incomplete-parent")
    assert r1.status_code in [200, 204]

    # Test api/v1 mount
    r2 = client.get("/api/v1/tree/next-incomplete-parent")
    assert r2.status_code in [200, 204]

    # Both should return the same status
    assert r1.status_code == r2.status_code


def test_next_incomplete_response_structure():
    """Test the response structure when data is returned."""
    r = client.get("/api/v1/tree/next-incomplete-parent")

    if r.status_code == 200:
        body = r.json()
        required_fields = ["parent_id", "missing_slots", "depth"]
        for field in required_fields:
            assert field in body

        # Validate field types
        assert isinstance(body["parent_id"], int)
        assert isinstance(body["depth"], int)
        assert isinstance(body["missing_slots"], str)  # Comma-separated string
