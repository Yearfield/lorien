# API Documentation (VM Core)

Overview
- Versioned base: `/api/v1`
- EngineLongBow is the ingest/export engine; UI and CLI call the API (no client-side CSV building)
- All endpoints return JSON unless specified otherwise
- Standard HTTP status codes: 200 (success), 201 (created), 204 (no content), 400 (bad request), 404 (not found), 409 (conflict), 422 (validation error), 500 (server error)

Canonical header (frozen)
```
D0,D1,D2,D3,D4,D5,D6,Notes
```

## Health & Status

### Health Check
- `GET /api/v1/health` → Comprehensive health status
  ```json
  {
    "ok": true,
    "status": "ok",
    "version": "6.8.0-beta.1",
    "db": {
      "path": "/path/app.db",
      "journal_mode": "wal",
      "tables": 5,
      "nodes": 123,
      "integrity": "ok",
      "objects": 14
    },
    "features": {"llm": false}
  }
  ```

### Health Metrics (Optional)
- `GET /api/v1/health/metrics` → Telemetry data (requires `ANALYTICS_ENABLED=true`)
  - Returns 404 when analytics is disabled
  - Returns non-PHI counters and metrics

Examples:
```bash
curl -sS http://127.0.0.1:8000/api/v1/health | jq
curl -sS http://127.0.0.1:8000/api/v1/health/metrics | jq
```

## Import (EngineLongBow)

### Preview Import
- `POST /api/v1/import/preview` (multipart `file`)
  - **Purpose**: Analyze file without writing to database
  - **Supports**: CSV and XLSX files
  - **Response** (200):
    ```json
    {
      "ok": true,
      "header": ["D0","D1","D2","D3","D4","D5","D6","Notes"],
      "stats": {"found_paths": 42},
      "errors": [
        {"row": 12, "msg": "parent (...) would exceed 5 children (preview)", "type": "value_error.max_children"}
      ]
    }
    ```

### Apply Import
- `POST /api/v1/import?mode=append|replace&enforce_five=true` (multipart `file`)
  - **Parameters**:
    - `mode`: `append` (default) or `replace`
    - `enforce_five`: `true` to enforce ≤5 children per parent (default: `false`)
  - **Success** (200):
    ```json
    {
      "ok": true,
      "inserted": 42,
      "parents_touched": 15,
      "roots": 3,
      "warnings": []
    }
    ```
  - **Validation Error** (422 when `enforce_five=true`):
    ```json
    {
      "ok": false,
      "error": "value_error.max_children",
      "detail": [{"parent_id": 7, "parent_label": "...", "count": 6, "msg": "parent ends with >5 children"}]
    }
    ```

Examples:
```bash
# Preview CSV
curl -sS -F file=@paths.csv http://127.0.0.1:8000/api/v1/import/preview | jq

# Apply (replace) with enforcement
curl -sS -F file=@paths.csv "http://127.0.0.1:8000/api/v1/import?mode=replace&enforce_five=true" | jq
```

## Tree Management

### Roots
- `GET /api/v1/tree/roots` → List all root nodes
  ```json
  {
    "items": [
      {"id": 1, "label": "vital measurement", "display_label": "Vital Measurement"}
    ],
    "total": 1
  }
  ```
- `POST /api/v1/tree/roots` → Create new root (201)
  ```json
  {"id": 1, "label": "New Root", "depth": 0}
  ```
- `DELETE /api/v1/tree/roots/{root_id}` → Delete root and all descendants (204)

### Children Management
- `GET /api/v1/tree/children?parent_id=123&only_red=false` → List children
  ```json
  {
    "items": [
      {"id": 2, "label": "child1", "slot": 1, "depth": 1, "parent_id": 123}
    ],
    "total": 1
  }
  ```
- `PUT /api/v1/tree/children` → Replace children atomically
  - **Body**: `{"parent_id": 123, "children": [{"label": "A"}, {"label": "B"}]}`
  - **Success** (200): `{"ok": true, "count": 2}`
  - **Conflict** (409): Slot already occupied
    ```json
    {
      "error": "slot_conflict",
      "slot": 2,
      "parent_id": 123,
      "hint": "Concurrent edit detected. Slot already occupied."
    }
    ```
  - **Validation** (422): Too many children or duplicates
    ```json
    {
      "detail": [
        {"loc": ["children"], "msg": "too many children: 6>5", "type": "value_error.max_children"}
      ]
    }
    ```

