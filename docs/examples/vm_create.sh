#!/usr/bin/env bash
BASE=${BASE:-http://127.0.0.1:8000/api/v1}
curl -s -X POST "$BASE/tree/vm" \
  -H 'Content-Type: application/json' \
  -d '{"label":"Example VM"}' | jq .
