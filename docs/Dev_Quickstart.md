# Dev Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Start API
uvicorn api.app:app --reload

# Streamlit (adapter)
API_BASE_URL=http://localhost:8000 bash tools/scripts/run_streamlit.sh

# Flutter (desktop)
cd ui_flutter
flutter run -d linux  # or windows|macos
```
