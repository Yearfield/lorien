-- 019_relax_slot_limit_again.sql
-- Fix regression from 017 that reintroduced slot BETWEEN 1 AND 5.
-- Allow unbounded child slots (slot >= 1) while keeping depth 0..6.

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

-- Drop dependent views before table rebuild
DROP VIEW IF EXISTS v_parents_exact_5;
DROP VIEW IF EXISTS v_missing_slots;
DROP VIEW IF EXISTS v_tree_coverage;
DROP VIEW IF EXISTS v_next_incomplete_parent;
DROP VIEW IF EXISTS v_paths_complete;

-- Rebuild nodes with relaxed slot constraint
CREATE TABLE nodes_new_019 (
    id         INTEGER PRIMARY KEY,
    parent_id  INTEGER NULL REFERENCES nodes(id) ON DELETE CASCADE,
    depth      INTEGER NOT NULL CHECK (depth BETWEEN 0 AND 6),
    slot       INTEGER NULL CHECK (
        (parent_id IS NULL AND slot IS NULL AND depth = 0) OR
        (parent_id IS NOT NULL AND slot IS NOT NULL AND slot >= 1 AND depth BETWEEN 1 AND 6)
    ),
    label      TEXT    NOT NULL,
    is_leaf    INTEGER NOT NULL DEFAULT 0,
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT    NOT NULL DEFAULT (datetime('now')),
    CHECK ( (depth = 0 AND parent_id IS NULL) OR (depth > 0 AND parent_id IS NOT NULL) )
);

-- Copy existing data
INSERT INTO nodes_new_019 (id, parent_id, depth, slot, label, is_leaf, created_at, updated_at)
SELECT id, parent_id, depth, slot, label, is_leaf, created_at, updated_at
FROM nodes;

-- Replace table
DROP TABLE nodes;
ALTER TABLE nodes_new_019 RENAME TO nodes;

-- Recreate indexes
CREATE UNIQUE INDEX IF NOT EXISTS idx_parent_slot_unique
  ON nodes(parent_id, slot) WHERE parent_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_nodes_parent_depth ON nodes(parent_id, depth);
CREATE INDEX IF NOT EXISTS idx_nodes_depth        ON nodes(depth);
CREATE INDEX IF NOT EXISTS idx_nodes_label        ON nodes(label);
CREATE INDEX IF NOT EXISTS idx_nodes_parent_slot  ON nodes(parent_id, slot);

-- Recreate triggers that were dropped with table replacement
CREATE TRIGGER IF NOT EXISTS tr_nodes_touch_on_update
AFTER UPDATE ON nodes
FOR EACH ROW
BEGIN
  UPDATE nodes
  SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now'),
      is_leaf    = CASE WHEN depth >= 5 THEN 1 ELSE 0 END
  WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS tr_nodes_touch_on_insert
AFTER INSERT ON nodes
FOR EACH ROW
BEGIN
  UPDATE nodes
  SET is_leaf    = CASE WHEN depth >= 5 THEN 1 ELSE 0 END,
      updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
  WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS tr_validate_parent_depth_equal
BEFORE INSERT ON nodes
FOR EACH ROW
WHEN NEW.parent_id IS NOT NULL
BEGIN
  SELECT CASE
    WHEN (SELECT depth FROM nodes WHERE id = NEW.parent_id) + 1 != NEW.depth
    THEN RAISE(ABORT, 'Child depth must equal parent depth + 1')
  END;
END;

CREATE TRIGGER IF NOT EXISTS tr_validate_root_parent
BEFORE INSERT ON nodes
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN NEW.depth = 0 AND NEW.parent_id IS NOT NULL
      THEN RAISE(ABORT, 'Root node must have NULL parent_id')
    WHEN NEW.depth > 0 AND NEW.parent_id IS NULL
      THEN RAISE(ABORT, 'Non-root node must have a parent_id')
  END;
END;

-- Recreate views consistent with depth up to 6
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
  SUM(CASE WHEN depth >= 5 THEN 1 ELSE 0 END) AS leaves
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
HAVING child_count < 5
ORDER BY p.depth, p.id
LIMIT 1;

CREATE VIEW IF NOT EXISTS v_paths_complete AS
SELECT
  p.id,
  p.label,
  p.depth,
  CASE WHEN p.depth >= 5 THEN 1 ELSE 0 END AS is_leaf
FROM nodes p
WHERE p.depth >= 5;

COMMIT;
PRAGMA foreign_keys=ON;
