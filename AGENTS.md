# AGENTS.md — Guiding Collaborative Assistants for “Lorien”

---

## Purpose

This document is a living guide for development agents (e.g., Cursor) collaborating on **Lorien**, a cross-platform decision-tree app. It summarizes:

- Project architecture & domain fundamentals
- Key pitfall areas and resolved bugs
- Workflow patterns & dev UX
- Technical constraints & guardrails
- Future directions & beta test goals

Think of this as “what every new agent should know before starting.”

---

## Project Overview

**Lorien** is a decision-tree tooling platform consisting of:

1. **SQLite Core**
   - Enforces exactly 5 children per parent
   - Root node represents a *Vital Measurement*
   - Triggers maintain timestamps, depth & slot integrity
   - Views and indexes support efficient queries

2. **FastAPI Backend**
   - Fully async endpoints for tree navigation, triage, flags, CSV export, and parent management
   - All blocking SQLite operations wrapped with `anyio.to_thread()` for non-blocking I/O
   - Async database connection management with proper transaction handling
   - Includes WAL-safe backup/restore
   - Serves health metadata: version, db state, feature flags (e.g., LLM)
   - **NEW**: Parent rename/merge endpoints with automatic duplicate detection and children selection
   - **SECURITY**: Production-mandatory authentication, rate limiting, input validation, security headers

3. **Flutter Desktop UI**
   - Editor + Parent detail flow, state via Riverpod
   - Accurate error handling and busy states
   - CSV export and patch UI for children/triage
   - No direct DB access—only communicates through API
   - **NEW**: Parent rename/merge UI with edit buttons, selection dialogs, and cross-pane navigation

4. **Streamlit Adapter (Dev-only)**
   - Lightweight prototype/UIs used during initial prototyping
   - Bridges Excel or CLI to API for batch imports

5. **Optional Local LLM Integration**
   - Guidance-only suggestions for diagnostic triage and actions
   - Feature-flagged off by default
   - Strict input/output shape; safety guardrails mandatory

---

## War Stories & Bug Patterns

Cursor should know the landscape:

- **Freezed/JSON codegen** needed to generate DTO parts
  → Many build errors due to missing `*.freezed.dart` and wrong imports

- **Riverpod types missing** (ConsumerWidget, WidgetRef)
  → Solution: add `flutter_riverpod` import and wrap root in `ProviderScope`

- **Dio v5 error field removal**
  → Old code used `error.error = …`; replaced with throwing new `DioException(..., error: msg)`

- **CardTheme mismatch** (deprecated in newer Flutter)
  → Switched to `CardThemeData(...)`

- **API versioning** now standardized under `/api/v1`
  → All endpoints mounted under versioned prefix; clients updated accordingly

- **JSON shape mismatches** with next-incomplete and children endpoints
  → DTO adjusted to accept both list and string; repo hardened to fallback shapes

- **"Tap to Retry" UI** after missing data
  → Seeded Vital Measurement and children via CLI; client adjusted to parse actual API shape

- **SQLite transaction errors** in merge operations
  → Issue: `cannot start a transaction within a transaction` when using explicit BEGIN/COMMIT
  → Solution: Remove explicit transaction handling, use SQLite's auto-commit mode with individual commits

- **404 errors during merge** with stale UI state
  → Issue: Flutter app trying to merge already-deleted parents from previous operations
  → Solution: Add state refresh after operations, better error handling, loading states to prevent multiple attempts

- **Missing navigation callbacks** between Flutter panes
  → Issue: Conflicts screen couldn't navigate to VM Builder with specific parent ID
  → Solution: Implement callback system with Riverpod state management for cross-pane navigation

- **Security vulnerabilities** in production deployments
  → Issue: No authentication, rate limiting, or input validation in production
  → Solution: Implemented comprehensive security middleware stack with environment-based configuration

---

## Dev Workflow & Patterns

### Branching & Versioning

- Use `main` for active development
- Tag only for public/releases (e.g., v1.0.0) not needed during internal iterations

### Cursor Collaboration

- Work in **small, atomic commits**, especially for UI and API coordination
- After each patch, run:
  - `flutter run -d linux --dart-define=API_BASE_URL=...`
  - Verify PrettyDioLogger shows correct endpoints & payloads
- **Security Testing**: Test authentication and security features in both development and production modes
- **Environment Configuration**: Always test with both `ENVIRONMENT=development` and `ENVIRONMENT=production`

### Rapid Sanity Checks

Use CLI or curl to verify backend:

```bash
# Development mode (no authentication required)
curl http://127.0.0.1:8000/api/v1/tree/next-incomplete-parent | jq .
curl -i GET http://127.0.0.1:8000/api/v1/tree/1/children

# Production mode (authentication required for write operations)
curl -H "Authorization: Bearer $AUTH_TOKEN" \
  http://127.0.0.1:8000/api/v1/tree/next-incomplete-parent | jq .
curl -H "Authorization: Bearer $AUTH_TOKEN" \
  -i POST http://127.0.0.1:8000/api/v1/tree/roots \
  -H "Content-Type: application/json" \
  -d '{"label": "Test Root"}'

Codegen

Always run flutter pub run build_runner build --delete-conflicting-outputs after DTO changes

Re-run flutter analyze, then r/r in app to refresh UI

Live Project Roadmap

Beta Readiness

Full CRUD flows: parent → children → triage → export

Backup/Restore stability

Multi-device setups and mobile support

LLM Integration (Optional)

Add /llm/fill-triage-actions; ensure JSON-only, style toggles, apply flag, leaf-only guard

Efficiency: max_tokens, char clamps, concurrency cap

Documentation & Release Artifacts

API.md, Schema.md, Backup_Restore.md, LLM_README.md, Dev Quickstart, Release Notes

Light doc tests ensure integrity (JSON blocks, canonical headers, version sync)

Beta Testing & Packaging

Make Flutter builds for Linux, Windows, macOS

CI snapshot for dev → test → release

Guide testers on CLI-based Excel import workflow

### Cursor Best Practices & Tips
    Be explicit about assumptions when they're necessary (e.g., assume only 1 root parent exists)
    Code references: always mention file names and approximate line numbers
    Use structured diff blocks for patches so they apply seamlessly
    Use PrettyDioLogger output in troubleshooting to pinpoint misaligned endpoints
    Respect safety and medical limitations; flag any requests that may breach guidance-only policy
    **Security**: Always test authentication and security features when making API changes
    **Environment**: Test changes in both development and production security configurations
    **Documentation**: Update security documentation when adding new endpoints or changing authentication requirements

### Summary Table
Layer Key Details
Core SQLite, 5-child enforce, schema
Backend FastAPI, health + API contracts + security middleware
Frontend Flutter desktop, Riverpod, queues
Prototyping Streamlit adapter
Extensions Optional LLM suggestion flow
Security Authentication, rate limiting, input validation, security headers

See also
- README: ./README.md
- Dev Quickstart: ./Dev_Quickstart.md
- Architecture: ./docs/Architecture.md
- API: ./docs/API.md
- Security Guide: ./docs/Security.md
- Security Deployment: ./docs/Security_Deployment.md
- UI Guide: ./docs/UI_Guide.md
- Runbook: ./docs/Runbook.md
- Migration: ./docs/Migration.md
