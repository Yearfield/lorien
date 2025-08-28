# Lorien Dev Quickstart

## Prerequisites
- Python 3.8+
- SQLite3
- Streamlit (for UI adapter)

## Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables (see below)
4. Run migrations: `python storage/migrate.py`
5. Start API: `python main.py`
6. Start Streamlit: `streamlit run ui_streamlit/app.py`

## Environment Variables
- `LORIEN_API_BASE`: API base URL (default: http://localhost:8000/api/v1)
- `DB_PATH`: Database file path
- `LLM_ENABLED`: Enable LLM features (default: false)
- `CORS_ALLOW_ALL`: Allow all origins for LAN access (default: false)

## LAN & CORS
Set `CORS_ALLOW_ALL=true` for LAN/mobile testing.

**Android Emulator base:** `http://10.0.2.2:<port>`  
**Device on LAN:** `http://<your-lan-ip>:<port>`

## Health & DB Path
`GET /api/v1/health` includes `version` and `db_path`. Ensure `DB_PATH` env var is set for correct resolution.

## Testing
Run tests with: `pytest tests/ -v`

## Architecture
- API-only: Streamlit adapter never touches database directly
- Versioned API: All endpoints mounted under `/api/v1`
- Invariant: Each parent must have exactly 5 children
