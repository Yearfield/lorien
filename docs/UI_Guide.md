# UI Guide (Flutter Shell)

Panes (NavigationRail)
- Home: dashboard with conflicts resolution, export tools, and submission placeholders
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

Home Dashboard
- Conflicts Card: scan for label conflicts across all depths, select union children (≤5), dry run preview, apply resolution
- Export Card: CSV/XLSX format selection, depth/root filters, native file picker save dialog, URL copy
- New Submission Card: placeholder for future bulk submission workflows

Conflicts Resolution
- Scan: `GET /api/v1/conflicts/scan` finds parents with same label but different child sets
- Detail Panel: shows union of all child labels as selectable chips (≤5 limit enforced)
- Dry Run: `POST /api/v1/conflicts/resolve` with `dry_run=true` shows changes without applying
- Apply: `POST /api/v1/conflicts/resolve` applies selected children to all matching parents
- Cross-depth: resolution applies to all parents with matching label regardless of depth

Export actions
- CSV/XLSX: `GET /api/v1/tree/export?format=csv|xlsx` with filters
- Native file picker: save dialog with proper file extensions
- URL copy: shareable export links with current filter settings

Notes
- Service-level ≤5 rule: the editor enforces ≤5 children; DB remains flexible via unique `(parent_id, slot)`
- Label-only conflicts: grouped by normalized label (case-insensitive, trimmed) across all depths
- Max depth enforcement: prevents adding children to D6 parents (would exceed D6 limit)
