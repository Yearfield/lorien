#!/usr/bin/env bash
set -euo pipefail
# Delete Python bytecode & caches
find api Engines ui_flutter -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
find api Engines ui_flutter -type f -name "*.pyc" -delete 2>/dev/null || true
echo "Bytecode cleaned."
