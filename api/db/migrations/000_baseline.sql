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

  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),

  CHECK ( (depth = 0 AND parent_id IS NULL) OR (depth > 0 AND parent_id IS NOT NULL) )
);

-- Exactly one child per slot under a given parent (partial unique)
CREATE UNIQUE INDEX IF NOT EXISTS idx_parent_slot_unique
  ON nodes(parent_id, slot)
  WHERE parent_id IS NOT NULL;

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_nodes_parent_id ON nodes(parent_id);
CREATE INDEX IF NOT EXISTS idx_nodes_depth_label ON nodes(depth, label);

-- Outcomes (if present in prod; keep as-is)
CREATE TABLE IF NOT EXISTS outcomes (
  id INTEGER PRIMARY KEY,
  node_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  text TEXT NOT NULL
);

-- Dictionary terms (if present in prod; keep as-is)
CREATE TABLE IF NOT EXISTS dictionary_terms (
  id        INTEGER PRIMARY KEY,
  type      TEXT NOT NULL,
  term      TEXT NOT NULL,
  normalized TEXT,
  hints     TEXT,
  red_flag  INTEGER DEFAULT 0,
  updated_at TEXT,
  created_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_dict_type_normalized ON dictionary_terms(type, normalized);
