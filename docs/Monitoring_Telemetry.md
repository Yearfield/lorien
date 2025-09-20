# Monitoring & Telemetry

## Health Endpoints
- `GET /api/v1/health` — version, SQLite pragmas, feature flags, optional metrics
- `GET /api/v1/llm/health` — 200 usable / 503 unavailable; include `checked_at` (UTC)

### Health JSON (fields)
- `version`: semantic version string
- `db`: `{ path, wal: true|false, foreign_keys: true|false }`
- `features`: `{ llm: bool, analytics: bool }`
- `metrics` (optional): counts, cache stats when `ANALYTICS_ENABLED=true`

## Runtime Metrics (when enabled)
- Table counts: nodes, triage, flags, audit
- Cache: size, hit/miss, TTL
- Export counters (last hour/day)

## SLOs / Budgets (targets)
- Health: p95 < 50ms
- Next Incomplete: p95 < 100ms
- Children upsert: p95 < 200ms
- CSV export: p95 < 2s (streaming)

## Operations
- Clear cache: `POST /api/v1/admin/performance/clear-cache`
- Index maintenance: `POST /api/v1/admin/performance/create-indexes`
- Backup/restore: see `docs/Backup_Restore.md`

## Logging
- Structured logs with request id and latency; redact sensitive headers
- Avoid logging PHI; avoid full prompts; clamp lengths

