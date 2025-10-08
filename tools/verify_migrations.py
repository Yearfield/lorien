#!/usr/bin/env python3
"""
Migration verification tool.

Checks that the migration system is properly configured and all migrations
are accounted for.
"""

import os
import sqlite3
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.db.migrate import (
    MIGRATIONS_DIR,
    SCHEMA_VERSION,
    apply_migrations,
    get_current_version,
)


def verify_migration_files():
    """Verify migration files exist and are properly numbered."""
    print("🔍 Verifying migration files...")

    if not MIGRATIONS_DIR.exists():
        print(f"❌ Migrations directory not found: {MIGRATIONS_DIR}")
        return False

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    if not migration_files:
        print("❌ No migration files found")
        return False

    print(f"✅ Found {len(migration_files)} migration files")

    # Check for gaps in numbering
    expected_count = SCHEMA_VERSION + 1  # 000-027 = 28 files for version 27
    if len(migration_files) != expected_count:
        print(
            f"⚠️  Warning: Expected {expected_count} migrations for version {SCHEMA_VERSION}, "
            f"found {len(migration_files)}"
        )

    # List all migrations
    print("\nMigration files:")
    for mf in migration_files:
        print(f"  - {mf.name}")

    return True


def verify_schema_version():
    """Verify SCHEMA_VERSION constant is set correctly."""
    print(f"\n🔍 Schema version: {SCHEMA_VERSION}")

    # Get highest migration number
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if migration_files:
        last_file = migration_files[-1].name
        try:
            last_num = int(last_file.split("_")[0])
            if last_num != SCHEMA_VERSION:
                print(
                    f"❌ SCHEMA_VERSION ({SCHEMA_VERSION}) doesn't match "
                    f"last migration ({last_num})"
                )
                return False
            print(f"✅ SCHEMA_VERSION matches last migration ({last_file})")
        except (ValueError, IndexError):
            print(f"⚠️  Warning: Can't parse migration number from {last_file}")

    return True


def verify_idempotency(db_path: str):
    """Verify migrations are idempotent by applying twice."""
    print(f"\n🔍 Testing idempotency with database: {db_path}")

    # Remove existing test database
    if os.path.exists(db_path):
        os.remove(db_path)
        print("  Removed existing test database")

    try:
        # First application
        print("  Applying migrations (1st time)...")
        count1 = apply_migrations(db_path)
        print(f"  ✅ Applied {count1} migrations")

        # Verify tracking table
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM schema_migrations")
        tracked = cursor.fetchone()[0]
        conn.close()
        print(f"  ✅ Tracked {tracked} migrations")

        # Second application (should be idempotent)
        print("  Applying migrations (2nd time - idempotency check)...")
        count2 = apply_migrations(db_path)

        if count2 == 0:
            print("  ✅ No migrations re-applied (idempotent)")
        else:
            print(f"  ❌ {count2} migrations re-applied (not idempotent!)")
            return False

        # Check version
        applied, target = get_current_version(db_path)
        print(f"  ✅ Current version: {applied} applied, {target} target")

        if applied == target:
            print("  ✅ Database is current")
        else:
            print(f"  ⚠️  Database needs upgrade: {applied}/{target}")

        return True

    except Exception as exc:
        print(f"  ❌ Migration failed: {exc}")
        return False


def verify_health_integration():
    """Verify health endpoint integration (by checking imports)."""
    print("\n🔍 Verifying health endpoint integration...")

    try:
        from api.routers.health import _get_schema_version_info

        print("  ✅ Health endpoint has schema version support")
        return True
    except ImportError as exc:
        print(f"  ❌ Health endpoint missing schema version: {exc}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Lorien Migration System Verification")
    print("=" * 60)

    results = []

    # Check 1: Migration files
    results.append(("Migration files", verify_migration_files()))

    # Check 2: Schema version
    results.append(("Schema version", verify_schema_version()))

    # Check 3: Health integration
    results.append(("Health integration", verify_health_integration()))

    # Check 4: Idempotency (with test database)
    test_db = os.getenv("LORIEN_TEST_DB", "/tmp/lorien_migration_test.db")
    results.append(("Idempotency", verify_idempotency(test_db)))

    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:12} {name}")

    all_passed = all(result[1] for result in results)

    print("=" * 60)
    if all_passed:
        print("✅ All checks passed!")
        print("\nMigration system is ready for use.")
        return 0
    else:
        print("❌ Some checks failed.")
        print("\nPlease review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
