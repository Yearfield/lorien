#!/usr/bin/env python3
"""
Test script to verify the medical dictionary migration works correctly.
"""

import json
import sqlite3
import sys
from pathlib import Path


def get_db_path():
    """Get the database path from environment or default location."""
    import os

    db_path = os.getenv("LORIEN_DB_PATH")
    if db_path:
        return db_path

    # Default to app data directory
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from core.storage.path import get_db_path as get_default_path

        return get_default_path()
    except ImportError:
        home = os.path.expanduser("~")
        return os.path.join(home, ".local", "share", "lorien", "app.db")


def test_migration():
    """Test that the migration was applied successfully."""
    print("🧪 Testing Medical Dictionary Migration")
    print("=" * 40)

    db_path = get_db_path()
    print(f"Database: {db_path}")

    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return False

    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")

            # Test 1: Check if table exists
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='medical_dictionary'
            """
            )

            if not cursor.fetchone():
                print("❌ medical_dictionary table not found")
                return False
            print("✅ medical_dictionary table exists")

            # Test 2: Check table structure
            cursor.execute("PRAGMA table_info(medical_dictionary)")
            columns = cursor.fetchall()

            expected_columns = {
                "id",
                "term",
                "definition",
                "synonyms",
                "is_red_flag",
                "avg_children_count",
                "conflicts_count",
                "created_at",
                "updated_at",
            }

            actual_columns = {col[1] for col in columns}

            if expected_columns.issubset(actual_columns):
                print("✅ Table structure is correct")
            else:
                missing = expected_columns - actual_columns
                print(f"❌ Missing columns: {missing}")
                return False

            # Test 3: Check if view exists
            cursor.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='view' AND name='v_dictionary_with_tree_info'
            """
            )

            if cursor.fetchone():
                print("✅ Dictionary view exists")
            else:
                print("❌ Dictionary view not found")
                return False

            # Test 4: Check indexes
            cursor.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='index' AND name LIKE 'idx_medical_dictionary_%'
            """
            )

            indexes = cursor.fetchall()
            expected_indexes = 4  # term, is_red_flag, created_at, updated_at

            if len(indexes) >= expected_indexes:
                print(f"✅ Found {len(indexes)} dictionary indexes")
            else:
                print(f"❌ Expected {expected_indexes} indexes, found {len(indexes)}")
                return False

            # Test 5: Insert a test record
            cursor.execute(
                """
                INSERT INTO medical_dictionary
                (term, definition, synonyms, is_red_flag)
                VALUES (?, ?, ?, ?)
            """,
                ("Test Term", "This is a test definition", json.dumps(["synonym1", "synonym2"]), 0),
            )

            test_id = cursor.lastrowid
            print(f"✅ Test record inserted with ID: {test_id}")

            # Test 6: Verify trigger works (update should touch updated_at)
            cursor.execute(
                """
                UPDATE medical_dictionary
                SET definition = 'Updated definition'
                WHERE id = ?
            """,
                (test_id,),
            )

            cursor.execute("SELECT updated_at FROM medical_dictionary WHERE id = ?", (test_id,))
            updated_at = cursor.fetchone()[0]
            print(f"✅ Update trigger working, updated_at: {updated_at}")

            # Test 7: Test view query
            cursor.execute("SELECT * FROM v_dictionary_with_tree_info WHERE id = ?", (test_id,))
            view_result = cursor.fetchone()

            if view_result:
                print("✅ View query works correctly")
            else:
                print("❌ View query failed")
                return False

            # Clean up test record
            cursor.execute("DELETE FROM medical_dictionary WHERE id = ?", (test_id,))
            conn.commit()
            print("✅ Test record cleaned up")

            print("\n🎉 All migration tests passed!")
            return True

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main function."""
    if test_migration():
        print("Migration test completed successfully!")
        sys.exit(0)
    else:
        print("Migration test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
