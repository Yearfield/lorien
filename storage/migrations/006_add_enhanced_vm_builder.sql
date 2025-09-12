-- Migration: Add Enhanced VM Builder System
-- Safe to re-apply (IF NOT EXISTS)
-- Date: 2025-09-12
-- Purpose: Add enhanced VM Builder with advanced planning and publishing

-- Enhanced VM drafts table
CREATE TABLE IF NOT EXISTS vm_drafts_enhanced (
    id TEXT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    parent_id INTEGER,
    draft_data TEXT,
    status TEXT DEFAULT 'draft',
    published_at DATETIME,
    published_by TEXT,
    plan_data TEXT,
    validation_data TEXT,
    metadata TEXT,
    FOREIGN KEY (parent_id) REFERENCES nodes(id) ON DELETE CASCADE
);

-- VM Builder audit table
CREATE TABLE IF NOT EXISTS vm_builder_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draft_id TEXT NOT NULL,
    action TEXT NOT NULL,
    actor TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    before_state TEXT,
    after_state TEXT,
    success BOOLEAN NOT NULL,
    message TEXT,
    metadata TEXT,
    FOREIGN KEY (draft_id) REFERENCES vm_drafts_enhanced(id) ON DELETE CASCADE
);

-- VM Builder templates table
CREATE TABLE IF NOT EXISTS vm_builder_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    template_data TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    is_public BOOLEAN DEFAULT 0,
    usage_count INTEGER DEFAULT 0
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_vm_drafts_enhanced_status 
    ON vm_drafts_enhanced(status);

CREATE INDEX IF NOT EXISTS idx_vm_drafts_enhanced_parent_id 
    ON vm_drafts_enhanced(parent_id);

CREATE INDEX IF NOT EXISTS idx_vm_drafts_enhanced_created_at 
    ON vm_drafts_enhanced(created_at);

CREATE INDEX IF NOT EXISTS idx_vm_builder_audit_draft_id 
    ON vm_builder_audit(draft_id);

CREATE INDEX IF NOT EXISTS idx_vm_builder_audit_timestamp 
    ON vm_builder_audit(timestamp);

CREATE INDEX IF NOT EXISTS idx_vm_builder_audit_action 
    ON vm_builder_audit(action);

CREATE INDEX IF NOT EXISTS idx_vm_builder_templates_name 
    ON vm_builder_templates(name);

CREATE INDEX IF NOT EXISTS idx_vm_builder_templates_created_by 
    ON vm_builder_templates(created_by);

-- Create views for easy querying
CREATE VIEW IF NOT EXISTS vm_drafts_summary AS
SELECT 
    status,
    COUNT(*) as count,
    MIN(created_at) as earliest,
    MAX(created_at) as latest
FROM vm_drafts_enhanced
GROUP BY status
ORDER BY count DESC;

CREATE VIEW IF NOT EXISTS vm_drafts_recent AS
SELECT 
    id,
    parent_id,
    status,
    created_at,
    updated_at,
    published_at,
    published_by
FROM vm_drafts_enhanced
ORDER BY updated_at DESC
LIMIT 50;

CREATE VIEW IF NOT EXISTS vm_builder_activity AS
SELECT 
    DATE(timestamp) as date,
    action,
    COUNT(*) as count,
    COUNT(CASE WHEN success = 1 THEN 1 END) as successful,
    COUNT(CASE WHEN success = 0 THEN 1 END) as failed
FROM vm_builder_audit
GROUP BY DATE(timestamp), action
ORDER BY date DESC, count DESC;

CREATE VIEW IF NOT EXISTS vm_builder_templates_popular AS
SELECT 
    id,
    name,
    description,
    usage_count,
    created_at,
    created_by
FROM vm_builder_templates
WHERE is_public = 1
ORDER BY usage_count DESC, created_at DESC;

-- Create triggers for automatic timestamp updates
CREATE TRIGGER IF NOT EXISTS vm_drafts_enhanced_timestamp_trigger
    AFTER UPDATE ON vm_drafts_enhanced
    WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE vm_drafts_enhanced 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS vm_builder_audit_timestamp_trigger
    AFTER INSERT ON vm_builder_audit
BEGIN
    UPDATE vm_builder_audit 
    SET timestamp = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;
