# Conflicts Resolution Guide

## Overview

The Conflicts Resolution system identifies and resolves inconsistencies in decision tree structures where parents with the same label have different child sets. This feature uses label-only grouping (ignoring depth) to find conflicts across the entire tree and provides tools to standardize child sets.

## Key Concepts

### Label-Only Grouping
- Conflicts are detected by grouping parents with identical normalized labels (case-insensitive, trimmed whitespace)
- Depth is ignored for conflict detection - parents at different depths with the same label are considered together
- Each conflict group appears once in the scan results, with all occurrences listed in the `parents` array

### Conflict Detection Criteria
A label is considered conflicted if either:
1. **Multiple occurrences with different child sets**: ≥2 parents have the same label but different children
2. **Union exceeds limit**: The union of all child labels across occurrences > 5

### Cross-Depth Resolution
- When resolving a conflict, the selected children are applied to ALL parents with that label across ALL depths
- This ensures consistency throughout the entire tree structure
- The `depth` parameter in the resolve payload is accepted but ignored for backward compatibility

## API Endpoints

### Scan Conflicts
```http
GET /api/v1/conflicts/scan
```

**Response Format:**
```json
[
  {
    "label": "hypertension",
    "occurrences": 3,
    "union_children": ["headache", "nausea", "vomiting", "chest pain", "myalgia", "dizziness"],
    "parents": [
      {"parent_id": 12, "depth": 1, "children": ["headache", "nausea", "vomiting"]},
      {"parent_id": 44, "depth": 2, "children": ["headache", "chest pain", "myalgia"]},
      {"parent_id": 67, "depth": 3, "children": ["dizziness", "nausea", "vomiting"]}
    ]
  }
]
```

### Resolve Conflicts
```http
POST /api/v1/conflicts/resolve
```

**Request Body:**
```json
{
  "label": "hypertension",
  "selected_children": ["headache", "nausea", "vomiting", "chest pain", "myalgia"],
  "dry_run": false
}
```

**Response Format:**
```json
{
  "updated_parents": 3,
  "children_per_parent": 5,
  "parents": [
    {
      "parent_id": 12,
      "removed": [],
      "added": ["chest pain", "myalgia"]
    },
    {
      "parent_id": 44,
      "removed": [],
      "added": ["nausea", "vomiting"]
    },
    {
      "parent_id": 67,
      "removed": ["dizziness"],
      "added": ["headache", "chest pain", "myalgia"]
    }
  ]
}
```

## Error Handling

### Too Many Children (422)
```json
{
  "detail": [
    {
      "loc": ["selected_children"],
      "msg": "too many children: 6>5",
      "type": "value_error.max_children"
    }
  ]
}
```

### Max Depth Exceeded (422)
```json
{
  "detail": [
    {
      "loc": ["label"],
      "msg": "parent at max depth; cannot add children beyond D6",
      "type": "value_error.max_depth"
    }
  ]
}
```

## UI Workflow

### 1. Scan for Conflicts
- Click "Scan" button in the Conflicts Card
- System queries all parents and groups by normalized label
- Results displayed as a list: `fever — 19 parents • union=10`

### 2. Select Conflict
- Tap on a conflict in the list to open detail panel
- Header shows: `Resolve: fever`
- Occurrences list shows each parent with depth: `D3 • Parent #12: headache, nausea, vomiting`

### 3. Choose Union Children
- Union chips display all possible child labels from all occurrences
- Select up to 5 children (≤5 limit enforced)
- UI prevents selection beyond the limit

### 4. Preview Changes (Dry Run)
- Click "Dry run" to see what changes would be made
- Shows which children would be added/removed for each parent
- No database changes are made

### 5. Apply Resolution
- Click "Apply" to commit the changes
- System applies selected children to all parents with matching label
- Conflicts list refreshes automatically after successful resolution

## Best Practices

### Before Resolving
1. **Review the union**: Ensure the selected children make medical/logical sense
2. **Check depth implications**: Consider how changes affect tree structure at different depths
3. **Use dry run**: Always preview changes before applying
4. **Validate selection**: Ensure ≤5 children and consider max depth constraints

### After Resolving
1. **Verify results**: Check that the conflict no longer appears in scan results
2. **Review tree structure**: Navigate through affected branches to ensure consistency
3. **Test workflows**: Ensure downstream processes work with the standardized structure

## Technical Details

### Database Operations
- Resolution is transactional - either all changes succeed or all are rolled back
- Children are deleted and re-inserted to maintain slot integrity
- Depth is calculated as `parent_depth + 1` for new children
- Slots are assigned sequentially (1, 2, 3, 4, 5)

### Performance Considerations
- Scan operation queries all nodes - performance scales with tree size
- Resolution affects all matching parents atomically
- Large trees may take several seconds for scan operations

### Constraints
- Maximum 5 children per parent (enforced)
- Maximum depth of D6 (children cannot be added to D6 parents)
- Label normalization: case-insensitive, trimmed whitespace
- Transactional integrity: all-or-nothing resolution

## Example Scenarios

### Scenario 1: Inconsistent Symptom Lists
**Problem**: Three "hypertension" parents have different symptom lists:
- Parent A (D1): headache, nausea, vomiting
- Parent B (D2): headache, chest pain, myalgia  
- Parent C (D3): dizziness, nausea, vomiting

**Resolution**: Select standardized symptoms: headache, nausea, vomiting, chest pain, myalgia
**Result**: All three parents now have identical child sets

### Scenario 2: Union Exceeds Limit
**Problem**: "fever" appears 5 times with union of 8 symptoms
**Resolution**: Choose 5 most important symptoms for standardization
**Result**: All "fever" parents standardized to the same 5 symptoms

### Scenario 3: Cross-Depth Consistency
**Problem**: "chest pain" at D2 and D4 have different follow-up questions
**Resolution**: Apply consistent follow-up questions across all depths
**Result**: Medical decision tree maintains consistency regardless of depth



