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
   - **NEW**: Subtree cloning with depth validation and capacity checking
   - **FIXED**: All endpoints now properly commit database transactions
   - **NEW**: Comprehensive conflict detection and resolution system via `/api/v1/conflicts/scan` and `/api/v1/conflicts/resolve`
   - **NEW**: Dictionary management endpoints for search, term details, merge operations, and statistics
   - **NEW**: Dictionary merge functionality with proper source term deletion and trigger management
   - **NEW**: Dictionary statistics endpoint with null-safe numeric field handling
   - **SECURITY**: Production-mandatory authentication, rate limiting, input validation, security headers

3. **Flutter Desktop UI**
   - Editor + Parent detail flow, state via Riverpod
   - Accurate error handling and busy states
   - CSV export and patch UI for children/triage
   - No direct DB access—only communicates through API
   - **NEW**: Parent rename/merge UI with edit buttons, selection dialogs, and cross-pane navigation
   - **NEW**: Subtree selection dialog for choosing which parent to clone when multiple exist
   - **NEW**: Partial subtree creation that builds as much of the tree as possible within depth limits
   - **FIXED**: UI now properly refreshes after delete operations
   - **FIXED**: Save functionality completely rebuilt - children now persist in UI after save
   - **NEW**: Comprehensive conflict resolution system with Home pane conflict detection and resolution
   - **NEW**: Dictionary management pane with search, term details, and merge functionality
   - **NEW**: Cross-pane synchronization - Dictionary pane updates when conflicts are resolved in Home pane
   - **NEW**: Dictionary statistics dialog with scrollable layout and proper error handling
   - **NEW**: Clickable conflict indicators in Dictionary pane for detailed conflict information

4. **Streamlit Adapter (Dev-only)**
   - Lightweight prototype/UIs used during initial prototyping
   - Bridges Excel or CLI to API for batch imports

5. **EngineWarhammer - Bayesian Disease Calculator**
   - Bayesian inference engine for disease probability calculations
   - Imports disease, symptom, and conditional probability data from CSV/Excel
   - Calculates P(Disease|Symptoms) using P(Disease), P(Symptom), and P(Symptom|Disease)
   - Integrated into Outcomes pane with engine selector architecture
   - **NEW**: Decision tree integration - sources symptoms directly from VM Builder
   - **NEW**: Hierarchical symptom selection with auto-calculation at 5 symptoms
   - **NEW**: Synonym management system for mapping decision tree to Warhammer symptoms
   - **NEW**: Symptom comparison tool to analyze coverage between systems
   - **NEW**: Confidence meters and detailed calculation explanations
   - **NEW**: "Scan VM Builder" button to refresh decision tree data (properly updates state)
   - Supports calculation history and data import/export workflows

6. **Optional Local LLM Integration**
   - Guidance-only suggestions for diagnostic triage and actions
   - Feature-flagged off by default
   - Strict input/output shape; safety guardrails mandatory

7. **Subtree Cloning System**
   - **Full Subtree Cloning**: Copies entire subtree structure with all descendants
   - **Partial Subtree Creation**: When full clone fails due to depth limits, creates as much as possible
   - **User Selection Dialog**: When multiple parents exist with same label, user chooses which to clone
   - **Depth Validation**: Enforces maximum depth of 6 (0-6, so 7 levels total)
   - **Capacity Checking**: Ensures destination parent has room for cloned children (max 5 per parent)
   - **Graceful Fallback**: Falls back to simple child if cloning fails for any reason

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

- **Missing database commits** in FastAPI endpoints
  → Issue: Child labels disappearing after save, delete operations not persisting
  → Root cause: Several endpoints (`add_child`, `create_root`, `put_children`, `delete_node`) missing `conn.commit()` calls
  → Solution: Added `await anyio.to_thread.run_sync(conn.commit)` after all INSERT/DELETE operations
  → Note: Database uses `isolation_level=None` (autocommit mode) but still requires explicit commits

- **Subtree cloning depth validation** inconsistencies
  → Issue: Clone operations failing with "cloned subtree would exceed depth limit" even when should work
  → Root cause: Validation logic had `dest_depth >= 5` instead of `dest_depth >= 6` (max depth is 6, not 5)
  → Solution: Updated validation to `dest_depth >= 6` to match actual depth limit
  → Note: Maximum depth is 6 (0-6, so 7 levels total)

