# Contributing to Lorien

## Database Testing

Tests run against a temporary SQLite database initialized via `/api/db/migrations/*.sql`. 

**Important**: Do not create schema ad-hoc in tests. Always use the migration system to ensure test and production databases have identical schemas.

### Test Database Setup

The test database is automatically created using the same migrations as production:

1. A temporary database is created for each test session
2. All migrations in `api/db/migrations/` are applied in order
3. The database path is set via `LORIEN_DB_PATH` environment variable
4. Tests use the unified schema via `api.db.get_conn()`

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -k "schema_alignment" -q
pytest -k "import_conflicts_via_upload" -q
pytest -k "conflicts_via_repo_seed" -q

# Run with verbose output
pytest -v
```

### Database Schema

The production database allows duplicate labels on nodes (required for conflict detection). Tests must not assume unique constraints on `nodes.label`.

Key constraints:
- `UNIQUE(parent_id, slot)` - prevents duplicate slots under same parent
- `UNIQUE(label) WHERE parent_id IS NULL` - prevents duplicate root labels only
- No `UNIQUE(label)` constraint - allows duplicate labels for conflicts
