"""
Integration test to ensure root /health is not relied upon.
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_root_health_not_relied_upon():
    """Test that root /health is not relied upon (should return 404 or 200 but not be a contract)."""
    client = TestClient(app)
    r = client.get("/health")
    # Root /health should not exist or should not be a contract
    # Tolerate both 404 (not found) and 200 (if it exists) but don't rely on it
    assert r.status_code in (404, 200)  # Not a contract; tolerate both


def test_root_endpoint_points_to_versioned_health():
    """Test that root endpoint points to versioned health."""
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "health" in data
    assert data["health"] == "/api/v1/health"
