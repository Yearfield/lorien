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

Export procedures
- CSV: `GET /api/v1/tree/export` → verify the header is `D0..D6, Notes`
- XLSX: `GET /api/v1/tree/export.xlsx`
- Sanity checks: count rows; check a few representative paths; ensure Notes column present

Migration notes
- Decommission legacy import/export routes; use EngineLongBow endpoints only
- Confirm service-level ≤5 rule alignment with consuming tools
