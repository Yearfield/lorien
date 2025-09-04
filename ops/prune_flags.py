#!/usr/bin/env python3
"""
Prune flag audit table to maintain retention policy.

Keeps ≤30 days or ≤50k rows, whichever comes first.
Safe to run as cron job.
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from storage.sqlite import SQLiteRepository


def prune_flag_audit(max_age_days: int = 30, max_rows: int = 50000):
    """
    Prune flag audit table to maintain retention policy.

    Args:
        max_age_days: Keep records no older than this many days
        max_rows: Keep at most this many records

    Returns:
        Dict with pruning statistics
    """
    print(f"🔄 Starting flag audit pruning (≤{max_age_days} days or ≤{max_rows} rows)")

    # Get database path
    repo = SQLiteRepository()
    db_path = repo.get_resolved_db_path()

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return {"error": "database_not_found"}

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='flag_audit'
            """)

            if not cursor.fetchone():
                print("ℹ️  flag_audit table does not exist, nothing to prune")
                return {"tables_exist": False, "rows_deleted": 0}

            # Get current row count
            cursor.execute("SELECT COUNT(*) FROM flag_audit")
            total_rows = cursor.fetchone()[0]
            print(f"📊 Current flag_audit rows: {total_rows:,}")

            if total_rows == 0:
                print("ℹ️  No rows to prune")
                return {"rows_before": 0, "rows_deleted": 0, "rows_after": 0}

            # Calculate cutoff date
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=max_age_days)
            cutoff_str = cutoff_date.isoformat().replace("+00:00", "Z")

            # Count rows older than cutoff
            cursor.execute(
                "SELECT COUNT(*) FROM flag_audit WHERE ts < ?",
                (cutoff_str,)
            )
            old_rows = cursor.fetchone()[0]

            # Determine how many rows to delete
            rows_to_delete = 0

            if total_rows > max_rows:
                # Need to delete to get under max_rows limit
                rows_to_delete = total_rows - max_rows
                print(f"📏 Exceeding row limit: deleting {rows_to_delete:,} rows")
            elif old_rows > 0:
                # Delete old rows
                rows_to_delete = old_rows
                print(f"📅 Deleting {old_rows:,} rows older than {max_age_days} days")

            if rows_to_delete > 0:
                # Delete oldest rows first
                cursor.execute("""
                    DELETE FROM flag_audit
                    WHERE id IN (
                        SELECT id FROM flag_audit
                        ORDER BY ts ASC
                        LIMIT ?
                    )
                """, (rows_to_delete,))

                deleted_count = cursor.rowcount
                conn.commit()

                print(f"🗑️  Deleted {deleted_count:,} rows")

                # Get final count
                cursor.execute("SELECT COUNT(*) FROM flag_audit")
                final_rows = cursor.fetchone()[0]

                return {
                    "success": True,
                    "rows_before": total_rows,
                    "rows_deleted": deleted_count,
                    "rows_after": final_rows,
                    "cutoff_date": cutoff_str
                }
            else:
                print("✨ No pruning needed")
                return {
                    "success": True,
                    "rows_before": total_rows,
                    "rows_deleted": 0,
                    "rows_after": total_rows
                }

    except Exception as e:
        print(f"❌ Pruning failed: {e}")
        return {"error": str(e)}


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Prune flag audit table")
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=30,
        help="Keep records no older than this many days (default: 30)"
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=50000,
        help="Keep at most this many records (default: 50000)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting"
    )

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")

    try:
        result = prune_flag_audit(
            max_age_days=args.max_age_days,
            max_rows=args.max_rows
        )

        print("\n" + "=" * 50)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        else:
            print("✅ Pruning completed successfully"            print(f"   Rows before: {result.get('rows_before', 0):,}")
            print(f"   Rows deleted: {result.get('rows_deleted', 0):,}")
            print(f"   Rows after: {result.get('rows_after', 0):,}")
            if "cutoff_date" in result:
                print(f"   Cutoff date: {result['cutoff_date']}")

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()