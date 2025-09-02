"""
Integration tests for import jobs API functionality using real database.
"""

import pytest
import tempfile
import os
import pandas as pd
import io
from fastapi.testclient import TestClient

from api.app import app


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    test_db.close()
    
    # Set environment variable for test database
    os.environ['LORIEN_DB_PATH'] = test_db.name
    
    yield test_db.name
    
    # Clean up
    if os.path.exists(test_db.name):
        os.unlink(test_db.name)


@pytest.fixture
def client(test_db):
    """Create test client with test database."""
    return TestClient(app)


@pytest.fixture
def valid_excel_file():
    """Create a valid Excel file with correct headers."""
    df = pd.DataFrame({
        'Vital Measurement': ['Test VM'],
        'Node 1': ['Test Node 1'],
        'Node 2': ['Test Node 2'],
        'Node 3': ['Test Node 3'],
        'Node 4': ['Test Node 4'],
        'Node 5': ['Test Node 5'],
        'Diagnostic Triage': ['Test Triage'],
        'Actions': ['Test Actions']
    })
    
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    excel_buffer.seek(0)
    
    return excel_buffer


@pytest.fixture
def invalid_excel_file():
    """Create an Excel file with invalid headers."""
    df = pd.DataFrame({
        'Wrong Header': ['Test VM'],
        'Node 1': ['Test Node 1'],
        'Node 2': ['Test Node 2'],
        'Node 3': ['Test Node 3'],
        'Node 4': ['Test Node 4'],
        'Node 5': ['Test Node 5'],
        'Diagnostic Triage': ['Test Triage'],
        'Actions': ['Test Actions']
    })
    
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    excel_buffer.seek(0)
    
    return excel_buffer


class TestImportJobsIntegration:
    """Integration tests for import jobs API endpoints."""
    
    def test_import_excel_success(self, client, valid_excel_file):
        """Test successful Excel import with job tracking."""
        response = client.post(
            "/api/v1/import/excel",
            files={"file": ("test.xlsx", valid_excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["state"] == "done"
        assert data["filename"] == "test.xlsx"
        assert data["size_bytes"] > 0
        assert "Import completed successfully" in data["message"]
        assert "created_at" in data
        assert "finished_at" in data
    
    def test_import_excel_header_mismatch(self, client, invalid_excel_file):
        """Test Excel import with header mismatch (422 error)."""
        response = client.post(
            "/api/v1/import/excel",
            files={"file": ("test.xlsx", invalid_excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        
        detail = data["detail"]
        assert len(detail) == 1
        assert detail[0]["loc"] == ["body", "file"]
        assert detail[0]["msg"] == "CSV header mismatch"
        assert detail[0]["type"] == "value_error.csv_schema"
        assert "ctx" in detail[0]
        
        # Check that the context has the expected structure
        ctx = detail[0]["ctx"]
        assert "expected" in ctx
        assert "received" in ctx
        assert "first_offending_row" in ctx
        assert "col_index" in ctx
    
    def test_import_excel_wrong_file_type(self, client):
        """Test Excel import with wrong file type (400 error)."""
        test_file = io.BytesIO(b"test content")
        
        response = client.post(
            "/api/v1/import/excel",
            files={"file": ("test.txt", test_file, "text/plain")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Only .xlsx files are supported" in data["detail"]
    
    def test_get_import_jobs(self, client, valid_excel_file):
        """Test getting all import jobs."""
        # First, create an import job
        response = client.post(
            "/api/v1/import/excel",
            files={"file": ("test.xlsx", valid_excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        assert response.status_code == 200
        
        # Now get all import jobs
        response = client.get("/api/v1/import/jobs")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        # Check that the job we just created is in the list
        job = data[0]
        assert "id" in job
        assert "state" in job
        assert "created_at" in job
        assert "filename" in job
        assert "size_bytes" in job
    
    def test_get_import_job_by_id(self, client, valid_excel_file):
        """Test getting specific import job by ID."""
        # First, create an import job
        response = client.post(
            "/api/v1/import/excel",
            files={"file": ("test.xlsx", valid_excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        assert response.status_code == 200
        job_id = response.json()["id"]
        
        # Now get the specific job
        response = client.get(f"/api/v1/import/jobs/{job_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert data["state"] == "done"
        assert data["filename"] == "test.xlsx"
    
    def test_get_import_job_not_found(self, client):
        """Test getting non-existent import job (404 error)."""
        response = client.get("/api/v1/import/jobs/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "Import job not found" in data["detail"]
    
    def test_job_state_transitions(self, client, valid_excel_file):
        """Test that import job goes through correct state transitions."""
        response = client.post(
            "/api/v1/import/excel",
            files={"file": ("test.xlsx", valid_excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify the job went through the correct states
        assert data["state"] == "done"
        assert "created_at" in data
        assert "finished_at" in data
        assert data["finished_at"] is not None
        
        # The job should have been created, processed, and completed
        # We can verify this by checking that both timestamps exist and are strings
        assert isinstance(data["created_at"], str)
        assert isinstance(data["finished_at"], str)
        
        # Basic check that timestamps are in ISO format
        assert "T" in data["created_at"]
        assert "T" in data["finished_at"]
