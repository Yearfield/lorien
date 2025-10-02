-- 015_triggers_guard_and_timestamps.sql
-- =====================================================================
-- Timestamp & Guard triggers for nodes
-- =====================================================================

-- Ensure a clean slate if migrations are re-applied in dev/test
DROP TRIGGER IF EXISTS trg_nodes_set_created_at;
DROP TRIGGER IF EXISTS trg_nodes_set_updated_at;
DROP TRIGGER IF EXISTS trg_nodes_depth_parent_guard_ins;
DROP TRIGGER IF EXISTS trg_nodes_depth_parent_guard_upd;

-- NOTE: SQLite cannot assign to NEW.updated_at in BEFORE UPDATE triggers.
-- We use AFTER UPDATE, updating the same row. This does not recurse unless
-- PRAGMA recursive_triggers = ON (default is OFF).
CREATE TRIGGER IF NOT EXISTS trg_nodes_set_updated_at
AFTER UPDATE ON nodes
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
  UPDATE nodes
  SET updated_at = CURRENT_TIMESTAMP
  WHERE id = NEW.id;
END;

-- Guard depth/parent relationship at write time (extra safety alongside CHECKs)
CREATE TRIGGER IF NOT EXISTS trg_nodes_depth_parent_guard_ins
BEFORE INSERT ON nodes
FOR EACH ROW
BEGIN
  SELECT
    CASE
      WHEN ( (NEW.depth = 0 AND NEW.parent_id IS NULL)
             OR (NEW.depth > 0 AND NEW.parent_id IS NOT NULL) )
      THEN NULL
      ELSE RAISE(ABORT, 'depth/parent invariant violation')
    END;
END;

CREATE TRIGGER IF NOT EXISTS trg_nodes_depth_parent_guard_upd
BEFORE UPDATE ON nodes
FOR EACH ROW
BEGIN
  SELECT
    CASE
      WHEN ( (NEW.depth = 0 AND NEW.parent_id IS NULL)
             OR (NEW.depth > 0 AND NEW.parent_id IS NOT NULL) )
      THEN NULL
      ELSE RAISE(ABORT, 'depth/parent invariant violation')
    END;
END;