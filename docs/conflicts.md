# Conflicts System Documentation

## Overview

The Conflicts system identifies and resolves data integrity issues in the decision tree, specifically focusing on **variant-sets conflicts** where duplicate parents have different 5-child label sets.

## Definition of Conflicts

A **conflict** exists when:

1. **Duplicate parents**: Multiple nodes have the same normalized label and same depth
2. **Exactly 5 children**: Each parent must have exactly 5 children (no more, no less)
3. **Variant sets**: The 5-child label sets differ across the duplicate parents

### Normalization Rules

Labels are normalized using:
- Unicode NFKC normalization
- Whitespace trimming and collapsing
- Case-insensitive comparison (casefold)

Examples:
- `"Chest Pain"` and `"chest pain"` are considered the same
- `"  Abdominal  Pain  "` and `"abdominal pain"` are considered the same

## API Endpoints

### GET /api/v1/tree/conflicts/conflicts

Lists conflicts with variant sets.

**Query Parameters:**
- `limit` (int, default=50): Maximum number of results
- `offset` (int, default=0): Pagination offset
- `only_exact_five` (bool, default=true): Only show parents with exactly 5 children
- `only_duplicate_parents` (bool, default=true): Only show parents with duplicates
- `require_variant_sets` (bool, default=true): Only show groups with different child sets

**Response Format:**
```json
{
  "items": [
    {
      "parent_id": 123,
      "label": "Hypertension",
      "depth": 0,
      "child_count": 5,
      "duplicate_parents": 2,
      "variant_sets": 2,
      "signatures": {
        "123": "headache|nausea|dizziness|chest pain|shortness of breath",
        "456": "headache|nausea|dizziness|chest pain|fatigue"
      }
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

**Guaranteed Non-Null Integer Fields:**
All integer fields in the response are guaranteed to be non-null:
- `parent_id`: Always an integer (0 if unknown)
- `depth`: Always an integer (0 if unknown)
- `child_count`: Always an integer (0 if unknown)
- `duplicate_parents`: Always an integer (0 if unknown)
- `variant_sets`: Always an integer (0 if unknown)
- `total`: Always an integer (0 if unknown)
- `limit`: Always an integer (0 if unknown)
- `offset`: Always an integer (0 if unknown)

### GET /api/v1/tree/conflicts/group

Loads conflict group data for resolution.

**Query Parameters:**
- `node_id` (int): Node ID to find group for
- `parent_id` (int): Parent ID (alternative to node_id)
- `label` (str): Label (required with parent_id)

**Response Format:**
```json
{
  "group": [
    {"id": 123},
    {"id": 456}
  ],
  "children": [
    {
      "child_id": 789,
      "from_id": 123,
      "slot": 1,
      "label": "Headache"
    }
  ],
  "summary": {
    "unique_children": 6,
    "total_children": 10
  }
}
```

### POST /api/v1/tree/conflicts/group/resolve

Resolves a conflict by choosing 5 labels to keep.

**Request Body:**
```json
{
  "keep_id": 123,
  "chosen_labels": ["Headache", "Nausea", "Dizziness", "Chest Pain", "Fatigue"]
}
```

**Response:**
```json
{
  "ok": true,
  "message": "Conflict resolved successfully"
}
```

## Architecture

### Core Engine (`api/core/conflicts_engine.py`)

Pure functions for conflict detection:
- `norm(s)`: Normalize strings for comparison
- `signature(child_labels)`: Create order-independent signatures
- `find_variant_set_conflicts(parents, children)`: Main detection logic
- `get_conflict_group_data(parents, children, target_id, target_label)`: Group data retrieval

### Service Layer (`api/services/conflicts_service.py`)

High-level service functions:
- `get_variant_conflicts(conn, limit, offset)`: Get conflicts using engine
- `get_conflict_group(conn, parent_id, label)`: Get group data using engine

### Repository Layer (`api/repositories/tree_repo.py`)

Database access functions:
- `list_parents_with_exact_five(conn, limit, offset)`: Get parents with exactly 5 children
- `list_children_for_parents(conn, parent_ids)`: Get children for specific parents

## Error Handling

### HTTP 422 (Validation Error)
- `must_choose_five`: Must select exactly 5 labels
- `duplicate_labels`: Labels must be unique
- `keep_id_not_in_group`: Invalid keep_id

### HTTP 409 (Conflict Error)
- Race condition during resolution
- Suggests reloading latest data

## Testing

### Backend Tests
- `tests/conflicts/test_variant_sets_detection.py`: Core engine tests
- `tests/conflicts/test_api_integration.py`: API integration tests
- `tests/conflicts/test_conflicts_identification.py`: Legacy detection tests

### Flutter Tests
- `ui_flutter/test/features/conflicts/conflicts_screen_resolve_test.dart`: UI tests
- `ui_flutter/test/features/conflicts/conflicts_group_toggle_test.dart`: Toggle tests
- `ui_flutter/test/features/conflicts/conflicts_progress_hud_test.dart`: Progress tests

## Performance

### Database Indexes
- `idx_nodes_parent_id`: For finding children by parent
- `idx_nodes_depth_label`: For grouping parents by depth and label
- `idx_nodes_parents`: Partial index for parent nodes only

### Optimization
- SQL pre-filters parents with exactly 5 children
- Engine processes only relevant data
- Signatures computed once per parent group

## Usage Examples

### Detecting Conflicts
```bash
# Get all conflicts
curl "http://127.0.0.1:8000/api/v1/tree/conflicts/conflicts"

# Get conflicts with specific parameters
curl "http://127.0.0.1:8000/api/v1/tree/conflicts/conflicts?limit=10&offset=0"
```

### Resolving Conflicts
```bash
# Load group for a specific node
curl "http://127.0.0.1:8000/api/v1/tree/conflicts/group?node_id=123"

# Resolve conflict
curl -X POST "http://127.0.0.1:8000/api/v1/tree/conflicts/group/resolve" \
  -H "Content-Type: application/json" \
  -d '{"keep_id": 123, "chosen_labels": ["A", "B", "C", "D", "E"]}'
```

## Migration from Legacy System

The new system is backward compatible:
- Legacy endpoints still work with `require_variant_sets=false`
- New engine is used by default for better accuracy
- UI automatically uses the new system

## Troubleshooting

### No Conflicts Found
- Check if there are actual duplicate parents in the database
- Verify parents have exactly 5 children
- Ensure child label sets are different

### Resolution Fails
- Verify exactly 5 unique labels are provided
- Check that keep_id exists in the conflict group
- Ensure no race conditions (try reloading)

### Performance Issues
- Check database indexes are created
- Consider reducing limit/offset for large datasets
- Monitor query execution times
