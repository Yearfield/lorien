# Import Formats

## Canonical 8‑Column Header (SoT)
Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions

See: `docs/API_HEADER_SOT.md` for the single source of truth.

## CSV (.csv)
- Encoding: UTF‑8
- Header row: required and must match the canonical header exactly
- Empty intermediate levels allowed (system materializes as needed)
- Excess columns are rejected with 422

## Excel (.xlsx)
- First sheet only
- Header row must match the canonical header
- Cells beyond 32767 chars are rejected

## Validation Rules (high‑level)
- Exactly 5 slots per parent (Node 1..5 semantics)
- Leaf rows may include triage/actions; non‑leaf rows ignore those fields
- Duplicate labels per slot are rejected

## Example (CSV)
```
Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions
Blood Pressure,Systolic,High,,,,Hypertension risk,Monitor weekly
Blood Pressure,Systolic,Normal,,,,OK,
```

