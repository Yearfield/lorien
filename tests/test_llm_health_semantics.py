"""
Test LLM health endpoint semantics with ready/checked_at.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_llm_health_503_has_ready_and_checked_at(monkeypatch):
    """Test health returns 503 when LLM_ENABLED=false with ready/checked_at."""
    monkeypatch.setenv("LLM_ENABLED", "false")
    r = client.get("/api/v1/llm/health")
    assert r.status_code == 503

    body = r.json()
    assert body["ready"] is False
    assert body["ok"] is False  # Backwards compatibility
    assert body["llm_enabled"] is False  # Backwards compatibility
    assert "checked_at" in body
    assert body["checked_at"].endswith("Z")  # ISO-8601 UTC


def test_llm_health_200_has_ready_and_checked_at(monkeypatch):
    """Test health returns 200 when LLM_ENABLED=true with ready/checked_at."""
    monkeypatch.setenv("LLM_ENABLED", "true")
    r = client.get("/api/v1/llm/health")
    assert r.status_code == 200

    body = r.json()
    assert body["ready"] is True
    assert body["ok"] is True  # Backwards compatibility
    assert body["llm_enabled"] is True  # Backwards compatibility
    assert "checked_at" in body
    assert body["checked_at"].endswith("Z")  # ISO-8601 UTC


def test_llm_health_dual_mount_root(monkeypatch):
    """Test LLM health works on root mount /llm/health."""
    monkeypatch.setenv("LLM_ENABLED", "false")
    r = client.get("/llm/health")
    assert r.status_code == 503

    body = r.json()
    assert body["ready"] is False
    assert "checked_at" in body


def test_llm_health_dual_mount_api_v1(monkeypatch):
    """Test LLM health works on /api/v1 mount."""
    monkeypatch.setenv("LLM_ENABLED", "true")
    r = client.get("/api/v1/llm/health")
    assert r.status_code == 200

    body = r.json()
    assert body["ready"] is True
    assert "checked_at" in body
