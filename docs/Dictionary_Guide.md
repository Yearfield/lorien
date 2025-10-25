# Dictionary System Guide

## Overview

The Dictionary system provides comprehensive medical term management with bidirectional synchronization to the decision tree structure. It serves as the universal symptoms list that connects the VM Builder, both engines (EngineWarhammer and EngineShortBow), and the Dictionary pane.

## Architecture

### Database Schema

The dictionary system uses the `medical_dictionary` table with the following structure:

```sql
CREATE TABLE medical_dictionary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT NOT NULL UNIQUE,
    definition TEXT,
    synonyms TEXT, -- JSON array as text
    is_red_flag INTEGER NOT NULL DEFAULT 0,
    avg_children_count INTEGER DEFAULT 0,
    conflicts_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
```

### Synchronization Triggers

The system maintains bidirectional synchronization through SQLite triggers:

- **`tr_sync_dictionary_on_node_change`**: Updates dictionary when node labels change
- **`tr_sync_dictionary_on_node_insert`**: Adds new terms to dictionary when nodes are inserted
- **`tr_sync_dictionary_on_node_delete`**: Updates dictionary when nodes are deleted
- **`tr_sync_nodes_on_dictionary_change`**: Updates node labels when dictionary terms change
- **`tr_sync_red_flags_on_dictionary_change`**: Handles red flag synchronization
- **`tr_medical_dictionary_touch_on_update`**: Updates timestamp on dictionary changes

## API Endpoints

### Search & Browse

**GET** `/api/v1/dictionary/search`

- Search medical terms with case-insensitive partial matching
- Parameters: `q` (query), `limit` (1-200), `offset` (≥0)
- Returns paginated results with term details

**GET** `/api/v1/dictionary/{term_id}`

- Get detailed information about a specific dictionary term
- Returns complete term object with relationships

**GET** `/api/v1/dictionary/term/{term_name}`

- Get dictionary term by name (case-insensitive)

### Statistics

**GET** `/api/v1/dictionary/stats`

- Get overall dictionary statistics (all terms in database)

**GET** `/api/v1/dictionary/stats/tree`

- Get statistics specifically for decision tree terms
- Only counts terms that exist in both `medical_dictionary` and `nodes` tables
- Provides accurate completion rates for decision tree terms

### Term Management

**PUT** `/api/v1/dictionary/{term_id}`

- Update dictionary term definition, synonyms, or red-flag status
- Automatically syncs changes to tree nodes

**PUT** `/api/v1/dictionary/{term_id}/rename`

- Rename a dictionary term and sync changes to tree nodes
- Includes conflict detection for duplicate terms

**POST** `/api/v1/dictionary/{term_id}/merge`

- Merge two dictionary terms by combining their children
- Includes children selection dialog (max 5 children)

### Import/Export

**GET** `/api/v1/dictionary/export/csv`

- Export dictionary as CSV file
- Parameters: `include_synonyms`, `include_red_flags`

**POST** `/api/v1/dictionary/upload`

- Upload medical dictionary file (CSV/XLSX)
- Parameters: `update_existing`, `create_new_terms`, `min_similarity`

### Tree Relationships

**GET** `/api/v1/dictionary/tree/{term_id}/relationships`

- Get tree relationships for a dictionary term
- Returns parents, children, and node information

## Flutter Implementation

### State Management

The Flutter dictionary system uses Riverpod for state management:

- **`DictionarySearchNotifier`**: Handles search functionality and results
- **`TermDetailsNotifier`**: Manages individual term details and editing
- **`DictionaryStatsNotifier`**: Provides statistics and completion rates
- **`DictionaryExportNotifier`**: Handles CSV export functionality
- **`DictionaryUploadNotifier`**: Manages file upload and validation

### Key Features

1. **Search Functionality**
   - Real-time search as you type
   - Debounced input (300ms delay)
   - Pagination support
   - Conflict count integration

2. **Refresh Button**
   - Manual refresh to update search results
   - Refreshes statistics after data changes
   - Provides immediate feedback

3. **Accurate Statistics**
   - Tree-specific statistics for decision tree terms only
   - Shows completion rates for definitions and synonyms
   - Reflects actual state of decision tree terms

4. **Term Management**
   - Edit definitions, synonyms, and red flag status
   - Rename terms with conflict detection
   - Merge terms with children selection
   - Bidirectional sync with tree nodes

## Data Flow

### Universal Symptoms List

The dictionary serves as the universal symptoms list that connects all components:

```
Decision Tree (nodes table)
    ↕ (bidirectional sync)
Medical Dictionary (medical_dictionary table)
    ↕ (API access)
Flutter Dictionary Pane
    ↕ (data sharing)
VM Builder
    ↕ (symptom access)
EngineWarhammer
    ↕ (symptom access)
EngineShortBow
```

### Synchronization Process

1. **Tree → Dictionary**: When nodes are created/updated in VM Builder
   - Triggers automatically create/update dictionary entries
   - Maintains term consistency across systems

2. **Dictionary → Tree**: When dictionary terms are updated
   - Changes propagate to corresponding tree nodes
   - Ensures label consistency in decision tree

3. **Conflict Detection**: Dictionary terms show conflict counts
   - Uses `/api/v1/conflicts/scan` endpoint
   - Filters conflicts for specific terms
   - Updates conflict counts in real-time

## Integration Points

### VM Builder Integration

- **Symptom Source**: VM Builder directly manipulates the `nodes` table
- **Dictionary Sync**: Changes automatically sync to dictionary via triggers
- **Red Flag Sync**: Red flag status synchronized between systems

### EngineWarhammer Integration

- **Decision Tree Access**: Uses `fetchDecisionTreeRoots()` and `fetchDecisionTreeChildren()`
- **Symptom Source**: Sources symptoms directly from decision tree structure
- **API Endpoints**: Connects to `/api/v1/tree/roots` and `/api/v1/tree/children`

### EngineShortBow Integration

- **Symptom Management**: Has its own symptom tables but can integrate
- **Probability Matrices**: Uses symptom co-occurrence data
- **Navigation**: Interactive symptom navigation with probability calculations

## Best Practices

### Data Consistency

1. **Always use API endpoints** for dictionary operations
2. **Avoid direct database manipulation** to prevent sync issues
3. **Use refresh button** after bulk operations
4. **Check conflict counts** before making changes

### Performance

1. **Use pagination** for large result sets
2. **Debounce search input** to avoid excessive API calls
3. **Cache statistics** and refresh when needed
4. **Use tree-specific stats** for accurate assessment

### Error Handling

1. **Handle null values** in API responses
2. **Provide user feedback** for failed operations
3. **Use retry mechanisms** for transient failures
4. **Validate input data** before API calls

## Troubleshooting

### Common Issues

1. **Null casting errors**: Fixed with proper null safety handling
2. **Inaccurate statistics**: Use tree-specific stats endpoint
3. **Sync issues**: Check trigger status and database integrity
4. **Search failures**: Verify API connectivity and response format

### Debugging

1. **Check API responses** with curl commands
2. **Verify database triggers** are active
3. **Test synchronization** between systems
4. **Monitor conflict detection** accuracy

## Future Enhancements

### Planned Features

1. **Bulk operations** for term management
2. **Advanced search** with filters and sorting
3. **Import validation** with detailed error reporting
4. **Export customization** with field selection
5. **Audit logging** for term changes
6. **Version control** for term definitions

### Integration Improvements

1. **Real-time updates** across all panes
2. **Conflict resolution** automation
3. **Symptom mapping** between engines
4. **Data validation** and integrity checks
