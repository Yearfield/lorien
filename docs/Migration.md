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

## EngineShortBow Migration

### Database Schema Updates

The following migration is applied automatically when the database is initialized:

**Migration 012**: `012_add_shortbow_tables.sql`

- Creates `shortbow_symptoms` table for symptom name storage
- Creates `shortbow_symptom_links` table for probability matrix data
- Creates `shortbow_calculations` table for navigation session history
- Adds indexes for performance optimization
- Creates triggers for timestamp management

### ShortBow Data Population

For new installations, import sample data to get started:

```bash
# Generate sample symptom matrix
python3 Engines/EngineShortBow/sample_generator.py

# Import via API (or use Flutter UI)
curl -X POST "http://localhost:8000/api/v1/shortbow/import" \
  -F "file=@sample_symptom_matrix.xlsx"
```

### Post-Migration Verification

After migration, verify:

- ShortBow Navigator accessible via VM Builder navigation button
- Import functionality works with Excel symptom matrices
- Navigation shows top symptoms and linked symptoms
- Calculation history saves and loads correctly
- Statistics endpoint returns accurate data
