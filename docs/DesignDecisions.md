# Design Decisions

## Slot Atomicity & Exactness
- Exactly 5 children per parent, slots 1..5.
- Enforced at DB level via `UNIQUE(parent_id,slot)` and triggers, and in API/UI validation.
- Multi-slot upserts run inside a single transaction (no partial writes).

## Header Guard
- Importers and CSV export insist on canonical headers in exact order.
- Imports with non-canonical headers fail fast with a helpful message.

## "Next Incomplete Parent" View
- Backed by indexed view over `nodes`; returns missing slots quickly.
- Stable ordering by `depth ASC, parent_id ASC`.

## WAL & Backup/Restore
- WAL mode is required for performance and concurrency.
- Backup uses `sqlite3 .backup` for a consistent snapshot.
- Restore removes `-wal`/`-shm` then uses `.restore` into a temp DB, atomically moved into place.

## DB Placement
- Env-first: `DB_PATH` respected.
- Defaults to OS app-data dir (`~/.local/share/lorien/app.db`, etc.).

## LLM Integration (Optional)
- Feature-flagged; off by default.
- Strict JSON-only prompting for *Diagnostic Triage* and *Actions* suggestions.
- Safety gate refuses dosing/prescriptions or diagnoses; guidance-only framing.
- Efficiency: low `max_tokens`, character clamps, concurrency limit, cache, rate-limit.

## UI Separation
- Streamlit adapter never touches DB directly; talks to FastAPI only.
- Flutter is primary UI for cross-platform distribution.

## Version Surfacing
- Single source of truth in `core/version.py`, exposed via `/health` and Flutter Settings/About.
