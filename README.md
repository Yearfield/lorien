# Lorien — VM‑First Builder on LongBow

VM‑first decision‑tree builder; EngineLongBow powers import/export; VM Builder is a core pane in a multi‑pane Flutter shell.

- UI: Flutter desktop shell with NavigationRail panes (Home dashboard, VM Builder, Outcomes, Flags, Settings)
- Engine: EngineLongBow is the sole engine for import/preview/apply/export
- API: Fully async FastAPI `/api/v1` with thread-offloaded SQLite operations for high concurrency, health, import, export, conflicts resolution, and tree editing

Key contracts

- Frozen 8‑column header: D0, D1, D2, D3, D4, D5, D6, Notes
- Option B rule: service‑level ≤5 children per parent (DB flexible; unique `(parent_id, slot)` on slots 1..5)
- Transactional import: `POST /api/v1/import?mode=append|replace&enforce_five=true` rolls back on violations (422 with offending parents)
- Conflicts resolution: label-only grouping across all depths with cross-depth resolution capabilities
- Enhanced export: CSV/XLSX with filters (max_depth, only_red, include_meta, root_ids)
- Health: `/api/v1/live`, `/api/v1/ready`, enhanced `/api/v1/health` (version, DB path + `exists`, journal mode, table count, node count, analytics/LLM feature flags)

Quick start

```bash
# Backend (VM Core)
export LORIEN_DB_PATH=/tmp/lorien.db
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.app:app --reload --host 127.0.0.1 --port 8000

# Health probes
curl -sS http://127.0.0.1:8000/api/v1/live | jq .
curl -sS http://127.0.0.1:8000/api/v1/ready | jq .
curl -sS http://127.0.0.1:8000/api/v1/health | jq .

# Conflicts resolution
curl -sS http://127.0.0.1:8000/api/v1/conflicts/scan | jq
curl -sS -X POST -H "Content-Type: application/json" \
  -d '{"label":"hypertension","selected_children":["headache","nausea","vomiting","chest pain","myalgia"],"dry_run":true}' \
  http://127.0.0.1:8000/api/v1/conflicts/resolve | jq

# Flutter (Linux example)
cd ui_flutter
flutter pub get
flutter run -d linux --dart-define=API_BASE=http://127.0.0.1:8000/api/v1
```

## Code Quality

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Lorien enforces **strict code quality standards**:

- **Formatting**: Ruff (100-char line length, auto-fixes most issues)
- **Type Safety**: Mypy strict mode (no implicit Any, full annotations)
- **Security**: pip-audit (fails on any known CVEs)
- **Testing**: Pytest strict mode (warnings as errors)
- **Pre-commit Hooks**: Automatic checks on every commit

See `docs/CI.md` for CI pipeline details and `docs/CONTRIBUTING.md` for contribution guidelines.

## Recent Updates

### Async Architecture & Thread Offloading (2025-01-08)

- **Fully Async API**: All endpoints converted to `async def` with non-blocking I/O
- **Thread Offloading**: All blocking SQLite operations wrapped with `anyio.to_thread()`
- **Async Repository**: TreeRepository methods fully async for high concurrency
- **Transaction Safety**: Async connection management with proper BEGIN/COMMIT/ROLLBACK handling
- **Performance**: Zero blocking I/O in event loop ensures fast response times under load

### Label-Only Conflicts & Enhanced Export (2025-01-03)

- **Conflicts Resolution**: Label-only grouping across all depths with cross-depth resolution
- **Home Dashboard**: Comprehensive dashboard with conflicts, export, and submission sections
- **Enhanced Export**: Advanced filtering (max_depth, only_red, include_meta, root_ids) with native file picker
- **API Improvements**: New conflicts endpoints, enhanced export filters, comprehensive health checks
- **UI Enhancements**: Riverpod state management, improved error handling, busy states

## Documentation Links

- Dev Quickstart: ./Dev_Quickstart.md
- Architecture: ./docs/Architecture.md
- API: ./docs/API.md
- UI Guide: ./docs/UI_Guide.md
- Conflicts Resolution: ./docs/Conflicts_Resolution.md
- Runbook: ./docs/Runbook.md
- Migration: ./docs/Migration.md

Structure

- `api/` — FastAPI app, VM Core routers, settings
- `Engines/EngineLongBow/` — ingest/store/present for the 8‑column contract
- `ui_flutter/` — multi‑pane Flutter shell with VM Builder as the authoring spine
