# Orphan Repair System

## Overview

The Orphan Repair System provides comprehensive detection and repair functionality for orphaned nodes in the Lorien decision tree database. It identifies various types of data integrity issues and provides safe, auditable repair options to maintain data quality.

## Features

### 1. Orphan Detection
- **Missing Parent**: Nodes that reference non-existent parent nodes
- **Invalid Depth**: Nodes with incorrect depth values (not parent_depth + 1)
- **Invalid Slot**: Nodes with slot numbers outside valid range (1-5) or null
- **Duplicate Slot**: Multiple children with the same slot number under one parent

### 2. Repair Actions
- **Delete Orphan**: Remove orphaned nodes (only if they have no children)
- **Reassign Parent**: Assign orphan to a new, valid parent
- **Fix Depth**: Correct depth to match parent depth + 1
- **Fix Slot**: Assign valid slot number (1-5)
- **Convert to Root**: Convert orphan to a root node
- **Merge with Sibling**: Combine orphan with a sibling node

### 3. Safety Features
- **Transaction Safety**: All repairs are wrapped in database transactions
- **Audit Trails**: Complete logging of all repair actions
- **Validation**: Pre-repair validation to prevent data corruption
- **Rollback**: Automatic rollback on repair failures
- **Impact Assessment**: Clear description of repair consequences

## Orphan Types

### Missing Parent Orphans
**Severity**: High  
**Description**: Nodes that reference a parent_id that doesn't exist in the database  
**Common Causes**: Data corruption, incomplete migrations, manual deletions  
**Suggested Actions**: Delete orphan, Convert to root

### Invalid Depth Orphans
**Severity**: Medium  
**Description**: Nodes where depth ≠ parent_depth + 1  
**Common Causes**: Manual data modification, migration errors  
**Suggested Actions**: Fix depth

### Invalid Slot Orphans
**Severity**: Medium  
**Description**: Nodes with slot numbers outside valid range (1-5) or null  
**Common Causes**: Data corruption, manual modification  
**Suggested Actions**: Fix slot

### Duplicate Slot Orphans
**Severity**: High  
**Description**: Multiple children with the same slot number under one parent  
**Common Causes**: Concurrent modifications, data corruption  
**Suggested Actions**: Fix slot, Merge with sibling

## API Endpoints

### Detection and Analysis
- `GET /admin/data-quality/orphan-repair/summary` - Get orphan summary statistics
- `GET /admin/data-quality/orphan-repair/orphans` - List orphaned nodes with repair suggestions
- `GET /admin/data-quality/orphan-repair/orphan-types` - Get orphan type descriptions
- `GET /admin/data-quality/orphan-repair/repair/actions` - Get available repair actions

### Repair Operations
- `POST /admin/data-quality/orphan-repair/repair/{orphan_id}` - Repair a specific orphan
- `POST /admin/data-quality/orphan-repair/repair/bulk` - Bulk repair multiple orphans
- `GET /admin/data-quality/orphan-repair/repair/history` - Get repair history

## Usage Examples

### Getting Orphan Summary
```python
import requests

# Get orphan summary
response = requests.get("/admin/data-quality/orphan-repair/summary")
summary = response.json()

print(f"Total orphans: {summary['total_orphans']}")
print(f"Status: {summary['status']}")
for orphan_type, count in summary['type_counts'].items():
    print(f"{orphan_type}: {count}")
```

### Listing Orphans
```python
# Get list of orphans
response = requests.get("/admin/data-quality/orphan-repair/orphans?limit=50")
orphans = response.json()

for orphan in orphans['items']:
    print(f"ID: {orphan['id']}, Type: {orphan['orphan_type']}")
    print(f"Label: {orphan['label']}, Severity: {orphan['severity']}")
    print(f"Suggested actions: {orphan['suggested_actions']}")
    print(f"Impact: {orphan['repair_impact']}")
```

### Repairing an Orphan
```python
# Delete an orphan (if it has no children)
repair_request = {
    "action": "delete_orphan",
    "reason": "Orphan has no children and is not needed"
}

response = requests.post(
    f"/admin/data-quality/orphan-repair/repair/{orphan_id}",
    json=repair_request
)

result = response.json()
if result['success']:
    print(f"Repair successful: {result['message']}")
else:
    print(f"Repair failed: {result['message']}")
```

### Fixing Depth
```python
# Fix depth of an orphan
repair_request = {
    "action": "fix_depth",
    "reason": "Correct depth to match parent"
}

response = requests.post(
    f"/admin/data-quality/orphan-repair/repair/{orphan_id}",
    json=repair_request
)
```

### Reassigning Parent
```python
# Reassign orphan to new parent
repair_request = {
    "action": "reassign_parent",
    "new_parent_id": 123,
    "reason": "Assign to correct parent"
}

response = requests.post(
    f"/admin/data-quality/orphan-repair/repair/{orphan_id}",
    json=repair_request
)
```

### Bulk Repair
```python
# Bulk repair multiple orphans
bulk_request = {
    "orphan_ids": [1, 2, 3, 4, 5],
    "action": "delete_orphan"
}

response = requests.post(
    "/admin/data-quality/orphan-repair/repair/bulk",
    json=bulk_request
)

results = response.json()
print(f"Successful: {len(results['results']['successful'])}")
print(f"Failed: {len(results['results']['failed'])}")
```

