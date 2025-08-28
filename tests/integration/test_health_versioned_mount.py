"""
Integration test for versioned health mount contract.
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_versioned_health_mount_contract():
    """Test that /api/v1/health returns the correct contract shape."""
    client = TestClient(app)
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert isinstance(data.get("version"), str)
    db = data.get("db", {})
    assert isinstance(db, dict)
    assert {"wal", "foreign_keys", "page_size", "path"}.issubset(set(db.keys()))
    assert isinstance(db["wal"], bool)
    assert isinstance(db["foreign_keys"], bool)
    assert isinstance(db["page_size"], int)
    assert isinstance(db["path"], str)
    features = data.get("features", {})
    assert isinstance(features, dict)
    assert isinstance(features.get("llm", False), bool)
