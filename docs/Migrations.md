# Database Migrations Guide

This document describes Lorien's database schema migration system, including versioning, upgrade procedures, and best practices.

---

## Table of Contents

1. [Overview](#overview)
2. [Migration System Architecture](#migration-system-architecture)
3. [Schema Versioning](#schema-versioning)
4. [Running Migrations](#running-migrations)
5. [Writing New Migrations](#writing-new-migrations)
6. [Idempotency Guidelines](#idempotency-guidelines)
7. [Migration Workflow](#migration-workflow)
8. [Troubleshooting](#troubleshooting)
9. [Migration History](#migration-history)

---

## Overview

Lorien uses a **versioned, idempotent migration system** to manage database schema evolution. Key features:

- ✅ **Automatic application** - Migrations run on every app startup
- ✅ **Idempotent** - Safe to run multiple times without errors
- ✅ **Tracked** - Each migration recorded in `schema_migrations` table
- ✅ **Sequential** - Applied in sorted filename order
- ✅ **Versioned** - Current schema version tracked and reported

### Migration Tracking Table

All applied migrations are tracked in the `schema_migrations` table:

```sql
CREATE TABLE schema_migrations (
    migration_name TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    checksum TEXT
);
```

Each migration is recorded only once. Subsequent startups skip already-applied migrations.

---

## Migration System Architecture

### Directory Structure

```
api/db/
├── migrate.py              # Migration engine
└── migrations/             # All migration SQL files
    ├── README.md
    ├── 000_baseline.sql
    ├── 001_conflicts_perf.sql
    ├── ...
    └── 027_add_large_workbook.sql
```

**Note:** The old `storage/migrations/` directory is deprecated. All migrations have been consolidated to `api/db/migrations/`.

### Migration Engine

The migration system is implemented in `api/db/migrate.py`:

- **`apply_migrations(db_path)`** - Apply all pending migrations (called on startup)
- **`get_schema_version()`** - Get target schema version
- **`get_current_version(db_path)`** - Get applied vs. target version

### Automatic Application

Migrations are automatically applied in `storage/sqlite.py`:

```python
def _init_database(self):
    """Initialize database with migrations."""
    from api.db.migrate import apply_migrations
    apply_migrations(self._db_path)
```

This runs every time the `SQLiteRepository` is initialized (i.e., on API startup).

---

## Schema Versioning

### Version Number

The current schema version is defined in `api/db/migrate.py`:

```python
SCHEMA_VERSION = 27  # Matches 027_add_large_workbook.sql
```

**When adding a new migration:**

1. Create migration file with next sequential number
2. Update `SCHEMA_VERSION` to match

### Version Reporting

Schema version is exposed via the health endpoint:

```bash
curl http://127.0.0.1:8000/api/v1/health | jq '.db'
```

Response includes:

```json
{
  "db": {
    "schema_version": 27,
    "schema_target": 27,
    "schema_status": "current",
    ...
  }
}
```

**Status Values:**

- `current` - All migrations applied
- `pending_upgrade` - New migrations available
- `pending_initial_migration` - Fresh database
- `error` - Migration tracking failed

---

## Running Migrations

### Automatic (Recommended)

Migrations run automatically when you start the API:

```bash
export LORIEN_DB_PATH=/tmp/lorien.db
uvicorn api.app:app --reload
```

You'll see log output:

```
INFO:api.db.migrate:Applying migration: 020_add_red_flag_audit.sql
INFO:api.db.migrate:Applying migration: 021_add_flags_namespace.sql
INFO:api.db.migrate:Applied 2 new migration(s) to /tmp/lorien.db
```

### Manual (Legacy)

You can also run the deprecated manual migration tool:

```bash
python storage/migrate.py
```

**Note:** This is deprecated. Use the automatic system instead.

### Fresh Database

For a fresh database:

1. Delete existing database: `rm $LORIEN_DB_PATH`
2. Start API: `uvicorn api.app:app`
3. All migrations apply automatically

### Checking Migration Status

Query the tracking table:

```bash
sqlite3 $LORIEN_DB_PATH "SELECT * FROM schema_migrations ORDER BY migration_name"
```

Or use the health endpoint:

```bash
curl -s http://127.0.0.1:8000/api/v1/health | jq '.db.schema_version'
```

---

## Writing New Migrations

### Step 1: Create Migration File

Create a new file in `api/db/migrations/` with the next sequential number:

```bash
cd api/db/migrations
touch 028_add_my_feature.sql
```

### Step 2: Write Idempotent SQL

Use constructs that are safe to run multiple times:

```sql
-- Migration: Add my_feature
-- Date: 2025-10-08
-- Purpose: Add feature_table for tracking user preferences
-- Safe to re-apply: Yes (uses IF NOT EXISTS)

-- Create table
CREATE TABLE IF NOT EXISTS feature_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    preference TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_feature_user_id
    ON feature_table(user_id);

CREATE INDEX IF NOT EXISTS idx_feature_created_at
    ON feature_table(created_at);

-- Create triggers
DROP TRIGGER IF EXISTS trg_feature_updated_at;
CREATE TRIGGER trg_feature_updated_at
AFTER UPDATE ON feature_table
FOR EACH ROW
BEGIN
    UPDATE feature_table
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
```

### Step 3: Update Schema Version

Edit `api/db/migrate.py`:

```python
SCHEMA_VERSION = 28  # Matches 028_add_my_feature.sql
```

### Step 4: Test Locally

Test on a dev database:

```bash
export LORIEN_DB_PATH=/tmp/test-lorien.db
rm -f /tmp/test-lorien.db
uvicorn api.app:app --host 127.0.0.1 --port 8000
```

Check logs for successful migration.

### Step 5: Test Idempotency

Restart the app to verify the migration doesn't fail when re-run:

```bash
# Ctrl+C to stop, then restart
uvicorn api.app:app --host 127.0.0.1 --port 8000
```

You should see:

```
DEBUG:api.db.migrate:Skipping already-applied migration: 028_add_my_feature.sql
```

### Step 6: Commit

```bash
git add api/db/migrations/028_add_my_feature.sql api/db/migrate.py
git commit -m "Add migration 028: my_feature table"
```

---

## Idempotency Guidelines

All migrations **must be idempotent** - safe to run multiple times. Follow these patterns:

### ✅ Safe Patterns

#### Tables

```sql
CREATE TABLE IF NOT EXISTS my_table (...);
```

#### Indexes

```sql
CREATE INDEX IF NOT EXISTS idx_my_index ON my_table(column);
```

#### Views

```sql
DROP VIEW IF EXISTS my_view;
CREATE VIEW my_view AS SELECT ...;
```

#### Triggers

```sql
DROP TRIGGER IF EXISTS trg_my_trigger;
CREATE TRIGGER trg_my_trigger ...;
```

#### Columns (Add)

**Option 1: Use ALTER TABLE with IF NOT EXISTS (SQLite 3.35.0+)**

```sql
ALTER TABLE my_table ADD COLUMN IF NOT EXISTS new_column TEXT;
```

**Option 2: Check sqlite_master first**

```sql
-- Check if column exists, then add if missing
-- Note: This requires procedural code, not pure SQL
-- Use Python in migration if needed
```

**Option 3: Recreate table (advanced)**

Use `CREATE TABLE` + `INSERT ... SELECT` + `DROP TABLE` + `RENAME` pattern.

### ❌ Unsafe Patterns

Avoid these - they fail on re-run:

```sql
-- DON'T: Fails if table exists
CREATE TABLE my_table (...);

-- DON'T: Fails if index exists
CREATE INDEX idx_my_index ON my_table(column);

-- DON'T: Fails if column exists (SQLite < 3.35)
ALTER TABLE my_table ADD COLUMN new_column TEXT;

-- DON'T: Destructive
DROP TABLE my_table;  -- Unless you immediately recreate it
```

### Data Migrations

For data transformations, use conditional logic:

```sql
-- Insert seed data only if missing
INSERT OR IGNORE INTO flags (id, label)
VALUES (1, 'Critical');

-- Update existing rows conditionally
UPDATE nodes
SET is_leaf = 1
WHERE depth >= 5 AND is_leaf = 0;
```

---

## Migration Workflow

### Development Workflow

1. **Identify schema change** needed for your feature
2. **Create migration file** with next sequential number
3. **Write idempotent SQL** following guidelines above
4. **Update SCHEMA_VERSION** in `api/db/migrate.py`
5. **Test locally** on fresh and existing databases
6. **Verify health endpoint** reports correct version
7. **Commit** migration file and version update
8. **Notify team** of new migration in PR

### Deployment Workflow

#### On Server

Migrations apply automatically when the API starts:

```bash
# Pull latest code
git pull origin main

# Restart API (migrations run automatically)
sudo systemctl restart lorien-api
```

Check logs:

```bash
sudo journalctl -u lorien-api -f
```

You should see:

```
INFO:api.db.migrate:Applying migration: 028_add_my_feature.sql
INFO:api.db.migrate:Applied 1 new migration(s) to /var/lib/lorien/app.db
```

### Rollback Strategy

Migrations are **forward-only**. Rollback requires manual intervention:

1. **Restore from backup** (recommended - see `docs/Backup_Restore.md`)
2. **Write compensating migration** (for minor changes)
3. **Manual SQL fixes** (last resort, document thoroughly)

**Best Practice:** Always backup before deploying migrations to production.

---

## Troubleshooting

### Migration Fails

**Symptom:** API won't start, logs show migration error

```
ERROR:api.db.migrate:Migration failed: UNIQUE constraint failed: nodes.label
```

**Solution:**

1. Fix the migration SQL to be idempotent
2. If already applied partially, manually clean up:

```bash
sqlite3 $LORIEN_DB_PATH
# Manually revert partial changes
DELETE FROM schema_migrations WHERE migration_name = '028_add_my_feature.sql';
```

3. Fix the migration file
4. Restart API

### Version Mismatch

**Symptom:** Health endpoint shows `schema_status: "unknown"`

This means more migrations are applied than expected (`applied > target`).

**Cause:** Someone applied migrations without updating `SCHEMA_VERSION`.

**Solution:**

1. Check actual applied migrations:

```bash
sqlite3 $LORIEN_DB_PATH "SELECT COUNT(*) FROM schema_migrations"
```

2. Update `SCHEMA_VERSION` in `api/db/migrate.py` to match

### Missing Tracking Table

**Symptom:** Fresh database fails to apply migrations

**Cause:** Migration system couldn't create `schema_migrations` table.

**Solution:**

1. Check database permissions
2. Delete database and recreate: `rm $LORIEN_DB_PATH`
3. Restart API

### Duplicate Migration Names

**Symptom:** Two migrations with same number exist

**Cause:** Merge conflict or concurrent development.

**Solution:**

1. Identify the duplicate
2. Renumber one to the next available slot
3. Update `SCHEMA_VERSION`
4. Commit fix

---

## Migration History

### Phase 1: Core Schema (000-019)

**000-019**: Initial schema and performance optimizations

- `000_baseline.sql` - Initial nodes table, indexes, triggers
- `001_conflicts_perf.sql` - Performance improvements
- `009_drop_label_unique.sql` - Allow duplicate labels
- `011_relax_slot_limit.sql` - Adjust slot constraints
- `012_create_views.sql` - Add convenience views
- `017_widen_depth_to_6.sql` - Extend tree depth limit
- `018_triggers_guard_and_timestamps.sql` - Add data integrity triggers
- `019_relax_slot_limit_again.sql` - Further slot adjustments

### Phase 2: Feature Additions (020-027)

**Consolidated from storage/migrations (Oct 2025)**

- `020_add_red_flag_audit.sql` - Red flag audit trail
- `021_add_flags_namespace.sql` - Generic flags system (node_flags, flag_audit)
- `022_add_dictionary_terms.sql` - Dictionary administration tables
- `023_add_enhanced_audit.sql` - Enhanced audit capabilities
- `024_add_dictionary_governance.sql` - Dictionary governance features
- `025_add_orphan_repair.sql` - Orphan node repair utilities
- `026_add_enhanced_vm_builder.sql` - Enhanced Vital Measurement builder
- `027_add_large_workbook.sql` - Large workbook import system

### Future Migrations (028+)

Add new migrations following the guidelines in this document.

---

## Best Practices Summary

### ✅ Do

- Write idempotent SQL using `IF NOT EXISTS`
- Include header comments (date, purpose, safety)
- Test on both fresh and existing databases
- Update `SCHEMA_VERSION` when adding migrations
- Use sequential numbering (028, 029, 030, ...)
- Commit migration file and version update together
- Back up production database before deploying

### ❌ Don't

- Use non-idempotent SQL (raw `CREATE TABLE`, etc.)
- Skip testing idempotency
- Forget to update `SCHEMA_VERSION`
- Renumber existing migrations
- Write destructive migrations without careful review
- Deploy to production without testing

---

## See Also

- `/api/db/migrate.py` - Migration engine implementation
- `/api/db/migrations/README.md` - Migration directory overview
- `/docs/Architecture.md` - Overall system architecture
- `/docs/Backup_Restore.md` - Database backup procedures
- `/docs/Dev_Quickstart.md` - Development setup guide

---

**Last Updated:** October 8, 2025
**Schema Version:** 27
