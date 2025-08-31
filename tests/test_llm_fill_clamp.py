"""
Tests for LLM fill character clamping and apply functionality.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_llm_fill_clamps_lengths_and_returns_json():
    """Test that LLM fill clamps text lengths and returns proper JSON."""
    payload = {
        "root": "Pulse",
        "nodes": ["Fast", "Irregular", "", "", ""],
        "triage_style": "diagnosis-only",
        "actions_style": "referral-only",
        "apply": False
    }
    
    r = client.post("/api/v1/llm/fill-triage-actions", json=payload)
    assert r.status_code == 200
    j = r.json()
    assert len(j["diagnostic_triage"]) <= 600
    assert len(j["actions"]) <= 800

def test_llm_fill_apply_non_leaf_returns_422_but_includes_suggestions():
    """Test that LLM fill with apply=true returns 422 for non-leaf but includes suggestions."""
    payload = {
        "root": "Pulse",
        "nodes": ["Fast", "Irregular", "", "", ""],
        "triage_style": "diagnosis-only",
        "actions_style": "referral-only",
        "apply": True
    }
    
    r = client.post("/api/v1/llm/fill-triage-actions", json=payload)
    assert r.status_code in (400, 422)
    
    # Suggestions should still be present in detail payload or response JSON
    data = r.json()
    if "diagnostic_triage" in data and "actions" in data:
        # Direct response format
        assert len(data["diagnostic_triage"]) <= 600
        assert len(data["actions"]) <= 800
    else:
        # Wrapped in detail format
        assert "detail" in data
        detail = data["detail"]
        if isinstance(detail, dict):
            assert "diagnostic_triage" in detail and "actions" in detail
            assert len(detail["diagnostic_triage"]) <= 600
            assert len(detail["actions"]) <= 800

def test_llm_fill_validates_style_values():
    """Test that LLM fill validates triage_style and actions_style values."""
    # Test invalid triage_style
    payload = {
        "root": "Pulse",
        "nodes": ["Fast", "Irregular", "", "", ""],
        "triage_style": "invalid-style",
        "actions_style": "referral-only",
        "apply": False
    }
    
    r = client.post("/api/v1/llm/fill-triage-actions", json=payload)
    assert r.status_code == 400
    assert "diagnosis-only" in r.text or "referral-only" in r.text
    
    # Test invalid actions_style
    payload2 = {
        "root": "Pulse",
        "nodes": ["Fast", "Irregular", "", "", ""],
        "triage_style": "diagnosis-only",
        "actions_style": "invalid-style",
        "apply": False
    }
    
    r2 = client.post("/api/v1/llm/fill-triage-actions", json=payload2)
    assert r2.status_code == 400
    assert "diagnosis-only" in r2.text or "referral-only" in r2.text

def test_llm_fill_requires_exactly_5_nodes():
    """Test that LLM fill requires exactly 5 nodes."""
    # Test with 4 nodes
    payload = {
        "root": "Pulse",
        "nodes": ["Fast", "Irregular", "", ""],
        "triage_style": "diagnosis-only",
        "actions_style": "referral-only",
        "apply": False
    }
    
    r = client.post("/api/v1/llm/fill-triage-actions", json=payload)
    assert r.status_code == 400
    assert "5 nodes" in r.text
    
    # Test with 6 nodes
    payload2 = {
        "root": "Pulse",
        "nodes": ["Fast", "Irregular", "", "", "", "Extra"],
        "triage_style": "diagnosis-only",
        "actions_style": "referral-only",
        "apply": False
    }
    
    r2 = client.post("/api/v1/llm/fill-triage-actions", json=payload2)
    assert r2.status_code == 400
    assert "5 nodes" in r2.text
