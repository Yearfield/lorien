# Architecture

Overview

- Flutter shell with NavigationRail panes talks to a FastAPI VM Core; SQLite stores the tree. Two engines: EngineLongBow (decision trees) and EngineShelob (pathogen data).

Diagram

```
Flutter Shell (Desktop)
  Panes: Home | VM Builder | Dictionary | Outcomes | Flags | Settings
        |                               ^
        |  REST (JSON + CSV/XLSX)       |
        v                               |
FastAPI (VM Core) — Fully Async + Security
  Middleware Stack (in order):
    • CORS — Cross-origin request handling
    • Observability — Request tracing & logging
    • Deprecation — Legacy route redirects
    • Authentication — Bearer token validation
    • Rate Limiting — Request & auth attempt limiting
    • Input Validation — XSS, SQL injection protection
    • Security Headers — HSTS, CSP, X-Frame-Options
  Routers: health | import | export | tree_basic | dictionary | conflicts | pathogens
        |   ^                     |                    ^                        ^
        |   |                     v                    |                        |
        |   |               EngineLongBow             |                EngineShelob
        |   |           (import/preview/export)       |            (pathogen import/CRUD)
        v   |                     |                   |                        |
     SQLite (WAL) — Thread-Offloaded                 |                        |
        ^                                           |                        |
        |         medical_dictionary + sync triggers |                        |
        |         pathogen tables + associations      |                        |
        +-------------------------------------------+------------------------+
```

State & validation

- EngineLongBow: Decision tree ingest/export engine with ≤5 children enforced at service layer
- EngineShelob: Pathogen data import/management engine with separate database tables
- Option B: ≤5 children enforced at the service layer; DB remains flexible with unique `(parent_id, slot)` in 1..5
- Depth 0..5, root at depth 0; slots 1..5 for children

Configuration

- Flutter: `--dart-define=API_BASE` (e.g., `http://127.0.0.1:8000/api/v1`)
- API: `LORIEN_DB_PATH` points to SQLite file; WAL enabled
- Security: Environment-based configuration with production defaults

Security Configuration

- **Environment-based**: Automatic security enforcement in production
- **Authentication**: Bearer token required for write operations in production
- **Rate Limiting**: Configurable request and authentication attempt limits
- **Input Validation**: Comprehensive protection against injection attacks
- **Security Headers**: HTTP security headers for browser protection
- **CORS**: Environment-specific origin restrictions

Versioning & health

- All endpoints mounted under `/api/v1`
- `/api/v1/health` returns: version, DB path, journal mode, table count, node count, security status

Async Architecture

- All API endpoints are fully async (`async def`)
- All blocking SQLite operations wrapped with `anyio.to_thread()` to prevent event loop blocking
- Database connection management is async with proper transaction handling (BEGIN/COMMIT/ROLLBACK)
- Repository layer (`TreeRepository`) uses async methods for all database operations
- EngineLongBow functions (import/export) are wrapped in thread offloading when called from async routers
- Zero blocking I/O in the async event loop ensures high concurrency and responsiveness

Security Architecture

- **Middleware Stack**: Security middleware applied in specific order for optimal protection
- **Authentication Flow**: Token validation with timing attack protection and failed attempt tracking
- **Input Sanitization**: All user inputs validated and sanitized before processing
- **Rate Limiting**: In-memory tracking with automatic cleanup for DoS protection
- **Security Logging**: Comprehensive audit trail for all security events
- **Environment Detection**: Automatic security enforcement based on deployment environment

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