## Database Schema

### Core Tables

#### orphan_repair_audit
Audit table for all repair operations:
- `id`: Primary key
- `orphan_id`: Reference to the orphaned node
- `action`: Repair action performed
- `actor`: User who performed the repair
- `timestamp`: When the repair was performed
- `before_state`: JSON of node state before repair
- `after_state`: JSON of node state after repair
- `success`: Whether the repair was successful
- `message`: Repair result message
- `warnings`: Any warnings generated during repair

### Views

#### orphan_repair_summary
Summary statistics of repair operations by action type.

#### orphan_repair_recent
Most recent repair operations (last 100).

#### orphan_repair_by_actor
Repair statistics grouped by actor.

## Repair Actions Details

### Delete Orphan
**When to use**: Orphan has no children and is not needed  
**Safety**: High - only deletes if no children exist  
**Irreversible**: Yes  
**Impact**: Removes the orphaned node completely

### Reassign Parent
**When to use**: Valid parent exists for the orphan  
**Safety**: Medium - validates parent exists and prevents circular references  
**Irreversible**: No  
**Impact**: Changes parent_id and updates depth accordingly

### Fix Depth
**When to use**: Orphan has valid parent but wrong depth  
**Safety**: High - only corrects depth calculation  
**Irreversible**: No  
**Impact**: Updates depth to parent_depth + 1

### Fix Slot
**When to use**: Orphan has invalid or missing slot number  
**Safety**: Medium - validates slot range and availability  
**Irreversible**: No  
**Impact**: Assigns valid slot number (1-5)

### Convert to Root
**When to use**: Orphan should become a root node  
**Safety**: Medium - converts to root with depth 0, slot 0  
**Irreversible**: Yes  
**Impact**: Makes orphan a root node, removes parent relationship

### Merge with Sibling
**When to use**: Orphan duplicates another child's slot  
**Safety**: Medium - combines labels and deletes orphan  
**Irreversible**: Yes  
**Impact**: Merges labels and removes duplicate

## Safety and Validation

### Pre-Repair Validation
- **Parent existence**: Validates parent exists for reassignment
- **Circular references**: Prevents self-referencing
- **Slot availability**: Ensures slot is available before assignment
- **Child dependencies**: Prevents deletion of nodes with children

### Transaction Safety
- All repairs are wrapped in database transactions
- Automatic rollback on any error
- Atomic operations ensure data consistency

### Audit Trail
- Complete logging of all repair actions
- Before/after state capture
- Actor identification
- Success/failure tracking
- Warning capture

## Monitoring and Analytics

### Repair Statistics
- Total repairs by action type
- Success/failure rates
- Repair frequency by actor
- Most common orphan types

### Health Monitoring
- Orphan count trends
- Repair success rates
- Data quality improvements
- System stability metrics

## Best Practices

### Before Repair
1. **Backup database** before major repair operations
2. **Review orphan summary** to understand scope
3. **Test repairs** on a copy of the database
4. **Plan repair strategy** based on orphan types

### During Repair
1. **Start with low-risk repairs** (depth fixes, slot fixes)
2. **Use bulk operations** for efficiency
3. **Monitor repair results** and adjust strategy
4. **Document repair decisions** with reasons

### After Repair
1. **Verify data integrity** after repairs
2. **Review audit logs** for any issues
3. **Update data quality metrics**
4. **Plan preventive measures**

## Troubleshooting

### Common Issues

#### "Cannot delete orphan with children"
**Cause**: Trying to delete an orphan that has child nodes  
**Solution**: Either delete children first or use a different repair action

#### "No available slots for parent"
**Cause**: Parent already has 5 children (all slots filled)  
**Solution**: Use merge action or reassign to different parent

#### "Cannot assign node as its own parent"
**Cause**: Attempting circular reference  
**Solution**: Choose a different parent or repair action

#### "New parent does not exist"
**Cause**: Referenced parent_id doesn't exist  
**Solution**: Use valid parent_id or different repair action

### Debugging Steps
1. Check orphan summary for overall health
2. Review specific orphan details
3. Examine repair history for patterns
4. Validate parent-child relationships
5. Check for concurrent modifications

## Integration

### With Data Quality System
- Integrates with existing data quality monitoring
- Extends data quality summary with orphan counts
- Provides repair capabilities for detected issues

### With Audit System
- All repairs are logged in audit system
- Integrates with enhanced audit functionality
- Provides comprehensive audit trails

### With RBAC System
- Respects user permissions for repair operations
- Tracks actor information for audit trails
- Supports role-based repair access

## Future Enhancements

### Planned Features
1. **Automated repair suggestions** based on patterns
2. **Scheduled repair jobs** for maintenance
3. **Repair impact analysis** before execution
4. **Integration with monitoring systems**
5. **Machine learning** for orphan prevention

### Extensibility
The system is designed to be easily extensible:
- Add new orphan types
- Implement custom repair actions
- Create specialized validation rules
- Add new audit fields
- Integrate with external systems
