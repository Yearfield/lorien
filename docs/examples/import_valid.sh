#!/usr/bin/env bash
BASE=${BASE:-http://127.0.0.1:8000/api/v1}
FILE=${1:-tests/fixtures/perfect_5_children.xlsx}
curl -s -F "file=@${FILE}" "$BASE/import" | jq .
