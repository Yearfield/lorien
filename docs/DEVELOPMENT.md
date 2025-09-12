# Development Guide

This document provides setup and development guidelines for the Lorien project.

## Prerequisites

- Python 3.10+
- Flutter SDK (for UI development)
- SQLite3
- Git

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

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write comprehensive docstrings
- Follow Flutter/Dart style guidelines

### Testing

- Run backend tests: `pytest`
- Run contract tests: `pytest tests/contracts/`
- Run Flutter tests: `flutter test`

### Documentation

- Keep documentation up to date
- Use the single source of truth for API headers
- Run documentation audit: `python tools/audit/docs_audit.py`

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
