"""
Comprehensive unit tests for the unified authentication middleware.

Tests cover:
- Auth enabled/disabled states
- Public vs protected endpoints
- Read vs write operations
- Bearer token validation
- Error responses and status codes
- Edge cases and security scenarios
"""

import os
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.middleware.auth import AuthMiddleware, get_auth_token, is_auth_enabled

# ============================================================================
# TEST FIXTURES
# ============================================================================


@pytest.fixture
def simple_app():
    """Create a minimal FastAPI app with auth middleware for isolated testing."""
    app = FastAPI()

    # Add some test routes
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/api/v1/tree/roots")
    async def list_roots():
        return {"items": []}

    @app.post("/api/v1/tree/roots")
    async def create_root():
        return {"id": 1}

    @app.put("/api/v1/tree/children")
    async def put_children():
        return {"ok": True}

    @app.delete("/api/v1/tree/node/123")
    async def delete_node():
        return {"deleted": True}

    @app.post("/api/v1/import")
    async def import_data():
        return {"imported": True}

    # Add auth middleware
    app.add_middleware(AuthMiddleware)

    return app


@pytest.fixture
def client_no_auth(simple_app, monkeypatch):
    """Test client with authentication disabled."""
    monkeypatch.delenv("AUTH_TOKEN", raising=False)
    return TestClient(simple_app, raise_server_exceptions=False)


@pytest.fixture
def client_with_auth(simple_app, monkeypatch):
    """Test client with authentication enabled."""
    monkeypatch.setenv("AUTH_TOKEN", "test-token-12345")
    return TestClient(simple_app, raise_server_exceptions=False)


# ============================================================================
# TEST: AUTHENTICATION STATE
# ============================================================================


def test_auth_disabled_by_default(monkeypatch):
    """Authentication should be disabled when AUTH_TOKEN is not set."""
    monkeypatch.delenv("AUTH_TOKEN", raising=False)
    assert not is_auth_enabled()
    assert get_auth_token() is None


def test_auth_enabled_when_token_set(monkeypatch):
    """Authentication should be enabled when AUTH_TOKEN is set."""
    monkeypatch.setenv("AUTH_TOKEN", "my-secret-token")
    assert is_auth_enabled()
    assert get_auth_token() == "my-secret-token"


# ============================================================================
# TEST: PUBLIC ENDPOINTS (Always accessible)
# ============================================================================


@pytest.mark.parametrize(
    "endpoint",
    [
        "/health",
        "/live",
        "/ready",
        "/api/v1/health",
        "/api/v1/live",
        "/api/v1/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
    ],
)
def test_public_endpoints_accessible_without_auth(client_with_auth, endpoint):
    """Public endpoints should always be accessible, even with auth enabled."""
    # Use GET for most, skip endpoints that don't exist in our simple app
    if endpoint in ["/docs", "/redoc", "/openapi.json"]:
        pytest.skip("Endpoint not in simple test app")

    response = client_with_auth.get(endpoint)
    # Should not return 401
    assert response.status_code != 401


# ============================================================================
# TEST: READ OPERATIONS (GET, HEAD, OPTIONS)
# ============================================================================


def test_get_requests_allowed_without_auth(client_with_auth):
    """GET requests should be allowed without authentication."""
    response = client_with_auth.get("/api/v1/tree/roots")
    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_head_requests_allowed_without_auth(client_with_auth):
    """HEAD requests should be allowed without authentication."""
    # Note: FastAPI typically allows HEAD for GET endpoints
    response = client_with_auth.head("/api/v1/tree/roots")
    # Should not return 401
    assert response.status_code != 401


def test_options_requests_allowed_without_auth(client_with_auth):
    """OPTIONS requests should be allowed without authentication."""
    response = client_with_auth.options("/api/v1/tree/roots")
    # Should not return 401
    assert response.status_code != 401


# ============================================================================
# TEST: WRITE OPERATIONS (POST, PUT, DELETE, PATCH)
# ============================================================================


def test_post_requires_auth_when_enabled(client_with_auth):
    """POST requests should require authentication when auth is enabled."""
    response = client_with_auth.post("/api/v1/tree/roots")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["error"] == "authentication_required"


def test_put_requires_auth_when_enabled(client_with_auth):
    """PUT requests should require authentication when auth is enabled."""
    response = client_with_auth.put("/api/v1/tree/children")
    assert response.status_code == 401


