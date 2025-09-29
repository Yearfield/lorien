-- 015_triggers_guard_and_timestamps.sql
BEGIN;

-- Normalize timestamps on INSERT/UPDATE (ISO8601Z)
DROP TRIGGER IF EXISTS trg_nodes_set_created_at;
DROP TRIGGER IF EXISTS trg_nodes_set_updated_at;

CREATE TRIGGER trg_nodes_set_created_at
BEFORE INSERT ON nodes
FOR EACH ROW
WHEN NEW.created_at IS NULL
BEGIN
  UPDATE nodes SET 
    created_at = strftime('%Y-%m-%dT%H:%M:%fZ','now'),
    updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
  WHERE rowid = NEW.rowid;
END;

CREATE TRIGGER trg_nodes_set_updated_at
BEFORE UPDATE ON nodes
FOR EACH ROW
BEGIN
  UPDATE nodes SET 
    updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
  WHERE rowid = NEW.rowid;
END;

-- Guard depth/parent relationship at write time (extra safety alongside CHECKs)
DROP TRIGGER IF EXISTS trg_nodes_depth_parent_guard_ins;
DROP TRIGGER IF EXISTS trg_nodes_depth_parent_guard_upd;

CREATE TRIGGER trg_nodes_depth_parent_guard_ins
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

CREATE TRIGGER trg_nodes_depth_parent_guard_upd
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

COMMIT;
