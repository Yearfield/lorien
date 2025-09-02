"""
Tests for health and LLM endpoints with environment-based behavior.
"""

import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch

from api.app import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health endpoints with dual-mount functionality."""
    
    def test_health_dual_mount(self, client):
        """Test that health endpoint is available at both root and versioned paths."""
        # Test root health
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "ok" in data
        assert "version" in data
        assert "db" in data
        assert "features" in data
        
        # Test versioned health
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "ok" in data
        assert "version" in data
        assert "db" in data
        assert "features" in data
        
        # Both should return same data
        assert response.json() == client.get("/health").json()
    
    def test_health_database_info(self, client):
        """Test that health endpoint includes database configuration."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "db" in data
        
        db_info = data["db"]
        assert "wal" in db_info
        assert "foreign_keys" in db_info
        assert "page_size" in db_info
        assert "path" in db_info
        
        # Database should be properly configured
        assert db_info["wal"] is True
        assert db_info["foreign_keys"] is True
        assert db_info["page_size"] > 0
        assert db_info["path"] is not None
    
    def test_health_features(self, client):
        """Test that health endpoint includes feature flags."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "features" in data
        
        features = data["features"]
        assert "llm" in features
        
        # LLM should be disabled by default
        assert features["llm"] is False


class TestLLMHealthEndpoint:
    """Test LLM health endpoint with environment-based gating."""
    
    @patch.dict(os.environ, {"LLM_ENABLED": "false"})
    def test_llm_health_disabled(self, client):
        """Test LLM health when LLM_ENABLED=false."""
        response = client.get("/api/v1/llm/health")
        assert response.status_code == 503
        
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert detail["ok"] is False
        assert detail["llm_enabled"] is False
    
    @patch.dict(os.environ, {"LLM_ENABLED": "true"})
    def test_llm_health_enabled(self, client):
        """Test LLM health when LLM_ENABLED=true."""
        response = client.get("/api/v1/llm/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["ok"] is True
        assert data["llm_enabled"] is True
    
    @patch.dict(os.environ, {"LLM_ENABLED": "TRUE"})
    def test_llm_health_case_insensitive(self, client):
        """Test that LLM_ENABLED is case-insensitive."""
        response = client.get("/api/v1/llm/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["ok"] is True
        assert data["llm_enabled"] is True
    
    def test_llm_health_dual_mount(self, client):
        """Test that LLM health is available at both root and versioned paths."""
        # Test root LLM health
        response = client.get("/llm/health")
        assert response.status_code in [200, 503]  # Depends on LLM_ENABLED
        
        # Test versioned LLM health
        response = client.get("/api/v1/llm/health")
        assert response.status_code in [200, 503]  # Depends on LLM_ENABLED


class TestRootEndpoint:
    """Test root endpoint with API information."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint provides API information."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data
        
        assert data["message"] == "Lorien API"
        assert data["docs"] == "/docs"
        assert data["health"] == "/api/v1/health"
