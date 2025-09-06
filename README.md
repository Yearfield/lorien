# Lorien

Decision-tree tooling with:
- **SQLite core** (exactly 5 children per parent)
- **FastAPI** service
- **Flutter UI** (desktop & mobile)
- **Streamlit adapter** (thin, dev-focused)
- **Optional local LLM** (feature-flagged, guidance-only) to suggest *Diagnostic Triage* and *Actions*

## Quickstart
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.app:app --reload
API: http://localhost:8000/api/v1 (see /docs and /api/v1/health)

Flutter UI: see ui_flutter/README or ui_flutter/docs/Flutter_UI_Spec.md

Streamlit (dev): API_BASE_URL=http://localhost:8000/api/v1 bash tools/scripts/run_streamlit.sh
```

## Backend Development

### Common import error: FastAPI Depends not defined
If you see `NameError: name 'Depends' is not defined` on startup, ensure the router file includes:
```python
from fastapi import APIRouter, Depends
```
and any other FastAPI primitives used in that file (HTTPException, Query, Path, Body, status).

Run `ruff check .` and `pytest -q` to catch this before startup.

## Docs
- [Project Overview](docs/ProjectOverview.md)
- [Design Decisions](docs/DesignDecisions.md)
- [API Reference](docs/API.md)
- [Schema](docs/Schema.md)
- [Backup & Restore](docs/Backup_Restore.md)
- [LLM (Optional)](docs/LLM_README.md)
- [WSL Setup](docs/Setup_WSL.md)
- [Dev Quickstart](docs/Dev_Quickstart.md)
- [Release Notes](docs/ReleaseNotes_v6.7.md)
- [License & Safety](docs/Medical_Safety.md)

**Not a medical device; guidance-only. See [docs/Medical_Safety.md](docs/Medical_Safety.md).**

MkDocs config included; to build local site: `pip install mkdocs mkdocs-material && mkdocs serve`
