# Documentation Audit Report

## File Status

| File | Status | Notes |
| --- | --- | --- |
| docs/API.md | Yellow | Updated health fields and export routes; still missing docs for conflicts, labels, calculator, VM builder. |
| docs/ENV.md | Green | Covers all active environment keys. |
| PHASE6_README.md | Green | Phase summary aligns with implementation. |
| Dev_Quickstart.md | Green | Setup steps match current commands. |
| README.md | Green | References versioned API paths. |
| CHANGELOG.md | Green | Recent changes recorded. |
| Tester_Onboarding.md | Red | File absent. |

## Endpoint Coverage (excerpt)

| Route | Documented | Example | Status codes |
| --- | --- | --- | --- |
| POST /import | No | – | – |
| GET /tree/export-json | Yes | Yes | 200 |
| GET /tree/stats | Yes | No | 200 |
| GET /tree/missing-slots-json | Yes | Yes | 200 |
| GET /tree/roots | Yes (corrected) | Yes | 200 |
| GET /tree/leaves | Yes | Yes | 200 |
| GET /tree/conflicts | No | – | – |
| GET /tree/labels | No | – | – |
| GET /tree/root-options | No | – | – |
| POST /tree/vm | No | – | – |

## Environment Keys

All documented keys are used in code: `LORIEN_DB_PATH`, `CORS_ALLOW_ALL`, `BASE_URL`, `LLM_ENABLED`, `LLM_PROVIDER`, `LLM_MODEL_PATH`, `ANALYTICS_ENABLED`.

## Workflow Coverage

A→F workflow is partially documented; conflict resolution and calculator flows remain undocumented.
