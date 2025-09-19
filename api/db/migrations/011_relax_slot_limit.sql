-- 011_relax_slot_limit.sql
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

-- Drop dependent views before table rebuild
DROP VIEW IF EXISTS v_parents_exact_5;
DROP VIEW IF EXISTS v_missing_slots;
DROP VIEW IF EXISTS v_tree_coverage;
DROP VIEW IF EXISTS v_next_incomplete_parent;
DROP VIEW IF EXISTS v_paths_complete;

-- Rebuild nodes with relaxed slot constraint (allow >=1, no upper bound)
CREATE TABLE IF NOT EXISTS nodes__new (
    id         INTEGER PRIMARY KEY,
    parent_id  INTEGER NULL REFERENCES nodes(id) ON DELETE CASCADE,
    depth      INTEGER NOT NULL CHECK (depth BETWEEN 0 AND 5),
    slot       INTEGER NULL CHECK (
        (parent_id IS NULL AND slot IS NULL AND depth = 0) OR
        (parent_id IS NOT NULL AND slot IS NOT NULL AND slot >= 1 AND depth BETWEEN 1 AND 5)
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
SELECT id, parent_id, depth, slot, label, is_leaf, created_at, updated_at
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

COMMIT;
PRAGMA foreign_keys=ON;
