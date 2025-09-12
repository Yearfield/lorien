-- Migration: Add Dictionary Governance System
-- Safe to re-apply (IF NOT EXISTS)
-- Date: 2025-09-11
-- Purpose: Add comprehensive dictionary governance with approval workflows, status management, and audit trails

-- Enhanced dictionary_terms table with governance fields
CREATE TABLE IF NOT EXISTS dictionary_terms_governance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    term TEXT NOT NULL,
    normalized TEXT NOT NULL,
    hints TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    version INTEGER NOT NULL DEFAULT 1,
    created_by TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_by TEXT,
    approved_at DATETIME,
    rejection_reason TEXT,
    approval_level TEXT NOT NULL DEFAULT 'none',
    tags TEXT,
    metadata TEXT,
    parent_id INTEGER,
    UNIQUE(type, normalized, version)
);

-- Dictionary workflows configuration
CREATE TABLE IF NOT EXISTS dictionary_workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT UNIQUE NOT NULL,
    approval_level TEXT NOT NULL DEFAULT 'none',
    requires_medical_review BOOLEAN DEFAULT 0,
    auto_approve_editors BOOLEAN DEFAULT 0,
    max_versions INTEGER DEFAULT 10,
    retention_days INTEGER DEFAULT 365,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Dictionary changes audit trail
CREATE TABLE IF NOT EXISTS dictionary_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    actor TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    before_state TEXT,
    after_state TEXT,
    reason TEXT,
    metadata TEXT,
    FOREIGN KEY (term_id) REFERENCES dictionary_terms_governance(id) ON DELETE CASCADE
);

-- Dictionary approvals queue
CREATE TABLE IF NOT EXISTS dictionary_approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term_id INTEGER NOT NULL,
    approver TEXT NOT NULL,
    status TEXT NOT NULL,
    reason TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (term_id) REFERENCES dictionary_terms_governance(id) ON DELETE CASCADE
);

-- Dictionary term relationships
CREATE TABLE IF NOT EXISTS dictionary_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER NOT NULL,
    child_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES dictionary_terms_governance(id) ON DELETE CASCADE,
    FOREIGN KEY (child_id) REFERENCES dictionary_terms_governance(id) ON DELETE CASCADE,
    UNIQUE(parent_id, child_id, relationship_type)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_dict_gov_type_status 
    ON dictionary_terms_governance(type, status);

CREATE INDEX IF NOT EXISTS idx_dict_gov_created_by 
    ON dictionary_terms_governance(created_by);

CREATE INDEX IF NOT EXISTS idx_dict_gov_updated_at 
    ON dictionary_terms_governance(updated_at);

CREATE INDEX IF NOT EXISTS idx_dict_gov_approved_by 
    ON dictionary_terms_governance(approved_by);

CREATE INDEX IF NOT EXISTS idx_dict_gov_approval_level 
    ON dictionary_terms_governance(approval_level);

CREATE INDEX IF NOT EXISTS idx_dict_changes_term_id 
    ON dictionary_changes(term_id);

CREATE INDEX IF NOT EXISTS idx_dict_changes_timestamp 
    ON dictionary_changes(timestamp);

CREATE INDEX IF NOT EXISTS idx_dict_changes_action 
    ON dictionary_changes(action);

CREATE INDEX IF NOT EXISTS idx_dict_approvals_term_id 
    ON dictionary_approvals(term_id);

CREATE INDEX IF NOT EXISTS idx_dict_approvals_status 
    ON dictionary_approvals(status);

CREATE INDEX IF NOT EXISTS idx_dict_relationships_parent 
    ON dictionary_relationships(parent_id);

CREATE INDEX IF NOT EXISTS idx_dict_relationships_child 
    ON dictionary_relationships(child_id);

-- Insert default workflows
INSERT OR IGNORE INTO dictionary_workflows 
(type, approval_level, requires_medical_review, auto_approve_editors, max_versions, retention_days)
VALUES 
('vital_measurement', 'medical_review', 1, 0, 5, 730),
('node_label', 'editor', 0, 1, 10, 365),
('outcome_template', 'medical_review', 1, 0, 3, 1095);

-- Create views for easy querying
CREATE VIEW IF NOT EXISTS dictionary_governance_summary AS
SELECT 
    id,
    type,
    term,
    normalized,
    status,
    version,
    created_by,
    created_at,
    updated_by,
    updated_at,
    approved_by,
    approved_at,
    approval_level,
    CASE 
        WHEN status = 'approved' THEN 'active'
        WHEN status = 'pending_approval' THEN 'pending'
        WHEN status = 'rejected' THEN 'rejected'
        WHEN status = 'deprecated' THEN 'deprecated'
        ELSE 'unknown'
    END as governance_status
FROM dictionary_terms_governance
ORDER BY updated_at DESC;

CREATE VIEW IF NOT EXISTS dictionary_pending_approvals AS
SELECT 
    id,
    type,
    term,
    normalized,
    hints,
    version,
    created_by,
    created_at,
    approval_level
FROM dictionary_terms_governance
WHERE status = 'pending_approval'
ORDER BY created_at ASC;

CREATE VIEW IF NOT EXISTS dictionary_approval_stats AS
SELECT 
    type,
    status,
    COUNT(*) as count
FROM dictionary_terms_governance
WHERE status IN ('approved', 'rejected')
GROUP BY type, status;

-- Create triggers for automatic version management
CREATE TRIGGER IF NOT EXISTS dictionary_version_trigger
    AFTER UPDATE ON dictionary_terms_governance
    WHEN NEW.status != OLD.status AND NEW.status = 'pending_approval'
BEGIN
    UPDATE dictionary_terms_governance 
    SET version = version + 1 
    WHERE id = NEW.id;
END;

-- Create trigger for automatic timestamp updates
CREATE TRIGGER IF NOT EXISTS dictionary_timestamp_trigger
    AFTER UPDATE ON dictionary_terms_governance
BEGIN
    UPDATE dictionary_terms_governance 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;
