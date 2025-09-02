#!/usr/bin/env bash
set -euo pipefail

# Smoke test script for Lorien Phase-6 Beta sanity check
# Usage: ./tools/smoke_beta.sh [base_url]
# Default base_url: http://127.0.0.1:8000/api/v1

base="${1:-http://127.0.0.1:8000/api/v1}"

echo "🚀 Lorien Phase-6 Beta Smoke Test"
echo "Base URL: $base"
echo "=================================="

echo ""
echo "📊 Health Check:"
health_response=$(curl -fsS "$base/health" 2>/dev/null || echo "FAILED")
if [ "$health_response" = "FAILED" ]; then
    echo "❌ Health check failed - is the server running?"
    exit 1
fi

# Extract version and status
version=$(echo "$health_response" | jq -r '.version // "unknown"' 2>/dev/null || echo "unknown")
health_ok=$(echo "$health_response" | jq -r '.ok // false' 2>/dev/null || echo "false")

if [ "$health_ok" = "true" ]; then
    echo "✅ Health: OK (Version: $version)"
else
    echo "❌ Health: FAILED"
    exit 1
fi

echo ""
echo "📈 Stats Check:"
stats_response=$(curl -fsS "$base/tree/stats" 2>/dev/null || echo "FAILED")
if [ "$stats_response" = "FAILED" ]; then
    echo "❌ Stats check failed"
    exit 1
fi

nodes=$(echo "$stats_response" | jq -r '.nodes // 0' 2>/dev/null || echo "0")
leaves=$(echo "$stats_response" | jq -r '.leaves // 0' 2>/dev/null || echo "0")
echo "✅ Stats: $nodes nodes, $leaves leaves"

echo ""
echo "⏭️ Next Incomplete Parent:"
next_incomplete_response=$(curl -i -s "$base/tree/next-incomplete-parent" | head -n1)
status_code=$(echo "$next_incomplete_response" | awk '{print $2}')

if [ "$status_code" = "204" ]; then
    echo "✅ Next incomplete: None (204 No Content)"
elif [ "$status_code" = "200" ]; then
    echo "✅ Next incomplete: Found (200 OK)"
else
    echo "❌ Next incomplete: Unexpected status $status_code"
    exit 1
fi

echo ""
echo "📊 CSV Export Header:"
export_response=$(curl -fsS "$base/calc/export" 2>/dev/null | head -n1 || echo "FAILED")
if [ "$export_response" = "FAILED" ]; then
    echo "❌ Export check failed"
    exit 1
fi

# Check if header contains expected columns
if echo "$export_response" | grep -q "Vital Measurement"; then
    echo "✅ Export header: Valid 8-column format"
else
    echo "❌ Export header: Invalid format"
    exit 1
fi

echo ""
echo "🤖 LLM Health:"
llm_response=$(curl -i -s "$base/llm/health" | head -n1)
llm_status=$(echo "$llm_response" | awk '{print $2}')

if [ "$llm_status" = "200" ]; then
    echo "✅ LLM health: Ready (200 OK)"
elif [ "$llm_status" = "503" ]; then
    echo "✅ LLM health: Disabled (503 Service Unavailable)"
else
    echo "❌ LLM health: Unexpected status $llm_status"
    exit 1
fi

echo ""
echo "🎉 All checks passed!"
echo ""
echo "Next steps:"
echo "1. Run: pytest -q"
echo "2. If tests pass: git tag v6.8.0-beta.1"
echo "3. Push tag: git push origin v6.8.0-beta.1"
