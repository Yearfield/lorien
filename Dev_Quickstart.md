# Developer Quickstart

Prerequisites
- Python 3.10+
- Flutter 3.22+ with desktop target (e.g., Linux)
- jq (for curl samples)

Environment
- `LORIEN_DB_PATH`: SQLite DB file path for API (e.g., `/tmp/lorien.db`)
- Flutter uses `--dart-define=API_BASE` for the API base URL (e.g., `http://127.0.0.1:8000/api/v1`)

Start the API (VM Core)
```bash
export LORIEN_DB_PATH=/tmp/lorien.db
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.app:app --reload --host 127.0.0.1 --port 8000
```

Start the Flutter app
```bash
cd ui_flutter
flutter pub get
flutter run -d linux --dart-define=API_BASE=http://127.0.0.1:8000/api/v1
```

Smoke checklist
- Health probes: `GET /api/v1/live`, `/api/v1/ready`, `/api/v1/health` show expected JSON
- Import preview: `POST /api/v1/import/preview` with a LongBow CSV/XLSX returns `errors[]` for over‑five within file
- Import apply: `POST /api/v1/import?mode=replace&enforce_five=true` rolls back and returns 422 when >5 children per parent
- VM Builder pane loads; can add a root, edit children, drill into nodes
- “Next Incomplete” CTA navigates using `GET /api/v1/tree/next-underfilled` and shows snackbars for 204/errors
- Busy overlay and error banner: long operations disable actions; save/import failures show error text

More details
- Architecture: ./docs/Architecture.md
- API reference: ./docs/API.md
