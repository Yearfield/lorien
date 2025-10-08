# Development Guide

This document provides setup and development guidelines for the Lorien project.

## Prerequisites

- Python 3.10+
- Flutter SDK (for UI development)
- SQLite3
- Git

Platform notes: see `docs/platforms/WSL.md` for WSL specifics.

## Setup

### Backend Setup

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd Lorien
   ```

2. Create and activate virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -e .[dev,test]
   ```

4. Initialize database:

   ```bash
   python -c "from api.db import ensure_schema; ensure_schema()"
   ```

5. Run the development server:

   ```bash
   python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to UI directory:

   ```bash
   cd ui_flutter
   ```

2. Install Flutter dependencies:

   ```bash
   flutter pub get
   ```

3. Run the Flutter app:

   ```bash
   flutter run -d linux --dart-define=API_BASE_URL=http://127.0.0.1:8000
   ```

## Development Guidelines

### Code Style & Formatting

All Python code is enforced with **strict formatting and linting**:

#### Automated Formatting

- **Ruff**: Fast Python linter and formatter (configured in `pyproject.toml`)
  - Line length: 100 characters
  - Enforces: PEP 8, import sorting, modern Python patterns, bug detection
  - Auto-fixes most issues

#### Pre-commit Hooks

Install hooks to automatically check code before committing:

```bash
pip install pre-commit
pre-commit install
```

Hooks run automatically on `git commit`:

- Ruff linting and formatting
- Mypy type checking (strict mode)
- Trailing whitespace removal
- End-of-file fixing
- YAML/JSON/TOML validation
- Security checks (detect-secrets)
- Markdown linting

#### Manual Formatting

Format code before committing:

```bash
# Auto-fix linting issues
ruff check . --fix

# Auto-format code
ruff format .

# Or run all pre-commit hooks manually
pre-commit run --all-files
```

#### Style Guidelines

- Follow PEP 8 for Python code
- Use type hints everywhere (prefer modern `dict` over `Dict`, `list` over `List`, `X | None` over `Optional[X]`)
- Write comprehensive docstrings
- Line length: 100 characters (enforced by Ruff)
- Import sorting: automatic (handled by Ruff)
- Follow Flutter/Dart style guidelines for Flutter code

#### CI Enforcement

All formatting and linting is **strictly enforced in CI**:

- `ruff check . --no-fix` - Fails on any linting violation
- `ruff format --check .` - Fails on any formatting issue
- `mypy --strict` - Fails on any type errors or warnings
- See `docs/CI.md` for full CI pipeline details

### Async Patterns

All API endpoints must be async and follow these patterns:

1. **Endpoint declarations**: Use `async def` for all route handlers
2. **Database operations**: Wrap all blocking SQLite calls with `anyio.to_thread()`
3. **Repository methods**: All TreeRepository methods are async
4. **EngineLongBow calls**: Wrap synchronous engine functions when calling from async context
5. **Transaction management**: Use async connection dependency with automatic BEGIN/COMMIT/ROLLBACK

Example:

```python
@router.get("/example")
async def example_endpoint(conn: sqlite3.Connection = Depends(get_db_connection)):
    # Wrap database execute calls
    cur = await anyio.to_thread(conn.execute, "SELECT * FROM nodes WHERE id=?", (1,))
    row = await anyio.to_thread(cur.fetchone)

    # Use async repository methods
    repo = TreeRepository(conn)
    children = await repo.list_children(parent_id=1)

    return {"data": children}
```

### Testing

Run tests with strict mode (warnings as errors):

```bash
# Backend tests with coverage
pytest --strict-warnings --strict-markers --cov=api --cov=core --cov=storage

# Contract tests
pytest tests/contracts/ --strict-warnings

# Flutter tests
flutter test

# Full CI test suite locally
pytest --strict-warnings --strict-markers --strict-config \
  --cov=api --cov=core --cov=storage \
  --cov-report=xml --cov-report=term-missing
```

### Documentation

- Keep documentation up to date
- Use the single source of truth for API headers
- Run documentation audit: `python tools/audit/docs_audit.py`

### Environment & Monitoring

- Configuration quickstart: see `docs/Dev_Quickstart.md` (Configuration section) for commonly used environment variables.
- Full environment reference previously in `ENV.md` has been consolidated into the quickstart and this guide.
- Health, metrics and SLOs: see `docs/Monitoring_Telemetry.md`.

### Database

- Use migrations for schema changes
- Test with both empty and populated databases
- Ensure foreign key constraints are enabled

## Project Structure

```
Lorien/
├── api/                    # FastAPI backend
│   ├── core/              # Core business logic
│   ├── routers/           # API route handlers
│   └── dependencies.py    # Dependency injection
├── ui_flutter/            # Flutter frontend
├── tests/                 # Test suite
├── docs/                  # Documentation
├── tools/                 # Development tools
└── pyproject.toml         # Python project configuration
```

## Common Tasks

### Adding New API Endpoints

1. Create router in `api/routers/`
2. Add to main app in `api/app.py`
3. Update API registry in `docs/API_ROUTES_REGISTRY.md`
4. Add tests in `tests/`
5. Run contract tests

### Updating Documentation

1. Update relevant documentation files
2. Run documentation audit
3. Ensure all tests pass
4. Update archive if needed

### Database Changes

1. Create migration script
2. Test with existing data
3. Update schema documentation
4. Run comprehensive tests

## Troubleshooting

### Common Issues

1. **Database connection errors**: Check SQLite file permissions
2. **Flutter build errors**: Run `flutter clean && flutter pub get`
3. **Import errors**: Check virtual environment activation
4. **Test failures**: Run `pytest -v` for detailed output

### Getting Help

- Check existing documentation
- Run diagnostic tools in `tools/audit/`
- Review test output for clues
- Check logs for error details
