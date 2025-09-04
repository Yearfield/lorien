#!/usr/bin/env bash
set -euo pipefail

# Default values
API_PORT=8000
API_HOST=127.0.0.1
API_PATH="api.app:app"
FLUTTER_DEVICE="linux"   # Change to chrome, emulator-5554, etc. if needed

echo "🔌 Starting Lorien API on http://$API_HOST:$API_PORT ..."
(
  cd "$(dirname "$0")"
  source .venv/bin/activate
  uvicorn $API_PATH --reload --host $API_HOST --port $API_PORT
) &

API_PID=$!
sleep 2

echo "📱 Starting Lorien Flutter app (device: $FLUTTER_DEVICE) ..."
(
  cd ui_flutter
  flutter pub get
  flutter run -d $FLUTTER_DEVICE
)

# Cleanup
kill $API_PID || true
