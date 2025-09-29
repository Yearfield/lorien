-- 015_perf_indexes.sql
BEGIN;

-- Depth filter acceleration (roots listing, coverage, scans)
CREATE INDEX IF NOT EXISTS idx_nodes_depth ON nodes(depth);

-- Case/space-insensitive label lookups used by engines and repo
CREATE INDEX IF NOT EXISTS idx_nodes_label_norm ON nodes( lower(trim(label)) );

COMMIT;

