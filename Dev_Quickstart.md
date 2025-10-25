# Developer Quickstart

Prerequisites

- Python 3.10+
- Flutter 3.22+ with desktop target (e.g., Linux)
- jq (for curl samples)

Environment

- `LORIEN_DB_PATH`: SQLite DB file path for API (e.g., `/tmp/lorien.db`)
- Flutter uses `--dart-define=API_BASE` for the API base URL (e.g., `http://127.0.0.1:8000/api/v1`)

Start the API (VM Core)

```bash
export LORIEN_DB_PATH=/tmp/lorien.db
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Install dev dependencies (includes formatters and linters)
pip install -e .[dev]

# Set up pre-commit hooks (recommended)
pre-commit install

# Database migrations run automatically on startup
uvicorn api.app:app --reload --host 127.0.0.1 --port 8000
```

**Note:** Database migrations are applied automatically when the API starts. See the [Database Migrations](#database-migrations) section below for details.

Start the Flutter app

```bash
cd ui_flutter
flutter pub get
flutter run -d linux --dart-define=API_BASE=http://127.0.0.1:8000/api/v1
```

Code Quality Checks
Before committing, run formatting and linting:

```bash
# Auto-format code (fixes most issues)
ruff check . --fix
ruff format .

# Or use pre-commit to run all checks
pre-commit run --all-files

# Manual CI checks (what runs in GitHub Actions)
ruff check . --no-fix              # Linting (fail on violations)
ruff format --check .              # Formatting check
mypy api/ core/ storage/ --strict  # Type checking
pytest --strict-warnings           # Tests (warnings as errors)
pip-audit --strict                 # Security vulnerabilities
```

Database Migrations
Lorien uses a versioned, idempotent migration system. Migrations are applied automatically on startup.

**Check migration status:**

```bash
# Via health endpoint
curl -s http://127.0.0.1:8000/api/v1/health | jq '.db.schema_version, .db.schema_target, .db.schema_status'

# Direct database query
sqlite3 $LORIEN_DB_PATH "SELECT COUNT(*) FROM schema_migrations"
```

**Fresh database:**

```bash
# Delete and recreate (migrations apply automatically)
rm $LORIEN_DB_PATH
uvicorn api.app:app --reload
```

**Writing new migrations:**

1. Create `api/db/migrations/NNN_description.sql` (next sequential number)
2. Use idempotent SQL: `CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`, etc.
3. Update `SCHEMA_VERSION` in `api/db/migrate.py`
4. Test on fresh and existing databases
5. See `docs/Migrations.md` for complete guide

**Example migration:**

```sql
-- Migration: Add feature_table
-- Date: 2025-10-08
-- Purpose: Track user preferences

CREATE TABLE IF NOT EXISTS feature_table (
    id INTEGER PRIMARY KEY,
    data TEXT
);

CREATE INDEX IF NOT EXISTS idx_feature_data
    ON feature_table(data);
```

Smoke checklist

- Health probes: `GET /api/v1/live`, `/api/v1/ready`, `/api/v1/health` show expected JSON
- Schema version: `/api/v1/health` shows `"schema_status": "current"`
- Import preview: `POST /api/v1/import/preview` with a LongBow CSV/XLSX returns `errors[]` for over‑five within file
- Import apply: `POST /api/v1/import?mode=replace&enforce_five=true` rolls back and returns 422 when >5 children per parent
- VM Builder pane loads; can add a root, edit children, drill into nodes
- "Next Incomplete" CTA navigates using `GET /api/v1/tree/next-underfilled` and shows snackbars for 204/errors
- Busy overlay and error banner: long operations disable actions; save/import failures show error text
- EngineShortBow: Navigation button in VM Builder opens ShortBow Navigator; can import Excel matrix and navigate symptoms

More details

- Architecture: ./docs/Architecture.md
- API reference: ./docs/API.md
- Migrations: ./docs/Migrations.md
- CI/CD: ./docs/CI.md
- Contributing: ./docs/CONTRIBUTING.md
