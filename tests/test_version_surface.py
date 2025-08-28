"""
Test that version is consistently surfaced across all endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app
from core.version import __version__

client = TestClient(app)


class TestVersionConsistency:
    """Test that version is consistent across all surfaces."""
    
    def test_health_endpoint_version_matches_core(self):
        """Test that /health returns the same version as core.version."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "version" in data
        assert data["version"] == __version__
    
    def test_api_v1_health_version_matches_core(self):
        """Test that /api/v1/health returns the same version as core.version."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "version" in data
        assert data["version"] == __version__
    
    def test_root_and_v1_health_versions_match(self):
        """Test that root and /api/v1 health endpoints return identical versions."""
        root_response = client.get("/health")
        v1_response = client.get("/api/v1/health")
        
        assert root_response.status_code == 200
        assert v1_response.status_code == 200
        
        root_data = root_response.json()
        v1_data = v1_response.json()
        
        assert root_data["version"] == v1_data["version"]
        assert root_data["version"] == __version__
    
    def test_fastapi_app_version_matches_core(self):
        """Test that FastAPI app version matches core.version."""
        assert app.version == __version__
    
    def test_version_is_string(self):
        """Test that version is a string value."""
        assert isinstance(__version__, str)
        assert len(__version__) > 0
    
    def test_version_format_consistent(self):
        """Test that version follows expected format."""
        # Version should start with 'v' and contain version numbers
        assert __version__.startswith('v')
        assert '.' in __version__
        
        # Should be parseable as version
        version_parts = __version__[1:].split('.')  # Remove 'v' prefix
        assert len(version_parts) >= 2  # At least major.minor
        
        for part in version_parts:
            assert part.isdigit() or part.isalnum()  # Numbers or alphanumeric


class TestVersionEndpoints:
    """Test that version is available at all expected endpoints."""
    
    def test_root_health_available(self):
        """Test that /health endpoint is available."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_api_v1_health_available(self):
        """Test that /api/v1/health endpoint is available."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
    
    def test_docs_show_correct_version(self):
        """Test that OpenAPI docs show the correct version."""
        response = client.get("/docs")
        assert response.status_code == 200
        
        # The docs endpoint should be accessible
        # Note: The version is in the OpenAPI schema, not directly in the HTML
        # This test just ensures the docs endpoint works
    
    def test_openapi_schema_has_correct_version(self):
        """Test that OpenAPI schema has the correct version."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "info" in schema
        assert "version" in schema["info"]
        assert schema["info"]["version"] == __version__


class TestVersionImports:
    """Test that version is imported correctly from core."""
    
    def test_core_version_importable(self):
        """Test that core.version can be imported."""
        try:
            from core.version import __version__
            assert __version__ is not None
        except ImportError:
            pytest.fail("core.version.__version__ could not be imported")
    
    def test_version_not_hardcoded(self):
        """Test that version is not hardcoded in app.py."""
        with open("api/app.py", "r") as f:
            app_content = f.read()
        
        # Should not contain hardcoded version strings
        hardcoded_versions = ["1.0.0", "2.0.0", "0.1.0"]
        for hardcoded in hardcoded_versions:
            assert hardcoded not in app_content, f"Hardcoded version {hardcoded} found in app.py"
    
    def test_version_not_hardcoded_in_health(self):
        """Test that version is not hardcoded in health router."""
        with open("api/routers/health.py", "r") as f:
            health_content = f.read()
        
        # Should not contain hardcoded version strings
        hardcoded_versions = ["1.0.0", "2.0.0", "0.1.0"]
        for hardcoded in hardcoded_versions:
            assert hardcoded not in health_content, f"Hardcoded version {hardcoded} found in health.py"


if __name__ == "__main__":
    pytest.main([__file__])
