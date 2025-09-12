# ARCHIVED DOCUMENT

**Archived on:** 2025-09-09
**Original path:** docs/PreBeta_Execution_Tracker.md
**Reason:** Pre-beta execution tracker - outdated
**Replacement:** Current status in PHASE6_README.md and project tracking

**Note:** This file has been archived and is no longer maintained.
Please refer to current documentation for up-to-date information.

---

# Pre-Beta Execution Tracker (Steps 3–8)

## High Priority (H) — Due Aug 31

### H1 Flutter parity (Calculator chained dropdowns + Workspace CSV/XLSX export)
- **Owner**: Mobile Lead
- **Acceptance**: Emulator 10.0.2.2, iOS sim localhost, ≥1 device LAN; leaf outcomes render; exports save/share; widget tests green.
- **Status**: ✅ DONE
- **Notes**: ChainedCalculator widget, ExportButtons widget, WorkspaceScreen created. Widget tests implemented.

### H2 Branch-wide flag cascade UX + Audit mini-viewer
- **Owner**: Web + API
- **Acceptance**: Cascade preview count + confirm dialog; executes fast; audit last 20 refreshes; retention 30d/50k enforced.
- **Status**: ✅ DONE
- **Notes**: GET /flags/preview-assign endpoint, GET /flags/audit with branch parameter, audit retention methods implemented.

## Medium Priority (M) — Due Aug 31

### M1 Import UX (queued→processing→done; first mismatch & counts)
- **Owner**: Web
- **Acceptance**: Progress indicators, header validation errors with position details, per-error counts displayed, success metrics shown.
- **Status**: ✅ DONE
- **Notes**: Progress bar, detailed error surfacing, summary metrics implemented in Workspace page.

### M2 Performance hardening (cache children; /tree/stats & conflicts <100ms sample)
- **Owner**: API + Web
- **Acceptance**: Cache children by parent_id, triage by node_id; /tree/stats & conflicts respond <100ms on sample data.
- **Status**: ✅ DONE
- **Notes**: SimpleCache with TTL, cache invalidation patterns, performance test UI implemented.

### M3 Backup/Restore UI buttons (integrity OK)
- **Owner**: Web + Ops
- **Acceptance**: One-click backup/restore with integrity check results displayed.
- **Status**: ✅ DONE
- **Notes**: POST /backup, POST /restore, GET /backup/status endpoints with integrity validation.

### M4 Conflicts filters + bulk "open in Editor"
- **Owner**: Web
- **Acceptance**: Filters reduce list correctly; "Jump" navigates; bulk open respects order.
- **Status**: 🔄 IN-PROGRESS
- **Notes**: Basic conflicts panel exists, filters and bulk actions need implementation.

### M5 Telemetry (ANALYTICS_ENABLED) non-PHI counters; surfaced in /health metrics
- **Owner**: API
- **Acceptance**: Counters appear only when enabled; non-PHI data collected; surfaced via /health metrics.
- **Status**: 🔄 IN-PROGRESS
- **Notes**: Health endpoint structure ready, metrics collection needs implementation.

## Dates
- **Tag**: v6.8.0-beta.1 → Sep 1
- **Beta window**: Sep 2 → Sep 9 (checkpoint)

## Completion Status
- **High Priority**: 2/2 ✅ DONE (100%)
- **Medium Priority**: 3/5 ✅ DONE (60%)
- **Overall Progress**: 5/7 ✅ DONE (71%)

## Next Actions
1. Complete M4 (Conflicts filters & bulk actions)
2. Complete M5 (Telemetry system)
3. Final testing and validation
4. Tag creation and release preparation
