"""
Test LLM fill apply on non-leaf returning 422 with suggestions.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_llm_apply_non_leaf_returns_422_with_suggestions_top_level():
    """Test that LLM apply=true on non-leaf returns 422 with suggestions at top-level."""
    payload = {
        "root": "Pulse",
        "nodes": ["Fast", "Irregular", "", "", ""],
        "triage_style": "diagnosis-only",
        "actions_style": "referral-only",
        "apply": True
    }
    
    r = client.post("/api/v1/llm/fill-triage-actions", json=payload)
    assert r.status_code == 422
    
    j = r.json()
    # PM contract: 422 with suggestions at TOP-LEVEL + error string
    assert "error" in j
    assert "diagnostic_triage" in j
    assert "actions" in j
    
    # Check error message
    assert "Cannot apply triage/actions to non-leaf node" in j["error"]
    
    # Check suggestions are present
    assert isinstance(j["diagnostic_triage"], str)
    assert isinstance(j["actions"], str)
    assert len(j["diagnostic_triage"]) > 0
    assert len(j["actions"]) > 0

def test_llm_apply_false_returns_200_with_suggestions():
    """Test that LLM apply=false returns 200 with suggestions."""
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
    assert "diagnostic_triage" in j
    assert "actions" in j
    assert "error" not in j

def test_llm_fill_word_limits_enforced():
    """Test that LLM fill enforces word limits."""
    payload = {
        "root": "Test",
        "nodes": ["A", "B", "C", "D", "E"],
        "triage_style": "diagnosis-only",
        "actions_style": "referral-only",
        "apply": False
    }
    
    r = client.post("/api/v1/llm/fill-triage-actions", json=payload)
    assert r.status_code == 200
    
    j = r.json()
    
    # Check that suggestions are within word limits
    triage_words = len(j["diagnostic_triage"].split())
    actions_words = len(j["actions"].split())
    
    assert triage_words <= 7, f"Triage has {triage_words} words, expected ≤7"
    assert actions_words <= 7, f"Actions has {actions_words} words, expected ≤7"
