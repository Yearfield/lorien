#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1

# Allow API_BASE_URL override
API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"

echo "Using API_BASE_URL=$API_BASE_URL"
export API_BASE_URL

# Run Streamlit from repo root
python -m streamlit run ui_streamlit/app.py
