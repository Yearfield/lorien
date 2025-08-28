-- Migration: Add red_flag_audit table
-- Safe to re-apply (IF NOT EXISTS)
-- Date: 2025-08-28
-- Purpose: Append-only audit trail for red flag assignments and removals

CREATE TABLE IF NOT EXISTS red_flag_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id INTEGER NOT NULL,
    flag_id INTEGER NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('assign', 'remove')),
    user TEXT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (flag_id) REFERENCES red_flags(id) ON DELETE CASCADE
);

-- Index for fast lookups by node and time
CREATE INDEX IF NOT EXISTS idx_red_flag_audit_node_ts
    ON red_flag_audit(node_id, ts);

-- Index for fast lookups by flag and time
CREATE INDEX IF NOT EXISTS idx_red_flag_audit_flag_ts
    ON red_flag_audit(flag_id, ts);

-- Index for user activity tracking
CREATE INDEX IF NOT EXISTS idx_red_flag_audit_user_ts
    ON red_flag_audit(user, ts);
