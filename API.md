# Lorien API Documentation

## Overview
The Lorien API provides endpoints for managing decision tree structures with strict 5-children rule enforcement.

## Base URL
- Development: `http://localhost:8000`
- Production: Configure via environment variables

## Mounts
All endpoints are available at both root (`/`) and versioned (`/api/v1`).

## Authentication
Currently no authentication required (development mode).

## Health Endpoints

### GET /health
Returns health status, version, and database information.

**Response:**
```json
{
  "status": "ok",
  "version": "v6.7.0",
  "db": {
    "wal": true,
    "foreign_keys": true,
    "page_size": 4096,
    "path": "/path/to/database.db"
  },
  "features": {
    "llm": false
  }
}
```

### GET /api/v1/health
Same as `/health` but with API versioning.

### GET /llm/health
Returns 200 if LLM is enabled, 503 if disabled.

## Tree Management

### GET /tree/next-incomplete-parent
Returns the next parent node that needs children.

### GET /tree/{parent_id}/children
Returns all children of a parent node.

### POST /tree/{parent_id}/children
Upserts multiple children at once (atomic operation).

**Request Body:**
```json
{
  "children": [
    {"slot": 1, "label": "Child 1"},
    {"slot": 2, "label": "Child 2"},
    {"slot": 3, "label": "Child 3"},
    {"slot": 4, "label": "Child 4"},
    {"slot": 5, "label": "Child 5"}
  ]
}
```

**Constraints:**
- Exactly 5 children required
- No duplicate slots
- Slots must be 1-5

## Flags Management

### GET /flags/search?q={query}
Search for red flags by name.

### POST /flags/assign
Assign a red flag to a node.

**Request Body:**
```json
{
  "node_id": 1,
  "red_flag_name": "Flag Name",
  "user": "username"
}
```

### DELETE /flags/remove
Remove a red flag from a node.

## Flags Audit
`GET /flags/audit?node_id=<int>&limit=<int>`
`POST /flags/audit` → `{ id, node_id, flag_id, action, user, ts }`

## CSV Export
`GET /calc/export` → CSV with canonical headers: "Diagnosis","Node 1","Node 2","Node 3","Node 4","Node 5"

Contract is frozen; UI must not add columns.

## Triage Management

### GET /triage/{node_id}
Get triage information for a node.

### PUT /triage/{node_id}
Update triage information for a node.

**Request Body:**
```json
{
  "diagnostic_triage": "Diagnostic information",
  "actions": "Actions to take"
}
```

## cURL Smoke Tests

Use these commands to quickly verify API functionality during development:

### Health Check
```bash
# Basic health check
curl -s http://localhost:8000/api/v1/health | jq

# LLM health status
curl -i http://localhost:8000/api/v1/llm/health
```

### Tree Operations
```bash
# Find next incomplete parent
curl -i http://localhost:8000/api/v1/tree/next-incomplete-parent

# Get parent children (Edit Tree)
curl -s http://localhost:8000/api/v1/tree/parent/123/children | jq

# Update parent children (bulk)
curl -X PUT http://localhost:8000/api/v1/tree/parent/123/children \
  -H 'Content-Type: application/json' \
  -d '{
    "version": 1,
    "children": [
      {"slot": 1, "label": "Fever"},
      {"slot": 2, "label": "Pain"},
      {"slot": 3, "label": "Cough"},
      {"slot": 4, "label": "Fatigue"},
      {"slot": 5, "label": "Headache"}
    ]
  }'
```

### Dictionary Operations
```bash
# Search dictionary terms
curl -s 'http://localhost:8000/api/v1/dictionary?type=node_label&query=fe&limit=10' | jq

# Import dictionary terms (with CSV file)
curl -X POST http://localhost:8000/api/v1/dictionary/import \
  -F 'file=@terms.csv'
```

### Outcomes Operations
```bash
# Update outcomes with validation
curl -X PUT http://localhost:8000/api/v1/outcomes/456 \
  -H 'Content-Type: application/json' \
  -d '{
    "diagnostic_triage": "Acute infection suspected",
    "actions": "Administer antibiotics immediately"
  }'
```

### Flags Operations
```bash
# List flags
curl -s 'http://localhost:8000/api/v1/flags?limit=20' | jq

# Assign flag with cascade
curl -X POST http://localhost:8000/api/v1/flags/assign \
  -H 'Content-Type: application/json' \
  -d '{
    "node_id": 123,
    "flag_id": 7,
    "cascade": true
  }'
```

### Export Operations
```bash
# CSV export
curl -s http://localhost:8000/api/v1/calc/export | head -5

# XLSX export (save to file)
curl -o export.xlsx http://localhost:8000/api/v1/calc/export.xlsx
```

### Path Operations
```bash
# Get node path (breadcrumb)
curl -s 'http://localhost:8000/api/v1/tree/path?node_id=456' | jq
```

## Error Handling
All endpoints return appropriate HTTP status codes and error messages in JSON format.

## Rate Limiting
Currently no rate limiting implemented.

## CORS
Configurable via `CORS_ALLOW_ALL` environment variable:
- `false` (default): Localhost only
- `true`: All origins allowed (for LAN access)
