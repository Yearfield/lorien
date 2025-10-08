#!/bin/bash
# Lorien API Development Server
# Starts API with temporary database for testing

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🚀 Starting Lorien API Development Server"
echo "=========================================="

# Configuration
DB_PATH="${LORIEN_DB_PATH:-/tmp/lorien_test.db}"
HOST="${API_HOST:-127.0.0.1}"
PORT="${API_PORT:-8000}"

echo "Database: $DB_PATH"
echo "Host: $HOST"
echo "Port: $PORT"
echo ""

# Ensure virtual environment is activated (auto-source .venv if present)
if [ -z "$VIRTUAL_ENV" ] && [ -f "$REPO_ROOT/.venv/bin/activate" ]; then
    echo "⚙️  Activating virtual environment at $REPO_ROOT/.venv"
    # shellcheck source=/dev/null
    source "$REPO_ROOT/.venv/bin/activate"
fi

if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Virtual environment not activated and .venv not found."
    echo "Run: python3 -m venv .venv && source .venv/bin/activate"
    exit 1
fi

# Clean up any existing test database
mkdir -p "$(dirname "$DB_PATH")"
if [ -f "$DB_PATH" ]; then
    echo "🧹 Removing existing test database..."
    rm -f "$DB_PATH"
fi
rm -f "${DB_PATH}-wal" "${DB_PATH}-shm" || true

# Set environment variables
export LORIEN_DB_PATH="$DB_PATH"
export ANALYTICS_ENABLED=false
export LLM_ENABLED=false

echo "📊 Starting uvicorn server..."
echo "API will be available at: http://$HOST:$PORT"
echo "Press Ctrl+C to stop"
echo ""

# Start the server
exec python -m uvicorn api.app:app --host "$HOST" --port "$PORT" --reload
