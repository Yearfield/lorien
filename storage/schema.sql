-- SQLite schema for decision tree application
-- Enforces exactly 5 children per parent; canonical depths 0..5; slots 0(root) / 1..5(children)

-- ---- Connection pragmas (note: foreign_keys must also be enabled per-connection in app code)
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = MEMORY;

-- ---- TABLES ----

-- Nodes table: each row is a node in the tree
CREATE TABLE IF NOT EXISTS nodes (
    id         INTEGER PRIMARY KEY,
    parent_id  INTEGER NULL REFERENCES nodes(id) ON DELETE CASCADE,
    depth      INTEGER NOT NULL CHECK (depth BETWEEN 0 AND 5),   -- 0=root (Vital Measurement)
    slot       INTEGER NOT NULL CHECK (
                   (depth = 0 AND slot = 0) OR                   -- root must be slot 0
                   (depth BETWEEN 1 AND 5 AND slot BETWEEN 1 AND 5)
               ),
    label      TEXT    NOT NULL,                                 -- display text
    is_leaf    INTEGER NOT NULL DEFAULT 0,                       -- convenience flag (depth==5)
    created_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    -- Parent presence and depth relationship:
    CHECK ( (depth = 0 AND parent_id IS NULL) OR (depth > 0 AND parent_id IS NOT NULL) )
);

-- Exactly one child per slot per parent (imposes max 5 children)
CREATE UNIQUE INDEX IF NOT EXISTS idx_parent_slot_unique
ON nodes(parent_id, slot) WHERE parent_id IS NOT NULL;

