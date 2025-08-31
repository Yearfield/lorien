"""
Tests for triage character caps validation.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_put_triage_rejects_over_caps():
    """Test that PUT /triage/{node_id} rejects text over character caps."""
    node_id = 1
    
    # Test diagnostic triage over 600 chars
    over_triage = "x" * 601
    r = client.put(f"/api/v1/triage/{node_id}", json={
        "diagnostic_triage": over_triage, 
        "actions": "ok"
    })
    assert r.status_code in (400, 422)
    assert "600" in r.text
    
    # Test actions over 800 chars
    over_actions = "y" * 801
    r2 = client.put(f"/api/v1/triage/{node_id}", json={
        "diagnostic_triage": "ok", 
        "actions": over_actions
    })
    assert r2.status_code in (400, 422)
    assert "800" in r2.text

def test_put_triage_accepts_valid_caps():
    """Test that PUT /triage/{node_id} accepts text at character caps."""
    node_id = 1
    
    # Test diagnostic triage at exactly 600 chars
    exact_triage = "x" * 600
    r = client.put(f"/api/v1/triage/{node_id}", json={
        "diagnostic_triage": exact_triage, 
        "actions": "ok"
    })
    # This might fail for other reasons (node not found, not a leaf, etc.)
    # but should not fail due to character caps
    if r.status_code == 422:
        assert "600" not in r.text  # Should not be a cap validation error
    
    # Test actions at exactly 800 chars
    exact_actions = "y" * 800
    r2 = client.put(f"/api/v1/triage/{node_id}", json={
        "diagnostic_triage": "ok", 
        "actions": exact_actions
    })
    # This might fail for other reasons but should not fail due to character caps
    if r2.status_code == 422:
        assert "800" not in r2.text  # Should not be a cap validation error
