# Lorien Phase 6B QA Verification Guide

## Overview
This document provides manual verification steps for Lorien Phase 6B features. All automated tests should pass before proceeding with manual verification.

## Prerequisites
1. Start the development server:
   ```bash
   source .venv/bin/activate
   make dev
   ```

2. Verify server is running:
   ```bash
   curl http://127.0.0.1:8000/health
   curl http://127.0.0.1:8000/api/v1/health
   ```

## 1. Flags Namespace Verification

### 1.1 List Flags
```bash
# Get all flags (should return empty initially)
curl http://127.0.0.1:8000/api/v1/flags/

# Expected: []
```

### 1.2 Create Sample Data
First, create some test nodes and flags via the database:
```bash
sqlite3 .tmp/lorien.db << 'EOF'
-- Create a test root
INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (NULL, 0, 0, 'Test Root', 0);
INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (1, 1, 1, 'Test Child', 1);

-- Create test flags
INSERT INTO flags (label) VALUES ('Important');
INSERT INTO flags (label) VALUES ('Review');
EOF
```

### 1.3 Test Flag Operations
```bash
# List flags (should return 2 flags)
curl http://127.0.0.1:8000/api/v1/flags/

# Assign flag to node
curl -X POST http://127.0.0.1:8000/api/v1/flags/assign \
  -H "Content-Type: application/json" \
  -d '{"node_id": 2, "flag_id": 1, "cascade": false}'

# Expected: {"affected": 1, "node_ids": [2]}

# Try to assign again (should be idempotent)
curl -X POST http://127.0.0.1:8000/api/v1/flags/assign \
  -H "Content-Type: application/json" \
  -d '{"node_id": 2, "flag_id": 1, "cascade": false}'

# Expected: {"affected": 0, "node_ids": [2]}

# Get audit trail
curl http://127.0.0.1:8000/api/v1/flags/audit

# Expected: Array with 1 audit record

# Remove flag
curl -X POST http://127.0.0.1:8000/api/v1/flags/remove \
  -H "Content-Type: application/json" \
  -d '{"node_id": 2, "flag_id": 1, "cascade": false}'

# Expected: {"affected": 1, "node_ids": [2]}
```

## 2. Next Incomplete Parent Verification

### 2.1 Test with Complete Tree
```bash
# Create a complete tree (all slots filled)
curl -X POST http://127.0.0.1:8000/api/v1/tree/roots \
  -H "Content-Type: application/json" \
  -d '{"label": "Complete Root"}'

# Get next incomplete parent
curl http://127.0.0.1:8000/api/v1/tree/next-incomplete-parent

# Expected: 204 No Content (all parents complete)
```

### 2.2 Test with Incomplete Tree
```bash
# Create incomplete tree
sqlite3 .tmp/lorien.db << 'EOF'
INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (NULL, 0, 0, 'Incomplete Root', 0);
INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (4, 1, 1, 'Child 1', 0);
INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (4, 1, 3, 'Child 3', 0);
-- Missing slots 2 and 4
EOF

# Get next incomplete parent
curl http://127.0.0.1:8000/api/v1/tree/next-incomplete-parent

# Expected: {"parent_id": 4, "label": "Incomplete Root", "missing_slots": "2,4", "depth": 0}
```

## 3. Outcomes Validation Verification

### 3.1 Test Valid Outcomes
```bash
# Create a leaf node
sqlite3 .tmp/lorien.db << 'EOF'
INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (NULL, 0, 0, 'Outcomes Test', 0);
INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (5, 1, 1, 'Leaf Node', 1);
EOF

# Test valid triage update
curl -X PUT http://127.0.0.1:8000/triage/6 \
  -H "Content-Type: application/json" \
  -d '{"diagnostic_triage": "Monitor patient closely", "actions": "Check vital signs"}'

# Expected: 200 OK
```

### 3.2 Test Invalid Outcomes
```bash
# Test word count violation
curl -X PUT http://127.0.0.1:8000/triage/6 \
  -H "Content-Type: application/json" \
  -d '{"diagnostic_triage": "word1 word2 word3 word4 word5 word6 word7 word8", "actions": "action1"}'

# Expected: 422 with word_count error

# Test prohibited dosing token
curl -X PUT http://127.0.0.1:8000/triage/6 \
  -H "Content-Type: application/json" \
  -d '{"diagnostic_triage": "take 10 mg daily", "actions": "check vitals"}'

# Expected: 422 with prohibited_token error
```

## 4. CSV/XLSX Import Verification

### 4.1 Test Valid Import
Create a valid Excel file:
```python
import pandas as pd
from io import BytesIO

# Create valid data
data = {
    "Vital Measurement": ["Root 1", "Root 2"],
    "Node 1": ["Child 1", "Child 2"],
    "Node 2": ["", ""],
    "Node 3": ["", ""],
    "Node 4": ["", ""],
    "Node 5": ["", ""],
    "Diagnostic Triage": ["Triage 1", "Triage 2"],
    "Actions": ["Action 1", "Action 2"]
}
df = pd.DataFrame(data)
df.to_excel("valid_import.xlsx", index=False)
```

```bash
# Import valid Excel file
curl -X POST http://127.0.0.1:8000/api/v1/import/excel \
  -F "file=@valid_import.xlsx"

# Expected: 200 OK with job details
```

