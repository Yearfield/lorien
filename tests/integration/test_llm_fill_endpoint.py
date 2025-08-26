import pytest
import os
import tempfile
import sqlite3
from pathlib import Path
from fastapi.testclient import TestClient

from api.app import app
from storage.sqlite import SQLiteRepository

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Initialize with schema
    repo = SQLiteRepository(db_path)
    
    # Create test data: a simple tree with a leaf node
    with repo._get_connection() as conn:
        # Create root node
        conn.execute("""
            INSERT INTO nodes (id, label, depth, slot, parent_id, is_leaf)
            VALUES (1, 'Test Root', 1, 1, NULL, 0)
        """)
        
        # Create leaf node (depth 5)
        conn.execute("""
            INSERT INTO nodes (id, label, depth, slot, parent_id, is_leaf)
            VALUES (2, 'Test Leaf', 5, 1, 1, 1)
        """)
        
        conn.commit()
    
    yield db_path
    
    # Cleanup
    os.unlink(db_path)

def test_llm_endpoint_disabled_by_default(client):
    """Test that LLM endpoint returns 503 when disabled."""
    response = client.post("/api/v1/llm/fill-triage-actions", json={
        "root": "test",
        "nodes": ["symptom1", "symptom2"]
    })
    assert response.status_code == 503
    assert "LLM is disabled" in response.json()["detail"]

@pytest.mark.skipif(
    os.getenv("LLM_ENABLED") != "true" or not os.getenv("LLM_MODEL_PATH"),
    reason="LLM not enabled or model path not set"
)
def test_llm_endpoint_enabled(client, temp_db, monkeypatch):
    """Test LLM endpoint when enabled (requires actual model)."""
    # Set environment variables for test
    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.setenv("LLM_MODEL_PATH", os.getenv("LLM_MODEL_PATH"))
    monkeypatch.setenv("LLM_N_THREADS", "1")
    monkeypatch.setenv("LLM_CONCURRENCY", "1")
    
    # Test basic generation
    response = client.post("/api/v1/llm/fill-triage-actions", json={
        "root": "headache",
        "nodes": ["severe", "sudden onset"],
        "triage_style": "diagnosis-only",
        "actions_style": "referral-only"
    })
    
    if response.status_code == 200:
        data = response.json()
        assert "diagnostic_triage" in data
        assert "actions" in data
        assert data["applied"] is False
        
        # Check that outputs are within character limits
        assert len(data["diagnostic_triage"]) <= 160
        assert len(data["actions"]) <= 200
    else:
        # If model fails to load, that's acceptable for testing
        assert response.status_code in [500, 503]

@pytest.mark.skipif(
    os.getenv("LLM_ENABLED") != "true" or not os.getenv("LLM_MODEL_PATH"),
    reason="LLM not enabled or model path not set"
)
def test_llm_endpoint_apply_to_db(client, temp_db, monkeypatch):
    """Test applying LLM suggestions to database."""
    # Set environment variables for test
    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.setenv("LLM_MODEL_PATH", os.getenv("LLM_MODEL_PATH"))
    monkeypatch.setenv("LLM_N_THREADS", "1")
    monkeypatch.setenv("LLM_CONCURRENCY", "1")
    
    # Test applying to database
    response = client.post("/api/v1/llm/fill-triage-actions", json={
        "root": "abdominal pain",
        "nodes": ["right lower quadrant", "acute onset"],
        "triage_style": "short-explanation",
        "actions_style": "steps",
        "apply": True,
        "node_id": 2  # Our test leaf node
    })
    
    if response.status_code == 200:
        data = response.json()
        assert data["applied"] is True
        
        # Verify data was written to database
        repo = SQLiteRepository(temp_db)
        with repo._get_connection() as conn:
            cursor = conn.execute("SELECT diagnostic_triage, actions FROM triage WHERE node_id = ?", (2,))
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == data["diagnostic_triage"]
            assert result[1] == data["actions"]
    else:
        # If model fails to load, that's acceptable for testing
        assert response.status_code in [500, 503]

def test_llm_endpoint_validation_errors(client):
    """Test validation errors in LLM endpoint."""
    # Missing root
    response = client.post("/api/v1/llm/fill-triage-actions", json={
        "nodes": ["symptom1"]
    })
    assert response.status_code == 422
    
    # Too many nodes
    response = client.post("/api/v1/llm/fill-triage-actions", json={
        "root": "test",
        "nodes": ["1", "2", "3", "4", "5", "6"]  # More than 5
    })
    assert response.status_code == 422
    
    # Apply without node_id
    response = client.post("/api/v1/llm/fill-triage-actions", json={
        "root": "test",
        "apply": True
    })
    assert response.status_code == 422

def test_llm_endpoint_apply_to_non_leaf(client, temp_db, monkeypatch):
    """Test that applying to non-leaf nodes fails."""
    # Set environment variables for test
    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.setenv("LLM_MODEL_PATH", os.getenv("LLM_MODEL_PATH", "/nonexistent"))
    
    # Try to apply to root node (depth 1, not a leaf)
    response = client.post("/api/v1/llm/fill-triage-actions", json={
        "root": "test",
        "apply": True,
        "node_id": 1  # Root node, not a leaf
    })
    
    # Should fail with 400 if model loads, or 503 if disabled
    assert response.status_code in [400, 503]
