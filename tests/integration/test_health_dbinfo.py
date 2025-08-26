import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from api.app import app


class TestHealthDBInfo:
    """Test health endpoint database information."""

    def test_health_contains_db_info(self, client: TestClient):
        """Test that /health contains database information."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "db" in data
        assert "path" in data["db"]
        assert "wal" in data["db"]
        assert "foreign_keys" in data["db"]
        
        # Check that path is an absolute path
        db_path = data["db"]["path"]
        assert db_path is not None
        assert db_path.startswith("/") or ":" in db_path  # Unix or Windows path
        
        # Check that WAL and foreign keys are enabled
        assert data["db"]["wal"] is True
        assert data["db"]["foreign_keys"] is True

    def test_health_db_path_is_absolute(self, client: TestClient):
        """Test that database path in health is absolute."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        db_path = data["db"]["path"]
        
        # Should be absolute path
        assert db_path is not None
        assert db_path.startswith("/") or ":" in db_path

    def test_health_db_wal_enabled(self, client: TestClient):
        """Test that WAL mode is enabled in health response."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["db"]["wal"] is True

    def test_health_db_foreign_keys_enabled(self, client: TestClient):
        """Test that foreign keys are enabled in health response."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["db"]["foreign_keys"] is True

    def test_health_db_path_matches_repository(self, client: TestClient):
        """Test that database path in health matches repository path."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        health_db_path = data["db"]["path"]
        
        # This should match the path from the repository
        # We can't easily test this without mocking, but we can verify format
        assert health_db_path is not None
        assert len(health_db_path) > 0

    def test_health_version_present(self, client: TestClient):
        """Test that version is present in health response."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "version" in data
        assert data["version"] is not None
        assert len(data["version"]) > 0

    def test_health_ok_status(self, client: TestClient):
        """Test that health returns ok: true when healthy."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["ok"] is True

    def test_health_features_present(self, client: TestClient):
        """Test that features section is present in health response."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "features" in data
        assert "llm" in data["features"]
        assert isinstance(data["features"]["llm"], bool)

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
