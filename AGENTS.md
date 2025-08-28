#  AGENTS.md — Guiding Collaborative Assistants for “Lorien”

---

##  Purpose

This document is a living guide for development agents (e.g., Cursor) collaborating on **Lorien**, a cross-platform decision-tree app. It summarizes:

- Project architecture & domain fundamentals  
- Key pitfall areas and resolved bugs  
- Workflow patterns & dev UX  
- Technical constraints & guardrails  
- Future directions & beta test goals

Think of this as “what every new agent should know before starting.”

---

##  Project Overview

**Lorien** is a decision-tree tooling platform consisting of:

1. **SQLite Core**  
   - Enforces exactly 5 children per parent  
   - Root node represents a *Vital Measurement*  
   - Triggers maintain timestamps, depth & slot integrity  
   - Views and indexes support efficient queries

2. **FastAPI Backend**  
   - Exposes endpoints for tree navigation, triage, flags, and CSV export  
   - Includes WAL-safe backup/restore  
   - Serves health metadata: version, db state, feature flags (e.g., LLM)

3. **Flutter Desktop UI**  
   - Editor + Parent detail flow, state via Riverpod  
   - Accurate error handling and busy states  
   - CSV export and patch UI for children/triage  
   - No direct DB access—only communicates through API

4. **Streamlit Adapter (Dev-only)**  
   - Lightweight prototype/UIs used during initial prototyping  
   - Bridges Excel or CLI to API for batch imports

5. **Optional Local LLM Integration**  
   - Guidance-only suggestions for diagnostic triage and actions  
   - Feature-flagged off by default  
   - Strict input/output shape; safety guardrails mandatory

---

##  War Stories & Bug Patterns

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

---

##  Dev Workflow & Patterns

### Branching & Versioning
- Use `main` for active development  
- Tag only for public/releases (e.g., v1.0.0) not needed during internal iterations

### Cursor Collaboration
- Work in **small, atomic commits**, especially for UI and API coordination
- After each patch, run:
  - `flutter run -d linux --dart-define=API_BASE_URL=...`
  - Verify PrettyDioLogger shows correct endpoints & payloads

### Rapid Sanity Checks
Use CLI or curl to verify backend:
```bash
curl http://127.0.0.1:8000/tree/next-incomplete-parent | jq .
curl -i GET /tree/1/children

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
    Be explicit about assumptions when they’re necessary (e.g., assume only 1 root parent exists)
    Code references: always mention file names and approximate line numbers
    Use structured diff blocks for patches so they apply seamlessly
    Use PrettyDioLogger output in troubleshooting to pinpoint misaligned endpoints
    Respect safety and medical limitations; flag any requests that may breach guidance-only policy

### Summary Table
Layer	Key Details
Core	SQLite, 5-child enforce, schema
Backend	FastAPI, health + API contracts
Frontend	Flutter desktop, Riverpod, queues
Prototyping	Streamlit adapter
Extensions	Optional LLM suggestion flow