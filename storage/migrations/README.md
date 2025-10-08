# Migration Files - DEPRECATED

⚠️ **This directory is deprecated.**

All migrations have been consolidated into `/api/db/migrations/` for consistency.

## Migration Mapping

The migrations from this directory have been renumbered and moved:

- `001_add_red_flag_audit.sql` → `api/db/migrations/020_add_red_flag_audit.sql`
- `002_add_flags_namespace.sql` → `api/db/migrations/021_add_flags_namespace.sql`
- `003_add_dictionary_terms.sql` → `api/db/migrations/022_add_dictionary_terms.sql`
- `003_add_enhanced_audit.sql` → `api/db/migrations/023_add_enhanced_audit.sql`
- `004_add_dictionary_governance.sql` → `api/db/migrations/024_add_dictionary_governance.sql`
- `005_add_orphan_repair.sql` → `api/db/migrations/025_add_orphan_repair.sql`
- `006_add_enhanced_vm_builder.sql` → `api/db/migrations/026_add_enhanced_vm_builder.sql`
- `007_add_large_workbook.sql` → `api/db/migrations/027_add_large_workbook.sql`

## For Developers

Please use `api/db/migrate.py` and `api/db/migrations/` going forward.

See `docs/Migrations.md` for the complete migration guide.