- **EngineWarhammer calculation accuracy** discrepancies
  → Issue: App calculator producing different results than Excel workbook
  → Root cause: Fallback logic and zero priors for infectious diseases
  → Solution: Reverted to strict Warhammer_v3.py rules - no fallbacks, diseases only scored if all conditionals exist
  → Note: Calculator now matches Excel exactly for same input data

- **Decision tree symptom integration** complexity
  → Issue: Symptom dropdown not using decision tree structure as source
  → Root cause: Initially used static symptom list instead of API-sourced tree data
  → Solution: Implemented hierarchical navigation with `fetchDecisionTreeRoots()` and `fetchDecisionTreeChildren()`
  → Note: Added "Scan VM Builder" button to refresh tree data after changes

- **Synonym management** normalization confusion
  → Issue: Case-only differences (e.g., "chest pain" vs "Chest Pain") appearing as explicit synonyms
  → Root cause: Symptom comparison logic not properly excluding normalized matches
  → Solution: Enhanced comparison API to exclude normalized matches from "extra_in_warhammer" list
  → Note: Added validation to prevent case-only synonym creation

- **Flutter subtree selection** missing user choice
  → Issue: When multiple parents exist with same label, app automatically picked first one
  → Solution: Added subtree selection dialog in Flutter UI with parent ID and depth information
  → Implementation: Dialog shows all available parents, user can choose which subtree to clone

- **Partial subtree creation** for depth-limited scenarios
  → Issue: When full subtree can't be cloned due to depth limits, app fell back to simple child
  → Solution: Implemented partial subtree creation that builds as much of the tree as possible within depth limits
  → Logic: Calculates max allowed depth based on destination parent, recursively creates children up to limit
  → Fallback: If partial creation fails, falls back to simple child with appropriate user feedback

- **EngineWarhammer "Scan VM Builder" button** not updating decision tree data
  → Issue: Button called API but didn't update Flutter state with new decision tree roots
  → Root cause: `refreshDecisionTreeData()` method fetched data but didn't update state variables
  → Solution: Updated method to properly store fetched roots and update state with new data
  → Implementation: Now updates `decisionTreeRoots`, `currentTreeOptions`, and resets navigation to root level

- **VM Builder save functionality** - children disappearing after save
  → Issue: New children added to VM Builder would disappear from UI after pressing save button
  → Root cause: Overly complex save logic with multiple branching paths, subtree cloning, and dialog selection that could fail silently
  → Solution: **COMPLETELY REBUILT** save functionality from scratch using simple API approach
  → Implementation:
  - Removed all complex logic for subtree cloning, partial subtrees, and dialog selection
  - Now uses simple `POST /api/v1/tree/child` endpoint as documented in API.md
  - Clear logic: find new children → add them one by one → reload UI
  - Proper error handling with user-friendly messages for "parent already has 5 children"
  - Explicit `reloadChildren()` and `notifyListeners()` calls for UI updates
  → Result: Save functionality now works reliably and children persist in UI
  → Note: This demonstrates the importance of following API documentation and keeping implementations simple

- **Conflict resolution UI state management** - UI not reflecting database changes
  → Issue: Home pane showed conflicts as resolved in UI but data wasn't actually updated
  → Root cause: State not properly cleared after successful conflict resolution
  → Solution: Explicitly clear `selectedConflict`, `unionSelected`, and `unionOptions` after successful `apply()` call
  → Implementation: Added state refresh and UI feedback (SnackBar) after conflict resolution
  → Result: UI now accurately reflects database state after conflict resolution

- **Dictionary conflict detection** - incorrect conflict counts in Dictionary pane
  → Issue: Dictionary pane showed incorrect conflict counts because it was querying non-existent `conflicts` table
  → Root cause: Dictionary search was using outdated conflict detection method
  → Solution: Modified `DictionaryRepo` to use `/api/v1/conflicts/scan` and filter results for specific terms
  → Implementation: Updated `DictionarySearchNotifier` and `TermDetailsNotifier` to use new conflict detection method
  → Result: Dictionary pane now shows accurate conflict counts synchronized with Home pane

- **Dictionary merge source term deletion** - source terms not being deleted after merge
  → Issue: After successful merge operation, source dictionary term remained in database
  → Root cause: SQLite triggers were recreating the source term after deletion during node updates
  → Solution: Implemented proper trigger management with `PRAGMA recursive_triggers = OFF` and reordered operations
  → Implementation:
  - Drop triggers before merge, update nodes first, then delete source term
  - Recreate triggers after merge with fallback definitions for missing tables
  - Use `use_conflicts_table=False` when conflicts table doesn't exist
  → Result: Source terms are now properly deleted after merge operations

