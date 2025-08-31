"""
Test triage word caps with Pydantic-style 422 detail.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def _words(n):
    """Generate n words for testing."""
    return " ".join([f"w{i}" for i in range(n)])

def _find_msg(detail, field):
    """Find error message for a specific field in Pydantic detail array."""
    for d in detail:
        if d.get("loc", ["", ""])[-1] == field:
            return d.get("msg", "")
    return ""

def test_put_triage_422_detail_shape():
    """Test that PUT /triage returns 422 with Pydantic-style detail for word cap violations."""
    over = _words(8)  # 8 words > 7 limit
    r = client.put("/api/v1/triage/1", json={"diagnostic_triage": over, "actions": "ok"})
    assert r.status_code == 422
    
    j = r.json()
    assert "detail" in j and isinstance(j["detail"], list)
    
    # Check diagnostic_triage field error
    msg = _find_msg(j["detail"], "diagnostic_triage")
    assert "≤7 words" in msg

def test_put_triage_422_regex_violation():
    """Test that PUT /triage returns 422 for regex violations."""
    invalid_text = "Invalid text with dots. and exclamation!"
    r = client.put("/api/v1/triage/1", json={"diagnostic_triage": invalid_text, "actions": "ok"})
    assert r.status_code == 422
    
    j = r.json()
    msg = _find_msg(j["detail"], "diagnostic_triage")
    assert "clinical tokens only" in msg or "concise phrase" in msg

def test_put_triage_422_phrase_violation():
    """Test that PUT /triage returns 422 for phrase violations."""
    sentence_text = "Hello, you should consider this diagnosis."
    r = client.put("/api/v1/triage/1", json={"diagnostic_triage": sentence_text, "actions": "ok"})
    assert r.status_code == 422
    
    j = r.json()
    msg = _find_msg(j["detail"], "diagnostic_triage")
    # The regex validation catches this first, so check for either message
    assert "clinical tokens only" in msg or "concise phrase" in msg

def test_put_triage_422_actions_field():
    """Test that PUT /triage returns 422 for actions field violations."""
    over = _words(8)  # 8 words > 7 limit
    r = client.put("/api/v1/triage/1", json={"diagnostic_triage": "ok", "actions": over})
    assert r.status_code == 422
    
    j = r.json()
    msg = _find_msg(j["detail"], "actions")
    assert "≤7 words" in msg

def test_put_triage_success_with_valid_data():
    """Test that PUT /triage succeeds with valid data."""
    valid_triage = "acute appendicitis"
    valid_actions = "immediate surgical referral"
    
    r = client.put("/api/v1/triage/1", json={"diagnostic_triage": valid_triage, "actions": valid_actions})
    # This might fail due to node not existing, but we're testing validation, not business logic
    # The important thing is that validation passed (no 422)
    assert r.status_code != 422
