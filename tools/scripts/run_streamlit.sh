#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1

# Change to repo root (directory containing this script is tools/scripts/)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

# Ensure the repo root is on PYTHONPATH so 'ui_streamlit' resolves reliably.
export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"

# Default API base (can be overridden by env); aligned with versioned mount.
export API_BASE_URL="${API_BASE_URL:-http://localhost:8000/api/v1}"

echo "Starting Streamlit with PYTHONPATH=$PYTHONPATH"
echo "API_BASE_URL=$API_BASE_URL"
exec streamlit run ui_streamlit/app.py
