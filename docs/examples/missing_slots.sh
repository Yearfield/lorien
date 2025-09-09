#!/usr/bin/env bash
BASE=${BASE:-http://127.0.0.1:8000/api/v1}
curl -s "$BASE/tree/missing-slots-json" | jq .
