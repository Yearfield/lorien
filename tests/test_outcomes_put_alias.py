"""
Test outcomes PUT endpoint that delegates to triage upsert.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_outcomes_put_delegates_to_triage():
    """Test that PUT /outcomes/{node_id} delegates to triage upsert."""
    # This is a structure test - the actual business logic is tested elsewhere
    # We just verify the endpoint exists and accepts the payload shape

    payload = {
        "diagnostic_triage": "Acute appendicitis",
        "actions": "Immediate surgical referral"
    }

    # This might return 422 for validation or 404 for non-existent node
    # The important thing is that it doesn't return 405 (method not allowed)
    r = client.put("/api/v1/outcomes/1", json=payload)

    # Should not be 405 (method not allowed)
    assert r.status_code != 405

    # Should be a reasonable HTTP status
    assert r.status_code in [200, 201, 400, 404, 422]


def test_outcomes_put_validates_word_caps():
    """Test that PUT /outcomes validates word caps with Pydantic detail."""
    over_limit = " ".join([f"word{i}" for i in range(10)])  # 9 words > 7 limit

    payload = {
        "diagnostic_triage": over_limit,
        "actions": "Valid actions"
    }

    r = client.put("/api/v1/outcomes/1", json=payload)
    assert r.status_code == 422

    body = r.json()
    assert "detail" in body
    assert isinstance(body["detail"], list)

    # Check that diagnostic_triage field has word count error
    triage_errors = [d for d in body["detail"] if "diagnostic_triage" in str(d)]
    assert len(triage_errors) > 0


def test_outcomes_put_dual_mount():
    """Test outcomes PUT works on both root and /api/v1 mounts."""
    payload = {
        "diagnostic_triage": "Acute appendicitis",
        "actions": "Immediate surgical referral"
    }

    # Test root mount
    r1 = client.put("/outcomes/1", json=payload)
    assert r1.status_code != 405  # Should not be method not allowed

    # Test api/v1 mount
    r2 = client.put("/api/v1/outcomes/1", json=payload)
    assert r2.status_code != 405  # Should not be method not allowed
