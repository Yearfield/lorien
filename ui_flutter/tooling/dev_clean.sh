#!/usr/bin/env bash
set -euo pipefail
pushd "$(dirname "$0")/.."

echo "🔄 Flutter clean…"
flutter clean || true
rm -rf build linux .dart_tool

echo "📦 Pub get…"
flutter pub get

echo "🧹 Kill stale desktop binaries…"
pkill -f decision_tree_manager || true

echo "▶️  Run (Linux desktop)…"
flutter run -d linux

popd
