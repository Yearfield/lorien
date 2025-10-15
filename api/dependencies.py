import sqlite3
from collections.abc import AsyncIterator
import logging
import os

from anyio import to_thread
from fastapi import Depends

from api.repositories.tree_repo import TreeRepository
from api.settings import get_db_path
from api.db.connection_pool import get_connection_pool

logger = logging.getLogger(__name__)


def _open_sqlite(path: str) -> sqlite3.Connection:
    """
    Legacy function for creating SQLite connections.
    Used for backward compatibility and testing.
    """
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


async def get_db_connection() -> AsyncIterator[sqlite3.Connection]:
    """
    Get a database connection from the connection pool.
    
    This is the preferred method for production use as it provides:
    - Connection pooling and reuse
    - Connection limits and monitoring
    - Performance metrics
    - Automatic transaction management
    """
    # Check if connection pooling is enabled
    use_pool = os.getenv("LORIEN_USE_CONNECTION_POOL", "true").lower() == "true"
    
    if use_pool:
        try:
            pool = get_connection_pool()
            async with pool.get_connection() as conn:
                yield conn
        except RuntimeError:
            # Fallback to legacy connection if pool not initialized
            logger.warning("Connection pool not available, falling back to legacy connection")
            async for conn in _legacy_db_connection():
                yield conn
                break
    else:
        async for conn in _legacy_db_connection():
            yield conn
            break


async def _legacy_db_connection() -> AsyncIterator[sqlite3.Connection]:
    """
    Legacy database connection method.
    Used when connection pooling is disabled or not available.
    """
    path = get_db_path()
    conn = _open_sqlite(path)
    try:
        await to_thread.run_sync(conn.execute, "BEGIN;")
        yield conn
        # Only commit if we haven't already rolled back
        try:
            await to_thread.run_sync(conn.execute, "COMMIT;")
        except sqlite3.OperationalError as e:
            if "no transaction is active" not in str(e):
                raise
    except Exception:
        try:
            await to_thread.run_sync(conn.execute, "ROLLBACK;")
        except sqlite3.OperationalError as e:
            if "no transaction is active" not in str(e):
                raise
        raise
    finally:
        conn.close()


async def get_repository(conn: sqlite3.Connection = Depends(get_db_connection)) -> TreeRepository:
    return TreeRepository(conn)
