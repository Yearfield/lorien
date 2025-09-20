import os, sqlite3
from contextlib import contextmanager
from .settings import get_db_path
from api.db.migrate import apply_migrations

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS nodes (
  id         INTEGER PRIMARY KEY,
  parent_id  INTEGER NULL REFERENCES nodes(id) ON DELETE CASCADE,
  depth      INTEGER NOT NULL CHECK (depth BETWEEN 0 AND 5),   -- 0=root (Vital Measurement)
  slot       INTEGER CHECK (
                 (depth = 0 AND slot IS NULL) OR               -- root can have NULL slot
                 (depth = 0 AND slot = 0) OR                   -- root can be slot 0
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

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_nodes_parent_depth ON nodes(parent_id, depth);
CREATE INDEX IF NOT EXISTS idx_nodes_depth        ON nodes(depth);
CREATE INDEX IF NOT EXISTS idx_nodes_label        ON nodes(label);
CREATE INDEX IF NOT EXISTS idx_nodes_parent_slot ON nodes(parent_id, slot);
CREATE INDEX IF NOT EXISTS idx_nodes_parent ON nodes(parent_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_nodes_parent_slot_unique ON nodes(parent_id, slot) WHERE slot IS NOT NULL;
"""

def ensure_schema(conn: sqlite3.Connection) -> None:
    """Apply the schema to the database connection using migrations"""
    # This function is kept for backward compatibility but now uses migrations
    db_path = get_db_path()
    apply_migrations(db_path)

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path(), isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

@contextmanager
def tx(conn: sqlite3.Connection):
    try:
        conn.execute("BEGIN")
        yield
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
