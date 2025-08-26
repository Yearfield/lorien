# API Reference

All responses are JSON unless noted. Base URL defaults to `http://localhost:8000`.

> **Auth**: None (local dev).  
> **Version**: Exposed via `/health.version`.

## Health

GET `/health`

- **200** `{ ok, version, db: { path, wal, foreign_keys }, features: { llm } }`

---

## Tree

### Get next incomplete parent
GET `/tree/next-incomplete-parent`

- **200** `{ parent_id: int, missing_slots: "2,4,5" }` or **204** when none.

### Get children (1..5) for a parent
GET `/tree/{parent_id}/children`

- **200** `[{ slot: 1..5, label: "..." , id?: int }, ...]`

### Upsert multiple slots atomically
POST `/tree/{parent_id}/children`
```json
{ "children": [ { "slot": 1, "label": "..." }, { "slot": 4, "label": "..." } ] }
```
- **200** `{ ok: true }`
- **409** slot conflict
- **422** validation

### Upsert single slot
POST `/tree/{parent_id}/child`
```json
{ "slot": 3, "label": "..." }
```

---

## Triage

### Get triage for a node
GET `/triage/{node_id}`

- **200** `{ "diagnostic_triage": "...", "actions": "..." }`
- **404** if none

### Put triage (leaf-only)
PUT `/triage/{node_id}`
```json
{ "diagnostic_triage": "...", "actions": "..." }
```
- **200** updated object
- **400** if not a leaf

---

## Flags

### Search flags
GET `/flags/search?q=term`

- **200** `[{ "id": 1, "name": "..." }]`

### Assign
POST `/flags/assign`
```json
{ "node_id": 123, "red_flag_name": "..." }
```
- **200** `{ ok: true }`

---

## Calculator

### Export CSV
GET `/calc/export`

- **200** CSV (content-disposition suggests filename)

Header order: `Vital Measurement,Node 1,...,Node 5,Diagnostic Triage,Actions`

---

## LLM (Optional — feature-flagged)

### LLM health
GET `/llm/health`

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
