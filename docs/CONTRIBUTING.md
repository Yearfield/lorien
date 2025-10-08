# Contributing to Lorien

## Code Quality Requirements

### Pre-commit Setup

**Required**: Install pre-commit hooks before making changes:

```bash
pip install pre-commit
pre-commit install
```

This ensures code quality checks run automatically on every commit:

- ✅ Ruff linting and formatting
- ✅ Mypy type checking (strict mode)
- ✅ Security checks (detect-secrets)
- ✅ File formatting (trailing whitespace, end-of-file)
- ✅ Markdown linting

### Code Formatting

All Python code must pass strict formatting and linting:

```bash
# Auto-fix most issues
ruff check . --fix
ruff format .

# Check before committing (what CI runs)
ruff check . --no-fix       # Fails on any linting violation
ruff format --check .       # Fails on any formatting issue
mypy api/ core/ storage/ --strict  # Fails on any type errors
```

### Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Pre-commit hooks are installed and passing
- [ ] All code is formatted (`ruff format .`)
- [ ] No linting violations (`ruff check .`)
- [ ] Type checking passes (`mypy api/ core/ storage/ --strict`)
- [ ] All tests pass (`pytest --strict-warnings`)
- [ ] No security vulnerabilities (`pip-audit --strict`)
- [ ] Documentation is updated if needed
- [ ] Commit messages are clear and descriptive

### CI Pipeline

All PRs must pass the full CI pipeline:

- **Lint**: Ruff linting and formatting
- **Type Check**: Mypy strict mode
- **Security**: pip-audit vulnerability scanning
- **Docs**: MkDocs build with strict mode
- **Tests**: Pytest on Python 3.10, 3.11, 3.12
- **Wiring Audit**: API contract verification

See `docs/CI.md` for detailed CI documentation.

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
