"""
Tests for import jobs API functionality.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import io

from api.app import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_repository():
    """Create mock repository."""
    return Mock()


class TestImportJobsAPI:
    """Test import jobs API endpoints."""
    
    @patch('api.routers.import_jobs.get_repository')
    @patch('pandas.read_excel')
    def test_import_excel_success(self, mock_read_excel, mock_get_repo, client):
        """Test successful Excel import with job tracking."""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Mock repository methods
        mock_repo.create_import_job.return_value = 1
        mock_repo.update_import_job.return_value = None
        mock_repo.get_import_job.return_value = {
            "id": 1,
            "state": "queued",
            "created_at": "2024-01-01T10:00:00Z",
            "finished_at": None,
            "message": None,
            "filename": "test.xlsx",
            "size_bytes": 1024
        }
        
        # Mock pandas read_excel
        mock_df = Mock()
        mock_df.columns.tolist.return_value = [
            "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
            "Diagnostic Triage", "Actions"
        ]
        mock_read_excel.return_value = mock_df
        
        # Create test file
        test_file = io.BytesIO(b"test content")
        
        response = client.post(
            "/api/v1/import/excel",
            files={"file": ("test.xlsx", test_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["state"] == "done"
        assert data["filename"] == "test.xlsx"
        assert data["size_bytes"] == 12  # Length of "test content"
        assert "Import completed successfully" in data["message"]
        
        # Verify job state transitions
        mock_repo.create_import_job.assert_called_with(
            state="queued",
            filename="test.xlsx",
            size_bytes=0
        )
        mock_repo.update_import_job.assert_any_call(1, size_bytes=12)
        mock_repo.update_import_job.assert_any_call(1, state="processing")
        mock_repo.update_import_job.assert_any_call(
            1, 
            state="done",
            message="Import completed successfully",
            finished_at=mock_repo.update_import_job.call_args_list[-1][1]["finished_at"]
        )
    
    @patch('api.routers.import_jobs.get_repository')
    @patch('pandas.read_excel')
    def test_import_excel_header_mismatch(self, mock_read_excel, mock_get_repo, client):
        """Test Excel import with header mismatch (422 error)."""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Mock repository methods
        mock_repo.create_import_job.return_value = 1
        mock_repo.update_import_job.return_value = None
        
        # Mock pandas read_excel with wrong headers
        mock_df = Mock()
        mock_df.columns.tolist.return_value = [
            "Wrong Header", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
            "Diagnostic Triage", "Actions"
        ]
        mock_read_excel.return_value = mock_df
        
        # Create test file
        test_file = io.BytesIO(b"test content")
        
        response = client.post(
            "/api/v1/import/excel",
            files={"file": ("test.xlsx", test_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
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
        
        # Verify job state transitions to failed
        mock_repo.update_import_job.assert_any_call(1, size_bytes=12)
        mock_repo.update_import_job.assert_any_call(1, state="processing")
        mock_repo.update_import_job.assert_any_call(
            1,
            state="failed",
            message=mock_repo.update_import_job.call_args_list[-1][1]["message"],
            finished_at=mock_repo.update_import_job.call_args_list[-1][1]["finished_at"]
        )
    
    @patch('api.routers.import_jobs.get_repository')
    def test_import_excel_wrong_file_type(self, mock_get_repo, client):
        """Test Excel import with wrong file type (400 error)."""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Create test file with wrong extension
        test_file = io.BytesIO(b"test content")
        
        response = client.post(
            "/api/v1/import/excel",
            files={"file": ("test.txt", test_file, "text/plain")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Only .xlsx files are supported" in data["detail"]
        
        # Repository should not be called for wrong file type
        mock_repo.create_import_job.assert_not_called()
    
    @patch('api.routers.import_jobs.get_repository')
    def test_get_import_jobs(self, mock_get_repo, client):
        """Test getting all import jobs."""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Mock repository methods
        mock_repo.get_import_jobs.return_value = [
            {
                "id": 1,
                "state": "done",
                "created_at": "2024-01-01T10:00:00Z",
                "finished_at": "2024-01-01T10:01:00Z",
                "message": "Import completed successfully",
                "filename": "test1.xlsx",
                "size_bytes": 1024
            },
            {
                "id": 2,
                "state": "failed",
                "created_at": "2024-01-01T11:00:00Z",
                "finished_at": "2024-01-01T11:01:00Z",
                "message": "Header mismatch",
                "filename": "test2.xlsx",
                "size_bytes": 2048
            }
        ]
        
        response = client.get("/api/v1/import/jobs")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Check first job
        assert data[0]["id"] == 1
        assert data[0]["state"] == "done"
        assert data[0]["filename"] == "test1.xlsx"
        
        # Check second job
        assert data[1]["id"] == 2
        assert data[1]["state"] == "failed"
        assert data[1]["filename"] == "test2.xlsx"
    
    @patch('api.routers.import_jobs.get_repository')
    def test_get_import_job_by_id(self, mock_get_repo, client):
        """Test getting specific import job by ID."""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Mock repository methods
        mock_repo.get_import_job.return_value = {
            "id": 1,
            "state": "done",
            "created_at": "2024-01-01T10:00:00Z",
            "finished_at": "2024-01-01T10:01:00Z",
            "message": "Import completed successfully",
            "filename": "test.xlsx",
            "size_bytes": 1024
        }
        
        response = client.get("/api/v1/import/jobs/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["state"] == "done"
        assert data["filename"] == "test.xlsx"
    
    @patch('api.routers.import_jobs.get_repository')
    def test_get_import_job_not_found(self, mock_get_repo, client):
        """Test getting non-existent import job (404 error)."""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Mock repository methods
        mock_repo.get_import_job.return_value = None
        
        response = client.get("/api/v1/import/jobs/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "Import job not found" in data["detail"]


class TestImportJobStateMachine:
    """Test import job state transitions."""
    
    @patch('api.routers.import_jobs.get_repository')
    @patch('pandas.read_excel')
    def test_job_state_transitions(self, mock_read_excel, mock_get_repo, client):
        """Test that import job goes through correct state transitions."""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        
        # Mock repository methods
        mock_repo.create_import_job.return_value = 1
        mock_repo.update_import_job.return_value = None
        mock_repo.get_import_job.return_value = {
            "id": 1,
            "state": "queued",
            "created_at": "2024-01-01T10:00:00Z",
            "finished_at": None,
            "message": None,
            "filename": "test.xlsx",
            "size_bytes": 1024
        }
        
        # Mock pandas read_excel
        mock_df = Mock()
        mock_df.columns.tolist.return_value = [
            "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
            "Diagnostic Triage", "Actions"
        ]
        mock_read_excel.return_value = mock_df
        
        # Create test file
        test_file = io.BytesIO(b"test content")
        
        response = client.post(
            "/api/v1/import/excel",
            files={"file": ("test.xlsx", test_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
        assert response.status_code == 200
        
        # Verify state transitions: queued -> processing -> done
        expected_calls = [
            # Initial creation
            ((1,), {"state": "queued", "filename": "test.xlsx", "size_bytes": 0}),
            # Update size after reading
            ((1,), {"size_bytes": 12}),
            # Start processing
            ((1,), {"state": "processing"}),
            # Mark as done
            ((1,), {"state": "done", "message": "Import completed successfully", "finished_at": "2024-01-01T10:01:00Z"})
        ]
        
        actual_calls = [(call[0], call[1]) for call in mock_repo.update_import_job.call_args_list]
        assert len(actual_calls) == len(expected_calls)
        
        for i, (expected_args, expected_kwargs) in enumerate(expected_calls):
            actual_args, actual_kwargs = actual_calls[i]
            assert actual_args == expected_args
            for key, value in expected_kwargs.items():
                if key != "finished_at":  # Skip timestamp comparison
                    assert actual_kwargs[key] == value
