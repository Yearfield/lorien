"""
Test outcomes validation rejects dosing/route/time tokens.
"""

from fastapi.testclient import TestClient
from api.app import app

c = TestClient(app)

def test_outcomes_put_rejects_dosing_tokens():
    # Test various prohibited tokens
    prohibited_cases = [
        ("Acute mg issue", "mg"),
        ("Immediate IV referral", "iv"),
        ("Take q6h", "q6h"),
        ("Give 5 ml", "ml"),
        ("PO medication", "po"),
        ("IM injection", "im"),
        ("SC dose", "sc"),
        ("PR route", "pr"),
        ("STAT order", "stat"),
        ("qid dosing", "qid"),
        ("tid schedule", "tid"),
        ("bid frequency", "bid"),
        ("od daily", "od"),
        ("qod alternate", "qod"),
        ("prn as needed", "prn"),
    ]

    for text, token in prohibited_cases:
        r = c.put("/api/v1/outcomes/9999", json={"diagnostic_triage": text, "actions": "Some action"})
        assert r.status_code == 422, f"Expected 422 for '{text}' containing '{token}'"
        detail = r.json()["detail"]
        assert len(detail) > 0
        assert "dosing" in detail[0]["msg"].lower() or "route" in detail[0]["msg"].lower()

        r2 = c.put("/api/v1/outcomes/9999", json={"diagnostic_triage": "Some triage", "actions": text})
        assert r2.status_code == 422, f"Expected 422 for actions '{text}' containing '{token}'"


def test_outcomes_put_allows_valid_phrases():
    # Test that valid phrases without prohibited tokens are accepted
    valid_cases = [
        "Acute appendicitis",
        "Surgical consultation needed",
        "Emergency department referral",
        "Medical management required",
        "Clinical observation indicated",
    ]

    for text in valid_cases:
        r = c.put("/api/v1/outcomes/9999", json={"diagnostic_triage": text, "actions": "Monitor patient"})
        # Should not be 422 due to prohibited tokens (though may fail for other reasons like node not found)
        if r.status_code == 422:
            detail = r.json()["detail"]
            # If it's a list of validation errors, check for prohibited token errors
            if isinstance(detail, list):
                for d in detail:
                    msg = d["msg"].lower()
                    assert "dosing" not in msg
                    assert "route" not in msg
            # If it's a string, it's a business logic error (like "leaf nodes only")
            elif isinstance(detail, str):
                assert "dosing" not in detail.lower()
                assert "route" not in detail.lower()


def test_outcomes_validation_combines_with_other_rules():
    # Test that word count validation takes precedence over prohibited tokens
    # This tests a phrase that's too long AND contains prohibited tokens
    long_text = "This is a very long diagnostic triage that exceeds seven words and contains mg dosing"
    r = c.put("/api/v1/outcomes/9999", json={"diagnostic_triage": long_text, "actions": "Some action"})
    assert r.status_code == 422
    detail = r.json()["detail"]
    # Should have word count validation error (first in chain)
    assert len(detail) == 1
    assert "7 words" in detail[0]["msg"]
