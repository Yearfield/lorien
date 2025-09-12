# Canonical API Endpoints (v6.x → v7.0 freeze)

This document defines the canonical API surface for Lorien v7.0. All endpoints listed here are considered stable and will be maintained through the v7.x series.

## Core Tree Operations

| Domain | Method | Path | Notes |
|---|---|---|---|
| Edit Tree | GET | `/api/v1/tree/parents/incomplete` | paged list of incomplete parents |
| Edit Tree | PUT | `/api/v1/tree/parents/{parent_id}/children` | atomic upsert slots 1..5 |
| Navigate | GET | `/api/v1/tree/next-incomplete-parent` | 204 when none available |
| Navigate | GET | `/api/v1/tree/navigate` | tree navigation with options |
| Navigate | GET | `/api/v1/tree/root-options` | root node options |
| Tree Stats | GET | `/api/v1/tree/stats` | tree statistics and metrics |
| Tree Stats | GET | `/api/v1/tree/progress` | completion progress |
| Tree Stats | GET | `/api/v1/tree/roots` | list of root nodes |
| Tree Stats | GET | `/api/v1/tree/leaves` | list of leaf nodes |
| Tree Admin | DELETE | `/api/v1/tree/{node_id}` | delete specific node |

## Outcomes & Triage

| Domain | Method | Path | Notes |
|---|---|---|---|
| Outcomes | GET | `/api/v1/triage/{node_id}` | leaf-only read |
| Outcomes | PUT | `/api/v1/triage/{node_id}` | ≤7 words, 422 on invalid |
| Outcomes | PUT | `/api/v1/outcomes/{node_id}` | alternative outcomes endpoint |

## LLM Integration

| Domain | Method | Path | Notes |
|---|---|---|---|
| LLM | GET | `/api/v1/llm/health` | 200 usable / 503 not usable |
| LLM | POST | `/api/v1/llm/fill-triage-actions` | JSON-only, ≤7-word outputs |

## Import/Export

| Domain | Method | Path | Notes |
|---|---|---|---|
| Import | POST | `/api/v1/import` | strict header ctx, 422 on mismatch |
| Import | POST | `/api/v1/import/preview` | preview import without applying |
| Export | GET | `/api/v1/tree/export` | 8-column frozen header CSV |
| Export | GET | `/api/v1/tree/export.xlsx` | Excel export |
| Export | GET | `/api/v1/export/csv` | CSV export alias |
| Export | GET | `/api/v1/export.xlsx` | Excel export alias |

## Dictionary Management

| Domain | Method | Path | Notes |
|---|---|---|---|
| Dictionary | GET | `/api/v1/dictionary` | type/query/limit/offset |
| Dictionary | POST | `/api/v1/dictionary` | 422 duplicate normalized |
| Dictionary | PUT | `/api/v1/dictionary/{id}` | update term |
| Dictionary | DELETE | `/api/v1/dictionary/{id}` | delete term |
| Normalize | GET | `/api/v1/dictionary/normalize` | {normalized:"..."} |

## Data Quality & Administration

| Domain | Method | Path | Notes |
|---|---|---|---|
| Data Quality | GET | `/api/v1/admin/data-quality/summary` | data quality metrics |
| Data Quality | POST | `/api/v1/admin/data-quality/repair/slot-gaps` | repair slot gaps |
| Data Quality | GET | `/api/v1/admin/data-quality/validation-rules` | validation rules |
| Performance | GET | `/api/v1/admin/performance/database-stats` | database statistics |
| Performance | POST | `/api/v1/admin/performance/create-indexes` | create performance indexes |
| Performance | GET | `/api/v1/admin/performance/health` | performance health check |
| Audit | GET | `/api/v1/admin/audit` | audit log entries |
| Audit | GET | `/api/v1/admin/audit/undoable` | undoable operations |
| Audit | POST | `/api/v1/admin/audit/{id}/undo` | undo operation |
| Audit | GET | `/api/v1/admin/audit/stats` | audit statistics |

## Multi-User & Concurrency

| Domain | Method | Path | Notes |
|---|---|---|---|
| Concurrency | GET | `/api/v1/concurrency/node/{id}/version` | get node version |
| Concurrency | GET | `/api/v1/concurrency/node/{id}/children-with-version` | children with version |
| Concurrency | POST | `/api/v1/concurrency/check-version` | check version match |
| Concurrency | GET | `/api/v1/concurrency/conflict-resolution-info` | conflict resolution info |

