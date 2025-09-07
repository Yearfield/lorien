#!/bin/bash
# Lorien API Development Server
# Starts API with temporary database for testing

set -e

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

# Ensure virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Virtual environment not activated. Run:"
    echo "source .venv/bin/activate"
    exit 1
fi

# Clean up any existing test database
if [ -f "$DB_PATH" ]; then
    echo "🧹 Cleaning up existing test database..."
    rm -f "$DB_PATH"
fi

# Set environment variables
export LORIEN_DB_PATH="$DB_PATH"
export ANALYTICS_ENABLED=false
export LLM_ENABLED=false

echo "📊 Starting uvicorn server..."
echo "API will be available at: http://$HOST:$PORT"
echo "Press Ctrl+C to stop"
echo ""

# Start the server
exec uvicorn api.app:app --host "$HOST" --port "$PORT" --reload
