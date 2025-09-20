# Release Process

## Overview
This process covers preparing and validating a release across API and UI.

## Steps
1. Changelog: update `CHANGELOG.md` and `ui_flutter/CHANGELOG.md`
2. Tests: run API + Flutter tests; verify coverage thresholds
3. Contracts: run CSV header freeze and health semantics tests
4. Docs: update `docs/API.md` (if endpoints changed) and SoT documents
5. Build: produce Flutter desktop builds (Linux/Windows/macOS)
6. Manual QA: follow Beta Acceptance Checklist
7. Tag and publish release notes (GitHub Releases), link artifacts

## Checklists
- UI: `ui_flutter/docs/RELEASE_CHECKLIST.md`
- Beta Acceptance: `docs/Beta_Acceptance_Checklist.md`

## Post‑release
- Monitor health endpoints and metrics
- Collect feedback; triage into next milestone

