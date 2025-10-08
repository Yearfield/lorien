-- Migration: Add Flags namespace tables
-- Safe to re-apply (IF NOT EXISTS)
-- Date: 2025-09-02
-- Purpose: Add flags, node_flags, and flag_audit tables for the new flags namespace

-- Flags table (simplified from red_flags)
CREATE TABLE IF NOT EXISTS flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Node-Flag associations (many-to-many)
CREATE TABLE IF NOT EXISTS node_flags (
    node_id INTEGER NOT NULL,
    flag_id INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (node_id, flag_id),
    FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (flag_id) REFERENCES flags(id) ON DELETE CASCADE
);

-- Flag audit trail (append-only)
CREATE TABLE IF NOT EXISTS flag_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id INTEGER NOT NULL,
    flag_id INTEGER NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('assign', 'remove')),
    user TEXT NULL,
    ts TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (flag_id) REFERENCES flags(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_flags_label ON flags(label);
CREATE INDEX IF NOT EXISTS idx_node_flags_node_id ON node_flags(node_id);
CREATE INDEX IF NOT EXISTS idx_node_flags_flag_id ON node_flags(flag_id);
CREATE INDEX IF NOT EXISTS idx_flag_audit_node_ts ON flag_audit(node_id, ts);
CREATE INDEX IF NOT EXISTS idx_flag_audit_flag_ts ON flag_audit(flag_id, ts);
CREATE INDEX IF NOT EXISTS idx_flag_audit_user_ts ON flag_audit(user, ts);
CREATE INDEX IF NOT EXISTS idx_flag_audit_ts ON flag_audit(ts);