### Navigation & Drilldown
- `GET /api/v1/tree/node?node_id=123` → Get node details
  ```json
  {"id": 123, "label": "Node Label", "depth": 2, "parent_id": 45}
  ```
- `GET /api/v1/tree/ancestors?node_id=123` → Get ancestor chain
  ```json
  {
    "items": [
      {"id": 1, "label": "Root", "depth": 0, "parent_id": null},
      {"id": 45, "label": "Parent", "depth": 1, "parent_id": 1}
    ],
    "total": 2
  }
  ```

### Authoring Assistance
- `GET /api/v1/tree/next-underfilled?root_id=1&after_id=999` → Find next parent with <5 children
  - Returns 200 with parent details or 204 if none found
- `PUT /api/v1/tree/edge/flag` → Set/unset red flags
  - **Body**: `{"parent_id": 1, "child_id": 2, "red_flag": true}`
  - **Response**: `{"ok": true, "parent_id": 1, "child_id": 2, "red_flag": true}`

### Cloning & Subtree Operations
- `GET /api/v1/tree/clone/candidates?label=hypertension` → Find clone sources
- `POST /api/v1/tree/clone` → Clone subtree
  - **Body**: `{"source_id": 123, "dest_parent_id": 456}`
  - **Response**: `{"ok": true, "created": 5}`
- `DELETE /api/v1/tree/node/{node_id}?dry_run=false` → Delete node/subtree
  - **Response**: `{"dry_run": false, "snapshot": {...}}`
- `POST /api/v1/tree/subtree/restore` → Restore from snapshot
  - **Body**: `{"snapshot": {"origin": {...}, "nodes": [...]}}`
  - **Response**: `{"restored": true, "new_origin_id": 789}`

## Export

### Primary Export Endpoints
- `GET /api/v1/tree/export?format=csv|xlsx` → Download file with filters
- `HEAD /api/v1/tree/export` → Get headers without downloading
- **Parameters**:
  - `format`: `csv` (default) or `xlsx`
  - `max_depth`: Maximum depth to export (0 = unlimited)
  - `root_ids`: Comma-separated root IDs to filter
  - `root_labels`: Comma-separated root labels to filter
  - `only_red`: Only export red-flagged paths (default: false)
  - `include_meta`: Include metadata columns (default: false)
  - `filename`: Custom filename for download

### JSON Export (Development)
- `GET /api/v1/tree/export-json?limit=50&offset=0` → JSON format for development
  ```json
  {
    "items": [
      {"D0": "Root", "D1": "Child", "D2": "", "D3": "", "D4": "", "D5": "", "D6": "", "Notes": ""}
    ],
    "total": 1,
    "limit": 50,
    "offset": 0
  }
  ```

### Legacy Aliases (Backward Compatibility)
- `GET /api/v1/export/csv` → CSV export (legacy)
- `GET /api/v1/export.xlsx` → XLSX export (legacy)

## Conflicts Resolution

### Scan Conflicts
- `GET /api/v1/conflicts/scan` → Find label conflicts across all depths
  ```json
  [
    {
      "label": "hypertension",
      "occurrences": 4,
      "union_children": ["headache", "nausea", "vomiting", "chest pain", "myalgia", "dizziness"],
      "parents": [
        {"parent_id": 12, "depth": 1, "children": ["headache", "nausea", "vomiting"]},
        {"parent_id": 44, "depth": 2, "children": ["headache", "chest pain", "myalgia"]},
        {"parent_id": 67, "depth": 3, "children": ["dizziness", "nausea", "vomiting"]}
      ],
      "skipped_parents": [
        {"parent_id": 91, "depth": 6, "children": ["existing child"], "reason": "max_depth"}
      ]
    }
  ]
  ```

