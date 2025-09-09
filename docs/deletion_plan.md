# Documentation Deletion Plan

| File/Section | Reason | Evidence | Action | Replacement |
| --- | --- | --- | --- | --- |
| `API.md` (root) | Outdated and duplicated API reference; misstates routes such as `POST /tree/roots`. | `rg -n "POST /tree/roots" docs/_archive/API.md` shows legacy verb while `api/routers/tree_stats_lists_router.py:8` defines `@router.get("/tree/roots")`. | Move to `docs/_archive/API.md` (done) | `docs/API.md` |
