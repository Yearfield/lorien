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
FastAPI (VM Core) — Fully Async
  Routers: health | import | export | tree_basic
        |   ^                     |
        |   |                     v
        |   |               EngineLongBow
        |   |           (import/preview/export)
        v   |                     |
     SQLite (WAL) — Thread-Offloaded
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

Async Architecture

- All API endpoints are fully async (`async def`)
- All blocking SQLite operations wrapped with `anyio.to_thread()` to prevent event loop blocking
- Database connection management is async with proper transaction handling (BEGIN/COMMIT/ROLLBACK)
- Repository layer (`TreeRepository`) uses async methods for all database operations
- EngineLongBow functions (import/export) are wrapped in thread offloading when called from async routers
- Zero blocking I/O in the async event loop ensures high concurrency and responsiveness

Data model (SQLite)

- `nodes(id, parent_id, depth, slot, label, is_leaf, created_at, updated_at)`
- Key constraint: `UNIQUE(parent_id, slot)` enabling ≤5 children via service validation
- Views/triggers support next‑underfilled queries and metadata integrity

Tree Operations

- **Basic CRUD**: Create, read, update, delete nodes via `/api/v1/tree/*` endpoints
- **Safe Child Addition**: Individual child creation via `POST /api/v1/tree/child` that preserves downstream data
- **Navigation**: Breadcrumb traversal, children listing, ancestor chains
- **Search**: Find nodes by label for duplicate detection and merge operations
- **Rename**: Update node labels with automatic duplicate detection
- **Merge**: Combine two parents with user-selected children (≤5 total)
  - Deletes source parent and all its children
  - Replaces target parent's children with selected set
  - Maintains referential integrity and slot constraints
  - Atomic transaction with rollback on failure
- **Cloning**: Duplicate subtrees with automatic slot management
- **Validation**: Enforces 5-child limit at service layer, not database constraints
