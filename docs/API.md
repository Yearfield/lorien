# API Reference

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

### POST /llm/fill-triage-actions
Fill triage actions using LLM (guidance only, no auto-apply).

**Request Body:**
```json
{
  "root": "Blood Pressure",
  "nodes": ["High", "Severe", "Chest Pain", "Emergency", "Immediate"],
  "triage_style": "clinical",
  "actions_style": "practical"
}
```

**Response:**
```json
{
  "diagnostic_triage": "Based on the path Blood Pressure → High → Severe → Chest Pain → Emergency → Immediate, consider clinical assessment.",
  "actions": "Recommended practical actions for this clinical scenario.",
  "note": "AI suggestions are guidance-only; dosing and diagnosis are refused. Review before saving."
}
```

**Features:**
- Feature-flagged: requires `LLM_ENABLED=true`
- Returns 503 when LLM is disabled
- Path context validation (exactly 5 nodes required)
- Guidance-only: user must review and save manually
- Safety notice about AI limitations

**Safety:**
- AI suggestions are guidance-only
- Dosing and diagnosis are refused
- Users must review and validate before saving
