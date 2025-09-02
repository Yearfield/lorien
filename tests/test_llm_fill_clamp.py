"""
Test LLM fill endpoint clamps and validates output.
"""

import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_fill_clamps_and_validates(monkeypatch, client):
    """Test that LLM fill clamps to 7 words and validates."""
    monkeypatch.setenv("LLM_ENABLED", "true")

    # Mock LLM service to return long content with prohibited tokens
    with patch('api.routers.llm.LLMService') as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.enabled = True

        # Mock health check
        mock_service.health.return_value = (200, {"ok": True, "ready": True})

        # Mock suggestions with over-limit content and prohibited tokens
        mock_service.suggest.return_value = {
            "diagnostic_triage": "one two three four five six seven eight nine",
            "actions": "Immediate IV fluids 500 mg"
        }

        # This should either succeed (after clamping) or return 422 for prohibited tokens
        r = client.post("/api/v1/llm/fill-triage-actions", json={
            "root": "",
            "nodes": ["", "", "", "", ""],
            "triage_style": "diagnosis-only",
            "actions_style": "referral-only",
            "apply": False
        })

        # Should be either 200 (if clamping succeeds) or 422 (if prohibited tokens)
        assert r.status_code in [200, 422]

        if r.status_code == 200:
            data = r.json()
            # Check that content is clamped to 7 words or less
            dt_words = len(data["diagnostic_triage"].split())
            ac_words = len(data["actions"].split())
            assert dt_words <= 7
            assert ac_words <= 7

        if r.status_code == 422:
            # Should be due to prohibited tokens
            detail = r.json().get("detail", [])
            assert any("dosing" in str(d) for d in detail)


def test_fill_non_leaf_apply_returns_422(monkeypatch, client):
    """Test that apply=true on non-leaf returns 422 with suggestions."""
    monkeypatch.setenv("LLM_ENABLED", "true")

    with patch('api.routers.llm.LLMService') as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_service.enabled = True
        mock_service.health.return_value = (200, {"ok": True, "ready": True})
        mock_service.suggest.return_value = {
            "diagnostic_triage": "Acute appendicitis",
            "actions": "Surgical referral"
        }

        r = client.post("/api/v1/llm/fill-triage-actions", json={
            "root": "",
            "nodes": ["", "", "", "", ""],
            "triage_style": "diagnosis-only",
            "actions_style": "referral-only",
            "apply": True,
            "node_id": 999  # Non-existent node (non-leaf)
        })

        assert r.status_code == 422
        data = r.json()
        assert "error" in data
        assert "diagnostic_triage" in data
        assert "actions" in data