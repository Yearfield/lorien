import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator
from fastapi import Depends
from api.settings import get_db_path
from api.repositories.tree_repo import TreeRepository

def _open_sqlite(path: str) -> sqlite3.Connection:
    # check_same_thread=False prevents SQLite from erroring when FastAPI/TestClient
    # runs handlers on a different thread. We still only use each connection per-request.
    conn = sqlite3.connect(
        path,
        detect_types=sqlite3.PARSE_DECLTYPES,
        isolation_level=None,  # autocommit-style; we will manage BEGIN/COMMIT manually
        check_same_thread=False,
    )
    conn.row_factory = sqlite3.Row
    # Pragmas on each open (safe, idempotent)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

def get_db_connection() -> Iterator[sqlite3.Connection]:
    path = get_db_path()
    conn = _open_sqlite(path)
    try:
        conn.execute("BEGIN;")
        yield conn
        # Only commit if we haven't already rolled back
        try:
            conn.execute("COMMIT;")
        except sqlite3.OperationalError as e:
            if "no transaction is active" not in str(e):
                raise
    except Exception:
        try:
            conn.execute("ROLLBACK;")
        except sqlite3.OperationalError as e:
            if "no transaction is active" not in str(e):
                raise
        raise
    finally:
        conn.close()

def get_repository(conn: sqlite3.Connection = Depends(get_db_connection)) -> TreeRepository:
    return TreeRepository(conn)