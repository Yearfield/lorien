# Design Decisions

This document captures key architectural and design decisions for the Lorien project.

## Core Architecture

### Database Design
- SQLite with WAL mode for ACID compliance
- Exactly 5 children per parent (enforced by triggers)
- Recursive CTEs for tree traversal
- Foreign key constraints enabled

### API Design
- RESTful endpoints with consistent error handling
- JSON responses (except CSV/XLSX exports)
- Dependency injection for repository access
- Retry logic with exponential backoff

## CSV Contract
- Frozen at 8 columns (see API.md). Any change requires a version bump, docs update, and test updates.

## LLM Posture
- OFF by default; guidance-only when enabled; never dosing/diagnosis in UI.

## Dual Mounts
- Keep both `/` and `/api/v1` to avoid path drift during beta.

## Audit Retention
- Append-only `red_flag_audit` with index `(node_id, ts)`.
- Retention cap: keep **30 days or 50,000 rows** (whichever first).
- Rotation: nightly job removes older/overflow rows; metrics emitted to health.

## Caching Strategy
- In-memory cache with TTL (5 minutes default)
- Cache invalidation on writes
- Pattern-based invalidation for related data

## Performance Targets
- `/tree/stats` and conflicts endpoints: <100ms on sample data
- Import operations: <30s for typical files
- Export operations: <10s for typical datasets

## Security Considerations
- No direct database access from UI layers
- Input validation on all endpoints
- SQL injection protection via parameterized queries
- CORS configuration for cross-origin requests

## Testing Strategy
- Unit tests for all business logic
- Integration tests for API endpoints
- Widget tests for Flutter components
- End-to-end tests for critical user flows