- **Dictionary UI refresh synchronization** - Dictionary pane not updating after operations
  → Issue: Dictionary pane didn't refresh after merge operations or conflict resolution
  → Root cause: Missing refresh calls and state management between different UI panes
  → Solution: Added cross-pane refresh calls and improved refresh logic
  → Implementation:
  - Added `refresh()` method to `DictionarySearchNotifier` with conflict count updates
  - Call `dictionarySearchProvider.notifier.refresh()` after merge operations
  - Call `dictionarySearchProvider.notifier.refresh()` after conflict resolution in Home pane
  → Result: All UI panes now stay synchronized after data changes

- **Dictionary statistics layout overflow** - yellow/black stripes in statistics dialog
  → Issue: Dictionary Statistics dialog showed layout overflow with yellow/black diagonal stripes
  → Root cause: Dialog content was too tall for available space, causing Flutter layout overflow
  → Solution: Made dialog scrollable with fixed dimensions and proper layout structure
  → Implementation:
  - Set fixed dialog dimensions (80% height, 60% width)
  - Wrapped content in `Expanded` widget with `SingleChildScrollView`
  - Removed `mainAxisSize: MainAxisSize.min` to allow proper expansion
  → Result: Statistics dialog now displays properly without layout overflow errors

- **Dictionary statistics null value errors** - type casting errors for null values
  → Issue: "type 'Null' is not a subtype of type 'num' in type cast" error in statistics dialog
  → Root cause: API returning null values for numeric fields, Flutter expecting non-null numbers
  → Solution: Added null-safe handling in both backend and frontend
  → Implementation:
  - Backend: Added explicit null checks and default values (0 or 0.0) for `avg_children` and `total_conflicts`
  - Frontend: Used null-aware operators (`?.`) and null-coalescing operators (`??`) in DTO parsing
  → Result: Statistics dialog now handles null values gracefully without type casting errors

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

# Test subtree cloning
curl -X POST http://127.0.0.1:8000/api/v1/tree/clone \
  -H "Content-Type: application/json" \
  -d '{"source_id": 555, "dest_parent_id": 2}' | jq .

# Test delete operations
curl -X DELETE http://127.0.0.1:8000/api/v1/tree/node/1519?dry_run=false | jq .

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
    **Database Commits**: Always add `conn.commit()` after INSERT/DELETE operations in FastAPI endpoints
    **Subtree Cloning**: Test both full clone and partial subtree creation scenarios
    **Error Handling**: Check actual error messages from API responses, not just error types
    **UI Refresh**: Ensure Flutter UI refreshes after database operations (delete, clone, etc.)
    **Keep It Simple**: When implementing features, follow API documentation exactly and avoid complex branching logic that can fail silently. Simple, direct implementations are more reliable and easier to debug than complex ones with multiple fallback paths.
    **Conflict Resolution**: Always clear UI state after successful operations to prevent stale data display
    **Cross-Pane Synchronization**: When data changes in one pane, refresh related panes to maintain consistency
    **Dictionary Management**: Use standardized conflict detection methods across all UI components
    **SQLite Triggers**: Be aware of trigger behavior during merge operations - disable triggers when needed
    **Null Safety**: Handle potential null values in both backend API responses and frontend DTO parsing
    **Layout Overflow**: Use scrollable containers for dialogs with potentially large content
    **State Management**: Explicitly clear state variables after successful operations to prevent UI inconsistencies

### Summary Table
Layer Key Details
Core SQLite, 5-child enforce, schema, depth 0-6, dictionary sync triggers
Backend FastAPI, health + API contracts + security middleware + subtree cloning + EngineWarhammer + conflict resolution + dictionary management
Frontend Flutter desktop, Riverpod, queues + subtree selection dialogs + Outcomes pane + conflict resolution + dictionary management
Prototyping Streamlit adapter
Extensions Optional LLM suggestion flow, EngineWarhammer Bayesian calculator with decision tree integration
Cloning Full/partial subtree cloning with depth validation and user selection
Security Authentication, rate limiting, input validation, security headers
EngineWarhammer Decision tree integration, synonym management, confidence visualization, auto-calculation
Conflict Resolution Home pane conflict detection, Dictionary pane conflict indicators, cross-pane synchronization
Dictionary Management Search, term details, merge operations, statistics, null-safe data handling

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
- EngineWarhammer Guide: ./docs/EngineWarhammer_Guide.md
