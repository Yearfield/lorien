# Lorien (LongBow Core + VM Builder)

This repo contains a minimal decision-tree authoring system:

- **EngineLongBow** for bulk import/export via a frozen 8-column header (D0..D6, Notes)
- **Minimal API** (FastAPI): health, import, export, basic tree operations (roots/children GET, atomic PUT children)
- **VM Builder (Flutter)**: single screen to author the tree stepwise (pick a root → edit its children → drill down)

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

## Structure

- `api/` — FastAPI app, migrations, minimal routers
- `Engines/EngineLongBow/` — ingest/store/present
- `ui_flutter/` — VM Builder only