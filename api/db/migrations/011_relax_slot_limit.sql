-- 011_relax_slot_limit.sql
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

-- Drop dependent views and triggers before table rebuild
DROP VIEW IF EXISTS v_parents_exact_5;
DROP VIEW IF EXISTS v_missing_slots;
DROP VIEW IF EXISTS v_tree_coverage;
DROP VIEW IF EXISTS v_next_incomplete_parent;
DROP VIEW IF EXISTS v_paths_complete;

-- Drop all triggers that reference the nodes table
DROP TRIGGER IF EXISTS tr_nodes_touch_on_update;
DROP TRIGGER IF EXISTS tr_nodes_touch_on_insert;
DROP TRIGGER IF EXISTS tr_validate_parent_depth_equal;
DROP TRIGGER IF EXISTS tr_validate_root_parent;
DROP TRIGGER IF EXISTS tr_triage_only_leaf;
DROP TRIGGER IF EXISTS tr_triage_touch_on_update;

-- Rebuild nodes with relaxed slot constraint (allow >=1, no upper bound)
CREATE TABLE IF NOT EXISTS nodes__new (
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
    -- Parent presence and depth relationship:
    CHECK ( (depth = 0 AND parent_id IS NULL) OR (depth > 0 AND parent_id IS NOT NULL) )
);

-- Copy data from old nodes to new table
INSERT INTO nodes__new (id, parent_id, depth, slot, label, is_leaf, created_at, updated_at)
SELECT id, parent_id, depth, slot, label, is_leaf, 
       COALESCE(created_at, datetime('now')) as created_at,
       COALESCE(updated_at, datetime('now')) as updated_at
FROM nodes;

-- Drop old table and rename
DROP TABLE nodes;
ALTER TABLE nodes__new RENAME TO nodes;

-- Recreate indexes (unique and perf indexes)
CREATE UNIQUE INDEX IF NOT EXISTS idx_parent_slot_unique
  ON nodes(parent_id, slot) WHERE parent_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_nodes_parent_depth
  ON nodes(parent_id, depth);

CREATE INDEX IF NOT EXISTS idx_nodes_label_depth
  ON nodes(label, depth);

-- Recreate triggers
CREATE TRIGGER tr_nodes_touch_on_update
AFTER UPDATE ON nodes
FOR EACH ROW
BEGIN
  UPDATE nodes
  SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now'),
      is_leaf    = CASE WHEN depth = 5 THEN 1 ELSE 0 END
  WHERE id = NEW.id;
END;

CREATE TRIGGER tr_nodes_touch_on_insert
AFTER INSERT ON nodes
FOR EACH ROW
BEGIN
  UPDATE nodes
  SET is_leaf    = CASE WHEN depth = 5 THEN 1 ELSE 0 END,
      updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
  WHERE id = NEW.id;
END;

CREATE TRIGGER tr_validate_parent_depth_equal
BEFORE INSERT ON nodes
FOR EACH ROW
WHEN NEW.parent_id IS NOT NULL
BEGIN
  SELECT CASE
    WHEN (SELECT depth FROM nodes WHERE id = NEW.parent_id) + 1 != NEW.depth
    THEN RAISE(ABORT, 'Child depth must equal parent depth + 1')
  END;
END;

CREATE TRIGGER tr_validate_root_parent
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

COMMIT;
PRAGMA foreign_keys=ON;
