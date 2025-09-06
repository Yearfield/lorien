#!/bin/bash
# Lorien Phase-6E Backend Integration Smoke Test
# Tests all new endpoints and functionality

set -e  # Exit on any error

# Configuration
BASE_URL="${BASE_URL:-http://127.0.0.1:8000/api/v1}"
DB_PATH="${LORIEN_DB_PATH:-./.tmp/lorien.db}"

echo "🚀 Lorien Phase-6E Backend Integration Smoke Test"
echo "==============================================="
echo "Base URL: $BASE_URL"
echo "Database: $DB_PATH"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function to make requests and check status
test_endpoint() {
    local method=$1
    local url=$2
    local expected_status=${3:-200}
    local description=$4
    local data=$5

    echo -n "Testing $description... "

    if [ -n "$data" ]; then
        response=$(curl -s -X $method "$BASE_URL$url" \
            -H "Content-Type: application/json" \
            -d "$data" \
            -w "HTTPSTATUS:%{http_code}")
    else
        response=$(curl -s -X $method "$BASE_URL$url" \
            -w "HTTPSTATUS:%{http_code}")
    fi

    http_code=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo $response | sed -e 's/HTTPSTATUS:.*//g')

    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ $http_code${NC}"
        return 0
    else
        echo -e "${RED}✗ Expected $expected_status, got $http_code${NC}"
        echo "Response: $body"
        return 1
    fi
}

# Test health endpoints
echo "1. Health & Environment"
echo "-----------------------"
test_endpoint GET "/health" 200 "Health endpoint"
test_endpoint GET "/llm/health" 503 "LLM health (expected 503 when disabled)"

# Test tree editing APIs
echo ""
echo "2. Tree Editing APIs"
echo "--------------------"
test_endpoint GET "/tree/missing-slots?limit=5" 200 "Missing slots listing"
test_endpoint GET "/tree/next-incomplete-parent" 204 "Next incomplete parent (may be 204)"

# Create a test VM for further testing
echo ""
echo "3. VM Builder"
echo "-------------"
test_endpoint POST "/tree/roots" 200 "Create VM" '{"label": "Test VM"}'

# Extract root_id from response (simplified)
root_response=$(curl -s -X POST "$BASE_URL/tree/roots" \
    -H "Content-Type: application/json" \
    -d '{"label": "Test VM 2"}')

if echo "$root_response" | grep -q '"root_id":'; then
    root_id=$(echo "$root_response" | grep -o '"root_id":[0-9]*' | grep -o '[0-9]*')
    echo "Created test VM with ID: $root_id"

    # Test parent and children APIs
    test_endpoint GET "/tree/$root_id" 200 "Get parent info"
    test_endpoint GET "/tree/$root_id/children" 200 "Get children"

    # Test slot operations
    test_endpoint PUT "/tree/$root_id/slot/1" 200 "Upsert slot 1" '{"label": "Test Node 1"}'
    test_endpoint GET "/tree/$root_id/children" 200 "Verify children after upsert"

    # Test bulk children update
    test_endpoint POST "/tree/$root_id/children" 200 "Bulk update children" '{
        "children": [
            {"slot": 2, "label": "Test Node 2"},
            {"slot": 3, "label": "Test Node 3"}
        ]
    }'
fi

# Test dictionary APIs
echo ""
echo "4. Dictionary APIs"
echo "------------------"
test_endpoint GET "/dictionary?type=node_label&query=test&limit=5" 200 "Dictionary search"
test_endpoint POST "/dictionary" 201 "Create dictionary term" '{
    "type": "node_label",
    "term": "Test Term",
    "hints": "Test hint",
    "red_flag": false
}'

# Test dictionary import
echo "# Create a simple CSV file for testing"
echo "type,term,hints,red_flag" > /tmp/test_terms.csv
echo "node_label,Fever,Symptom,true" >> /tmp/test_terms.csv
echo "node_label,Cough,Respiratory symptom,false" >> /tmp/test_terms.csv

test_endpoint POST "/dictionary/import" 200 "Dictionary import CSV" ""

# Test conflicts inspector
echo ""
echo "5. Conflicts Inspector"
echo "----------------------"
test_endpoint GET "/tree/conflicts/duplicate-labels?limit=5" 200 "Duplicate labels"
test_endpoint GET "/tree/conflicts/orphans?limit=5" 200 "Orphans"
test_endpoint GET "/tree/conflicts/depth-anomalies?limit=5" 200 "Depth anomalies"

# Test materialization (if we have data)
echo ""
echo "6. Materialization"
echo "------------------"
test_endpoint POST "/tree/materialize" 200 "Materialize all" '{
    "scope": "all",
    "enforce_five": true,
    "prune_safe": true
}'
test_endpoint GET "/tree/materialize/runs?limit=5" 200 "Materialization history"

# Test sheet wizard
echo ""
echo "7. Sheet Wizard"
echo "---------------"
wizard_response=$(curl -s -X POST "$BASE_URL/tree/wizard/sheet" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Test Sheet",
        "vms": [{
            "label": "Test VM Wizard",
            "node1": ["Node 1.1", "Node 1.2"],
            "node2": ["Node 2.1"]
        }]
    }')

if echo "$wizard_response" | grep -q '"staged_id":'; then
    staged_id=$(echo "$wizard_response" | grep -o '"staged_id":"[^"]*"' | grep -o '"[^"]*"$' | tr -d '"')
    echo "Staged sheet with ID: $staged_id"

    test_endpoint POST "/tree/wizard/sheet/commit" 200 "Commit sheet" "{
        \"staged_id\": \"$staged_id\",
        \"enforce_five\": true,
        \"prune_safe\": true
    }"
fi

# Test export (if available)
echo ""
echo "8. Export Functionality"
echo "-----------------------"
test_endpoint GET "/calc/export" 200 "CSV export"
test_endpoint GET "/tree/export" 200 "Tree export"

echo ""
echo "🎉 Phase-6E Smoke Test Complete!"
echo ""
echo "Next steps:"
echo "- Run with BASE_URL=http://your-server:8000/api/v1"
echo "- Check database integrity: sqlite3 $DB_PATH 'PRAGMA integrity_check;'"
echo "- Review logs for performance metrics"
echo "- Run full test suite: pytest tests/api/ -v"