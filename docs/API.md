# API Documentation (VM Core)

Overview

- Versioned base: `/api/v1`
- Fully async architecture with thread-offloaded SQLite operations for high concurrency
- All endpoints use `async def` with blocking I/O wrapped in `anyio.to_thread()`
- EngineLongBow is the ingest/export engine; UI and CLI call the API (no client-side CSV building)
- All endpoints return JSON unless specified otherwise
- Standard HTTP status codes: 200 (success), 201 (created), 204 (no content), 400 (bad request), 401 (unauthorized), 404 (not found), 409 (conflict), 422 (validation error), 429 (rate limited), 500 (server error)
- **Security**: Production deployments require Bearer token authentication for write operations

Canonical header (frozen)

```
D0,D1,D2,D3,D4,D5,D6,Notes
```

## Authentication & Security

### Authentication Requirements

- **Development**: Authentication optional (`AUTH_REQUIRED=false`)
- **Production**: Authentication mandatory (`AUTH_REQUIRED=true`)
- **Write Operations**: All POST, PUT, DELETE operations require valid Bearer token
- **Read Operations**: GET, HEAD, OPTIONS operations are public (no authentication required)
- **Public Endpoints**: Health, live, ready endpoints are always accessible

### Authentication Headers

```bash
# Required for write operations in production
Authorization: Bearer your-secure-token-here
```

### Security Features

- **Rate Limiting**: Configurable request limits per IP address
- **Input Validation**: Protection against SQL injection, XSS, path traversal
- **Security Headers**: HSTS, CSP, X-Frame-Options, and other security headers
- **CORS Protection**: Environment-specific origin restrictions
- **Failed Attempt Tracking**: Automatic IP blocking after repeated failed authentication attempts

### Error Responses

#### Authentication Required (401)
```json
{
  "detail": {
    "error": "authentication_required",
    "message": "Authorization header required for write operations",
    "hint": "Include 'Authorization: Bearer <token>' header"
  }
}
```

#### Invalid Token (401)
```json
{
  "detail": {
    "error": "invalid_token",
    "message": "Invalid authentication token"
  }
}
```

#### Rate Limited (429)
```json
{
  "detail": {
    "error": "rate_limited",
    "message": "Too many requests",
    "retry_after": "3600"
  }
}
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
      "exists": true,
      "journal_mode": "wal",
      "tables": 5,
      "nodes": 123,
      "integrity": "ok",
      "objects": 14
    },
    "features": {
      "llm": false,
      "llm_requested": false,
      "analytics": false
    }
  }
  ```

  - `llm_requested` mirrors the environment toggle; when true but `llm=false`, health degrades to `"status": "degraded"` to signal missing model assets.
  - `analytics` tracks the `ANALYTICS_ENABLED` flag; the health metrics endpoint is only available when this value is `true`.

### Health Metrics (Optional)

- `GET /api/v1/health/metrics` → Telemetry data (requires `ANALYTICS_ENABLED=true`)
  - Returns 404 when analytics is disabled (`ANALYTICS_ENABLED=false`)
  - Async endpoint with thread-offloaded database operations
  - Runs count collection off the main event loop and always returns a `nodes` counter (0 on failure)

Examples:

```bash
# Health check (public endpoint)
curl -sS http://127.0.0.1:8000/api/v1/health | jq

# Health metrics (requires authentication if AUTH_REQUIRED=true)
curl -sS -H "Authorization: Bearer $AUTH_TOKEN" \
  http://127.0.0.1:8000/api/v1/health/metrics | jq
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
        {"row": 12, "msg": "parent 'Hypertension' would exceed 5 children with 'Severe' (preview)", "type": "value_error.max_children"}
      ]
    }
    ```

  - Depth validation is schema-aware. If future headers extend beyond `D6`, preview errors report the actual deepest allowed column (e.g., `"depth exceeds D7"`).

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

  - Warnings bundle both in-file heuristics and database lookups; repeated rows for the same parent/child combination are de-duplicated.

Examples:

