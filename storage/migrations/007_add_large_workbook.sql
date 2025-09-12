-- Migration: Add Large Workbook Management System
-- Safe to re-apply (IF NOT EXISTS)
-- Date: 2025-09-12
-- Purpose: Add tables for large workbook import management with chunking and progress tracking

-- Import jobs table
CREATE TABLE IF NOT EXISTS large_import_jobs (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    total_rows INTEGER NOT NULL,
    chunk_size INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    progress_data TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    error_message TEXT,
    metadata TEXT
);

-- Import chunks table
CREATE TABLE IF NOT EXISTS large_import_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    start_row INTEGER NOT NULL,
    end_row INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    processed_at DATETIME,
    result_data TEXT,
    error_message TEXT,
    FOREIGN KEY (job_id) REFERENCES large_import_jobs(id) ON DELETE CASCADE
);

-- Performance monitoring table
CREATE TABLE IF NOT EXISTS large_import_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    chunk_index INTEGER,
    operation TEXT NOT NULL,
    duration_ms INTEGER NOT NULL,
    memory_mb REAL,
    rows_processed INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES large_import_jobs(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_large_import_jobs_status 
    ON large_import_jobs(status);

CREATE INDEX IF NOT EXISTS idx_large_import_jobs_created_at 
    ON large_import_jobs(created_at);

CREATE INDEX IF NOT EXISTS idx_large_import_chunks_job_id 
    ON large_import_chunks(job_id);

CREATE INDEX IF NOT EXISTS idx_large_import_chunks_status 
    ON large_import_chunks(status);

CREATE INDEX IF NOT EXISTS idx_large_import_chunks_chunk_index 
    ON large_import_chunks(job_id, chunk_index);

CREATE INDEX IF NOT EXISTS idx_large_import_performance_job_id 
    ON large_import_performance(job_id);

CREATE INDEX IF NOT EXISTS idx_large_import_performance_operation 
    ON large_import_performance(operation);

CREATE INDEX IF NOT EXISTS idx_large_import_performance_timestamp 
    ON large_import_performance(timestamp);

-- Create views for easy querying
CREATE VIEW IF NOT EXISTS large_import_jobs_summary AS
SELECT 
    status,
    COUNT(*) as count,
    AVG(total_rows) as avg_rows,
    AVG(chunk_size) as avg_chunk_size,
    MIN(created_at) as earliest,
    MAX(created_at) as latest
FROM large_import_jobs
GROUP BY status
ORDER BY count DESC;

CREATE VIEW IF NOT EXISTS large_import_performance_summary AS
SELECT 
    job_id,
    operation,
    COUNT(*) as operation_count,
    AVG(duration_ms) as avg_duration_ms,
    MIN(duration_ms) as min_duration_ms,
    MAX(duration_ms) as max_duration_ms,
    SUM(rows_processed) as total_rows_processed
FROM large_import_performance
GROUP BY job_id, operation
ORDER BY job_id, operation;

CREATE VIEW IF NOT EXISTS large_import_chunks_progress AS
SELECT 
    job_id,
    COUNT(*) as total_chunks,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_chunks,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_chunks,
    COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_chunks,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_chunks,
    ROUND(COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*), 2) as completion_percentage
FROM large_import_chunks
GROUP BY job_id
ORDER BY job_id;

-- Create triggers for automatic timestamp updates
CREATE TRIGGER IF NOT EXISTS large_import_jobs_timestamp_trigger
    AFTER UPDATE ON large_import_jobs
    WHEN NEW.status != OLD.status
BEGIN
    UPDATE large_import_jobs 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS large_import_chunks_timestamp_trigger
    AFTER UPDATE ON large_import_chunks
    WHEN NEW.status = 'completed' AND OLD.status != 'completed'
BEGIN
    UPDATE large_import_chunks 
    SET processed_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;
