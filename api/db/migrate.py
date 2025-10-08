"""
Schema migration system for Lorien.

This module provides versioned, idempotent database migrations using a
schema_migrations tracking table. Each migration is applied exactly once
and recorded with a timestamp.

Migration files must be named with a numeric prefix (e.g., 000_baseline.sql,
001_add_feature.sql) and are applied in sorted order.
"""

import logging
import pathlib
import sqlite3

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = pathlib.Path(__file__).with_suffix("").parent / "migrations"

# Current schema version (update this when adding migrations)
SCHEMA_VERSION = 27  # Matches 027_add_large_workbook.sql


def get_schema_version() -> int:
    """Get the current target schema version."""
    return SCHEMA_VERSION


def apply_migrations(db_path: str) -> int:
    """
    Apply all pending migrations to the database at db_path.

    This function is idempotent - it tracks which migrations have been applied
    and only runs new ones. Safe to call on every app startup.

    Args:
        db_path: Path to SQLite database file

    Returns:
        Number of migrations applied in this run

    Raises:
        sqlite3.Error: If migration fails
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON;")

    try:
        # Ensure tracking table exists
        _ensure_migrations_table(conn)

        # Get already-applied migrations
        applied = _get_applied_migrations(conn)
        logger.debug(f"Already applied migrations: {applied}")

        # Get all migration files sorted by name
        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

        # Apply only pending migrations
        applied_count = 0
        for migration_file in migration_files:
            migration_name = migration_file.name

            if migration_name in applied:
                logger.debug(f"Skipping already-applied migration: {migration_name}")
                continue

            logger.info(f"Applying migration: {migration_name}")
            _apply_single_migration(conn, migration_file)
            applied_count += 1

        conn.commit()

        if applied_count > 0:
            logger.info(f"Applied {applied_count} new migration(s) to {db_path}")
        else:
            logger.debug(f"No new migrations to apply (current: {len(applied)})")

        return applied_count

    except Exception as e:
        conn.rollback()
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        conn.close()


def get_current_version(db_path: str) -> tuple[int, int]:
    """
    Get the current schema version from the database.

    Args:
        db_path: Path to SQLite database file

    Returns:
        Tuple of (applied_count, target_version) where:
        - applied_count: number of migrations applied
        - target_version: current SCHEMA_VERSION constant
    """
    conn = sqlite3.connect(db_path)
    try:
        # Check if migrations table exists
        cursor = conn.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='schema_migrations'
            """
        )
        if not cursor.fetchone():
            return (0, SCHEMA_VERSION)

        # Count applied migrations
        cursor = conn.execute("SELECT COUNT(*) FROM schema_migrations")
        result = cursor.fetchone()
        applied = result[0] if result else 0

        return (applied, SCHEMA_VERSION)
    finally:
        conn.close()


def _ensure_migrations_table(conn: sqlite3.Connection):
    """Create the migrations tracking table if it doesn't exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            migration_name TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
            checksum TEXT
        )
        """
    )
    conn.commit()


def _get_applied_migrations(conn: sqlite3.Connection) -> list[str]:
    """Get list of already-applied migration names."""
    cursor = conn.execute("SELECT migration_name FROM schema_migrations ORDER BY migration_name")
    return [row[0] for row in cursor.fetchall()]


def _apply_single_migration(conn: sqlite3.Connection, migration_file: pathlib.Path):
    """Apply a single migration file and record it."""
    migration_name = migration_file.name
    sql = migration_file.read_text(encoding="utf-8").strip()

    if not sql:
        logger.warning(f"Migration {migration_name} is empty, skipping")
        return

    # Execute the migration
    conn.executescript(sql)

    # Record it as applied
    conn.execute("INSERT INTO schema_migrations (migration_name) VALUES (?)", (migration_name,))
    logger.debug(f"Recorded migration: {migration_name}")
