PRAGMA foreign_keys = ON;

-- Nodes
CREATE TABLE IF NOT EXISTS nodes (
  id        INTEGER PRIMARY KEY,
  parent_id INTEGER NULL REFERENCES nodes(id) ON DELETE CASCADE,
  depth     INTEGER NOT NULL CHECK (depth BETWEEN 0 AND 5),

  -- Root: slot NULL; Non-root: slot 1..5
  slot      INTEGER NULL CHECK (
    (parent_id IS NULL AND slot IS NULL AND depth = 0) OR
    (parent_id IS NOT NULL AND slot BETWEEN 1 AND 5 AND depth BETWEEN 1 AND 5)
  ),

  label     TEXT NOT NULL,       -- Duplicates allowed (no UNIQUE on label)
  is_leaf   INTEGER NOT NULL DEFAULT 0,

  -- Timestamps: present from baseline so later trigger migrations can rely on them
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CHECK ( (depth = 0 AND parent_id IS NULL) OR (depth > 0 AND parent_id IS NOT NULL) )
);

-- Exactly one child per slot under a given parent (partial unique)
CREATE UNIQUE INDEX IF NOT EXISTS idx_parent_slot_unique
  ON nodes(parent_id, slot)
  WHERE parent_id IS NOT NULL;

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_nodes_parent_id ON nodes(parent_id);
CREATE INDEX IF NOT EXISTS idx_nodes_depth_label ON nodes(depth, label);
