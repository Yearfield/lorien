#!/usr/bin/env python3
"""
Populate medical dictionary from existing nodes in the database.
This script extracts unique terms from the nodes table and creates dictionary entries.
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
        # Add parent directory to path to import core modules
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from core.storage.path import get_db_path as get_default_path

        return get_default_path()
    except ImportError:
        # Fallback to default path
        home = os.path.expanduser("~")
        return os.path.join(home, ".local", "share", "lorien", "app.db")


def normalize_term(term):
    """Normalize term for consistent storage and comparison."""
    if not term:
        return ""
    return term.strip()


def get_children_count(conn, term):
    """Get the average number of children for a term across all its occurrences."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT COUNT(*) as child_count
        FROM nodes n1
        JOIN nodes n2 ON n2.parent_id = n1.id
        WHERE LOWER(TRIM(n1.label)) = LOWER(TRIM(?))
    """,
        (term,),
    )

    result = cursor.fetchone()
    return result[0] if result else 0


def get_conflicts_count(conn, term):
    """Get the number of conflicts for a term using the existing conflict system."""
    cursor = conn.cursor()

    # Count occurrences of this term across different depths
    cursor.execute(
        """
        SELECT COUNT(*) as occurrences
        FROM nodes
        WHERE LOWER(TRIM(label)) = LOWER(TRIM(?))
    """,
        (term,),
    )

    result = cursor.fetchone()
    occurrences = result[0] if result else 0

    # If more than 1 occurrence, it's a potential conflict
    return max(0, occurrences - 1)


def is_red_flag_term(conn, term):
    """Check if a term is associated with any red flags."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM nodes n
        JOIN node_red_flags nrf ON nrf.node_id = n.id
        WHERE LOWER(TRIM(n.label)) = LOWER(TRIM(?))
    """,
        (term,),
    )

    result = cursor.fetchone()
    return (result[0] > 0) if result else False


def populate_dictionary(db_path):
    """Populate the medical dictionary from existing nodes."""
    print(f"🔄 Populating medical dictionary from database: {db_path}")

    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")

            # Check if dictionary table exists
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='medical_dictionary'
            """
            )

            if not cursor.fetchone():
                print("❌ medical_dictionary table not found. Please run migration first.")
                return False

            # Get all unique terms from nodes
            cursor.execute(
                """
                SELECT DISTINCT LOWER(TRIM(label)) as normalized_term, label as original_term
                FROM nodes
                WHERE label IS NOT NULL AND TRIM(label) != ''
                ORDER BY normalized_term
            """
            )

            terms = cursor.fetchall()
            print(f"Found {len(terms)} unique terms to process")

            # Process each term
            inserted_count = 0
            skipped_count = 0

            for normalized_term, original_term in terms:
                if not normalized_term:
                    continue

                # Check if term already exists in dictionary
                cursor.execute(
                    "SELECT id FROM medical_dictionary WHERE LOWER(term) = ?", (normalized_term,)
                )
                if cursor.fetchone():
                    skipped_count += 1
                    continue

                # Calculate metrics for this term
                avg_children = get_children_count(conn, original_term)
                conflicts = get_conflicts_count(conn, original_term)
                is_red_flag = is_red_flag_term(conn, original_term)

                # Insert into dictionary
                cursor.execute(
                    """
                    INSERT INTO medical_dictionary
                    (term, definition, synonyms, is_red_flag, avg_children_count, conflicts_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        original_term,  # Store original casing
                        None,  # Definition will be filled later via UI/import
                        json.dumps([]),  # Empty synonyms array
                        int(is_red_flag),
                        avg_children,
                        conflicts,
                    ),
                )

                inserted_count += 1

                if inserted_count % 100 == 0:
                    print(f"Processed {inserted_count} terms...")

            conn.commit()

            print("✅ Dictionary population complete:")
            print(f"   - Inserted: {inserted_count} new terms")
            print(f"   - Skipped: {skipped_count} existing terms")
            print(f"   - Total processed: {len(terms)}")

            return True

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main function."""
    print("📚 Medical Dictionary Population Script")
    print("=" * 40)

    db_path = get_db_path()
    print(f"Database: {db_path}")

    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)

    if populate_dictionary(db_path):
        print("🎉 Dictionary population completed successfully!")
        sys.exit(0)
    else:
        print("❌ Dictionary population failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