### Resolve Conflicts
- `POST /api/v1/conflicts/resolve` → Apply standardized children to all matching parents
  - **Body**: `{"label": "hypertension", "selected_children": ["headache", "nausea", "vomiting", "chest pain", "myalgia"], "dry_run": false}`
  - **Success** (200):
    ```json
    {
      "updated_parents": 3,
      "children_per_parent": 5,
      "parents": [
        {"parent_id": 12, "removed": [], "added": ["chest pain", "myalgia"]},
        {"parent_id": 44, "removed": [], "added": ["nausea", "vomiting"]},
        {"parent_id": 67, "removed": ["dizziness"], "added": ["headache", "chest pain", "myalgia"]}
      ],
      "skipped_parents": [
        {"parent_id": 91, "depth": 6, "reason": "max_depth", "children": ["existing child"]}
      ]
    }
    ```
  - **Validation Errors** (422):
    - Too many children: `{"detail": [{"loc": ["selected_children"], "msg": "too many children: 6>5", "type": "value_error.max_children"}]}`
    - Max depth exceeded: `{"detail": [{"loc": ["label"], "msg": "all parents at max depth; cannot add children beyond D6", "type": "value_error.max_depth"}]}`

## Examples

### Import Operations
```bash
# Preview import
curl -sS -F "file=@data.csv;type=text/csv" http://127.0.0.1:8000/api/v1/import/preview | jq .

# Apply import with enforcement
curl -sS -F "file=@data.csv;type=text/csv" \
  "http://127.0.0.1:8000/api/v1/import?mode=replace&enforce_five=true" | jq .
```

### Tree Navigation
```bash
# List roots
curl -sS http://127.0.0.1:8000/api/v1/tree/roots | jq .

# Get children
curl -sS "http://127.0.0.1:8000/api/v1/tree/children?parent_id=1&only_red=false" | jq .

# Find next underfilled parent
curl -sS "http://127.0.0.1:8000/api/v1/tree/next-underfilled?root_id=1" | jq .

# Clone subtree
curl -sS -X POST http://127.0.0.1:8000/api/v1/tree/clone \
  -H "Content-Type: application/json" \
  -d '{"source_id": 123, "dest_parent_id": 456}' | jq .
```

### Export Operations
```bash
# CSV export with filters
curl -L "http://127.0.0.1:8000/api/v1/tree/export?format=csv&max_depth=3&only_red=false" -o tree.csv

# XLSX export with metadata
curl -L "http://127.0.0.1:8000/api/v1/tree/export?format=xlsx&include_meta=true&root_ids=1,2" -o tree.xlsx

# JSON export for development
curl -sS "http://127.0.0.1:8000/api/v1/tree/export-json?limit=100" | jq .
```

### Conflicts Resolution
```bash
# Scan for conflicts
curl -sS http://127.0.0.1:8000/api/v1/conflicts/scan | jq .

# Dry run resolution
curl -sS -X POST http://127.0.0.1:8000/api/v1/conflicts/resolve \
  -H "Content-Type: application/json" \
  -d '{"label":"hypertension","selected_children":["headache","nausea","vomiting","chest pain","myalgia"],"dry_run":true}' | jq .

# Apply resolution
curl -sS -X POST http://127.0.0.1:8000/api/v1/conflicts/resolve \
  -H "Content-Type: application/json" \
  -d '{"label":"hypertension","selected_children":["headache","nausea","vomiting","chest pain","myalgia"],"dry_run":false}' | jq .
```

## API Contracts & Rules

### Core Constraints
- **Option B Enforcement**: ≤5 children per parent (enforced at service level)
- **Max Depth**: D6 is the maximum depth (D0-D6 = 7 levels total)
- **Concurrent Edits**: Handled via slot conflicts (409 status)
- **Label Normalization**: Case-insensitive, whitespace-trimmed for conflicts

### Import/Export
- **Engine**: EngineLongBow handles all import/export operations
- **Format**: Canonical CSV/XLSX with frozen header `D0,D1,D2,D3,D4,D5,D6,Notes`
- **Validation**: Import can enforce ≤5 children when `enforce_five=true`
- **Transaction**: Import is transactional when `enforce_five=true` (rollback on violations)

### Conflicts Resolution
- **Grouping**: By normalized label only (ignores depth)
- **Scope**: Applies to all parents with matching label across all depths
- **Validation**: Enforces ≤5 children and max depth D6
- **Transaction**: All changes are atomic

### Response Standards
- **Format**: JSON responses with structured error details
- **Status Codes**: Standard HTTP codes with specific error types
- **Versioning**: All endpoints under `/api/v1` prefix
- **Error Format**: `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}`
