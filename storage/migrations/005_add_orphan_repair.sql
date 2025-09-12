-- Migration: Add Orphan Repair System
-- Safe to re-apply (IF NOT EXISTS)
-- Date: 2025-09-12
-- Purpose: Add comprehensive orphan repair system with audit trails

-- Orphan repair audit table
CREATE TABLE IF NOT EXISTS orphan_repair_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orphan_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    actor TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    before_state TEXT,
    after_state TEXT,
    success BOOLEAN NOT NULL,
    message TEXT,
    warnings TEXT,
    FOREIGN KEY (orphan_id) REFERENCES nodes(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_orphan_repair_audit_orphan_id 
    ON orphan_repair_audit(orphan_id);

CREATE INDEX IF NOT EXISTS idx_orphan_repair_audit_timestamp 
    ON orphan_repair_audit(timestamp);

CREATE INDEX IF NOT EXISTS idx_orphan_repair_audit_action 
    ON orphan_repair_audit(action);

CREATE INDEX IF NOT EXISTS idx_orphan_repair_audit_actor 
    ON orphan_repair_audit(actor);

-- Create views for easy querying
CREATE VIEW IF NOT EXISTS orphan_repair_summary AS
SELECT 
    action,
    COUNT(*) as total_repairs,
    COUNT(CASE WHEN success = 1 THEN 1 END) as successful_repairs,
    COUNT(CASE WHEN success = 0 THEN 1 END) as failed_repairs,
    ROUND(COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*), 2) as success_rate
FROM orphan_repair_audit
GROUP BY action
ORDER BY total_repairs DESC;

CREATE VIEW IF NOT EXISTS orphan_repair_recent AS
SELECT 
    id,
    orphan_id,
    action,
    actor,
    timestamp,
    success,
    message
FROM orphan_repair_audit
ORDER BY timestamp DESC
LIMIT 100;

CREATE VIEW IF NOT EXISTS orphan_repair_by_actor AS
SELECT 
    actor,
    COUNT(*) as total_repairs,
    COUNT(CASE WHEN success = 1 THEN 1 END) as successful_repairs,
    COUNT(CASE WHEN success = 0 THEN 1 END) as failed_repairs,
    MIN(timestamp) as first_repair,
    MAX(timestamp) as last_repair
FROM orphan_repair_audit
GROUP BY actor
ORDER BY total_repairs DESC;

-- Create trigger for automatic timestamp updates
CREATE TRIGGER IF NOT EXISTS orphan_repair_timestamp_trigger
    AFTER INSERT ON orphan_repair_audit
BEGIN
    UPDATE orphan_repair_audit 
    SET timestamp = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;
