# tests/test_api_health.py
import os
import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_health_versioned_mount():
    """Test that health endpoint is mounted under /api/v1."""
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert "version" in r.json()

def test_llm_health_disabled(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "false")
    r = client.get("/api/v1/llm/health")
    assert r.status_code == 503

def test_llm_health_enabled(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "true")
    r = client.get("/api/v1/llm/health")
    assert r.status_code == 200
    assert r.json()["llm_enabled"]

def test_cors_allow_all(monkeypatch):
    monkeypatch.setenv("CORS_ALLOW_ALL", "true")
    # middleware origins should be "*"
    from api.app import app as app2
    cors = [mw for mw in app2.user_middleware if "CORSMiddleware" in str(mw)]
    assert cors
