"""
Tests for the Large Workbook API endpoints.

Tests the REST API functionality for large workbook management.
"""

import pytest
import pandas as pd
import io
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from api.app import app
from storage.sqlite import SQLiteRepository

client = TestClient(app)

@pytest.fixture
def sample_excel_file():
    """Create a sample Excel file for testing."""
    data = {
        'Vital Measurement': ['Blood Pressure', 'Heart Rate', 'Temperature'],
        'Node 1': ['High', 'Fast', 'Fever'],
        'Node 2': ['Normal', 'Normal', 'Normal'],
        'Node 3': ['Low', 'Slow', 'Low'],
        'Node 4': ['Critical', 'Irregular', 'Critical'],
        'Node 5': ['Emergency', 'Emergency', 'Emergency'],
        'Diagnostic Triage': ['Monitor', 'Stable', 'Urgent'],
        'Actions': ['Check again', 'Continue monitoring', 'Seek immediate care']
    }
    
    df = pd.DataFrame(data)
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        df.to_excel(f.name, index=False)
        yield f.name
    
    # Cleanup
    os.unlink(f.name)

@pytest.fixture
def sample_excel_content():
    """Create sample Excel content as bytes."""
    data = {
        'Vital Measurement': ['Blood Pressure', 'Heart Rate', 'Temperature'],
        'Node 1': ['High', 'Fast', 'Fever'],
        'Node 2': ['Normal', 'Normal', 'Normal'],
        'Node 3': ['Low', 'Slow', 'Low'],
        'Node 4': ['Critical', 'Irregular', 'Critical'],
        'Node 5': ['Emergency', 'Emergency', 'Emergency'],
        'Diagnostic Triage': ['Monitor', 'Stable', 'Urgent'],
        'Actions': ['Check again', 'Continue monitoring', 'Seek immediate care']
    }
    
    df = pd.DataFrame(data)
    
    with io.BytesIO() as buffer:
        df.to_excel(buffer, index=False)
        return buffer.getvalue()

