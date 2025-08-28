# Dev Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Start API
uvicorn api.app:app --reload

# Streamlit (adapter) — note: API is versioned
API_BASE_URL=http://localhost:8000/api/v1 bash tools/scripts/run_streamlit.sh

# Flutter (desktop)
cd ui_flutter
flutter run -d linux  # or windows|macos
```

## UI Parity (Phase 6)

### Streamlit Adapter
- **Workspace**: Excel import via API, CSV export with header preview, Health widget
- **Conflicts**: Missing slots display, Next Incomplete jump, slot violation detection  
- **Outcomes**: Leaf-only triage grid, inline editing, search/filter

### Architecture Discipline
- Streamlit uses API client only (no direct DB/Sheets access)
- All endpoints mounted under `/api/v1`
- CSV header contract frozen at 8 columns exactly
- LLM OFF by default; no dosing/diagnosis suggestions

### LAN & CORS
Set `CORS_ALLOW_ALL=true` for LAN/mobile testing:
- Android emulator: `http://10.0.2.2:<port>`
- Device on LAN: `http://<your-lan-ip>:<port>`

### Health & DB Path
`GET /api/v1/health` includes `version` and `db_path`. Ensure `DB_PATH` env var is set.

## Streamlit Adapter
Adapter uses the API only. Excel import is supported via a simple upload widget that POSTs to `/api/v1/import/excel`.
