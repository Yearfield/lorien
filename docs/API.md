# API Documentation

## Overview
The Lorien API provides endpoints for managing decision trees, red flags, and triage data.

## Mounts
All endpoints are available at both root (`/`) and versioned (`/api/v1`).

## CSV / XLSX Export (Contract Frozen)
Header (exact order; case-sensitive; comma-separated):
`Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions`

Endpoints: `GET /calc/export`, `GET /tree/export`, and XLSX variants `/calc/export.xlsx`, `/tree/export.xlsx`.

UI (Flutter/Streamlit) must not construct CSV/XLSX; always call the API.

## LLM Health
`GET /llm/health` → 503 when disabled; 200 JSON when enabled. LLM is **OFF by default**.

## LLM Fill
`POST /llm/fill-triage-actions` → ≤7 words, phrases only, regex `^[A-Za-z0-9 ,\\-]+$`, JSON-only; Copy-From-VM via `?vm=`.

## Health
`GET /health` (+ `/api/v1/health`) → `{ status|ok, version, db:{ path, wal, foreign_keys }, features:{ llm }, metrics?: {...} }`

## Telemetry
`GET /health` includes `metrics.telemetry` when `ANALYTICS_ENABLED=true` (non-PHI counters only).

## Authentication
Most endpoints require no authentication. Some endpoints may require API keys in the future.

## Rate Limiting
Currently no rate limiting is implemented. Consider implementing if needed for production use.

## Error Handling
All endpoints return appropriate HTTP status codes:
- 200: Success
- 400: Bad Request
- 404: Not Found
- **422: Unprocessable Entity** (semantic/validation errors)
- 500: Internal Server Error

**All semantic/validation errors return 422 Unprocessable Entity.**

Body field errors follow FastAPI/Pydantic default format:
```json
{
  "detail": [
    {
      "loc": ["body", "diagnostic_triage"], 
      "msg": "Diagnostic Triage must be ≤7 words", 
      "type": "value_error.word_count"
    }
  ]
}
```

## Endpoints

All responses are JSON unless noted. Base URL defaults to `http://localhost:8000/api/v1`.

> **Auth**: None (local dev).  
> **Version**: Exposed via `/api/v1/health.version`.

## Health

GET `/api/v1/health`

- **200** `{ ok, version, db: { path, wal, foreign_keys }, features: { llm } }`

---

## Tree

### Get next incomplete parent
GET `/api/v1/tree/next-incomplete-parent`

- **200** `{ parent_id: int, missing_slots: "2,4,5" }` or **204** when none.

### Get children (1..5) for a parent
GET `/api/v1/tree/{parent_id}/children`

- **200** `[{ slot: 1..5, label: "..." , id?: int }, ...]`

### Upsert multiple slots atomically
POST `/api/v1/tree/{parent_id}/children`
```json
{ "children": [ { "slot": 1, "label": "..." }, { "slot": 4, "label": "..." } ] }
```
- **200** `{ ok: true }`
- **409** slot conflict
- **422** validation

### Upsert single slot
POST `/api/v1/tree/{parent_id}/child`
```json
{ "slot": 3, "label": "..." }
```

---

## Triage

### Get triage for a node
GET `/api/v1/triage/{node_id}`

- **200** `{ "diagnostic_triage": "...", "actions": "..." }`
- **404** if none

### Put triage (leaf-only)
PUT `/api/v1/triage/{node_id}`
```json
{ "diagnostic_triage": "...", "actions": "..." }
```
- **200** updated object
- **400** if not a leaf

---

## Flags

### Search flags
GET `/api/v1/flags/search?q=term`

- **200** `[{ "id": 1, "name": "..." }]`

### Assign
POST `/api/v1/flags/assign`
```json
{ "node_id": 123, "red_flag_name": "..." }
```
- **200** `{ ok: true }`

---

## Calculator

### Export CSV
GET `/api/v1/calc/export`

- **200** CSV (content-disposition suggests filename)

**Canonical 8-Column Header:**
```
Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions
```

**Column Details:**
- **Vital Measurement**: Root node label (depth=0)
- **Node 1-5**: Child node labels (depth=1-5)
- **Diagnostic Triage**: Clinical assessment for leaf nodes
- **Actions**: Recommended actions for leaf nodes

---

## LLM (Optional — feature-flagged)

### LLM health
GET `/api/v1/llm/health`

- **200** `{ enabled, model_path, n_threads, n_ctx, n_gpu_layers }`
- **503** when disabled

### Fill triage/actions (targeted)
POST `/llm/fill-triage-actions`
```json
{
  "root": "Chest pain",
  "nodes": ["Sudden onset", "Radiates to back", "Hypotension", "Sweating", "Collapse"],
  "triage_style": "diagnosis-only",
  "actions_style": "referral-only",
  "apply": false,
  "node_id": 987  // required only when apply=true (must be a leaf)
}
```
- **200** `{ "diagnostic_triage":"...", "actions":"...", "applied": false }`
- **400** missing node_id when apply=true, or non-leaf
- **503** when LLM disabled

**Safety**: the LLM is guidance-only; dosing/prescription requests are refused.

## CSV Export (Contract Frozen)

**Header (exact order):**
`Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions`

