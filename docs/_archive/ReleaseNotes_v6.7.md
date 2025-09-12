# ARCHIVED DOCUMENT

**Archived on:** 2025-09-09
**Original path:** docs/ReleaseNotes_v6.7.md
**Reason:** Old release notes - superseded by v6.8.0-beta.1
**Replacement:** docs/Release_Notes_v6.8.0-beta.1.md

**Note:** This file has been archived and is no longer maintained.
Please refer to current documentation for up-to-date information.

---

# Release Notes v6.7

- Phase 5.6: Golden E2E, header guard, concurrency, performance smoke.
- Phase 5.7: Streamlit adapter (API-only), dev config (poll watcher).
- Phase 5.8: Canonical DB placement, Python CLI for backup/restore, WAL-safe scripts.
- Phase 5.9: Optional local LLM for triage/actions (feature-flagged; JSON-only; safety gate).
- Phase 5.10: Docs & versioning. Health exposes version and DB info. README overhaul.

**Upgrade notes:**
- DB path is env-first (`DB_PATH`); defaults to OS app-data dir.
- Restore script removes WAL/SHM and uses logical `.restore`.
- LLM remains OFF unless explicitly enabled.
