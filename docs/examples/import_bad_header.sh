#!/usr/bin/env bash
BASE=${BASE:-http://127.0.0.1:8000/api/v1}
TMP=$(mktemp)
printf 'Bad,Header\n' > "$TMP"
curl -s -F "file=@${TMP};type=text/csv" "$BASE/import" | jq .
rm "$TMP"
