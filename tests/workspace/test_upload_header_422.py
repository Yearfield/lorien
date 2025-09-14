import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_upload_with_wrong_header_returns_422(client):
    """Test that uploading with wrong header returns 422 with detailed context"""
    # Create a CSV with wrong header
    wrong_header_csv = "wrong_col1,wrong_col2,wrong_col3\nvalue1,value2,value3"
    
    response = client.post(
        "/api/v1/import?mode=replace",
        files={"file": ("test.csv", wrong_header_csv, "text/csv")}
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert len(data["detail"]) > 0
    
    # Check that the error has the correct structure
    error = data["detail"][0]
    assert error["loc"] == ["header"]
    assert error["type"] == "value_error.header_mismatch"
    assert "ctx" in error
    assert "expected" in error["ctx"]
    assert "received" in error["ctx"]
    assert "col_index" in error["ctx"]

def test_upload_with_partial_header_returns_422(client):
    """Test that uploading with partial header returns 422"""
    # Create a CSV with only some columns
    partial_header_csv = "Vital Measurement,Node 1\nTest Root,Test Node"
    
    response = client.post(
        "/api/v1/import?mode=replace",
        files={"file": ("test.csv", partial_header_csv, "text/csv")}
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert len(data["detail"]) > 0
    
    error = data["detail"][0]
    assert error["loc"] == ["header"]
    assert error["type"] == "value_error.header_mismatch"

def test_upload_with_correct_header_returns_200(client):
    """Test that uploading with correct header returns 200"""
    # Create a CSV with correct header
    correct_header_csv = """Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions
Test Root,Test Node 1,Test Node 2,,,,Test Triage,Test Actions"""
    
    response = client.post(
        "/api/v1/import?mode=replace",
        files={"file": ("test.csv", correct_header_csv, "text/csv")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "rows" in data
    assert "mode" in data
    assert data["mode"] == "replace"