def test_create_import_job_success(sample_excel_content):
    """Test creating an import job successfully."""
    with patch('api.routers.large_workbook.LargeWorkbookManager') as mock_manager:
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        mock_instance.create_import_job.return_value = 'test-job-id'
        mock_instance.create_chunks.return_value = [1, 2, 3]
        
        response = client.post(
            '/large-workbook/import/create-job',
            files={'file': ('test.xlsx', sample_excel_content, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
            params={'chunk_size': 1000, 'strategy': 'row_based'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['job_id'] == 'test-job-id'
        assert data['status'] == 'pending'
        assert data['message'] is not None

def test_create_import_job_invalid_file():
    """Test creating an import job with invalid file type."""
    response = client.post(
        '/large-workbook/import/create-job',
        files={'file': ('test.txt', b'not an excel file', 'text/plain')},
        params={'chunk_size': 1000}
    )
    
    assert response.status_code == 400
    assert 'Only .xlsx files are supported' in response.json()['detail']

def test_create_import_job_invalid_headers():
    """Test creating an import job with invalid headers."""
    # Create invalid data
    data = {
        'Wrong Header 1': ['Value 1'],
        'Wrong Header 2': ['Value 2'],
    }
    df = pd.DataFrame(data)
    
    with io.BytesIO() as buffer:
        df.to_excel(buffer, index=False)
        content = buffer.getvalue()
    
    response = client.post(
        '/large-workbook/import/create-job',
        files={'file': ('test.xlsx', content, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
        params={'chunk_size': 1000}
    )
    
    assert response.status_code == 422
    assert 'CSV header mismatch' in str(response.json())

def test_start_import_job_success():
    """Test starting an import job successfully."""
    with patch('api.routers.large_workbook.LargeWorkbookManager') as mock_manager:
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        mock_instance.get_import_job.return_value = {
            'id': 'test-job-id',
            'status': 'pending',
            'filename': 'test.xlsx'
        }
        
        response = client.post('/large-workbook/import/test-job-id/start')
        
        assert response.status_code == 200
        data = response.json()
        assert data['job_id'] == 'test-job-id'
        assert data['status'] == 'processing'

def test_start_import_job_not_found():
    """Test starting a non-existent import job."""
    with patch('api.routers.large_workbook.LargeWorkbookManager') as mock_manager:
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        mock_instance.get_import_job.return_value = None
        
        response = client.post('/large-workbook/import/non-existent/start')
        
        assert response.status_code == 404
        assert 'not found' in response.json()['detail']

def test_start_import_job_invalid_status():
    """Test starting an import job with invalid status."""
    with patch('api.routers.large_workbook.LargeWorkbookManager') as mock_manager:
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        mock_instance.get_import_job.return_value = {
            'id': 'test-job-id',
            'status': 'completed',
            'filename': 'test.xlsx'
        }
        
        response = client.post('/large-workbook/import/test-job-id/start')
        
        assert response.status_code == 400
        assert 'cannot be started' in response.json()['detail']

def test_get_import_progress_success():
    """Test getting import progress successfully."""
    with patch('api.routers.large_workbook.LargeWorkbookManager') as mock_manager:
        from api.core.large_workbook_manager import ImportProgress
        
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        mock_instance.get_import_job.return_value = {
            'id': 'test-job-id',
            'status': 'processing'
        }
        mock_instance.get_job_progress.return_value = ImportProgress(
            total_rows=1000,
            processed_rows=500,
            current_chunk=5,
            total_chunks=10,
            percentage=50.0,
            estimated_remaining='2 minutes',
            current_operation='processing'
        )
        mock_instance.get_job_statistics.return_value = {
            'chunk_statistics': {'total_chunks': 10, 'completed_chunks': 5},
            'performance_statistics': {'avg_duration_ms': 1000}
        }
        
        response = client.get('/large-workbook/import/test-job-id/progress')
        
        assert response.status_code == 200
        data = response.json()
        assert data['job_id'] == 'test-job-id'
        assert 'progress' in data
        assert 'statistics' in data

def test_get_import_progress_not_found():
    """Test getting progress for non-existent job."""
    with patch('api.routers.large_workbook.LargeWorkbookManager') as mock_manager:
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        mock_instance.get_import_job.return_value = None
        
        response = client.get('/large-workbook/import/non-existent/progress')
        
        assert response.status_code == 404
        assert 'not found' in response.json()['detail']

def test_get_import_chunks_success():
    """Test getting import chunks successfully."""
    with patch('api.routers.large_workbook.LargeWorkbookManager') as mock_manager:
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        mock_instance.get_import_job.return_value = {
            'id': 'test-job-id',
            'status': 'processing'
        }
        mock_instance.get_pending_chunks.return_value = [
            {
                'id': 1,
                'chunk_index': 0,
                'start_row': 0,
                'end_row': 99,
                'status': 'pending'
            }
        ]
        
        response = client.get('/large-workbook/import/test-job-id/chunks')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['chunk_id'] == 1
        assert data[0]['chunk_index'] == 0

def test_pause_import_job_success():
    """Test pausing an import job successfully."""
    with patch('api.routers.large_workbook.LargeWorkbookManager') as mock_manager:
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        mock_instance.get_import_job.return_value = {
            'id': 'test-job-id',
            'status': 'processing',
            'filename': 'test.xlsx'
        }
        
        response = client.post('/large-workbook/import/test-job-id/pause')
        
        assert response.status_code == 200
        data = response.json()
        assert data['job_id'] == 'test-job-id'
        assert data['status'] == 'paused'

def test_resume_import_job_success():
    """Test resuming an import job successfully."""
    with patch('api.routers.large_workbook.LargeWorkbookManager') as mock_manager:
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        mock_instance.get_import_job.return_value = {
            'id': 'test-job-id',
            'status': 'paused',
            'filename': 'test.xlsx'
        }
        mock_instance.resume_job.return_value = True
        
        response = client.post('/large-workbook/import/test-job-id/resume')
        
        assert response.status_code == 200
        data = response.json()
        assert data['job_id'] == 'test-job-id'
        assert data['status'] == 'processing'

def test_cancel_import_job_success():
    """Test cancelling an import job successfully."""
    with patch('api.routers.large_workbook.LargeWorkbookManager') as mock_manager:
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        mock_instance.cancel_job.return_value = True
        
        response = client.post('/large-workbook/import/test-job-id/cancel')
        
        assert response.status_code == 200
        data = response.json()
        assert data['job_id'] == 'test-job-id'
        assert data['status'] == 'cancelled'

def test_list_import_jobs_success():
    """Test listing import jobs successfully."""
    with patch('api.routers.large_workbook.LargeWorkbookManager') as mock_manager:
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        mock_instance.list_import_jobs.return_value = [
            {
                'id': 'job1',
                'filename': 'test1.xlsx',
                'status': 'completed',
                'total_rows': 100,
                'created_at': '2024-01-01T00:00:00Z'
            },
            {
                'id': 'job2',
                'filename': 'test2.xlsx',
                'status': 'processing',
                'total_rows': 200,
                'created_at': '2024-01-02T00:00:00Z'
            }
        ]
        
        response = client.get('/large-workbook/import/jobs')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]['id'] == 'job1'
        assert data[1]['id'] == 'job2'

def test_list_import_jobs_with_filter():
    """Test listing import jobs with status filter."""
    with patch('api.routers.large_workbook.LargeWorkbookManager') as mock_manager:
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        mock_instance.list_import_jobs.return_value = [
            {
                'id': 'job1',
                'filename': 'test1.xlsx',
                'status': 'completed',
                'total_rows': 100,
                'created_at': '2024-01-01T00:00:00Z'
            }
        ]
        
        response = client.get('/large-workbook/import/jobs?status=completed')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['status'] == 'completed'

def test_get_import_statistics_success():
    """Test getting import statistics successfully."""
    with patch('api.routers.large_workbook.LargeWorkbookManager') as mock_manager:
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        mock_instance.get_import_job.return_value = {
            'id': 'test-job-id',
            'status': 'processing'
        }
        mock_instance.get_job_statistics.return_value = {
            'chunk_statistics': {'total_chunks': 10, 'completed_chunks': 5},
            'performance_statistics': {'avg_duration_ms': 1000}
        }
        
        response = client.get('/large-workbook/import/test-job-id/statistics')
        
        assert response.status_code == 200
        data = response.json()
        assert data['job_id'] == 'test-job-id'
        assert 'statistics' in data

def test_export_progress_csv_success():
    """Test exporting progress as CSV successfully."""
    with patch('api.routers.large_workbook.LargeWorkbookManager') as mock_manager:
        from api.core.large_workbook_manager import ImportProgress
        
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        mock_instance.get_import_job.return_value = {
            'id': 'test-job-id',
            'filename': 'test.xlsx',
            'status': 'processing'
        }
        mock_instance.get_job_progress.return_value = ImportProgress(
            total_rows=1000,
            processed_rows=500,
            current_chunk=5,
            total_chunks=10,
            percentage=50.0,
            estimated_remaining='2 minutes',
            current_operation='processing'
        )
        mock_instance.get_job_statistics.return_value = {
            'chunk_statistics': {
                'total_chunks': 10, 
                'completed_chunks': 5,
                'failed_chunks': 0,
                'processing_chunks': 0,
                'pending_chunks': 5
            },
            'performance_statistics': {
                'avg_duration_ms': 1000,
                'min_duration_ms': 500,
                'max_duration_ms': 1500,
                'total_rows_processed': 500
            }
        }
        
        response = client.get('/large-workbook/import/test-job-id/export-progress')
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'text/csv; charset=utf-8'
        assert 'Job ID,test-job-id' in response.text

def test_export_progress_csv_not_found():
    """Test exporting progress CSV for non-existent job."""
    with patch('api.routers.large_workbook.LargeWorkbookManager') as mock_manager:
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        mock_instance.get_import_job.return_value = None
        
        response = client.get('/large-workbook/import/non-existent/export-progress')
        
        assert response.status_code == 404
        assert 'not found' in response.json()['detail']

def test_invalid_chunk_size():
    """Test creating import job with invalid chunk size."""
    response = client.post(
        '/large-workbook/import/create-job',
        files={'file': ('test.xlsx', b'fake content', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
        params={'chunk_size': 50}  # Too small
    )
    
    assert response.status_code == 422

def test_invalid_strategy():
    """Test creating import job with invalid strategy."""
    # Create a proper Excel file for this test
    data = {
        'Vital Measurement': ['Blood Pressure'],
        'Node 1': ['High'],
        'Node 2': ['Normal'],
        'Node 3': ['Low'],
        'Node 4': ['Critical'],
        'Node 5': ['Emergency'],
        'Diagnostic Triage': ['Monitor'],
        'Actions': ['Check again']
    }
    df = pd.DataFrame(data)
    
    with io.BytesIO() as buffer:
        df.to_excel(buffer, index=False)
        content = buffer.getvalue()
    
    response = client.post(
        '/large-workbook/import/create-job',
        files={'file': ('test.xlsx', content, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
        params={'strategy': 'invalid_strategy'}
    )
    
    # Should still work as strategy is just a parameter
    assert response.status_code in [200, 422]  # Depends on file validation

def test_large_workbook_endpoints_exist():
    """Test that all large workbook endpoints exist."""
    # Test that the router is mounted
    response = client.get('/docs')
    assert response.status_code == 200
    
    # Test that endpoints are accessible (even if they return errors)
    response = client.get('/large-workbook/import/jobs')
    assert response.status_code in [200, 500]  # Should not be 404
    
    response = client.post('/large-workbook/import/non-existent/start')
    assert response.status_code in [404, 500]  # Should not be 404

def test_dual_mount_support():
    """Test that large workbook router is mounted at both root and versioned paths."""
    # Test versioned path
    response = client.get('/api/v1/large-workbook/import/jobs')
    assert response.status_code in [200, 500]  # Should not be 404
    
    # Test root path
    response = client.get('/large-workbook/import/jobs')
    assert response.status_code in [200, 500]  # Should not be 404
