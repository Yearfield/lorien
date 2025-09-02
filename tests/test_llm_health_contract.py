"""
Test LLM health endpoint contracts.
"""

from pathlib import Path
import os
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_health_disabled_503(monkeypatch, client):
    """Test health returns 503 when LLM_ENABLED=false."""
    monkeypatch.setenv("LLM_ENABLED", "false")
    r = client.get("/api/v1/llm/health")
    assert r.status_code == 503
    j = r.json()
    assert j["ok"] is False and "checked_at" in j


def test_health_enabled_missing_model_503(monkeypatch, client):
    """Test health returns 503 when enabled but model file missing."""
    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.setenv("LLM_MODEL_PATH", "/fake/model.bin")

    # Mock Path.exists to return False
    original_exists = Path.exists
    Path.exists = lambda self: False

    try:
        r = client.get("/api/v1/llm/health")
        assert r.status_code == 503
        assert r.json()["ready"] is False
    finally:
        Path.exists = original_exists


def test_health_enabled_ready_200(monkeypatch, client):
    """Test health returns 200 when enabled and model exists."""
    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.setenv("LLM_MODEL_PATH", "/fake/model.bin")

    # Mock Path.exists to return True
    original_exists = Path.exists
    Path.exists = lambda self: True

    try:
        r = client.get("/api/v1/llm/health")
        assert r.status_code == 200
        assert r.json()["ok"] is True and "checked_at" in r.json()
    finally:
        Path.exists = original_exists


def test_health_checked_at_format(monkeypatch, client):
    """Test that checked_at is in ISO-8601 format."""
    monkeypatch.setenv("LLM_ENABLED", "false")
    r = client.get("/api/v1/llm/health")

    checked_at = r.json()["checked_at"]
    assert checked_at.endswith("Z")  # ISO-8601 UTC indicator