## VM Builder

| Domain | Method | Path | Notes |
|---|---|---|---|
| VM Builder | POST | `/api/v1/tree/vm/draft` | create draft |
| VM Builder | GET | `/api/v1/tree/vm/draft/{id}` | get draft |
| VM Builder | PUT | `/api/v1/tree/vm/draft/{id}` | update draft |
| VM Builder | DELETE | `/api/v1/tree/vm/draft/{id}` | delete draft |
| VM Builder | GET | `/api/v1/tree/vm/drafts` | list drafts |
| VM Builder | POST | `/api/v1/tree/vm/draft/{id}/plan` | calculate diff plan |
| VM Builder | POST | `/api/v1/tree/vm/draft/{id}/publish` | publish draft |
| VM Builder | GET | `/api/v1/tree/vm/stats` | VM Builder statistics |

## System & Health

| Domain | Method | Path | Notes |
|---|---|---|---|
| Health | GET | `/api/v1/health` | system health check |
| Health | GET | `/api/v1/health/metrics` | system metrics (when enabled) |
| Root | GET | `/` | root endpoint with service info |
| Root | GET | `/api/v1/` | versioned root endpoint |

## Legacy Routes (Deprecated)

> **Deprecation Notice**: The following routes return `Deprecation: true` and `Sunset: v7.0` headers.

| Domain | Method | Path | Notes | Migration Path |
|---|---|---|---|---|
| Legacy | GET | `/tree/slots/{parent_id}` | legacy slot access | Use `/api/v1/tree/{parent_id}/children` |
| Legacy | PUT | `/tree/slots/{parent_id}/slot/{slot}` | legacy slot update | Use `/api/v1/tree/parents/{parent_id}/children` |
| Legacy | DELETE | `/tree/slots/{parent_id}/slot/{slot}` | legacy slot deletion | Use `/api/v1/tree/parents/{parent_id}/children` |

### Migration Guide

**From Legacy Tree Slots to Modern Children API:**

- **Legacy**: `PUT /tree/slots/{parent_id}/slot/{slot}` with `{"label": "..."}`
- **Modern**: `PUT /api/v1/tree/parents/{parent_id}/children` with `{"slots": [{"slot": 1, "label": "..."}]}`

- **Legacy**: `DELETE /tree/slots/{parent_id}/slot/{slot}`
- **Modern**: `PUT /api/v1/tree/parents/{parent_id}/children` with `{"slots": [{"slot": 1, "label": ""}]}` (empty label removes)

**Benefits of Migration:**
- Atomic operations on multiple slots
- Better error handling and validation
- Consistent API patterns
- Future-proof endpoint structure

## Route Patterns

### Path Parameters
- `{parent_id}`: Integer parent node ID (≥1)
- `{node_id}`: Integer node ID (≥1)  
- `{id}`: Integer or UUID identifier
- `{slot}`: Integer slot number (1-5)

### Query Parameters
- `limit`: Integer, maximum results (default varies by endpoint)
- `offset`: Integer, pagination offset
- `type`: String, filter by type
- `query`: String, search query
- `dry_run`: Boolean, preview without applying changes

### Response Headers
- `Deprecation`: "true" for legacy routes
- `Sunset`: "v7.0" for legacy routes
- `ETag`: Version identifier for concurrency control
- `Content-Type`: "application/json" or "text/csv" or "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

### Status Codes
- `200`: Success
- `201`: Created
- `204`: No Content (e.g., no incomplete parents)
- `400`: Bad Request
- `401`: Unauthorized (when auth enabled)
- `404`: Not Found
- `409`: Conflict (e.g., slot contention)
- `412`: Precondition Failed (e.g., stale edit)
- `422`: Unprocessable Entity (validation error)
- `500`: Internal Server Error
- `503`: Service Unavailable (e.g., LLM not available)

## Versioning Strategy

- **v7.0**: Current stable version with all canonical endpoints
- **v7.x**: Backward compatible patches and additions
- **v8.0**: Planned breaking changes (legacy route removal)

## Dual-Mount Support

All canonical endpoints are available at both:
- `/api/v1/{endpoint}` (versioned)
- `/{endpoint}` (bare)

This ensures backward compatibility while encouraging versioned usage.
