-- 017_widen_depth_to_6.sql
-- Widen depth constraint to allow 0..6 (7 levels: D0..D6)

-- First, drop dependent views
DROP VIEW IF EXISTS v_parents_exact_5;
DROP VIEW IF EXISTS v_missing_slots;
DROP VIEW IF EXISTS v_tree_coverage;
DROP VIEW IF EXISTS v_next_incomplete_parent;
DROP VIEW IF EXISTS v_paths_complete;

-- Alter the existing table to widen the depth constraint
-- SQLite doesn't support ALTER COLUMN CHECK, so we need to recreate the constraint
-- We'll do this by creating a new table and copying data

PRAGMA foreign_keys=off;
BEGIN TRANSACTION;

-- Create new table with widened depth constraint
CREATE TABLE nodes_new (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  parent_id INTEGER REFERENCES nodes(id) ON DELETE CASCADE,
  depth INTEGER NOT NULL CHECK (depth BETWEEN 0 AND 6),
  slot INTEGER NULL CHECK (
    (parent_id IS NULL AND slot IS NULL AND depth = 0) OR
    (parent_id IS NOT NULL AND slot >= 1 AND depth BETWEEN 1 AND 6)
  ),
  label TEXT NOT NULL,
  is_leaf INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Copy all data from existing table
INSERT INTO nodes_new (id, parent_id, depth, slot, label, is_leaf, created_at, updated_at)
SELECT id, parent_id, depth, slot, label, is_leaf, created_at, updated_at
FROM nodes;

-- Drop old table and rename new one
DROP TABLE nodes;
ALTER TABLE nodes_new RENAME TO nodes;

-- Recreate essential indexes
CREATE INDEX IF NOT EXISTS idx_nodes_parent_id ON nodes(parent_id);
CREATE INDEX IF NOT EXISTS idx_nodes_depth ON nodes(depth);
CREATE INDEX IF NOT EXISTS idx_nodes_label_ci ON nodes(LOWER(TRIM(label)));

COMMIT;
PRAGMA foreign_keys=on;

-- Recreate views with updated depth constraints
CREATE VIEW IF NOT EXISTS v_parents_exact_5 AS
SELECT
  p.id AS parent_id,
  COUNT(c.id) AS child_count,
  GROUP_CONCAT(c.label, ', ') AS children
FROM nodes p
LEFT JOIN nodes c ON c.parent_id = p.id
WHERE p.depth BETWEEN 0 AND 5
GROUP BY p.id
HAVING child_count = 5;

CREATE VIEW IF NOT EXISTS v_missing_slots AS
SELECT
  p.id AS parent_id,
  TRIM(
    GROUP_CONCAT(
      CASE 
        WHEN NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = p.id AND c.slot = 1) THEN '1'
        WHEN NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = p.id AND c.slot = 2) THEN '2'
        WHEN NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = p.id AND c.slot = 3) THEN '3'
        WHEN NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = p.id AND c.slot = 4) THEN '4'
        WHEN NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = p.id AND c.slot = 5) THEN '5'
        WHEN NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = p.id AND c.slot = 6) THEN '6'
        WHEN NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = p.id AND c.slot = 7) THEN '7'
        WHEN NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = p.id AND c.slot = 8) THEN '8'
        WHEN NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = p.id AND c.slot = 9) THEN '9'
        WHEN NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = p.id AND c.slot = 10) THEN '10'
        ELSE NULL
      END, ', '
    )
  ) AS missing_slots
FROM nodes p
WHERE p.parent_id IS NOT NULL
GROUP BY p.id;

CREATE VIEW IF NOT EXISTS v_tree_coverage AS
SELECT
  depth,
  COUNT(*) AS total_nodes,
  SUM(CASE WHEN depth = 6 THEN 1 ELSE 0 END) AS leaves
FROM nodes
GROUP BY depth
ORDER BY depth;

CREATE VIEW IF NOT EXISTS v_next_incomplete_parent AS
SELECT
  p.id,
  p.label,
  p.depth,
  COUNT(c.id) AS child_count
FROM nodes p
LEFT JOIN nodes c ON c.parent_id = p.id
WHERE p.depth < 6
GROUP BY p.id, p.label, p.depth
HAVING child_count = 0
ORDER BY p.depth, p.id
LIMIT 1;

CREATE VIEW IF NOT EXISTS v_paths_complete AS
SELECT
  p.id,
  p.label,
  p.depth,
  CASE WHEN p.depth = 6 THEN 1 ELSE 0 END AS is_leaf
FROM nodes p
WHERE p.depth = 6;
