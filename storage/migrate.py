#!/usr/bin/env python3
"""
Migration runner for Lorien database schema updates.
"""

import os
import sys
import sqlite3
from pathlib import Path

def get_db_path():
    """Get the database path from environment or default location."""
    db_path = os.getenv("LORIEN_DB_PATH")
    if db_path:
        return db_path
    
    # Default to app data directory
    try:
        from core.storage.path import get_db_path as get_default_path
        return get_default_path()
    except ImportError:
        # Fallback to default path
        home = os.path.expanduser("~")
        return os.path.join(home, ".local", "share", "lorien", "app.db")

def run_migration(db_path: str, migration_file: str):
    """Run a single migration file."""
    print(f"Running migration: {migration_file}")
    
    # Read migration SQL - look in migrations subdirectory
    migration_path = Path(__file__).parent / "migrations" / migration_file
    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_path}")
        return False
    
    with open(migration_path, 'r') as f:
        migration_sql = f.read()
    
    # Apply migration
    try:
        with sqlite3.connect(db_path) as conn:
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Run migration
            conn.executescript(migration_sql)
            conn.commit()
            
            print(f"✅ Migration {migration_file} applied successfully")
            return True
            
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    """Main migration runner."""
    print("🔄 Lorien Database Migration Runner")
    print("=" * 40)
    
    # Get database path
    db_path = get_db_path()
    print(f"Database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print("Please ensure the database exists before running migrations.")
        sys.exit(1)
    
    # List of migrations to run (in order)
    migrations = [
        "001_add_red_flag_audit.sql"
    ]
    
    print(f"\nFound {len(migrations)} migration(s) to apply")
    
    # Run migrations
    success_count = 0
    for migration in migrations:
        if run_migration(db_path, migration):
            success_count += 1
    
    print(f"\n{'=' * 40}")
    print(f"Migration Summary: {success_count}/{len(migrations)} successful")
    
    if success_count == len(migrations):
        print("🎉 All migrations completed successfully!")
        sys.exit(0)
    else:
        print("❌ Some migrations failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
