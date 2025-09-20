-- 014_edge_meta.sql
BEGIN;

CREATE TABLE IF NOT EXISTS edge_meta (
  parent_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  child_id  INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  red_flag  INTEGER NOT NULL DEFAULT 0 CHECK (red_flag IN (0,1)),
  PRIMARY KEY (parent_id, child_id)
);

CREATE INDEX IF NOT EXISTS idx_edge_meta_parent ON edge_meta(parent_id);
CREATE INDEX IF NOT EXISTS idx_edge_meta_child ON edge_meta(child_id);

COMMIT;