-- Triage per LEAF node only (depth=5)
CREATE TABLE IF NOT EXISTS triage (
    node_id           INTEGER PRIMARY KEY REFERENCES nodes(id) ON DELETE CASCADE,
    diagnostic_triage TEXT,     -- nullable; can be edited later
    actions           TEXT,     -- nullable
    created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Red flags catalogue
CREATE TABLE IF NOT EXISTS red_flags (
    id          INTEGER PRIMARY KEY,
    name        TEXT UNIQUE NOT NULL,
    description TEXT,
    severity    TEXT CHECK(severity IN ('low','medium','high','critical')) DEFAULT 'medium',
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Junction: node <-> red flag (many-to-many)
CREATE TABLE IF NOT EXISTS node_red_flags (
    node_id     INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    red_flag_id INTEGER NOT NULL REFERENCES red_flags(id) ON DELETE CASCADE,
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    PRIMARY KEY (node_id, red_flag_id)
);

-- ---- INDEXES ----
CREATE INDEX IF NOT EXISTS idx_nodes_parent_depth ON nodes(parent_id, depth);
CREATE INDEX IF NOT EXISTS idx_nodes_depth        ON nodes(depth);
CREATE INDEX IF NOT EXISTS idx_nodes_label        ON nodes(label);
CREATE INDEX IF NOT EXISTS idx_node_red_flags_node ON node_red_flags(node_id);
CREATE INDEX IF NOT EXISTS idx_node_red_flags_flag ON node_red_flags(red_flag_id);

-- Performance indexes for next incomplete parent queries
CREATE INDEX IF NOT EXISTS idx_nodes_parent_slot ON nodes(parent_id, slot);
CREATE INDEX IF NOT EXISTS idx_nodes_parent_depth ON nodes(parent_id, depth);

-- ---- VIEWS ----

-- Parents with exactly 5 children (fast check)
CREATE VIEW IF NOT EXISTS v_parents_exact_5 AS
SELECT
  p.id       AS parent_id,
  COUNT(c.id) AS child_count,
  GROUP_CONCAT(c.label, ', ') AS children
FROM nodes p
LEFT JOIN nodes c ON c.parent_id = p.id
WHERE p.depth BETWEEN 0 AND 4
GROUP BY p.id
HAVING child_count = 5;

-- Parents with missing children and which slots are missing
CREATE VIEW IF NOT EXISTS v_missing_slots AS
WITH slots(slot) AS (VALUES (1),(2),(3),(4),(5))
SELECT
  p.id AS parent_id,
  GROUP_CONCAT(s.slot) AS missing_slots
FROM nodes p
CROSS JOIN slots s
LEFT JOIN nodes c
  ON c.parent_id = p.id AND c.slot = s.slot
WHERE p.depth BETWEEN 0 AND 4
  AND c.id IS NULL
GROUP BY p.id
HAVING missing_slots IS NOT NULL;

-- Next incomplete parents (no LIMIT here; API can order/limit as needed)
CREATE VIEW IF NOT EXISTS v_next_incomplete_parent AS
SELECT
  p.parent_id,
  m.missing_slots
FROM (
  SELECT id AS parent_id, depth
  FROM nodes
  WHERE depth BETWEEN 0 AND 4
) p
JOIN v_missing_slots m ON m.parent_id = p.parent_id
ORDER BY p.depth ASC, p.parent_id ASC;

-- Tree coverage summary
CREATE VIEW IF NOT EXISTS v_tree_coverage AS
SELECT
  depth,
  COUNT(*) AS total_nodes,
  SUM(CASE WHEN depth = 5 THEN 1 ELSE 0 END) AS leaf_count
FROM nodes
GROUP BY depth
ORDER BY depth;

-- Materialized paths (complete root→leaf) for export
CREATE VIEW IF NOT EXISTS v_paths_complete AS
SELECT
  r.id    AS root_id,
  r.label AS vital_measurement,
  n1.label AS node_1,
  n2.label AS node_2,
  n3.label AS node_3,
  n4.label AS node_4,
  n5.label AS node_5,
  t.diagnostic_triage,
  t.actions,
  n5.id   AS leaf_id
FROM nodes r
JOIN nodes n1 ON n1.parent_id = r.id  AND n1.depth = 1
JOIN nodes n2 ON n2.parent_id = n1.id AND n2.depth = 2
JOIN nodes n3 ON n3.parent_id = n2.id AND n3.depth = 3
JOIN nodes n4 ON n4.parent_id = n3.id AND n4.depth = 4
JOIN nodes n5 ON n5.parent_id = n4.id AND n5.depth = 5
LEFT JOIN triage t ON t.node_id = n5.id
WHERE r.depth = 0;

-- ---- TRIGGERS ----

-- Keep updated_at + is_leaf in sync on nodes UPDATE
CREATE TRIGGER IF NOT EXISTS tr_nodes_touch_on_update
AFTER UPDATE ON nodes
FOR EACH ROW
BEGIN
  UPDATE nodes
  SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now'),
      is_leaf    = CASE WHEN depth = 5 THEN 1 ELSE 0 END
  WHERE id = NEW.id;
END;

-- Ensure is_leaf set on INSERT (and touch updated_at)
CREATE TRIGGER IF NOT EXISTS tr_nodes_touch_on_insert
AFTER INSERT ON nodes
FOR EACH ROW
BEGIN
  UPDATE nodes
  SET is_leaf    = CASE WHEN depth = 5 THEN 1 ELSE 0 END,
      updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
  WHERE id = NEW.id;
END;

-- Validate parent-child depth relation: child.depth must equal parent.depth + 1
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

-- Enforce root parent rule explicitly (already covered by CHECK, but defensive)
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

-- Triage only allowed for leaf nodes (depth = 5)
CREATE TRIGGER IF NOT EXISTS tr_triage_only_leaf
BEFORE INSERT ON triage
FOR EACH ROW
BEGIN
  SELECT CASE
    WHEN (SELECT depth FROM nodes WHERE id = NEW.node_id) != 5
      THEN RAISE(ABORT, 'Triage is only allowed for leaf nodes (depth=5)')
  END;
END;

-- Touch triage.updated_at on UPDATE
CREATE TRIGGER IF NOT EXISTS tr_triage_touch_on_update
AFTER UPDATE ON triage
FOR EACH ROW
BEGIN
  UPDATE triage
  SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
  WHERE node_id = NEW.node_id;
END;