`GET /calc/export` and `GET /tree/export` must return CSV with the exact header above.
UI (Streamlit + Flutter) must call API; no CSV construction in UI.

## Conflicts & Integrity

### Missing Slots
`GET /tree/missing-slots` → Returns parents with missing child slots
```json
{
  "parents_with_missing_slots": [
    {
      "parent_id": 1,
      "label": "Blood Pressure",
      "depth": 1,
      "missing_slots": [3, 5]
    }
  ],
  "total_count": 1
}
```

### Next Incomplete Parent
`GET /tree/next-incomplete-parent` → Returns next parent needing completion
```json
{
  "parent_id": 1,
  "missing_slots": [3, 5]
}
```

## Outcomes & Triage

### Search Triage
`GET /triage/search?leaf_only=true&query=...` → Search triage records
```json
{
  "results": [
    {
      "node_id": 5,
      "label": "High BP",
      "path": "Blood Pressure → High BP",
      "diagnostic_triage": "Monitor closely",
      "actions": "Check every 2 hours",
      "is_leaf": true,
      "updated_at": "2024-01-01T12:00:00"
    }
  ],
  "total_count": 1,
  "leaf_only": true
}
```

### Update Triage
`PUT /triage/{node_id}` → Update triage for leaf nodes only
```json
{
  "diagnostic_triage": "New triage text",
  "actions": "New actions"
}
```

**Response:**
```json
{
  "message": "Triage updated successfully",
  "node_id": 5,
  "updated_at": "2024-01-01T12:00:00"
}
```

**Error (non-leaf):**
```json
{
  "detail": "Triage can only be updated for leaf nodes"
}
```

## Excel Export

### GET /calc/export.xlsx
Export calculator data as Excel workbook.

**Response:** Excel file with `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

**Headers:**
- `Content-Disposition: attachment; filename=calculator_export.xlsx`
- `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

**Sheet:** CalculatorExport

### GET /tree/export.xlsx
Export tree data as Excel workbook.

**Response:** Excel file with `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

**Headers:**
- `Content-Disposition: attachment; filename=tree_export.xlsx`
- `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

**Sheet:** TreeExport

## Root Management

### POST /tree/roots
Create a new root (vital measurement) with 5 preseeded child slots.

**Request Body:**
```json
{
  "label": "Blood Pressure",
  "children": ["High", "Normal", "Low"]
}
```

**Response:**
```json
{
  "root_id": 123,
  "children": [
    {"id": 124, "slot": 1, "label": "High"},
    {"id": 125, "slot": 2, "label": "Normal"},
    {"id": 126, "slot": 3, "label": "Low"},
    {"id": 127, "slot": 4, "label": ""},
    {"id": 128, "slot": 5, "label": ""}
  ],
  "message": "Created root 'Blood Pressure' with 5 child slots"
}
```

**Validation:**
- `label` cannot be empty
- `children` array cannot exceed 5 items
- Creates exactly 5 child slots (empty labels for unused slots)

## Tree Statistics

### GET /tree/stats
Get tree completeness statistics.

**Response:**
```json
{
  "nodes": 1234,
  "roots": 12,
  "leaves": 456,
  "complete_paths": 400,
  "incomplete_parents": 35
}
```

**Metrics:**
- `nodes`: Total number of nodes in the tree
- `roots`: Number of root nodes (depth 0)
- `leaves`: Number of leaf nodes (depth 5)
- `complete_paths`: Number of complete root→leaf paths
- `incomplete_parents`: Number of parents with fewer than 5 children

## LLM Integration

### LLM Health
- `GET /api/v1/llm/health` - Check if LLM service is available
- Returns 503 when disabled, 200 when enabled

### LLM Fill — Triage & Actions
`POST /api/v1/llm/fill-triage-actions`

**Body:**
```json
{
  "root": "<string>",
  "nodes": ["<n1>","<n2>","<n3>","<n4>","<n5>"],  // exactly 5 strings; empty "" allowed
  "triage_style": "diagnosis-only" | "referral-only",
  "actions_style": "diagnosis-only" | "referral-only",
  "apply": false
}
```

**Response (always JSON):**
```json
{ 
  "diagnostic_triage": "<=600 chars>", 
  "actions": "<=800 chars>" 
}
```

**Notes:**
- Outputs are server-clamped to the caps above.
- If `apply=true` and the target is not a leaf, server returns 422 but still includes suggestions in the JSON body so the client may copy manually.

## Triage Management

### Search Triage Records
- `GET /api/v1/triage/search` - Search triage records with filtering
- Supports `leaf_only`, `query`, `vm`, `sort`, and `limit` parameters

### Get Triage for Node
- `GET /api/v1/triage/{node_id}` - Get triage information for a specific node

### Update Triage
- `PUT /api/v1/triage/{node_id}` - Update triage for a node (leaf-only)
- Enforces character caps: diagnostic_triage ≤600 chars, actions ≤800 chars
- Returns 422 on validation errors

### Triage — Copy From last VM
`GET /api/v1/triage/search?vm=<vital_measurement>&leaf_only=true&sort=updated_at:desc&limit=1`

Returns the most recent record under the given Vital Measurement for pre-fill in the client.
