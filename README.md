# Lorien (LongBow Core + VM Builder)

This repo contains a minimal decision-tree authoring system:

- **EngineLongBow** for bulk import/export via a frozen 8-column header (D0..D6, Notes)
- **Minimal API** (FastAPI): health, import, export, basic tree operations (roots/children GET, atomic PUT children)
- **VM Builder (Flutter)**: single screen to author the tree stepwise (pick a root → edit its children → drill down)
  - Import: In the left panel, choose Replace or Append, pick a CSV/XLSX in the LongBow 8-column header, and click Import. On success, roots refresh automatically.
  - Breadcrumbs: Click any crumb to jump to that ancestor's children.
  - Tap a child to drill into it and edit its children
  - Delete a root via the trash icon; deletion is cascading
  - **Note**: The database stores any number of children. The editor's 'Next <5' and v_missing_slots view treat '5' as a workflow helper (not a storage constraint).

## Quick Start

```bash
# Backend
export LORIEN_DB_PATH=/tmp/lorien.db
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

# Health
curl -sS http://127.0.0.1:8000/api/v1/health | jq

# Import CSV (LongBow)
curl -sS -F "file=@/path/to/data.csv;type=text/csv" "http://127.0.0.1:8000/api/v1/import?mode=replace" | jq

# Export CSV
curl -sS "http://127.0.0.1:8000/api/v1/tree/export?format=csv&limit=100" -o export.csv

# Flutter
cd ui_flutter && flutter pub get && flutter run -d linux
```

## API Surface

- `GET /api/v1/health`
- `POST /api/v1/import?mode=replace|append` (EngineLongBow)
- `GET /api/v1/tree/export?format=csv|xlsx`
- `GET /api/v1/tree/roots`
- `GET /api/v1/tree/children?parent_id=<id>`
- `PUT /api/v1/tree/children` — atomic replace children for a parent
- `DELETE /api/v1/tree/root?root_id=<id>` — delete root and its subtree
- `GET /api/v1/tree/node?node_id=<id>` — get node details for navigation

## Structure

- `api/` — FastAPI app, migrations, minimal routers
- `Engines/EngineLongBow/` — ingest/store/present
- `ui_flutter/` — VM Builder only