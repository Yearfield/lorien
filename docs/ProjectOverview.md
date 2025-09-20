# Project Overview

## 1) Purpose
A cross-platform decision-tree editor for clinical workflows. The app enforces a strict “exactly five children per parent” rule, exports a calculator-ready view of the tree, and can optionally run a small local medical LLM for guidance (not diagnosis).

## 2) Canonical Data Shape (Non-Negotiable)
Columns and their meanings:
- **D0** (root label)
- **D1**, **D2**, **D3**, **D4**, **D5**, **D6**
- **Notes** (optional metadata ignored during ingest)

Each parent must have **exactly 5** children, occupying slots 1..5. Off-by-one or shifted inserts are invalid.

## 3) Architecture at a Glance
core/ # pure Python domain logic + validators
api/ # FastAPI exposing core to UIs
ui_flutter/ # Flutter (desktop + mobile) consuming api/
ui_streamlit/# legacy UI for continuity (thin wrapper)
llm/ # optional local LLM (llama-cpp-python)
tools/ # scripts, migrations helpers
docs/ # this file, user/developer docs
tests/ # unit + integration tests

markdown
Copy code

### Core Responsibilities
- **rules.py**: tree invariants, validators, “next incomplete parent”
- **engine.py**: apply edits, propagate children to depth 5, compute calculator rows
- **storage/sqlite.py**: repository pattern over SQLite (WAL enabled)
- **importers/exporters**: map Excel/Google Sheets ⇄ DB (fixes prior off-by-one bug)

### API Responsibilities
- List roots and children for navigation
- Replace a parent’s children atomically
- Import/export canonical CSV or XLSX data via EngineLongBow
- Health metadata (version, database pragmas, feature flags)
- (Optional) `/llm/complete` for local guidance when enabled

### Flutter Responsibilities
- **Editor**: browse parents, “Skip to next incomplete parent,” manage 5 slots
- **ParentDetail**: add/replace children in slots 1..5, reorder within limits
- **Calculator**: selection → export CSV
- State via Riverpod/Bloc; server URL configurable

## 4) Data Model (SQLite)
- `nodes(id, parent_id, depth, slot, label, is_leaf, created_at, updated_at)`
- Constraints:
  - `CHECK(depth BETWEEN 0 AND 5)`, `CHECK(slot BETWEEN 0 AND 5)`
  - `UNIQUE(parent_id, slot)` (enforces 1 child per slot)
- WAL mode enabled; DB placed in OS-appropriate app-data directory.

## 5) Workflows

### Import
1. Read Excel/Google Sheet with canonical column names.
2. Build/normalize tree; enforce exact slot placement next to parent.
3. Validate; report/repair violations.

### Edit
- Add/replace child in slot (1..5) under parent.
- Auto-propagate to maintain complete paths to depth 5.
- “Skip to next incomplete parent” to accelerate curation.

### Calculator
- Select rows; export CSV where **Diagnosis** forms a new header row and the selected **Node 1..5** entries become rows with quality/metadata.

### Export
- Push back to Excel/Google Sheets only when explicitly requested.
- Maintain exact adjacency/slot integrity.

## 6) LLM (Optional)
- Place a quantized **GGUF** model file in `llm/models/` (path set in config).
- `llama-cpp-python` for local inference via FastAPI router.
- Safety system prompt; guidance only (no final diagnoses).

## 7) Dev & Ops
- **Run API**: `uvicorn api.server:app --reload`
- **Run Flutter**: `flutter run -d windows|macos|linux|android|ios`
- **Tests**: `pytest -q`
- **Format**: `ruff check --fix && black .` (Python), `dart format .` (Flutter)
- **Linux inotify (dev)**:
sudo sysctl fs.inotify.max_user_instances=1024
sudo sysctl fs.inotify.max_user_watches=1048576

pgsql
Copy code

## 8) Naming & Conventions
- Columns exactly as: D0 → D1..D6 → Notes.
- Slots 1..5 map to Node 1..5 (no gaps; no reindexing).
- Commits follow conventional commits (feat/fix/chore/docs/test).

## 9) Testing Strategy
- Unit tests for validators and insertion semantics (off-by-one regression).
- Import/export golden tests to guarantee stable mapping.
- API integration tests for critical routes (tree edits, next-incomplete, CSV).

## 10) Roadmap
- v1: Local SQLite + Flutter desktop/mobile + API bridge.
- v1.1: Optional LLM endpoint enabled.
- v1.2: Sync service (optional) to Postgres for multi-user collaboration.
- v1.3: Auto-updater for desktop, improved analytics with DuckDB (desktop only).