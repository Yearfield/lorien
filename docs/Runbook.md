# Runbook

Start/stop API

- Start (dev): `uvicorn api.app:app --reload --host 127.0.0.1 --port 8000`
- Env: set `LORIEN_DB_PATH` to select the SQLite file

Health probes

- Liveness: `GET /api/v1/live` → `{status: "live"}`
- Readiness: `GET /api/v1/ready` → `{status: "ready"|"not_ready"}` (checks `nodes` table)
- Health: `GET /api/v1/health` → version, DB path, journal mode, table count, node count

Backup/restore SQLite

- Stop writers for consistent copy
- Copy DB + WAL artifacts if present: `*.db`, `*.db-wal`, `*.db-shm`
- WAL check: `PRAGMA journal_mode` should be `wal`; see `/api/v1/health.db.journal_mode`
- See ./Backup_Restore.md for end-to-end guidance

Import troubleshooting

- 422 during preview: `errors[]` includes row numbers for parents exceeding 5 children in-file
- 422 during apply with `enforce_five=true`: API rolls back and returns offending parents
- 409 on save: slot conflict (concurrent edit); user may retry after reloading children
- Recovery: rerun preview, correct the file (dedupe, group to ≤5 per parent), apply again

Rename/Merge troubleshooting

- 404 during merge: One or both parents no longer exist (already deleted or renamed)
  - Check parent IDs exist: `GET /api/v1/tree/node?node_id=123`
  - Refresh UI state to avoid stale references
  - Use search to find current parent locations: `GET /api/v1/tree/search-by-label?label=name`
- 422 during merge: More than 5 children selected
  - UI enforces exactly 5 children maximum
  - API validates selection count before processing
- 500 during merge: Database transaction error
  - Check API logs for specific SQLite errors
  - Verify database integrity: `GET /api/v1/health` → `db.integrity`
  - Restart API if persistent transaction issues
- Recovery: Use search endpoint to locate parents, verify children counts, retry operation

Export procedures

- CSV: `GET /api/v1/tree/export` → verify the header is `D0..D6, Notes`
- XLSX: `GET /api/v1/tree/export.xlsx`
- Sanity checks: count rows; check a few representative paths; ensure Notes column present

Migration notes

- Decommission legacy import/export routes; use EngineLongBow endpoints only
- Confirm service-level ≤5 rule alignment with consuming tools
