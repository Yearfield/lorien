import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_upload_replace_mode_atomic(client):
    """Test that replace mode atomically clears old data and imports new data"""
    # First, seed some initial data
    initial_csv = """Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions
Initial Root,Initial Node 1,Initial Node 2,,,,Initial Triage,Initial Actions"""
    
    # Upload initial data
    response1 = client.post(
        "/api/v1/import?mode=replace",
        files={"file": ("initial.csv", initial_csv, "text/csv")}
    )
    assert response1.status_code == 200
    
    # Verify initial data exists
    export_response = client.get("/api/v1/tree/export?format=csv&limit=10")
    assert export_response.status_code == 200
    assert "Initial Root" in export_response.text
    
    # Now upload different data in replace mode
    new_csv = """Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions
New Root,New Node 1,New Node 2,,,,New Triage,New Actions"""
    
    response2 = client.post(
        "/api/v1/import?mode=replace",
        files={"file": ("new.csv", new_csv, "text/csv")}
    )
    assert response2.status_code == 200
    
    # Verify old data is gone and new data exists
    export_response2 = client.get("/api/v1/tree/export?format=csv&limit=10")
    assert export_response2.status_code == 200
    assert "Initial Root" not in export_response2.text
    assert "New Root" in export_response2.text

def test_upload_append_mode_preserves_existing(client):
    """Test that append mode preserves existing data"""
    # First, seed some initial data
    initial_csv = """Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions
Initial Root,Initial Node 1,Initial Node 2,,,,Initial Triage,Initial Actions"""
    
    # Upload initial data
    response1 = client.post(
        "/api/v1/import?mode=replace",
        files={"file": ("initial.csv", initial_csv, "text/csv")}
    )
    assert response1.status_code == 200
    
    # Now upload additional data in append mode
    additional_csv = """Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions
Additional Root,Additional Node 1,Additional Node 2,,,,Additional Triage,Additional Actions"""
    
    response2 = client.post(
        "/api/v1/import?mode=append",
        files={"file": ("additional.csv", additional_csv, "text/csv")}
    )
    assert response2.status_code == 200
    
    # Verify both datasets exist
    export_response = client.get("/api/v1/tree/export?format=csv&limit=10")
    assert export_response.status_code == 200
    assert "Initial Root" in export_response.text
    assert "Additional Root" in export_response.text

def test_upload_hard_replace_mode_resets_everything(client):
    """Test that hard_replace mode resets everything including schema"""
    # First, seed some initial data
    initial_csv = """Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions
Initial Root,Initial Node 1,Initial Node 2,,,,Initial Triage,Initial Actions"""
    
    # Upload initial data
    response1 = client.post(
        "/api/v1/import?mode=replace",
        files={"file": ("initial.csv", initial_csv, "text/csv")}
    )
    assert response1.status_code == 200
    
    # Now upload new data in hard_replace mode
    new_csv = """Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions
Hard Reset Root,Hard Reset Node 1,Hard Reset Node 2,,,,Hard Reset Triage,Hard Reset Actions"""
    
    response2 = client.post(
        "/api/v1/import?mode=hard_replace",
        files={"file": ("new.csv", new_csv, "text/csv")}
    )
    assert response2.status_code == 200
    
    # Verify old data is gone and new data exists
    export_response2 = client.get("/api/v1/tree/export?format=csv&limit=10")
    assert export_response2.status_code == 200
    assert "Initial Root" not in export_response2.text
    assert "Hard Reset Root" in export_response2.text
