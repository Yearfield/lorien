"""
Tests for the Large Workbook Manager.

Tests the core functionality of chunked import processing,
progress tracking, and job management.
"""

import pytest
import sqlite3
import pandas as pd
import tempfile
import os
from datetime import datetime, timezone

from api.core.large_workbook_manager import (
    LargeWorkbookManager,
    ImportStatus,
    ChunkStrategy,
    ImportProgress,
    ChunkResult
)

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Create basic tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create nodes table
    cursor.execute("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            depth INTEGER NOT NULL,
            slot INTEGER NOT NULL,
            label TEXT NOT NULL,
            is_leaf INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES nodes(id)
        )
    """)
    
    # Create triage table
    cursor.execute("""
        CREATE TABLE triage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id INTEGER NOT NULL,
            diagnostic_triage TEXT,
            actions TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (node_id) REFERENCES nodes(id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    os.unlink(db_path)

@pytest.fixture
def manager(temp_db):
    """Create a LargeWorkbookManager instance."""
    conn = sqlite3.connect(temp_db)
    return LargeWorkbookManager(conn)

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame({
        'Vital Measurement': ['Blood Pressure', 'Heart Rate', 'Temperature'],
        'Node 1': ['High', 'Fast', 'Fever'],
        'Node 2': ['Normal', 'Normal', 'Normal'],
        'Node 3': ['Low', 'Slow', 'Low'],
        'Node 4': ['Critical', 'Irregular', 'Critical'],
        'Node 5': ['Emergency', 'Emergency', 'Emergency'],
        'Diagnostic Triage': ['Monitor', 'Stable', 'Urgent'],
        'Actions': ['Check again', 'Continue monitoring', 'Seek immediate care']
    })

def test_create_import_job(manager):
    """Test creating an import job."""
    job_id = manager.create_import_job(
        filename='test.xlsx',
        total_rows=1000,
        chunk_size=100,
        metadata={'test': True}
    )
    
    assert job_id is not None
    assert len(job_id) > 0
    
    # Verify job was created
    job = manager.get_import_job(job_id)
    assert job is not None
    assert job['filename'] == 'test.xlsx'
    assert job['total_rows'] == 1000
    assert job['chunk_size'] == 100
    assert job['status'] == ImportStatus.PENDING.value
    assert job['metadata']['test'] is True

def test_create_chunks(manager):
    """Test creating chunks for an import job."""
    job_id = manager.create_import_job('test.xlsx', 1000, 100)
    chunks = manager.create_chunks(job_id, 1000, 100)
    
    assert len(chunks) == 10  # 1000 rows / 100 chunk_size = 10 chunks
    
    # Verify chunks were created
    pending_chunks = manager.get_pending_chunks(job_id)
    assert len(pending_chunks) == 10
    
    # Check first chunk
    first_chunk = pending_chunks[0]
    assert first_chunk['chunk_index'] == 0
    assert first_chunk['start_row'] == 0
    assert first_chunk['end_row'] == 99
    assert first_chunk['status'] == 'pending'
    
    # Check last chunk
    last_chunk = pending_chunks[-1]
    assert last_chunk['chunk_index'] == 9
    assert last_chunk['start_row'] == 900
    assert last_chunk['end_row'] == 999

def test_process_chunk(manager, sample_data):
    """Test processing a single chunk."""
    job_id = manager.create_import_job('test.xlsx', 3, 1)
    chunks = manager.create_chunks(job_id, 3, 1)
    
    # Process first chunk
    chunk_id = chunks[0]
    result = manager.process_chunk(job_id, chunk_id, sample_data.iloc[0:1])
    
    assert result.rows_processed == 1
    assert result.created_roots == 1
    assert result.created_nodes == 5
    assert result.updated_outcomes == 1
    assert len(result.errors) == 0

def test_job_progress(manager):
    """Test getting job progress."""
    job_id = manager.create_import_job('test.xlsx', 100, 10)
    manager.create_chunks(job_id, 100, 10)
    
    progress = manager.get_job_progress(job_id)
    
    assert progress.total_rows == 100
    assert progress.processed_rows == 0
    assert progress.current_chunk == 0
    assert progress.total_chunks == 10
    assert progress.percentage == 0.0

def test_update_job_status(manager):
    """Test updating job status."""
    job_id = manager.create_import_job('test.xlsx', 100, 10)
    
    # Update to processing
    manager.update_job_status(job_id, ImportStatus.PROCESSING)
    job = manager.get_import_job(job_id)
    assert job['status'] == ImportStatus.PROCESSING.value
    assert job['started_at'] is not None
    
    # Update to completed
    manager.update_job_status(job_id, ImportStatus.COMPLETED)
    job = manager.get_import_job(job_id)
    assert job['status'] == ImportStatus.COMPLETED.value
    assert job['completed_at'] is not None

def test_list_import_jobs(manager):
    """Test listing import jobs."""
    # Create multiple jobs
    job1 = manager.create_import_job('test1.xlsx', 100, 10)
    job2 = manager.create_import_job('test2.xlsx', 200, 20)
    job3 = manager.create_import_job('test3.xlsx', 300, 30)
    
    # Update statuses
    manager.update_job_status(job1, ImportStatus.COMPLETED)
    manager.update_job_status(job2, ImportStatus.PROCESSING)
    # job3 remains pending
    
    # List all jobs
    all_jobs = manager.list_import_jobs()
    assert len(all_jobs) == 3
    
    # List by status
    completed_jobs = manager.list_import_jobs(status=ImportStatus.COMPLETED)
    assert len(completed_jobs) == 1
    assert completed_jobs[0]['id'] == job1
    
    processing_jobs = manager.list_import_jobs(status=ImportStatus.PROCESSING)
    assert len(processing_jobs) == 1
    assert processing_jobs[0]['id'] == job2

def test_cancel_job(manager):
    """Test cancelling a job."""
    job_id = manager.create_import_job('test.xlsx', 100, 10)
    manager.create_chunks(job_id, 100, 10)
    
    # Cancel job
    success = manager.cancel_job(job_id)
    assert success is True
    
    # Verify job was cancelled
    job = manager.get_import_job(job_id)
    assert job['status'] == ImportStatus.CANCELLED.value
    
    # Verify chunks were cancelled
    pending_chunks = manager.get_pending_chunks(job_id)
    assert len(pending_chunks) == 0  # All chunks should be cancelled

def test_resume_job(manager):
    """Test resuming a job."""
    job_id = manager.create_import_job('test.xlsx', 100, 10)
    manager.create_chunks(job_id, 100, 10)
    
    # Pause job
    manager.update_job_status(job_id, ImportStatus.PAUSED)
    
    # Resume job
    success = manager.resume_job(job_id)
    assert success is True
    
    # Verify job was resumed
    job = manager.get_import_job(job_id)
    assert job['status'] == ImportStatus.PROCESSING.value

def test_job_statistics(manager, sample_data):
    """Test getting job statistics."""
    job_id = manager.create_import_job('test.xlsx', 3, 1)
    chunks = manager.create_chunks(job_id, 3, 1)
    
    # Process some chunks
    manager.process_chunk(job_id, chunks[0], sample_data.iloc[0:1])
    manager.process_chunk(job_id, chunks[1], sample_data.iloc[1:2])
    
    stats = manager.get_job_statistics(job_id)
    
    assert 'chunk_statistics' in stats
    assert 'performance_statistics' in stats
    
    chunk_stats = stats['chunk_statistics']
    assert chunk_stats['total_chunks'] == 3
    assert chunk_stats['completed_chunks'] == 2
    assert chunk_stats['pending_chunks'] == 1

def test_process_single_row(manager):
    """Test processing a single row of data."""
    cursor = manager.conn.cursor()
    
    result = manager._process_single_row(
        cursor,
        'Blood Pressure',
        ['High', 'Normal', 'Low', 'Critical', 'Emergency'],
        'Monitor closely',
        'Check again in 15 minutes'
    )
    
    assert result['created_roots'] == 1
    assert result['created_nodes'] == 5
    assert result['updated_outcomes'] == 1
    
    # Verify data was inserted
    cursor.execute("SELECT COUNT(*) FROM nodes WHERE depth = 0")
    root_count = cursor.fetchone()[0]
    assert root_count == 1
    
    cursor.execute("SELECT COUNT(*) FROM nodes WHERE depth = 1")
    node_count = cursor.fetchone()[0]
    assert node_count == 5
    
    cursor.execute("SELECT COUNT(*) FROM triage")
    triage_count = cursor.fetchone()[0]
    assert triage_count == 1

def test_ensure_leaf_path(manager):
    """Test ensuring leaf path creation."""
    cursor = manager.conn.cursor()
    
    # Create root
    cursor.execute("""
        INSERT INTO nodes (parent_id, depth, slot, label, is_leaf)
        VALUES (NULL, 0, 0, 'Blood Pressure', 0)
    """)
    root_id = cursor.lastrowid
    
    # Ensure leaf path
    leaf_id = manager._ensure_leaf_path(
        cursor,
        root_id,
        ['High', 'Normal', 'Low', 'Critical', 'Emergency']
    )
    
    assert leaf_id is not None
    
    # Verify path was created (should create 5 levels of depth)
    cursor.execute("SELECT COUNT(*) FROM nodes WHERE depth > 0")
    total_nodes = cursor.fetchone()[0]
    assert total_nodes == 5  # 5 levels of depth
    
    # Verify leaf node
    cursor.execute("SELECT is_leaf FROM nodes WHERE id = ?", (leaf_id,))
    is_leaf = cursor.fetchone()[0]
    assert is_leaf == 1
    
    # Verify the path structure
    cursor.execute("SELECT depth, slot, label FROM nodes WHERE depth > 0 ORDER BY depth, slot")
    nodes = cursor.fetchall()
    assert len(nodes) == 5
    assert nodes[0][0] == 1  # depth 1
    assert nodes[0][1] == 1  # slot 1
    assert nodes[0][2] == 'High'  # label

def test_chunk_result_creation():
    """Test ChunkResult creation and properties."""
    result = ChunkResult(
        rows_processed=10,
        created_roots=2,
        created_nodes=8,
        updated_nodes=5,
        updated_outcomes=3,
        errors=['Error 1', 'Error 2'],
        warnings=['Warning 1']
    )
    
    assert result.rows_processed == 10
    assert result.created_roots == 2
    assert result.created_nodes == 8
    assert result.updated_nodes == 5
    assert result.updated_outcomes == 3
    assert len(result.errors) == 2
    assert len(result.warnings) == 1

def test_import_progress_creation():
    """Test ImportProgress creation and properties."""
    progress = ImportProgress(
        total_rows=1000,
        processed_rows=500,
        current_chunk=5,
        total_chunks=10,
        percentage=50.0,
        estimated_remaining='2 minutes',
        current_operation='processing'
    )
    
    assert progress.total_rows == 1000
    assert progress.processed_rows == 500
    assert progress.current_chunk == 5
    assert progress.total_chunks == 10
    assert progress.percentage == 50.0
    assert progress.estimated_remaining == '2 minutes'
    assert progress.current_operation == 'processing'

def test_import_status_enum():
    """Test ImportStatus enum values."""
    assert ImportStatus.PENDING.value == 'pending'
    assert ImportStatus.PROCESSING.value == 'processing'
    assert ImportStatus.PAUSED.value == 'paused'
    assert ImportStatus.COMPLETED.value == 'completed'
    assert ImportStatus.FAILED.value == 'failed'
    assert ImportStatus.CANCELLED.value == 'cancelled'

def test_chunk_strategy_enum():
    """Test ChunkStrategy enum values."""
    assert ChunkStrategy.ROW_BASED.value == 'row_based'
    assert ChunkStrategy.SIZE_BASED.value == 'size_based'
    assert ChunkStrategy.MEMORY_BASED.value == 'memory_based'

def test_large_workbook_manager_initialization(manager):
    """Test that LargeWorkbookManager initializes correctly."""
    assert manager.conn is not None
    
    # Verify tables were created
    cursor = manager.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='large_import_jobs'")
    assert cursor.fetchone() is not None
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='large_import_chunks'")
    assert cursor.fetchone() is not None
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='large_import_performance'")
    assert cursor.fetchone() is not None
