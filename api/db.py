import os, sqlite3
from contextlib import contextmanager

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS nodes (
  id        INTEGER PRIMARY KEY,
  parent_id INTEGER REFERENCES nodes(id) ON DELETE CASCADE,
  label     TEXT NOT NULL,
  depth     INTEGER NOT NULL CHECK(depth BETWEEN 0 AND 5),
  slot      INTEGER CHECK(slot BETWEEN 1 AND 5),
  UNIQUE(parent_id, slot),
  UNIQUE(parent_id, label)
);
CREATE INDEX IF NOT EXISTS idx_nodes_parent ON nodes(parent_id);
-- Stabilize root uniqueness by label (NULL-safe via partial unique index)
CREATE UNIQUE INDEX IF NOT EXISTS ux_roots_label
  ON nodes(label) WHERE parent_id IS NULL;

CREATE TABLE IF NOT EXISTS outcomes (
  node_id  INTEGER PRIMARY KEY REFERENCES nodes(id) ON DELETE CASCADE,
  diagnostic_triage TEXT NOT NULL,
  actions          TEXT NOT NULL
);

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
"""

def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)

def get_conn() -> sqlite3.Connection:
    db_path = os.getenv("LORIEN_DB", "lorien.db")
    conn = sqlite3.connect(db_path, isolation_level=None, check_same_thread=False)
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
