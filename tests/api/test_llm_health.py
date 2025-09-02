"""
Tests for LLM health endpoint with hermetic mocking.
"""

import re
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.app import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def _ends_with_z(s: str) -> bool:
    """Check if string ends with Z (ISO-8601 UTC indicator)."""
    return isinstance(s, str) and s.endswith("Z")


def test_health_disabled_returns_503(monkeypatch, client):
    """Test health returns 503 when LLM_ENABLED=false."""
    monkeypatch.setenv("LLM_ENABLED", "false")
    r = client.get("/api/v1/llm/health")
    assert r.status_code == 503
    body = r.json()
    assert body["ok"] is False and body["llm_enabled"] is False and body["ready"] is False
    assert body["checks"] == []
    assert _ends_with_z(body["checked_at"])


def test_health_enabled_missing_model_returns_503(monkeypatch, client):
    """Test health returns 503 when enabled but model file missing."""
    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.setenv("LLM_MODEL_PATH", "/fake/model.bin")

    # Simulate missing file
    with patch.object(Path, "exists", return_value=False):
        r = client.get("/api/v1/llm/health")
        assert r.status_code == 503
        body = r.json()
        assert body["ok"] is False and body["llm_enabled"] is True and body["ready"] is False
        assert any(c["name"] == "model_path" and c["ok"] is False for c in body["checks"])
        assert _ends_with_z(body["checked_at"])


def test_health_enabled_ready_returns_200(monkeypatch, client):
    """Test health returns 200 when enabled and ready."""
    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.setenv("LLM_MODEL_PATH", "/fake/model.bin")

    # Pretend the model exists and provider is ready
    with patch.object(Path, "exists", return_value=True):
        r = client.get("/api/v1/llm/health")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True and body["ready"] is True and body["llm_enabled"] is True
        assert any(c["name"] == "model_path" and c["ok"] is True for c in body["checks"])
        assert _ends_with_z(body["checked_at"])


def test_health_internal_error_returns_500(monkeypatch, client):
    """Test health returns 500 on internal errors."""
    monkeypatch.setenv("LLM_ENABLED", "true")

    # Mock provider to raise exception
    from core.llm.service import LLMService

    class BoomProvider:
        def health(self):
            raise RuntimeError("boom")
        def suggest(self, prompt: str):
            return {}

    original_resolve = LLMService.__init__

    def mock_init(self):
        original_resolve(self)
        self.provider = BoomProvider()

    monkeypatch.setattr(LLMService, "__init__", mock_init)

    r = client.get("/api/v1/llm/health")
    assert r.status_code == 500
    body = r.json()
    assert body["ok"] is False and body["error"] == "internal" and _ends_with_z(body["checked_at"])


def test_health_dual_mount_root_path(monkeypatch, client):
    """Test that health endpoint works at root path (dual-mount)."""
    # Explicitly disable LLM
    monkeypatch.setenv("LLM_ENABLED", "false")
    r = client.get("/llm/health")
    assert r.status_code == 503
    body = r.json()
    assert body["ok"] is False and body["llm_enabled"] is False
    assert _ends_with_z(body["checked_at"])


def test_health_dual_mount_api_path(monkeypatch, client):
    """Test that health endpoint works at /api/v1 path (dual-mount)."""
    # Explicitly disable LLM
    monkeypatch.setenv("LLM_ENABLED", "false")
    r = client.get("/api/v1/llm/health")
    assert r.status_code == 503
    body = r.json()
    assert body["ok"] is False and body["llm_enabled"] is False
    assert _ends_with_z(body["checked_at"])


def test_fill_triage_actions_503_when_disabled(monkeypatch, client):
    """Test fill-triage-actions returns 503 when LLM disabled."""
    monkeypatch.setenv("LLM_ENABLED", "false")

    payload = {
        "root": "Test Root",
        "nodes": ["Node 1", "Node 2"],
        "apply": False
    }

    r = client.post("/api/v1/llm/fill-triage-actions", json=payload)
    assert r.status_code == 503


def test_fill_triage_actions_422_non_leaf_apply(monkeypatch, client):
    """Test fill-triage-actions returns 422 for non-leaf apply with suggestions."""
    monkeypatch.setenv("LLM_ENABLED", "true")

    # Mock the database connection and cursor
    from unittest.mock import MagicMock
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (False,)  # is_leaf = False
    mock_conn.cursor.return_value = mock_cursor

    # Create a context manager mock
    from unittest.mock import MagicMock
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_conn
    mock_context.__exit__.return_value = None

    with patch("api.routers.llm.get_db_connection", return_value=mock_context):
        payload = {
            "root": "Test Root",
            "nodes": ["Node 1", "Node 2", "Node 3", "Node 4", "Node 5"],  # Exactly 5 nodes required
            "apply": True,
            "node_id": 1
        }

        r = client.post("/api/v1/llm/fill-triage-actions", json=payload)
        assert r.status_code == 422
        body = r.json()
        assert "Cannot apply triage/actions to non-leaf node" in body["error"]
        assert "diagnostic_triage" in body
        assert "actions" in body


def test_fill_triage_actions_success_no_apply(monkeypatch, client):
    """Test fill-triage-actions success without apply."""
    monkeypatch.setenv("LLM_ENABLED", "true")

    payload = {
        "root": "Test Root",
        "nodes": ["Node 1", "Node 2", "Node 3", "Node 4", "Node 5"],  # Exactly 5 nodes required
        "apply": False
    }

    r = client.post("/api/v1/llm/fill-triage-actions", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "diagnostic_triage" in body
    assert "actions" in body
    assert body["applied"] is False


def test_fill_triage_actions_missing_node_id_apply(monkeypatch, client):
    """Test fill-triage-actions requires node_id when apply=true."""
    monkeypatch.setenv("LLM_ENABLED", "true")

    payload = {
        "root": "Test Root",
        "nodes": ["Node 1", "Node 2", "Node 3", "Node 4", "Node 5"],  # Exactly 5 nodes required
        "apply": True
        # Missing node_id
    }

    r = client.post("/api/v1/llm/fill-triage-actions", json=payload)
    assert r.status_code == 422  # Pydantic validation errors return 422
    response_data = r.json()
    assert "detail" in response_data
    # Pydantic validation error should mention node_id requirement
    assert any("node_id" in str(error) for error in response_data["detail"])
