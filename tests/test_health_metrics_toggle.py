"""
Test health endpoint metrics toggle functionality.
"""

import os
from fastapi.testclient import TestClient
from api.app import app

def test_metrics_hidden_by_default(monkeypatch):
    """Test that metrics are hidden when ANALYTICS_ENABLED is not set."""
    monkeypatch.delenv("ANALYTICS_ENABLED", raising=False)
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    
    # When analytics is disabled, metrics field should be None or absent
    data = r.json()
    if "metrics" in data:
        assert data["metrics"] is None or data["metrics"] == {}
    else:
        assert "metrics" not in data

def test_metrics_present_when_enabled(monkeypatch):
    """Test that metrics are present when ANALYTICS_ENABLED is true."""
    monkeypatch.setenv("ANALYTICS_ENABLED", "true")
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert "metrics" in r.json()

def test_metrics_structure_when_enabled(monkeypatch):
    """Test that metrics have the expected structure when enabled."""
    monkeypatch.setenv("ANALYTICS_ENABLED", "true")
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    
    metrics = r.json().get("metrics", {})
    assert "telemetry" in metrics
    assert "table_counts" in metrics
    assert "audit_retention" in metrics
    assert "cache" in metrics

def test_metrics_api_v1_mount(monkeypatch):
    """Test that metrics work at /api/v1/health mount."""
    monkeypatch.setenv("ANALYTICS_ENABLED", "true")
    client = TestClient(app)
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert "metrics" in r.json()

def test_metrics_root_mount(monkeypatch):
    """Test that metrics work at root /health mount."""
    monkeypatch.setenv("ANALYTICS_ENABLED", "true")
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert "metrics" in r.json()
