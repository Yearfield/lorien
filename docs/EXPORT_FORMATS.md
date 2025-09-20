# Export Formats

## Canonical 8‑Column Header (SoT)
Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions

See: `docs/API_HEADER_SOT.md` for the single source of truth.

## CSV Export
- Endpoint: `GET /api/v1/tree/export`
- Streaming response; use HTTP client to write to file
- Content‑Type: `text/csv`
- Filename: `lorien_export.csv`

## Excel Export
- Endpoint: `GET /api/v1/tree/export.xlsx`
- Content‑Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Filename: `lorien_export.xlsx`

## Contract
- UI clients must not construct CSV/XLSX manually; always call the API
- Header is frozen and must match exactly

