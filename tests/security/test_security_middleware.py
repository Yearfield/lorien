"""
Tests for security middleware and authentication.
"""

import os

from fastapi.testclient import TestClient

from api.app import app
from api.security import get_security_config


class TestSecurityMiddleware:
    """Test security middleware functionality."""

    def setup_method(self):
        """Set up test environment."""
        from api.security import reset_security_config

        # Reset environment for each test
        os.environ.clear()
        os.environ.update(
            {
                "ENVIRONMENT": "development",
                "AUTH_REQUIRED": "false",
                "SECURITY_HEADERS_ENABLED": "true",
                "RATE_LIMIT_ENABLED": "false",
                "INPUT_VALIDATION_ENABLED": "true",
            }
        )

        # Reset security config singleton
        reset_security_config()

        self.client = TestClient(app)

    def test_security_headers_present(self):
        """Test that security headers are added to responses."""
        response = self.client.get("/api/v1/health")

        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_input_validation_middleware(self):
        """Test input validation middleware."""
        # Test with potentially dangerous input
        response = self.client.get("/api/v1/health?test=<script>alert('xss')</script>")

        # Should still work for health endpoint (it's public)
        assert response.status_code == 200

    def test_cors_configuration(self):
        """Test CORS configuration."""
        response = self.client.options("/api/v1/health")

        assert response.status_code == 200
        # CORS headers should be present
        assert "Access-Control-Allow-Origin" in response.headers

    def test_authentication_not_required_development(self):
        """Test that authentication is not required in development."""
        # POST request should work without auth in development
        response = self.client.post(
            "/api/v1/import/preview", files={"file": ("test.csv", "D0,D1\nTest,Test")}
        )

        # Should get a response (might be 422 for invalid file, but not 401)
        assert response.status_code != 401

    def test_authentication_required_production(self):
        """Test that authentication is required in production."""
        # Set production environment
        os.environ.update(
            {
                "ENVIRONMENT": "production",
                "AUTH_TOKEN": "test-token-123",
                "AUTH_REQUIRED": "true",
            }
        )

        # Create new client with production settings
        client = TestClient(app)

        # POST request without auth should fail
        response = client.post(
            "/api/v1/import/preview", files={"file": ("test.csv", "D0,D1\nTest,Test")}
        )

        assert response.status_code == 401
        assert "authentication_required" in response.json()["detail"]["error"]

    def test_authentication_with_valid_token(self):
        """Test authentication with valid token."""
        # Set up authentication
        os.environ.update(
            {
                "ENVIRONMENT": "production",
                "AUTH_TOKEN": "test-token-123",
                "AUTH_REQUIRED": "true",
            }
        )

        client = TestClient(app)

        # POST request with valid token should work
        response = client.post(
            "/api/v1/import/preview",
            files={"file": ("test.csv", "D0,D1\nTest,Test")},
            headers={"Authorization": "Bearer test-token-123"},
        )

        # Should not be 401 (might be other error codes for invalid file)
        assert response.status_code != 401

    def test_authentication_with_invalid_token(self):
        """Test authentication with invalid token."""
        # Set up authentication
        os.environ.update(
            {
                "ENVIRONMENT": "production",
                "AUTH_TOKEN": "test-token-123",
                "AUTH_REQUIRED": "true",
            }
        )

        client = TestClient(app)

        # POST request with invalid token should fail
        response = client.post(
            "/api/v1/import/preview",
            files={"file": ("test.csv", "D0,D1\nTest,Test")},
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401
        assert "invalid_token" in response.json()["detail"]["error"]

    def test_authentication_missing_header(self):
        """Test authentication with missing Authorization header."""
        # Set up authentication
        os.environ.update(
            {
                "ENVIRONMENT": "production",
                "AUTH_TOKEN": "test-token-123",
                "AUTH_REQUIRED": "true",
            }
        )

        client = TestClient(app)

        # POST request without Authorization header should fail
        response = client.post(
            "/api/v1/import/preview", files={"file": ("test.csv", "D0,D1\nTest,Test")}
        )

        assert response.status_code == 401
        assert "authentication_required" in response.json()["detail"]["error"]

    def test_public_endpoints_always_accessible(self):
        """Test that public endpoints are always accessible."""
        # Set up authentication
        os.environ.update(
            {
                "ENVIRONMENT": "production",
                "AUTH_TOKEN": "test-token-123",
                "AUTH_REQUIRED": "true",
            }
        )

        client = TestClient(app)

        # Health endpoint should be accessible without auth
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        # Live endpoint should be accessible without auth
        response = client.get("/api/v1/live")
        assert response.status_code == 200

        # Ready endpoint should be accessible without auth
        response = client.get("/api/v1/ready")
        assert response.status_code == 200


class TestSecurityConfiguration:
    """Test security configuration functionality."""

    def setup_method(self):
        """Set up test environment."""
        from api.security import reset_security_config

        # Reset environment for each test
        os.environ.clear()

        # Reset security config singleton
        reset_security_config()

    def test_security_config_development(self):
        """Test security configuration in development."""
        os.environ.update(
            {
                "ENVIRONMENT": "development",
                "AUTH_REQUIRED": "false",
            }
        )

        # Reset config to pick up new environment
        from api.security import reset_security_config

        reset_security_config()

        config = get_security_config()

        assert config.environment == "development"
        assert config.is_production is False
        assert config.auth_required is False

    def test_security_config_production(self):
        """Test security configuration in production."""
        os.environ.update(
            {
                "ENVIRONMENT": "production",
                "AUTH_TOKEN": "test-token",
                "AUTH_REQUIRED": "true",
            }
        )

        # Reset config to pick up new environment
        from api.security import reset_security_config

        reset_security_config()

        config = get_security_config()

        assert config.environment == "production"
        assert config.is_production is True
        assert config.auth_required is True
        assert config.auth_token == "test-token"

    def test_security_config_cors_origins(self):
        """Test CORS origins configuration."""
        os.environ.update(
            {
                "CORS_ORIGINS": "https://example.com,https://app.example.com",
            }
        )

        # Reset config to pick up new environment
        from api.security import reset_security_config

        reset_security_config()

        config = get_security_config()

        assert "https://example.com" in config.cors_origins
        assert "https://app.example.com" in config.cors_origins

    def test_security_config_rate_limiting(self):
        """Test rate limiting configuration."""
        os.environ.update(
            {
                "RATE_LIMIT_ENABLED": "true",
                "RATE_LIMIT_REQUESTS": "50",
            }
        )

        # Reset config to pick up new environment
        from api.security import reset_security_config

        reset_security_config()

        config = get_security_config()

        assert config.rate_limit_enabled is True
        assert config.rate_limit_requests == 50
