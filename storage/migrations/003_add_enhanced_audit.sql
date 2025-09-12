-- Migration: Add Enhanced Audit System
-- Safe to re-apply (IF NOT EXISTS)
-- Date: 2025-09-11
-- Purpose: Add enhanced audit tables with expanded operation types and undo capabilities

-- Enhanced audit_log table with expanded capabilities
CREATE TABLE IF NOT EXISTS enhanced_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    operation TEXT NOT NULL,
    target_id INTEGER,
    target_type TEXT,
    actor TEXT,
    context_json TEXT,
    payload_json TEXT,
    undo_data_json TEXT,
    is_undoable BOOLEAN DEFAULT 0,
    undo_timeout_seconds INTEGER,
    requires_confirmation BOOLEAN DEFAULT 0,
    undone_by INTEGER,
    undone_at DATETIME,
    undo_reason TEXT,
    parent_operation_id INTEGER,
    operation_group_id TEXT,
    severity TEXT DEFAULT 'info',
    tags TEXT
);

-- Audit operation groups for batch operations
CREATE TABLE IF NOT EXISTS audit_operation_groups (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    status TEXT DEFAULT 'in_progress',
    total_operations INTEGER DEFAULT 0,
    completed_operations INTEGER DEFAULT 0,
    failed_operations INTEGER DEFAULT 0
);

-- Audit tags for categorization
CREATE TABLE IF NOT EXISTS audit_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    color TEXT DEFAULT '#007bff',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_enhanced_audit_timestamp 
    ON enhanced_audit_log(timestamp);

CREATE INDEX IF NOT EXISTS idx_enhanced_audit_operation 
    ON enhanced_audit_log(operation);

CREATE INDEX IF NOT EXISTS idx_enhanced_audit_target 
    ON enhanced_audit_log(target_id, target_type);

CREATE INDEX IF NOT EXISTS idx_enhanced_audit_actor 
    ON enhanced_audit_log(actor);

CREATE INDEX IF NOT EXISTS idx_enhanced_audit_undoable 
    ON enhanced_audit_log(is_undoable, undone_by);

CREATE INDEX IF NOT EXISTS idx_enhanced_audit_group 
    ON enhanced_audit_log(operation_group_id);

CREATE INDEX IF NOT EXISTS idx_enhanced_audit_severity 
    ON enhanced_audit_log(severity);

CREATE INDEX IF NOT EXISTS idx_enhanced_audit_tags 
    ON enhanced_audit_log(tags);

-- Insert default audit tags
INSERT OR IGNORE INTO audit_tags (name, description, color) VALUES
    ('tree', 'Tree structure operations', '#28a745'),
    ('flags', 'Flag assignment operations', '#ffc107'),
    ('triage', 'Triage status operations', '#17a2b8'),
    ('dictionary', 'Dictionary operations', '#6f42c1'),
    ('import', 'Data import operations', '#fd7e14'),
    ('export', 'Data export operations', '#20c997'),
    ('backup', 'Backup operations', '#6c757d'),
    ('restore', 'Restore operations', '#dc3545'),
    ('auth', 'Authentication operations', '#e83e8c'),
    ('bulk', 'Bulk operations', '#6f42c1'),
    ('system', 'System operations', '#343a40'),
    ('failed', 'Failed operations', '#dc3545'),
    ('maintenance', 'Maintenance operations', '#6c757d'),
    ('conflict', 'Conflict resolution', '#ffc107'),
    ('vm_builder', 'VM Builder operations', '#17a2b8');

-- Create view for easy audit log querying
CREATE VIEW IF NOT EXISTS audit_log_summary AS
SELECT 
    id,
    timestamp,
    operation,
    target_id,
    target_type,
    actor,
    is_undoable,
    undone_by,
    undone_at,
    severity,
    tags,
    CASE 
        WHEN undone_by IS NOT NULL THEN 'undone'
        WHEN is_undoable = 1 THEN 'undoable'
        ELSE 'not_undoable'
    END as undo_status
FROM enhanced_audit_log
ORDER BY timestamp DESC;

-- Create view for operation group statistics
CREATE VIEW IF NOT EXISTS audit_group_stats AS
SELECT 
    g.id,
    g.name,
    g.description,
    g.status,
    g.total_operations,
    g.completed_operations,
    g.failed_operations,
    COUNT(l.id) as actual_operations,
    g.created_at,
    g.completed_at
FROM audit_operation_groups g
LEFT JOIN enhanced_audit_log l ON g.id = l.operation_group_id
GROUP BY g.id, g.name, g.description, g.status, g.total_operations, 
         g.completed_operations, g.failed_operations, g.created_at, g.completed_at;
