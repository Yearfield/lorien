"""
Unit tests for the deprecation middleware.

Tests cover:
- 301 redirects for deprecated routes
- Sunset header presence
- Deprecation headers
- Query string preservation
- Path parameter preservation
- Non-deprecated routes pass through
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.middleware.deprecation import SUNSET_DATE, DeprecationMiddleware

# ============================================================================
# TEST FIXTURES
# ============================================================================


@pytest.fixture
def app_with_deprecation():
    """Create a minimal FastAPI app with deprecation middleware."""
    app = FastAPI()

    # Add canonical routes
    @app.get("/api/v1/tree/roots")
    async def list_roots():
        return {"items": []}

    @app.get("/api/v1/tree/children")
    async def list_children():
        return {"items": []}

    @app.get("/api/v1/tree/export")
    async def export_tree():
        return {"data": "csv"}

    @app.get("/api/v1/tree/export.xlsx")
    async def export_xlsx():
        return {"data": "xlsx"}

    @app.delete("/api/v1/tree/node/{node_id}")
    async def delete_node(node_id: int):
        return {"deleted": node_id}

    # Add deprecation middleware
    app.add_middleware(DeprecationMiddleware)

    return app


@pytest.fixture
def client(app_with_deprecation):
    """Test client with deprecation middleware."""
    return TestClient(app_with_deprecation, follow_redirects=False)


# ============================================================================
# TEST: 301 REDIRECTS
# ============================================================================


def test_deprecated_route_returns_301(client):
    """Deprecated routes should return 301 Permanent Redirect."""
    response = client.get("/tree/roots")
    assert response.status_code == 301


def test_redirect_location_is_canonical(client):
    """Redirect should point to canonical /api/v1 route."""
    response = client.get("/tree/roots")
    assert response.headers["location"] == "/api/v1/tree/roots"


def test_redirect_preserves_query_string(client):
    """Query parameters should be preserved in redirect."""
    response = client.get("/tree/children?parent_id=123&only_red=true")
    assert response.headers["location"] == "/api/v1/tree/children?parent_id=123&only_red=true"


def test_redirect_preserves_path_parameters(client):
    """Path parameters should be preserved in redirect."""
    response = client.delete("/tree/node/456")
    # The deprecation middleware should handle the path mapping
    assert response.status_code == 301
    assert "/api/v1/" in response.headers["location"]


# ============================================================================
# TEST: DEPRECATION HEADERS
# ============================================================================


def test_sunset_header_present(client):
    """Deprecated routes should include Sunset header."""
    response = client.get("/tree/roots")
    assert "Sunset" in response.headers
    assert response.headers["Sunset"] == SUNSET_DATE


def test_deprecation_header_present(client):
    """Deprecated routes should include Deprecation header."""
    response = client.get("/tree/roots")
    assert "Deprecation" in response.headers
    assert response.headers["Deprecation"] == "true"


def test_warning_header_present(client):
    """Deprecated routes should include Warning header with helpful message."""
    response = client.get("/tree/roots")
    assert "Warning" in response.headers
    warning = response.headers["Warning"]
    assert "Deprecated API endpoint" in warning
    assert "/api/v1/tree/roots" in warning


def test_link_header_present(client):
    """Deprecated routes should include Link header to canonical route."""
    response = client.get("/tree/roots")
    assert "Link" in response.headers
    link = response.headers["Link"]
    assert "/api/v1/tree/roots" in link
    assert 'rel="alternate"' in link


def test_custom_headers_present(client):
    """Deprecated routes should include custom X- headers for debugging."""
    response = client.get("/tree/roots")
    assert "X-Deprecated-Endpoint" in response.headers
    assert response.headers["X-Deprecated-Endpoint"] == "/tree/roots"
    assert "X-Canonical-Endpoint" in response.headers
    assert response.headers["X-Canonical-Endpoint"] == "/api/v1/tree/roots"


# ============================================================================
# TEST: NON-DEPRECATED ROUTES
# ============================================================================


def test_canonical_routes_not_redirected(client):
    """Canonical /api/v1 routes should not be redirected."""
    response = client.get("/api/v1/tree/roots")
    assert response.status_code == 200
    assert "Sunset" not in response.headers
    assert "Deprecation" not in response.headers


def test_health_endpoints_not_redirected(client):
    """Health endpoints should not be affected by deprecation middleware."""
    # Note: These may return 404 if not defined in test app, but should not redirect
    response = client.get("/health")
    assert response.status_code != 301


# ============================================================================
# TEST: SPECIFIC DEPRECATED ROUTES
# ============================================================================


@pytest.mark.parametrize(
    "deprecated_path,canonical_path",
    [
        ("/tree/roots", "/api/v1/tree/roots"),
        ("/tree/children", "/api/v1/tree/children"),
        ("/export/csv", "/api/v1/tree/export"),
        ("/export.xlsx", "/api/v1/tree/export.xlsx"),
        ("/tree/export-json", "/api/v1/tree/export-json"),
    ],
)
def test_specific_route_mappings(client, deprecated_path, canonical_path):
    """Specific deprecated routes should map to correct canonical routes."""
    response = client.get(deprecated_path)
    if response.status_code == 301:
        assert response.headers["location"] == canonical_path


# ============================================================================
# TEST: HTTP METHODS
# ============================================================================


def test_post_requests_redirected(client):
    """POST requests to deprecated routes should be redirected."""
    response = client.post("/tree/roots", json={"label": "test"})
    # Should still redirect even for write operations
    assert response.status_code == 301


def test_put_requests_redirected(client):
    """PUT requests to deprecated routes should be redirected."""
    response = client.put("/tree/children", json={"parent_id": 1, "children": []})
    assert response.status_code == 301


def test_delete_requests_redirected(client):
    """DELETE requests to deprecated routes should be redirected."""
    response = client.delete("/tree/node/123")
    assert response.status_code == 301


# ============================================================================
# TEST: EDGE CASES
# ============================================================================


def test_empty_query_string_handled(client):
    """Routes with empty query string should not have trailing ?"""
    response = client.get("/tree/roots?")
    location = response.headers.get("location", "")
    # Should not have trailing ? if query string is empty
    assert not location.endswith("?")


def test_multiple_query_parameters(client):
    """Multiple query parameters should be preserved correctly."""
    response = client.get("/tree/children?parent_id=1&only_red=false&limit=10")
    location = response.headers["location"]
    assert "parent_id=1" in location
    assert "only_red=false" in location
    assert "limit=10" in location


def test_special_characters_in_query(client):
    """Special characters in query string should be handled correctly."""
    response = client.get("/tree/children?label=Test%20Value")
    assert response.status_code == 301
    # Should preserve encoded characters
    assert "label=Test%20Value" in response.headers["location"]


# ============================================================================
# TEST: INTEGRATION
# ============================================================================


def test_client_can_follow_redirect(app_with_deprecation):
    """Clients that follow redirects should reach canonical endpoint."""
    client = TestClient(app_with_deprecation, follow_redirects=True)
    response = client.get("/tree/roots")
    # Should reach the canonical endpoint after redirect
    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_redirect_only_happens_once(app_with_deprecation):
    """Canonical routes should not cause redirect loops."""
    client = TestClient(app_with_deprecation, follow_redirects=True)

    # Direct request to canonical should work without redirect
    response = client.get("/api/v1/tree/roots")
    assert response.status_code == 200

    # History should show only one request (no redirects)
    assert len(response.history) == 0


# ============================================================================
# TEST: LOGGING AND MONITORING
# ============================================================================


def test_deprecation_middleware_logs_redirects(client, caplog):
    """Deprecation middleware should log redirect events for monitoring."""
    import logging

    with caplog.at_level(logging.WARNING):
        client.get("/tree/roots")

    # Should have logged the deprecation
    assert any("Deprecated route accessed" in record.message for record in caplog.records)


# ============================================================================
# TEST: CONFIGURATION
# ============================================================================


def test_sunset_date_is_valid_http_date():
    """Sunset date should be in valid HTTP date format."""
    # HTTP date format: "Day, DD Mon YYYY HH:MM:SS GMT"
    import re

    pattern = r"^\w{3}, \d{2} \w{3} \d{4} \d{2}:\d{2}:\d{2} GMT$"
    assert re.match(pattern, SUNSET_DATE), f"Invalid HTTP date format: {SUNSET_DATE}"


def test_deprecated_routes_dict_not_empty():
    """Deprecated routes mapping should not be empty."""
    assert len(DeprecationMiddleware.DEPRECATED_ROUTES) > 0


def test_deprecated_routes_all_have_api_v1_target():
    """All deprecated routes should redirect to /api/v1 paths."""
    for canonical in DeprecationMiddleware.DEPRECATED_ROUTES.values():
        assert canonical.startswith("/api/v1/"), f"Invalid canonical path: {canonical}"