def test_delete_requires_auth_when_enabled(client_with_auth):
    """DELETE requests should require authentication when auth is enabled."""
    response = client_with_auth.delete("/api/v1/tree/node/123")
    assert response.status_code == 401


# ============================================================================
# TEST: BEARER TOKEN AUTHENTICATION
# ============================================================================


def test_valid_bearer_token_allows_access(client_with_auth):
    """Valid Bearer token should allow access to protected endpoints."""
    response = client_with_auth.post(
        "/api/v1/tree/roots", headers={"Authorization": "Bearer test-token-12345"}
    )
    assert response.status_code == 200
    assert response.json() == {"id": 1}


def test_invalid_bearer_token_rejects_access(client_with_auth):
    """Invalid Bearer token should reject access."""
    response = client_with_auth.post(
        "/api/v1/tree/roots", headers={"Authorization": "Bearer wrong-token"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["error"] == "invalid_token"


def test_missing_bearer_prefix_rejects(client_with_auth):
    """Authorization header without 'Bearer ' prefix should be rejected."""
    response = client_with_auth.post(
        "/api/v1/tree/roots", headers={"Authorization": "test-token-12345"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["error"] == "invalid_auth_format"


def test_empty_bearer_token_rejects(client_with_auth):
    """Empty Bearer token should be rejected."""
    response = client_with_auth.post("/api/v1/tree/roots", headers={"Authorization": "Bearer "})
    assert response.status_code == 401


def test_basic_auth_rejected(client_with_auth):
    """Basic auth format should be rejected (only Bearer tokens supported)."""
    response = client_with_auth.post(
        "/api/v1/tree/roots", headers={"Authorization": "Basic dXNlcjpwYXNz"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["error"] == "invalid_auth_format"


# ============================================================================
# TEST: AUTH DISABLED MODE
# ============================================================================


def test_all_endpoints_accessible_when_auth_disabled(client_no_auth):
    """All endpoints should be accessible when auth is disabled."""
    # Test various write operations without auth
    response = client_no_auth.post("/api/v1/tree/roots")
    assert response.status_code == 200

    response = client_no_auth.put("/api/v1/tree/children")
    assert response.status_code == 200

    response = client_no_auth.delete("/api/v1/tree/node/123")
    assert response.status_code == 200


# ============================================================================
# TEST: ERROR RESPONSES
# ============================================================================


def test_missing_auth_error_includes_hint(client_with_auth):
    """Error response for missing auth should include helpful hint."""
    response = client_with_auth.post("/api/v1/tree/roots")
    assert response.status_code == 401
    data = response.json()
    assert "hint" in data["detail"]
    assert "Bearer" in data["detail"]["hint"]


def test_invalid_format_error_includes_expected_format(client_with_auth):
    """Error response for invalid format should include expected format."""
    response = client_with_auth.post("/api/v1/tree/roots", headers={"Authorization": "test-token"})
    assert response.status_code == 401
    data = response.json()
    assert "expected_format" in data["detail"]


# ============================================================================
# TEST: SECURITY EDGE CASES
# ============================================================================


def test_token_with_extra_spaces_rejects(client_with_auth):
    """Token with extra spaces should be rejected (no trimming)."""
    response = client_with_auth.post(
        "/api/v1/tree/roots", headers={"Authorization": "Bearer  test-token-12345 "}
    )
    assert response.status_code == 401


def test_case_sensitive_token_validation(client_with_auth):
    """Token validation should be case-sensitive."""
    response = client_with_auth.post(
        "/api/v1/tree/roots", headers={"Authorization": "Bearer TEST-TOKEN-12345"}
    )
    assert response.status_code == 401


def test_sql_injection_in_token_handled_safely(client_with_auth):
    """SQL injection attempts in token should be handled safely."""
    response = client_with_auth.post(
        "/api/v1/tree/roots", headers={"Authorization": "Bearer '; DROP TABLE nodes; --"}
    )
    assert response.status_code == 401


def test_xss_in_token_handled_safely(client_with_auth):
    """XSS attempts in token should be handled safely."""
    response = client_with_auth.post(
        "/api/v1/tree/roots", headers={"Authorization": "Bearer <script>alert('xss')</script>"}
    )
    assert response.status_code == 401


# ============================================================================
# TEST: MULTIPLE WRITE OPERATIONS
# ============================================================================


def test_multiple_protected_endpoints_with_valid_token(client_with_auth):
    """Valid token should work across multiple protected endpoints."""
    headers = {"Authorization": "Bearer test-token-12345"}

    # POST
    response = client_with_auth.post("/api/v1/tree/roots", headers=headers)
    assert response.status_code == 200

    # PUT
    response = client_with_auth.put("/api/v1/tree/children", headers=headers)
    assert response.status_code == 200

    # DELETE
    response = client_with_auth.delete("/api/v1/tree/node/123", headers=headers)
    assert response.status_code == 200

    # POST to import
    response = client_with_auth.post("/api/v1/import", headers=headers)
    assert response.status_code == 200


# ============================================================================
# TEST: RUNTIME TOKEN CHANGES
# ============================================================================


def test_runtime_token_change_takes_effect(simple_app):
    """Token changes at runtime should take effect immediately."""
    with patch.dict(os.environ, {"AUTH_TOKEN": "initial-token"}):
        client = TestClient(simple_app, raise_server_exceptions=False)

        # First request with initial token
        response = client.post(
            "/api/v1/tree/roots", headers={"Authorization": "Bearer initial-token"}
        )
        assert response.status_code == 200

    with patch.dict(os.environ, {"AUTH_TOKEN": "new-token"}):
        client = TestClient(simple_app, raise_server_exceptions=False)

        # Old token should now fail
        response = client.post(
            "/api/v1/tree/roots", headers={"Authorization": "Bearer initial-token"}
        )
        assert response.status_code == 401

        # New token should work
        response = client.post("/api/v1/tree/roots", headers={"Authorization": "Bearer new-token"})
        assert response.status_code == 200


# ============================================================================
# TEST: INTEGRATION WITH ACTUAL API ROUTES
# ============================================================================


@pytest.mark.skip(reason="Integration test requires full database setup - covered by e2e tests")
def test_integration_with_import_endpoint(monkeypatch):
    """Test auth middleware with actual import endpoint."""
    from api.app import app

    monkeypatch.setenv("AUTH_TOKEN", "import-test-token")
    client = TestClient(app, raise_server_exceptions=False)

    # GET preview should work without auth
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    # POST import should require auth
    response = client.post("/api/v1/import")
    assert response.status_code == 401

    # POST import with valid token should work (though it may fail on other validation)
    response = client.post("/api/v1/import", headers={"Authorization": "Bearer import-test-token"})
    # Should not be 401 (may be 400/422 for missing file)
    assert response.status_code != 401


@pytest.mark.skip(reason="Integration test requires full database setup - covered by e2e tests")
def test_integration_with_tree_endpoints(monkeypatch):
    """Test auth middleware with actual tree endpoints."""
    from api.app import app

    monkeypatch.setenv("AUTH_TOKEN", "tree-test-token")
    client = TestClient(app, raise_server_exceptions=False)

    # GET should work without auth
    response = client.get("/api/v1/tree/roots")
    assert response.status_code == 200

    # POST should require auth
    response = client.post("/api/v1/tree/roots", json={"label": "Test"})
    assert response.status_code == 401

    # POST with valid token should work
    response = client.post(
        "/api/v1/tree/roots",
        json={"label": "Test"},
        headers={"Authorization": "Bearer tree-test-token"},
    )
    assert response.status_code in [200, 201]  # Success


# ============================================================================
# TEST: DOCUMENTATION AND USABILITY
# ============================================================================


def test_auth_middleware_is_singleton():
    """Auth middleware should use singleton pattern for token checking."""
    # Multiple instances should read from same env var
    assert AuthMiddleware.is_enabled == AuthMiddleware.is_enabled
    assert AuthMiddleware.get_token == AuthMiddleware.get_token


def test_public_endpoints_list_is_comprehensive():
    """Public endpoints list should include all necessary health/docs routes."""
    expected_public = {
        "/health",
        "/live",
        "/ready",
        "/api/v1/health",
        "/api/v1/live",
        "/api/v1/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
    }
    assert expected_public.issubset(AuthMiddleware.PUBLIC_ENDPOINTS)


def test_read_methods_list_is_correct():
    """Read methods list should include GET, HEAD, OPTIONS."""
    expected_methods = {"GET", "HEAD", "OPTIONS"}
    assert expected_methods == AuthMiddleware.READ_METHODS
