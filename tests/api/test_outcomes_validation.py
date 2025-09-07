"""
Test outcomes server rules (still enforced).

Verifies that PUT with over-long (>7 words) or dosing tokens returns 422.
"""

import pytest
import requests


@pytest.fixture
def base_url():
    return "http://127.0.0.1:8000/api/v1"


def test_outcomes_validation_overlong_text(base_url):
    """Test that outcomes validation rejects over-long text (>7 words)."""

    # Create over-long text (>7 words)
    overlong_text = "This is a very long diagnostic triage that exceeds the seven word limit and should be rejected by the server validation rules."

    payload = {
        "diagnostic_triage": overlong_text,
        "actions": "Some action"
    }

    # Try to update outcomes
    response = requests.put(
        f"{base_url}/outcomes/1",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print(f"Overlong text response status: {response.status_code}")
    print(f"Overlong text response body: {response.text}")

    # Should return 422 for validation error
    assert response.status_code == 422


def test_outcomes_validation_dosing_tokens(base_url):
    """Test that outcomes validation rejects dosing tokens."""

    payload = {
        "diagnostic_triage": "Some diagnosis with take 5mg dosage",
        "actions": "Some action"
    }

    response = requests.put(
        f"{base_url}/outcomes/1",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print(f"Dosing token response status: {response.status_code}")

    # Should return 422 for dosing token error
    assert response.status_code == 422