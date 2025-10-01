# UI Guide (Flutter Shell)

Panes (NavigationRail)
- Home: high-level welcome/status
- VM Builder: primary authoring pane (roots list, children editor, breadcrumbs)
- Outcomes: read-only outcomes view (future extensibility)
- Flags: filter and visualize red-flagged edges
- Settings: environment and diagnostics

VM Builder behaviors
- Import panel: pick CSV/XLSX, choose Append/Replace; uses `POST /api/v1/import` and shows status text
- Breadcrumbs: tap to jump to an ancestor’s children
- Children editor: add labels, drill into a child to edit its children
- Save: `PUT /api/v1/tree/children` atomically replaces children for the current parent
- Next Incomplete CTA: uses `GET /api/v1/tree/next-underfilled`; shows a snackbar for success/empty/error
- Busy overlay: long operations disable actions/buttons; navigation guarded during save/import
- Error banner/text: 409 slot conflicts and 422 validation surface as inline messages

Switching API targets
- Use Flutter define: `--dart-define=API_BASE=http://127.0.0.1:8000/api/v1`
- Default when unset: `http://127.0.0.1:8000/api/v1`

Export actions
- CSV: `GET /api/v1/tree/export` (download from the right header)
- XLSX: `GET /api/v1/tree/export.xlsx`

Notes
- Service-level ≤5 rule: the editor enforces ≤5 children; DB remains flexible via unique `(parent_id, slot)`
