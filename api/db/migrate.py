import sqlite3
import pathlib
import os

MIGRATIONS_DIR = pathlib.Path(__file__).with_suffix("").parent / "migrations"

def apply_migrations(db_path: str):
    """Apply all migrations in order to the database at db_path"""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON;")
    
    # Get all migration files sorted by name
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    
    for migration_file in migration_files:
        print(f"Applying migration: {migration_file.name}")
        sql = migration_file.read_text(encoding="utf-8").strip()
        if sql:
            conn.executescript(sql)
    
    conn.commit()
    conn.close()
    print(f"Applied {len(migration_files)} migrations to {db_path}")

def get_migration_version(db_path: str) -> int:
    """Get the current migration version from the database"""
    conn = sqlite3.connect(db_path)
    try:
        # Check if migrations table exists
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='schema_migrations'
        """)
        if not cursor.fetchone():
            return 0
        
        # Get the latest migration version
        cursor = conn.execute("SELECT MAX(version) FROM schema_migrations")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0
    finally:
        conn.close()

def create_migrations_table(conn):
    """Create the migrations tracking table"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
        )
    """)