"""
Dependency injection for FastAPI application.
"""

import sqlite3
from typing import Iterator

from storage.sqlite import SQLiteRepository

from api.settings import get_db_path


def get_repository() -> SQLiteRepository:
    """Return a configured repository instance."""
    return SQLiteRepository()


def _open_conn() -> sqlite3.Connection:
    """Open a new database connection with standard pragmas applied."""
    conn = sqlite3.connect(get_db_path(), check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def get_db_connection() -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection for request-scoped usage."""
    conn = _open_conn()
    try:
        yield conn
    finally:
        try:
            conn.close()
        except Exception:
            pass
