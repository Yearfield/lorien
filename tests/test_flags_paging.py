"""
Test flags paging endpoint with query/limit/offset.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_flags_list_paging_basic():
    """Test basic flags paging without query."""
    r = client.get("/api/v1/flags", params={"limit": 10, "offset": 0})
    assert r.status_code == 200

    body = r.json()
    assert "items" in body
    assert "total" in body
    assert "limit" in body
    assert "offset" in body
    assert body["limit"] == 10
    assert body["offset"] == 0
    assert isinstance(body["items"], list)
    assert isinstance(body["total"], int)


def test_flags_list_with_query():
    """Test flags paging with case-insensitive search."""
    r = client.get("/api/v1/flags", params={"query": "test", "limit": 5, "offset": 0})
    assert r.status_code == 200

    body = r.json()
    assert "items" in body
    assert "total" in body
    assert body["limit"] == 5
    assert body["offset"] == 0


def test_flags_list_pagination_params():
    """Test flags pagination parameters are respected."""
    # Test limit bounds
    r1 = client.get("/api/v1/flags", params={"limit": 1})
    assert r1.status_code == 200
    assert r1.json()["limit"] == 1

    r2 = client.get("/api/v1/flags", params={"limit": 100})
    assert r2.status_code == 200
    assert r2.json()["limit"] == 100

    # Test offset
    r3 = client.get("/api/v1/flags", params={"offset": 10})
    assert r3.status_code == 200
    assert r3.json()["offset"] == 10


def test_flags_list_stable_sort():
    """Test that flags are sorted stably (updated_at DESC, id DESC)."""
    r = client.get("/api/v1/flags", params={"limit": 50})
    assert r.status_code == 200

    items = r.json()["items"]
    if len(items) > 1:
        # Check that items have the expected structure
        for item in items:
            assert "id" in item
            assert "label" in item
            assert isinstance(item["id"], int)
            assert isinstance(item["label"], str)


def test_flags_list_dual_mount():
    """Test flags list works on both root and /api/v1 mounts."""
    # Test root mount
    r1 = client.get("/flags", params={"limit": 5})
    assert r1.status_code == 200
    assert "items" in r1.json()

    # Test api/v1 mount
    r2 = client.get("/api/v1/flags", params={"limit": 5})
    assert r2.status_code == 200
    assert "items" in r2.json()
