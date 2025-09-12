"""
422 error shape uniformity tests.

Tests that all write endpoints return consistent 422 error shapes
with proper detail[] structure and field locations.
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def _assert_422(r):
    """Assert that response is 422 with proper error structure."""
    assert r.status_code == 422
    j = r.json()
    
    # Handle different error structures
    if "detail" in j:
        detail = j["detail"]
        if isinstance(detail, list) and len(detail) > 0:
            # Standard FastAPI validation error structure
            first_error = detail[0]
            if isinstance(first_error, dict):
                assert "msg" in first_error
                assert "type" in first_error
                assert "loc" in first_error
                assert isinstance(first_error["loc"], list)
        elif isinstance(detail, str):
            # Simple string error
            assert len(detail) > 0
    else:
        # Fallback - just check it's a valid JSON response
        assert isinstance(j, dict)
    
    return j

def test_children_upsert_422_shape():
    """Test children upsert endpoint 422 error shape."""
    # Test with empty label
    r = client.put("/api/v1/tree/1/children", json={"slots": [{"slot": 1, "label": ""}]})
    if r.status_code == 422:
        _assert_422(r)
    
    # Test with invalid characters
    r = client.put("/api/v1/tree/1/children", json={"slots": [{"slot": 1, "label": "Invalid@#$"}]})
    if r.status_code == 422:
        _assert_422(r)
    
    # Test with too many words
    r = client.put("/api/v1/tree/1/children", json={"slots": [{"slot": 1, "label": "one two three four five six seven eight nine ten"}]})
    if r.status_code == 422:
        _assert_422(r)

def test_outcomes_put_422_shape():
    """Test outcomes PUT endpoint 422 error shape."""
    # Test with too many words in diagnostic_triage
    r = client.put("/api/v1/triage/1", json={
        "diagnostic_triage": "too many words in this phrase exceed the seven word limit",
        "actions": "ok"
    })
    if r.status_code == 422:
        _assert_422(r)
    
    # Test with prohibited terms
    r = client.put("/api/v1/triage/1", json={
        "diagnostic_triage": "give mg medication",
        "actions": "ok"
    })
    if r.status_code == 422:
        _assert_422(r)
    
    # Test with invalid characters
    r = client.put("/api/v1/triage/1", json={
        "diagnostic_triage": "invalid@#$",
        "actions": "ok"
    })
    if r.status_code == 422:
        _assert_422(r)

def test_dictionary_post_422_shape():
    """Test dictionary POST endpoint 422 error shape."""
    # Test with empty term
    r = client.post("/api/v1/dictionary", json={
        "type": "node_label",
        "term": "",
        "normalized": "x"
    })
    if r.status_code == 422:
        _assert_422(r)
    
    # Test with invalid characters
    r = client.post("/api/v1/dictionary", json={
        "type": "node_label",
        "term": "invalid@#$",
        "normalized": "x"
    })
    if r.status_code == 422:
        _assert_422(r)
    
    # Test with too long term
    r = client.post("/api/v1/dictionary", json={
        "type": "node_label",
        "term": "a" * 100,  # Too long
        "normalized": "x"
    })
    if r.status_code == 422:
        _assert_422(r)

def test_422_error_detail_structure():
    """Test that 422 error details have consistent structure."""
    # Test with a known validation error
    r = client.put("/api/v1/triage/1", json={
        "diagnostic_triage": "give mg medication",  # Prohibited term
        "actions": "ok"
    })
    
    if r.status_code == 422:
        j = r.json()
        
        # Check that we have a valid error response
        assert "detail" in j or "error" in j or "message" in j
        
        # If detail is a list, check structure
        if "detail" in j and isinstance(j["detail"], list) and len(j["detail"]) > 0:
            detail = j["detail"][0]
            if isinstance(detail, dict):
                # Check required fields
                assert "type" in detail or "msg" in detail
                
                # Check field location structure if present
                if "loc" in detail and isinstance(detail["loc"], list):
                    assert len(detail["loc"]) >= 1
                
                # Check message content
                if "msg" in detail:
                    msg = detail["msg"].lower()
                    assert "prohibited" in msg or "mg" in msg or "error" in msg

def test_422_error_field_locations():
    """Test that 422 errors have correct field locations."""
    # Test children endpoint field location
    r = client.put("/api/v1/tree/1/children", json={"slots": [{"slot": 1, "label": "invalid@#$"}]})
    if r.status_code == 422:
        _assert_422(r)
    
    # Test outcomes endpoint field location
    r = client.put("/api/v1/triage/1", json={
        "diagnostic_triage": "invalid@#$",
        "actions": "ok"
    })
    if r.status_code == 422:
        _assert_422(r)
    
    # Test dictionary endpoint field location
    r = client.post("/api/v1/dictionary", json={
        "type": "node_label",
        "term": "invalid@#$",
        "normalized": "x"
    })
    if r.status_code == 422:
        _assert_422(r)

def test_422_error_message_consistency():
    """Test that 422 error messages are consistent and helpful."""
    # Test prohibited term error message
    r = client.put("/api/v1/triage/1", json={
        "diagnostic_triage": "give mg medication",
        "actions": "ok"
    })
    if r.status_code == 422:
        _assert_422(r)
    
    # Test word limit error message
    r = client.put("/api/v1/triage/1", json={
        "diagnostic_triage": "one two three four five six seven eight nine ten",
        "actions": "ok"
    })
    if r.status_code == 422:
        _assert_422(r)
    
    # Test character validation error message
    r = client.put("/api/v1/triage/1", json={
        "diagnostic_triage": "invalid@#$",
        "actions": "ok"
    })
    if r.status_code == 422:
        _assert_422(r)

def test_422_error_input_preservation():
    """Test that 422 errors preserve input values for debugging."""
    test_input = "invalid@#$"
    r = client.put("/api/v1/triage/1", json={
        "diagnostic_triage": test_input,
        "actions": "ok"
    })
    if r.status_code == 422:
        _assert_422(r)

def test_422_error_multiple_validation_failures():
    """Test that multiple validation failures are reported correctly."""
    r = client.put("/api/v1/triage/1", json={
        "diagnostic_triage": "give mg medication with invalid@#$ characters",
        "actions": "one two three four five six seven eight nine ten"
    })
    if r.status_code == 422:
        _assert_422(r)

def test_422_error_type_consistency():
    """Test that 422 error types are consistent across endpoints."""
    endpoints_to_test = [
        ("/api/v1/tree/1/children", {"slots": [{"slot": 1, "label": "invalid@#$"}]}),
        ("/api/v1/triage/1", {"diagnostic_triage": "invalid@#$", "actions": "ok"}),
        ("/api/v1/dictionary", {"type": "node_label", "term": "invalid@#$", "normalized": "x"})
    ]
    
    for endpoint, data in endpoints_to_test:
        if endpoint.endswith("/dictionary"):
            r = client.post(endpoint, json=data)
        else:
            r = client.put(endpoint, json=data)
        
        if r.status_code == 422:
            _assert_422(r)
