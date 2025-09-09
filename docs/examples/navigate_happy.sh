#!/usr/bin/env bash
BASE=${BASE:-http://127.0.0.1:8000/api/v1}
curl -s "$BASE/tree/navigate?root=1&n1=2&n2=3&n3=&n4=&n5=&q=" | jq .