```bash
# Preview CSV (requires authentication for write operations)
curl -sS -F file=@paths.csv \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  http://127.0.0.1:8000/api/v1/import/preview | jq

# Apply (replace) with enforcement (requires authentication)
curl -sS -F file=@paths.csv \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  "http://127.0.0.1:8000/api/v1/import?mode=replace&enforce_five=true" | jq
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

- `POST /api/v1/tree/child` → Add single child safely
  - **Purpose**: Add individual children without affecting existing children or their downstream data
  - **Body**: `{"parent_id": 123, "label": "New Child"}`
  - **Success** (200/201): `{"ok": true, "parent_id": 123, "label": "New Child", "slot": 3}`
  - **Validation** (422): Parent at max depth or already has 5 children

    ```json
    {
      "detail": [
        {"loc": ["parent_id"], "msg": "cannot add children beyond depth 6", "type": "value_error.max_depth"}
      ]
    }
    ```

    ```json
    {
      "detail": [
        {"loc": ["parent_id"], "msg": "parent already has 5 children", "type": "value_error.max_children"}
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

### Parent Rename & Merge Operations

- `GET /api/v1/tree/search-by-label?label=coughing` → Find parents by label

  ```json
  {
    "items": [
      {"id": 252, "label": "Coughing", "depth": 4},
      {"id": 553, "label": "Coughing", "depth": 4}
    ],
    "total": 2
  }
  ```

- `PUT /api/v1/tree/node/{node_id}/rename` → Rename parent node

  **Body:**

  ```json
  {"label": "New Parent Name"}
  ```

  **Response:**

  ```json
  {"ok": true, "node_id": 252, "new_label": "New Parent Name"}
  ```

- `POST /api/v1/tree/merge-parents` → Merge two parents with selected children

  **Body:**

  ```json
  {
    "current_parent_id": 553,
    "existing_parent_id": 252,
    "selected_children": ["Dry Cough", "Wet Cough", "Hemoptysis", "Shortness of breath", "Fever"]
  }
  ```

  **Response:**

  ```json
  {"ok": true, "merged_parent_id": 252, "deleted_parent_id": 553}
  ```

  **Notes:**
  - Merges the current parent into the existing parent
  - Replaces all children of the existing parent with the selected children
  - Deletes the current parent and all its children
  - Selected children must be exactly 5 or fewer
  - Automatically handles slot assignment and depth updates

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
# Preview import (requires authentication for write operations)
curl -sS -F "file=@data.csv;type=text/csv" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  http://127.0.0.1:8000/api/v1/import/preview | jq .

# Apply import with enforcement (requires authentication)
curl -sS -F "file=@data.csv;type=text/csv" \
  "http://127.0.0.1:8000/api/v1/import?mode=replace&enforce_five=true" | jq .
```

### Tree Navigation

```bash
# List roots
curl -sS http://127.0.0.1:8000/api/v1/tree/roots | jq .

# Get children
curl -sS "http://127.0.0.1:8000/api/v1/tree/children?parent_id=1&only_red=false" | jq .

# Add single child safely
curl -sS -X POST http://127.0.0.1:8000/api/v1/tree/child \
  -H "Content-Type: application/json" \
  -d '{"parent_id": 123, "label": "New Child"}' | jq .

# Find next underfilled parent
curl -sS "http://127.0.0.1:8000/api/v1/tree/next-underfilled?root_id=1" | jq .

# Clone subtree
curl -sS -X POST http://127.0.0.1:8000/api/v1/tree/clone \
  -H "Content-Type: application/json" \
  -d '{"source_id": 123, "dest_parent_id": 456}' | jq .

# Search for parents by label
curl -sS "http://127.0.0.1:8000/api/v1/tree/search-by-label?label=coughing" | jq .

# Rename a parent
curl -sS -X PUT "http://127.0.0.1:8000/api/v1/tree/node/252/rename" \
  -H "Content-Type: application/json" \
  -d '{"label": "Cough"}' | jq .

# Merge two parents with selected children
curl -sS -X POST "http://127.0.0.1:8000/api/v1/tree/merge-parents" \
  -H "Content-Type: application/json" \
  -d '{
    "current_parent_id": 553,
    "existing_parent_id": 252,
    "selected_children": ["Dry Cough", "Wet Cough", "Hemoptysis", "Shortness of breath", "Fever"]
  }' | jq .
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
