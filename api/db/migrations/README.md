# Lorien Schema Migrations

This directory contains all database schema migrations for Lorien, applied automatically on startup.

## Migration System

- Migrations are applied in filename sort order (e.g., `000_baseline.sql`, `001_conflicts_perf.sql`, etc.)
- Each migration is tracked in the `schema_migrations` table
- Migrations are **idempotent** - safe to run multiple times
- Use `CREATE TABLE IF NOT EXISTS` and similar constructs in your migrations

## Current Schema Version

**Version 27** (as of 027_add_large_workbook.sql)

## Migration Naming Convention

```
NNN_description.sql
```

Where:

- `NNN` is a zero-padded sequential number (000, 001, 002, ...)
- `description` is a brief snake_case description of the change

## Writing New Migrations

1. Create a new `.sql` file with the next sequential number
2. Use idempotent SQL (IF NOT EXISTS, IF NOT PRESENT, etc.)
3. Include a comment header with date, purpose, and safety notes
4. Update `SCHEMA_VERSION` in `/api/db/migrate.py`
5. Test on a dev database before committing

### Example Migration Template

```sql
-- Migration: Add feature_name
-- Date: YYYY-MM-DD
-- Purpose: Brief description of what this migration does
-- Safe to re-apply: Yes (uses IF NOT EXISTS)

CREATE TABLE IF NOT EXISTS new_table (
    id INTEGER PRIMARY KEY,
    data TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_new_table_data
    ON new_table(data);
```

## Migration History

### Core Schema (000-019)

- `000_baseline.sql` - Initial schema with nodes, triggers
- `001-019` - Performance, constraints, and schema evolution

### Feature Additions (020-027)

- `020_add_red_flag_audit.sql` - Red flag audit trail
- `021_add_flags_namespace.sql` - Generic flags system
- `022_add_dictionary_terms.sql` - Dictionary and versioning
- `023_add_enhanced_audit.sql` - Enhanced audit capabilities
- `024_add_dictionary_governance.sql` - Dictionary governance
- `025_add_orphan_repair.sql` - Orphan node repair utilities
- `026_add_enhanced_vm_builder.sql` - Enhanced VM builder
- `027_add_large_workbook.sql` - Large workbook import system

## See Also

- `/docs/Migrations.md` - Complete migration guide and best practices
- `/api/db/migrate.py` - Migration engine implementation
- `/storage/schema.sql` - Deprecated, reference only
