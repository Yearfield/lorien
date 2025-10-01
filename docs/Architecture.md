# Architecture

Overview
- Flutter shell with NavigationRail panes talks to a FastAPI VM Core; SQLite stores the tree. EngineLongBow is the only engine.

Diagram
```
Flutter Shell (Desktop)
  Panes: Home | VM Builder | Outcomes | Flags | Settings
        |                               ^
        |  REST (JSON + CSV/XLSX)       |
        v                               |
FastAPI (VM Core)
  Routers: health | import | export | tree_basic
        |   ^                     |
        |   |                     v
        |   |               EngineLongBow
        |   |           (import/preview/export)
        v   |                     |
     SQLite (WAL)
```

State & validation
- EngineLongBow is the sole ingest/export engine
- Option B: ≤5 children enforced at the service layer; DB remains flexible with unique `(parent_id, slot)` in 1..5
- Depth 0..5, root at depth 0; slots 1..5 for children

Configuration
- Flutter: `--dart-define=API_BASE` (e.g., `http://127.0.0.1:8000/api/v1`)
- API: `LORIEN_DB_PATH` points to SQLite file; WAL enabled

Versioning & health
- All endpoints mounted under `/api/v1`
- `/api/v1/health` returns: version, DB path, journal mode, table count, node count

Data model (SQLite)
- `nodes(id, parent_id, depth, slot, label, is_leaf, created_at, updated_at)`
- Key constraint: `UNIQUE(parent_id, slot)` enabling ≤5 children via service validation
- Views/triggers support next‑underfilled queries and metadata integrity
