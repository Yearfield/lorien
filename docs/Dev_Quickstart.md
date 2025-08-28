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

## Phase-6B Features

### Excel Export
- **Calculator Export**: `GET /calc/export.xlsx` - Full calculator data as Excel
- **Tree Export**: `GET /tree/export.xlsx` - Complete tree data as Excel
- **Headers**: Both exports use the frozen 8-column canonical header
- **Format**: Excel workbooks with proper MIME types and download headers

### New Vital Measurement Creation
- **Endpoint**: `POST /tree/roots` - Create root with 5 preseeded child slots
- **UI**: Workspace page includes form for creating new vital measurements
- **Validation**: Enforces exactly 5 children, optional initial labels
- **Deep-linking**: Successfully created roots link to Editor page

### Completeness Summary
- **Endpoint**: `GET /tree/stats` - Tree statistics and completeness metrics
- **Metrics**: Total nodes, roots, leaves, complete paths, incomplete parents
- **UI**: Workspace page shows summary cards and "Jump to Next Incomplete" button
- **Navigation**: Direct navigation to incomplete parents for editing

### LLM Integration (Feature-Flagged)
- **Endpoint**: `POST /llm/fill-triage-actions` - AI-powered triage suggestions
- **Control**: `LLM_ENABLED=true` environment variable required
- **Safety**: Guidance-only, no auto-apply, user must review and save
- **UI**: Outcomes page shows "Fill with LLM" button for leaf nodes
- **Context**: Uses full path context (root → node1..node5) for suggestions

### Calculator with Chained Dropdowns
- **UI**: Sequential dropdowns from root → node1..node5
- **Logic**: Changing higher-level selections resets deeper ones
- **Outcomes**: Displays triage data when leaf is reached
- **Export**: Single-path export for selected calculator path
- **Headers**: Maintains 8-column canonical CSV format

### Dual Mount Strategy
- **Root Paths**: All endpoints available at `/` (e.g., `/calc/export.xlsx`)
- **Versioned Paths**: Same endpoints at `/api/v1` (e.g., `/api/v1/calc/export.xlsx`)
- **Consistency**: Identical responses and behavior at both paths
- **Backward Compatibility**: Existing clients continue to work

### Dependencies
- **Excel Support**: `openpyxl` for Excel file generation
- **File Upload**: `python-multipart` for Excel import handling
- **Data Processing**: `pandas` for DataFrame operations
- **Installation**: `pip install openpyxl python-multipart`
