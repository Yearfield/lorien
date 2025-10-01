# Migration to LongBow VM Core

Scope
- Migrate from legacy routes/engines to EngineLongBow with the frozen 8-column contract.

Steps
- Export legacy tree to the canonical 8-column CSV: `D0..D6, Notes`
- Import via VM Core: `POST /api/v1/import?mode=replace&enforce_five=true`
- Verify: health probes, a few representative paths, and export round-trip (CSV/XLSX)

Decommission
- Remove non-LongBow engines/routes from clients and scripts
- Use EngineLongBow-only endpoints for preview/apply/export

Rules & alignment
- Option B: enforce ≤5 children per parent at the service layer; DB remains flexible via unique `(parent_id, slot)` 1..5
- Clients should not construct CSV/XLSX; always call API
