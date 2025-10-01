# API Documentation (VM Core)

Overview
- Versioned base: `/api/v1`
- EngineLongBow is the ingest/export engine; UI and CLI call the API (no client-side CSV building)

Canonical header (frozen)
```
D0,D1,D2,D3,D4,D5,D6,Notes
```

Health
- `GET /api/v1/live` → `{ "status": "live" }`
- `GET /api/v1/ready` → `{ "status": "ready"|"not_ready", "db": { "has_nodes_table": true|false } }`
- `GET /api/v1/health` →
  ```json
  {
    "version": "6.8.0-beta.1",
    "db": {"path": "/path/app.db", "journal_mode": "wal", "tables": 5, "nodes": 123},
    "llm": false,
    "status": "ok"
  }
  ```
Examples:
```bash
curl -sS http://127.0.0.1:8000/api/v1/live | jq
curl -sS http://127.0.0.1:8000/api/v1/ready | jq
curl -sS http://127.0.0.1:8000/api/v1/health | jq
```

Import (EngineLongBow)
- Preview: `POST /api/v1/import/preview` (multipart `file`)
  - 200:
    ```json
    {"ok": true, "header": ["D0","D1","D2","D3","D4","D5","D6","Notes"],
     "stats": {"found_paths": 42},
     "errors": [{"row": 12, "msg": "parent (...) would exceed 5 children (preview)", "type": "value_error.max_children"}]}
    ```
Examples:
```bash
# Preview CSV
curl -sS -F file=@paths.csv http://127.0.0.1:8000/api/v1/import/preview | jq

# Apply (replace) with enforcement
curl -sS -F file=@paths.csv "http://127.0.0.1:8000/api/v1/import?mode=replace&enforce_five=true" | jq
```
- Apply: `POST /api/v1/import?mode=append|replace&enforce_five=true` (multipart `file`)
  - 200: `{ "ok": true, "result": { ... } }`
  - 422 (when `enforce_five=true` and any parent ends >5):
    ```json
    {"ok": false, "error": "value_error.max_children",
     "detail": [{"parent_id": 7, "parent_label": "...", "count": 6, "msg": "parent ends with >5 children"}]}
    ```

Tree (editing/navigation)
- Roots
  - `GET /api/v1/tree/roots` → `{ "items": [{"id":1, "label":"..."}], "total": 1 }`
  - `POST /api/v1/tree/roots` → `201 { "id": 1, "label": "...", "depth": 0 }`
  - `DELETE /api/v1/tree/roots/{root_id}` → `204 No Content`
- Children
  - `GET /api/v1/tree/children?parent_id=123[&only_red=false]` → `{ "items": [...], "total": N }`
  - `PUT /api/v1/tree/children` (body: `{ "parent_id": 123, "children": [{"label": "A"}, {"label": "B"}] }`)
    - 200: `{ "ok": true, "count": 2 }`
    - 409 (concurrent slot conflict):
      ```json
      {"error": "slot_conflict", "slot": 2, "parent_id": 123, "hint": "Concurrent edit detected. Slot already occupied."}
      ```
    - 422 (validation):
      ```json
      {"detail": [{"loc": ["children"], "msg": "duplicate labels", "type": "value_error.duplicate"}]}
      ```
      or
      ```json
      {"detail": [{"loc": ["children"], "msg": "too many children: 6>5", "type": "value_error.max_children"}]}
      ```
- Drilldown
  - `GET /api/v1/tree/node?node_id=123` → `{ "id": 123, "label": "...", "depth": 2, "parent_id": 45 }`
  - `GET /api/v1/tree/ancestors?node_id=123` → `{ "items": [{"id":1,"label":"..."}, ...], "total": 3 }`
- Next underfilled (authoring assist)
  - `GET /api/v1/tree/next-underfilled[?root_id=1][&after_id=999]` → `200 { "parent_id": 7, ... }` or `204` when none
- Edge flags
  - `PUT /api/v1/tree/edge/flag` (body: `{ "parent_id": 1, "child_id": 2, "red_flag": true }`) → `{ "ok": true, ... }`

Export
- CSV (canonical): `GET /api/v1/tree/export` → `text/csv` with frozen header
- XLSX: `GET /api/v1/tree/export.xlsx` → spreadsheet with the same columns
- JSON (dev aid): `GET /api/v1/tree/export-json`
- Aliases (legacy): `/api/v1/export/csv`, `/api/v1/export.xlsx`

Curl examples
```bash
# Preview
curl -sS -F "file=@data.csv;type=text/csv" http://127.0.0.1:8000/api/v1/import/preview | jq .

# Apply (replace) with service-level ≤5 enforcement
curl -sS -F "file=@data.csv;type=text/csv" \
  "http://127.0.0.1:8000/api/v1/import?mode=replace&enforce_five=true" | jq .

# Export CSV / XLSX
curl -L "http://127.0.0.1:8000/api/v1/tree/export" -o tree.csv
curl -L "http://127.0.0.1:8000/api/v1/tree/export.xlsx" -o tree.xlsx
```

Contracts & rules
- Frozen header exactly: `D0..D6, Notes`
- Option B ≤5 enforced at API/import; DB flexible via unique `(parent_id, slot)`
- Import is transactional when `enforce_five=true` (rollback on violations)
