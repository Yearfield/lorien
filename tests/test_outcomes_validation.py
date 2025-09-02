"""
Test outcomes validation with word caps, regex, and dosing token bans.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_put_outcomes_rejects_over_7_words(client):
    """Test that PUT /triage rejects over 7 words."""
    body = {"diagnostic_triage": "one two three four five six seven eight", "actions": "Short"}
    r = client.put("/api/v1/triage/1", json=body)
    assert r.status_code == 422
    assert any("≤7 words" in (d.get("msg", "") or "") for d in r.json().get("detail", []))


def test_put_outcomes_rejects_dosing_tokens(client):
    """Test that PUT /triage rejects dosing tokens."""
    body = {"diagnostic_triage": "Acute pain", "actions": "Paracetamol 500 mg"}
    r = client.put("/api/v1/triage/1", json=body)
    assert r.status_code == 422
    assert any("dosing" in (d.get("msg", "") or "") for d in r.json().get("detail", []))


def test_put_outcomes_rejects_invalid_chars(client):
    """Test that PUT /triage rejects invalid characters."""
    body = {"diagnostic_triage": "Acute pain!", "actions": "Refer to specialist"}
    r = client.put("/api/v1/triage/1", json=body)
    assert r.status_code == 422
    assert any("invalid characters" in (d.get("msg", "") or "") for d in r.json().get("detail", []))


def test_put_outcomes_accepts_valid_input(client):
    """Test that PUT /triage accepts valid input."""
    body = {"diagnostic_triage": "Acute appendicitis", "actions": "Surgical referral"}
    r = client.put("/api/v1/triage/1", json=body)
    # This might return 404 if node doesn't exist, but validation should pass
    assert r.status_code != 422
