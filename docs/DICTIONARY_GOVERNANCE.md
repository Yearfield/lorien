# Dictionary Governance System

## Overview

The Dictionary Governance System provides comprehensive management and approval workflows for medical dictionary terms in the Lorien application. It ensures data quality, consistency, and proper oversight through role-based approval processes, version control, and audit trails.

## Features

### 1. Approval Workflows
- **Multi-level approval**: Different term types require different approval levels
- **Auto-approval**: Editor-level terms can be auto-approved for trusted users
- **Medical review**: Critical terms require medical professional approval
- **Bulk operations**: Approve or reject multiple terms at once

### 2. Status Management
- **Draft**: Newly created terms pending review
- **Pending Approval**: Terms awaiting approval
- **Approved**: Terms that have been approved and are active
- **Rejected**: Terms that have been rejected with reasons
- **Deprecated**: Terms that are no longer recommended
- **Archived**: Terms that have been archived

### 3. Version Control
- **Automatic versioning**: Terms are versioned when status changes
- **Change tracking**: Complete audit trail of all modifications
- **Rollback capability**: Ability to revert to previous versions

### 4. Audit Trails
- **Complete change history**: Every action is logged with actor and timestamp
- **Before/after states**: Track exactly what changed
- **Reason tracking**: Capture why changes were made
- **Metadata support**: Additional context for changes

## Term Types and Workflows

### Vital Measurement Terms
- **Approval Level**: Medical Review Required
- **Auto-approve Editors**: No
- **Max Versions**: 5
- **Retention**: 730 days
- **Description**: Critical medical measurements that require expert validation

### Node Label Terms
- **Approval Level**: Editor
- **Auto-approve Editors**: Yes
- **Max Versions**: 10
- **Retention**: 365 days
- **Description**: General node labels that can be managed by editors

### Outcome Template Terms
- **Approval Level**: Medical Review Required
- **Auto-approve Editors**: No
- **Max Versions**: 3
- **Retention**: 1095 days
- **Description**: Clinical outcome templates requiring medical expertise

## API Endpoints

### Term Management
- `GET /dictionary/governance/terms` - List terms with filtering
- `POST /dictionary/governance/terms` - Create new term
- `PUT /dictionary/governance/terms/{term_id}` - Update existing term
- `GET /dictionary/governance/terms/pending` - Get pending approvals

### Approval Workflows
- `POST /dictionary/governance/terms/{term_id}/approve` - Approve a term
- `POST /dictionary/governance/terms/{term_id}/reject` - Reject a term
- `POST /dictionary/governance/terms/bulk-approve` - Bulk approve terms
- `POST /dictionary/governance/terms/bulk-reject` - Bulk reject terms

### Audit and History
- `GET /dictionary/governance/terms/{term_id}/changes` - Get change history
- `GET /dictionary/governance/stats` - Get governance statistics
- `GET /dictionary/governance/workflows` - Get workflow configurations

## Database Schema

### Core Tables

#### dictionary_terms_governance
Main table storing dictionary terms with governance metadata:
- `id`: Primary key
- `type`: Term type (vital_measurement, node_label, outcome_template)
- `term`: Display text
- `normalized`: Normalized version for searching
- `hints`: Additional context
- `status`: Current approval status
- `version`: Version number
- `created_by`: User who created the term
- `created_at`: Creation timestamp
- `updated_by`: User who last updated
- `updated_at`: Last update timestamp
- `approved_by`: User who approved
- `approved_at`: Approval timestamp
- `rejection_reason`: Reason for rejection
- `approval_level`: Required approval level
- `tags`: JSON array of tags
- `metadata`: JSON object for additional data

#### dictionary_workflows
Configuration for different term type workflows:
- `type`: Term type
- `approval_level`: Required approval level
- `requires_medical_review`: Boolean flag
- `auto_approve_editors`: Boolean flag
- `max_versions`: Maximum versions to keep
- `retention_days`: Days to retain data

#### dictionary_changes
Audit trail for all term changes:
- `id`: Primary key
- `term_id`: Reference to term
- `action`: Action performed (create, update, approve, reject, etc.)
- `actor`: User who performed the action
- `timestamp`: When the action occurred
- `before_state`: JSON of state before change
- `after_state`: JSON of state after change
- `reason`: Reason for the change
- `metadata`: Additional context