### 4.2 Test Invalid Import
Create an invalid Excel file:
```python
import pandas as pd

# Create invalid data (wrong header)
data = {
    "Wrong Header": ["Root 1", "Root 2"],
    "Node 1": ["Child 1", "Child 2"],
    "Node 2": ["", ""],
    "Node 3": ["", ""],
    "Node 4": ["", ""],
    "Node 5": ["", ""],
    "Diagnostic Triage": ["Triage 1", "Triage 2"],
    "Actions": ["Action 1", "Action 2"]
}
df = pd.DataFrame(data)
df.to_excel("invalid_import.xlsx", index=False)
```

```bash
# Import invalid Excel file
curl -X POST http://127.0.0.1:8000/api/v1/import/excel \
  -F "file=@invalid_import.xlsx"

# Expected: 422 with detailed error information
```

## 5. Red Flag Bulk Operations Verification

### 5.1 Test Bulk Attach
```bash
# Create red flags
sqlite3 .tmp/lorien.db << 'EOF'
INSERT INTO red_flags (name, description) VALUES ('Critical', 'High priority');
INSERT INTO red_flags (name, description) VALUES ('Review', 'Needs review');
EOF

# Bulk attach red flags
curl -X POST http://127.0.0.1:8000/red-flags/bulk-attach \
  -H "Content-Type: application/json" \
  -d '{"node_id": 2, "red_flag_ids": [1, 2]}'

# Expected: {"message": "Successfully attached 2 red flags", "attached_count": 2}
```

### 5.2 Test Bulk Detach
```bash
# Bulk detach red flags
curl -X POST http://127.0.0.1:8000/red-flags/bulk-detach \
  -H "Content-Type: application/json" \
  -d '{"node_id": 2, "red_flag_ids": [1]}'

# Expected: {"message": "Successfully detached 1 red flags", "detached_count": 1}
```

### 5.3 Test Audit Trail
```bash
# Get audit trail
curl http://127.0.0.1:8000/red-flags/audit

# Expected: Array of audit records with attach/detach actions
```

## 6. Performance Verification

### 6.1 Next Incomplete Parent Performance
```bash
# Time the next-incomplete-parent endpoint
time curl http://127.0.0.1:8000/api/v1/tree/next-incomplete-parent

# Expected: Response time < 100ms
```

### 6.2 Tree Stats Performance
```bash
# Time the stats endpoint
time curl http://127.0.0.1:8000/api/v1/tree/stats

# Expected: Response time < 100ms
```

## 7. Environment Configuration Verification

### 7.1 Test LLM Disabled
```bash
# Check LLM health
curl http://127.0.0.1:8000/api/v1/llm/health

# Expected: {"ok": false, "llm_enabled": false}
```

### 7.2 Test CORS Settings
```bash
# Check CORS headers from different origin
curl -H "Origin: http://localhost:3000" \
     http://127.0.0.1:8000/api/v1/health \
     -v

# Expected: CORS headers in response
```

## 8. Dual Mounting Verification

### 8.1 Test Root Path Endpoints
```bash
# Test health at root
curl http://127.0.0.1:8000/health

# Test tree stats at root
curl http://127.0.0.1:8000/tree/stats

# Test flags at root
curl http://127.0.0.1:8000/flags/
```

### 8.2 Test Versioned Path Endpoints
```bash
# Test health at versioned path
curl http://127.0.0.1:8000/api/v1/health

# Test tree stats at versioned path
curl http://127.0.0.1:8000/api/v1/tree/stats

# Test flags at versioned path
curl http://127.0.0.1:8000/api/v1/flags/
```

## 9. Acceptance Criteria Checklist

- [ ] `/api/v1/flags/` routes meet namespace + contract
- [ ] Cascade assign/remove returns accurate affected & node_ids
- [ ] Audit rows: one per effective change; retention ≤30d/≤50k
- [ ] `/api/v1/tree/next-incomplete-parent` returns correct shape in <100ms; 204 when none
- [ ] Outcomes normalization + caps + regex + dosing-token checks enforced
- [ ] LLM suggestions always normalized, ≤7 words, regex-compliant, no dosing tokens
- [ ] Roots creation preseeds exactly 5 children; stats consistent
- [ ] Export XLSX uses V1 header; conflicts endpoints respond within expectations
- [ ] Docs updated; version single-sourced

## 10. Automated Test Verification

Run all test suites:
```bash
# Run all tests
make test

# Run specific test suites
python -m pytest tests/api/test_outcomes_validation.py -v
python -m pytest tests/api/test_next_incomplete_parent.py -v
python -m pytest tests/api/test_flags_namespace.py -v
python -m pytest tests/contract/test_csv_contract.py -v

# Expected: All tests pass (exit code 0)
```

## 11. Cleanup

After verification:
```bash
# Clean up test files
rm -f valid_import.xlsx invalid_import.xlsx

# Stop development server
# Ctrl+C in the terminal running the server
```

## Notes

- All endpoints should work at both `/` and `/api/v1/` paths
- Error responses should be properly structured with `type` and `ctx` fields
- Performance targets: <100ms for tree operations
- All validation should be server-side enforced
- LLM functionality should be disabled by default
