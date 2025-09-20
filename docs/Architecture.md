# Architecture

## Overview
Cross‑platform decision‑tree tooling with a frozen 8‑column contract and exactly‑5 children invariant.

## Components
- `core/`: domain logic, validators, invariants (next‑incomplete, exactly‑5 children)
- `api/`: FastAPI exposing tree navigation, edit, import/export, health, optional LLM
- `ui_flutter/`: Desktop/mobile UI with Riverpod, GoRouter, Dio
- `ui_streamlit/`: Dev adapter for prototyping and imports
- `storage/`: SQLite DAL with WAL + FK enabled

## Data Model (SQLite)
- `nodes(id, parent_id, depth, slot, label, is_leaf, created_at, updated_at)`
- Constraints: `UNIQUE(parent_id, slot)`, `CHECK(depth BETWEEN 0 AND 5)`, `CHECK(slot BETWEEN 0 AND 5)`
- Views: missing slots, next‑incomplete parent, materialized export rows

## API Design
- RESTful JSON; CSV/XLSX via export endpoints
- Canonical versioned mount `/api/v1/*` (clients use this). Bare mounts exist for legacy compatibility.
- Atomic children upsert per parent; 409/422 semantics documented in `docs/API.md`

## CSV Contract
- Frozen 8‑column header (see `docs/API_HEADER_SOT.md`)
- UI must call API for CSV/XLSX; no client‑side construction

## Key Design Decisions
- SQLite + WAL for local durability and simplicity
- Strict slot semantics (1..5) to ensure consistent tree shape
- Optional local LLM: OFF by default; guidance‑only

## Workflows
- Import: Excel/CSV normalization → validate → apply
- Edit: parent detail with slots → next‑incomplete navigation
- Export: stream CSV/XLSX from materialized views

