-- 013_path_meta.sql
-- Add path metadata table to store D6 (Diagnostic Triage) and Notes (Actions) per leaf path
BEGIN;

CREATE TABLE IF NOT EXISTS path_meta (
  leaf_id INTEGER PRIMARY KEY
         REFERENCES nodes(id) ON DELETE CASCADE,
  d6     TEXT,   -- "Diagnostic Triage" (or other D6 semantics)
  notes  TEXT    -- "Actions/Notes"
);

-- Helpful for scanning leaves quickly (optional; PK already indexed)
CREATE INDEX IF NOT EXISTS idx_path_meta_leaf ON path_meta(leaf_id);

COMMIT;
