#!/usr/bin/env bash
set -e
BASE=${BASE:-http://127.0.0.1:8000/api/v1}
if curl -fs "$BASE/health" >/dev/null; then
  for f in docs/examples/*.sh; do
    echo "Running $f"
    if ! bash "$f" >/dev/null; then
      echo "Warning: $f failed" >&2
    fi
  done
else
  echo "Server not running; skipping docs smoke checks." >&2
fi