#### dictionary_approvals
Approval records:
- `id`: Primary key
- `term_id`: Reference to term
- `approver`: User who approved/rejected
- `status`: Approval status (approved/rejected)
- `reason`: Reason for decision
- `timestamp`: When decision was made

## Usage Examples

### Creating a Term
```python
from api.core.dictionary_governance import DictionaryGovernanceManager

# Create a new term
term_id = manager.create_term(
    type="vital_measurement",
    term="Blood Pressure",
    normalized="blood pressure",
    hints="Systolic and diastolic pressure measurement",
    created_by="medical_professional",
    tags=["cardiovascular", "vital_signs"],
    metadata={"unit": "mmHg", "normal_range": "90-140/60-90"}
)
```

### Approving a Term
```python
# Approve a pending term
success = manager.approve_term(
    term_id=123,
    approver="admin",
    reason="Medically accurate and clinically relevant"
)
```

### Bulk Operations
```python
# Bulk approve multiple terms
results = manager.bulk_approve(
    term_ids=[123, 124, 125],
    approver="admin",
    reason="Batch approval after medical review"
)
```

### Getting Change History
```python
# Get all changes for a term
changes = manager.get_term_changes(term_id=123)
for change in changes:
    print(f"{change.action} by {change.actor} at {change.timestamp}")
    if change.reason:
        print(f"Reason: {change.reason}")
```

## Security and Permissions

### Role-Based Access
- **System**: Can create and manage all terms
- **Admin**: Can approve/reject terms, manage workflows
- **Editor**: Can create and auto-approve editor-level terms
- **Medical Professional**: Can approve medical review terms
- **User**: Can create terms but requires approval

### Data Validation
- **Term validation**: Ensures terms meet format requirements
- **Normalization**: Consistent search and comparison
- **Duplicate prevention**: Prevents duplicate terms per type
- **Version control**: Maintains data integrity

## Monitoring and Analytics

### Governance Statistics
- Total terms by status and type
- Pending approvals by type
- Recent activity (last 7 days)
- Approval rates (last 30 days)
- Average time to approval

### Audit Reports
- Complete change history
- Approval patterns
- User activity
- Data quality metrics

## Integration

### With Existing Dictionary System
The governance system extends the existing dictionary functionality:
- Maintains backward compatibility
- Enhances existing API endpoints
- Adds governance layer on top of basic CRUD

### With RBAC System
- Integrates with user roles and permissions
- Respects approval level requirements
- Tracks actor information for audit trails

### With Audit System
- Logs all governance actions
- Integrates with enhanced audit system
- Provides comprehensive audit trails

## Configuration

### Environment Variables
- `DICTIONARY_GOVERNANCE_ENABLED`: Enable/disable governance features
- `DEFAULT_APPROVAL_LEVEL`: Default approval level for new terms
- `AUTO_APPROVE_EDITORS`: Whether to auto-approve editor actions

### Workflow Customization
Workflows can be customized by modifying the `dictionary_workflows` table:
- Change approval levels
- Modify auto-approval settings
- Adjust version limits
- Update retention periods

## Best Practices

### Term Creation
1. Use clear, descriptive terms
2. Provide helpful hints
3. Add relevant tags and metadata
4. Follow naming conventions

### Approval Process
1. Review terms thoroughly
2. Provide clear rejection reasons
3. Use bulk operations for efficiency
4. Monitor approval queues regularly

### Data Management
1. Regular cleanup of old versions
2. Archive deprecated terms
3. Monitor governance statistics
4. Review audit trails periodically

## Troubleshooting

### Common Issues
1. **Terms stuck in pending**: Check approval level requirements
2. **Auto-approval not working**: Verify user roles and workflow settings
3. **Version conflicts**: Check for concurrent modifications
4. **Audit trail missing**: Ensure proper logging configuration

### Debugging
1. Check governance statistics
2. Review change history
3. Verify workflow configuration
4. Check user permissions

## Future Enhancements

### Planned Features
1. **Notification system**: Alert approvers of pending terms
2. **Workflow automation**: Rule-based auto-approval
3. **Integration APIs**: Connect with external medical databases
4. **Advanced analytics**: Machine learning insights
5. **Mobile support**: Mobile approval interface

### Extensibility
The system is designed to be easily extensible:
- Add new term types
- Create custom workflows
- Implement additional approval levels
- Add new audit actions
