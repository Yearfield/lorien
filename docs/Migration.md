# Migration to LongBow VM Core

Scope

- Migrate from legacy routes/engines to EngineLongBow with the frozen 8-column contract.

Steps

- Export legacy tree to the canonical 8-column CSV: `D0..D6, Notes`
- Import via VM Core: `POST /api/v1/import?mode=replace&enforce_five=true`
- Verify: health probes, a few representative paths, and export round-trip (CSV/XLSX)

Decommission

- Remove non-LongBow engines/routes from clients and scripts
- Use EngineLongBow-only endpoints for preview/apply/export

Rules & alignment

- Option B: enforce ≤5 children per parent at the service layer; DB remains flexible via unique `(parent_id, slot)` 1..5
- Clients should not construct CSV/XLSX; always call API

## Dictionary Migration

### Database Schema Updates

The following migrations are applied automatically when the database is initialized:

1. **Migration 008**: `008_add_medical_dictionary.sql`
   - Creates `medical_dictionary` table with term management capabilities
   - Adds indexes for performance optimization
   - Creates `v_dictionary_with_tree_info` view for tree relationships

2. **Migration 009**: `009_add_dictionary_sync_triggers.sql`
   - Adds bidirectional synchronization triggers between dictionary and tree nodes
   - Ensures data consistency when terms are modified
   - Handles red flag synchronization with VM Builder

### Dictionary Population

For existing databases, run the population script to extract terms from existing tree nodes:

```bash
python storage/populate_dictionary.py
```

This script:

- Extracts unique labels from the `nodes` table
- Calculates children count and conflicts for each term
- Populates the `medical_dictionary` table with initial data
- Maintains referential integrity with existing tree structure

### Post-Migration Verification

After migration, verify:

- Dictionary pane appears in navigation
- Search functionality works with existing terms
- Red flag synchronization works between Dictionary and VM Builder
- Export/import functionality operates correctly
- Database triggers maintain data consistency
