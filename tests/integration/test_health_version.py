import pytest
from fastapi.testclient import TestClient
from api.app import app
from core.version import __version__

@pytest.fixture
def client():
    return TestClient(app)

def test_health_version_matches_core_version(client):
    """Test that /health exposes the version from core.version."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "version" in data
    assert data["version"] == __version__
    assert data["version"] == "v6.7.0"

def test_health_contains_required_fields(client):
    """Test that /health contains all required fields."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    
    # Required top-level fields
    assert "ok" in data
    assert "version" in data
    assert "db" in data
    assert "features" in data
    
    # Required db fields
    db_info = data["db"]
    assert "path" in db_info
    assert "wal" in db_info
    assert "foreign_keys" in db_info
    
    # Required features fields
    features = data["features"]
    assert "llm" in features
    assert isinstance(features["llm"], bool)
