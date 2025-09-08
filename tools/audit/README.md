# Wiring Audit

This suite inspects FastAPI routes, validates **dual-mount** coverage, scans Flutter for API usages and named routes, and produces `AUDIT_REPORT.md`.

## Quick run

```bash
# From repo root
python3 tools/audit/gen_audit_report.py
# Open the report
${EDITOR:-vim} AUDIT_REPORT.md
```

## What it checks

- Enumerates backend routes and methods
- Verifies dual-mount pairs: every `/...` also exists at `/api/v1/...` (and vice versa)
- Greps Flutter for `Uri.parse('...')` / raw paths / `pushNamed('/route')`
- Runs `pytest -q` and embeds the summary

## CI/Local guard

Run as a test suite:

```bash
pytest -q tests/test_dual_mount_contract.py tests/test_core_endpoints_exist.py
```

## Smoke commands

```bash
# 1) Generate the markdown report
python3 tools/audit/gen_audit_report.py

# 2) View dual-mount diffs (JSON)
python3 tools/audit/check_dual_mount.py

# 3) Just list routes (JSON)
python3 tools/audit/wiring_audit.py

# 4) See Flutter API usage (JSON)
python3 tools/audit/scan_dart_api_calls.py

# 5) Run the two audit tests
pytest -q tests/test_dual_mount_contract.py tests/test_core_endpoints_exist.py
```

## Definition of Done (binary)

`python3 tools/audit/gen_audit_report.py` writes `AUDIT_REPORT.md` containing:

- All FastAPI routes/methods
- Dual-mount status per base path (OK / MISSING) with examples
- All Flutter API URLs and pushNamed routes discovered
- Pytest summary line(s)

`tests/test_dual_mount_contract.py` passes (no missing dual-mount pairs).

`tests/test_core_endpoints_exist.py` passes (all required A→F + extended endpoints exist with proper methods).

No existing app code paths are modified; this is a non-intrusive audit layer you can run any time.
