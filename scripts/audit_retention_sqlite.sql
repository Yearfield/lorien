-- Audit Retention Script
-- Retain last 30 days or cap at 50k rows (whichever first).

-- First, identify rows to delete based on age (older than 30 days)
DELETE FROM red_flag_audit
WHERE id IN (
    SELECT id FROM red_flag_audit
    WHERE ts < datetime('now','-30 days')
);

-- Then, if we still have more than 50k rows, remove the oldest ones
DELETE FROM red_flag_audit
WHERE id IN (
    SELECT id FROM red_flag_audit
    WHERE id NOT IN (
        SELECT id FROM red_flag_audit
        ORDER BY ts DESC, id DESC
        LIMIT 50000
    )
);

-- Log the retention operation (only if we have valid data)
-- Note: We can't insert NULL values due to constraints, so we'll skip this for now
-- INSERT INTO red_flag_audit (node_id, flag_id, action, user, ts)
-- VALUES (NULL, NULL, 'retention_cleanup', 'system', datetime('now'));

-- Create a view for monitoring retention status
CREATE VIEW IF NOT EXISTS audit_retention_status AS
SELECT 
    COUNT(*) as total_rows,
    MIN(ts) as oldest_record,
    MAX(ts) as newest_record,
    CASE 
        WHEN COUNT(*) > 50000 THEN 'OVER_LIMIT'
        WHEN MIN(ts) < datetime('now','-30 days') THEN 'OVER_AGE'
        ELSE 'OK'
    END as retention_status
FROM red_flag_audit;
