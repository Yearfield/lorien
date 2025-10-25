# UI Guide (Flutter Shell)

## Navigation Structure

The app uses a `NavigationRail` with 7 main sections:

1. **Home** - Dashboard with conflicts resolution, export tools, and submission placeholders
2. **VM Builder** - Primary authoring pane (roots list, children editor, breadcrumbs)
3. **Dictionary** - Medical term management with search, edit, and synchronization
4. **P Builder** - Pathogen data import and management system (EngineShelob)
5. **Outcomes** - Read-only outcomes view (future extensibility)
6. **Flags** - Filter and visualize red-flagged edges
7. **Settings** - Environment and diagnostics

## Dictionary Pane

### Core Features

- **Search Functionality**: Search medical terms by typing in the search field
  - Empty search returns all terms with pagination
  - Real-time search as you type
  - Results show term name, definition, synonyms, and red flag status
- **Refresh Button**: Manual refresh to update search results and statistics
- **Term Details Dialog**: Click any term to open detailed editing interface
  - **Editable Fields**: Term name, definition, synonyms (comma-separated)
  - **Red Flag Toggle**: Mark terms as red flags (syncs to VM Builder)
  - **Tree Relationships**: View parents and children in the tree structure
  - **Statistics**: Shows average children count and conflicts count
- **Accurate Statistics**: Tree-specific statistics showing completion rates for decision tree terms only
- **Rename & Merge Operations**:
  - **Rename**: Change term name with automatic conflict detection
  - **Merge**: Combine terms with children selection dialog (max 5 children)
  - **Conflict Resolution**: Interactive selection for handling merge conflicts
- **Export Functionality**: Export dictionary to CSV or XLSX format
  - Includes term, definition, synonyms, red flag status, and statistics
- **Upload Functionality**: Import medical dictionaries from CSV/XLSX files
  - **File Validation**: Checks file structure and format
  - **Matching Logic**: Finds existing terms and suggests spelling corrections
  - **Batch Processing**: Handles large dictionary files efficiently
- **Red Flag Synchronization**: Changes in Dictionary immediately reflect in VM Builder
  - Updates edge_meta table for proper red flag display
  - Bidirectional sync ensures consistency across the application

### Data Synchronization

- **Bidirectional Sync**: Dictionary changes automatically sync to tree nodes
- **Database Triggers**: Maintain data consistency between dictionary and tree
- **Conflict Detection**: Identifies spelling errors and duplicate terms
- **Real-time Updates**: Changes are immediately visible across all panes

## P Builder Pane (EngineShelob)

### Core Features

- **Pathogen Database Management**: Import and manage pathogen data from spreadsheet files
- **Import Functionality**: Upload CSV or XLSX files containing pathogen data
  - **File Format Support**: Handles both CSV and Excel (.xlsx) formats
  - **Large File Support**: Up to 50MB file size limit for comprehensive datasets
  - **Automatic Column Detection**: Intelligently separates pathogen properties from binary associations
  - **Import Statistics**: Shows detailed results including pathogens created/updated and associations processed
- **Pathogen List View**: Browse all imported pathogens with pagination and search
  - **Search Functionality**: Real-time search by pathogen name
  - **Association Filtering**: Filter pathogens by specific associations or show only pathogens with associations
  - **Statistics Display**: Shows total pathogens, associations, and average associations per pathogen
- **Pathogen Detail Dialog**: Click any pathogen to view detailed information
  - **Comprehensive Information**: Displays all pathogen properties including classification, transmission, resistance, clinical data
  - **Association Display**: Shows all binary associations (symptoms, diseases, environmental factors)
  - **Inline Editing**: Edit pathogen name, basic information, and transmission/resistance data
  - **Create New Pathogen**: Add new pathogens manually with the "+Pathogen" button
- **Data Management**:
  - **Upsert Behavior**: Re-importing updates existing data without duplicates
  - **Association Management**: Binary associations (0/1) are stored efficiently with only positive associations saved
  - **Data Integrity**: Foreign key constraints ensure data consistency

### Data Structure

- **Pathogen Properties**: Classification, NT, pathogen name, vaccine, toxin, transmission, antibiotic resistance, host, commensal, disease, incubation, diagnosis, treatment, prevention, notes
- **Binary Associations**: Symptoms, diseases, environmental factors, geographic regions, etc. (stored as 0/1 values)
- **Separate Database Tables**: Isolated from decision tree data to maintain system separation

## VM Builder Pane

### Core Behaviors

- **Import Panel**: Pick CSV/XLSX files, choose Append/Replace mode
  - Uses `POST /api/v1/import` with status feedback
  - Shows validation errors and warnings
- **Breadcrumbs**: Tap to jump to ancestor's children
- **Children Editor**: Add labels, drill into children to edit their children
- **Child Addition Workflow**:
  - Type child label in "Add child label" field and press "Add" button
  - New child appears immediately in the list (local state)
  - Press "Save" to persist new children to server safely
  - Click on saved children to drill into them and add their children
  - System detects unsaved changes and prevents drilling until saved
- **Save Operation**: Smart save logic that preserves downstream data
  - **Safe Addition**: When only adding new children, uses `POST /api/v1/tree/child` to add individually
  - **Full Replacement**: When modifying existing children, uses `PUT /api/v1/tree/children` (with warning)
  - **User Protection**: Warns before destructive operations that could lose downstream data
- **Next Incomplete**: Uses `GET /api/v1/tree/next-underfilled` with snackbar feedback
- **State Management**: Busy overlay during long operations, navigation guarded during save/import
- **Error Handling**: 409 slot conflicts and 422 validation errors surface as inline messages

### Parent Rename & Merge

- **Edit Button**: Click the edit icon next to parent title to rename
- **Rename Dialog**: Enter new parent name with validation
- **Duplicate Detection**: Automatically searches for existing parents with same name
- **Merge Confirmation**: When duplicates found, shows merge options:
  - **Simple Merge**: If ≤5 unique children total, merges automatically
  - **Children Selection**: If >5 unique children, shows selection dialog
- **Selection Dialog**:
  - Lists all unique children from both parents
  - Must select exactly 5 children to proceed
  - Shows selection count (e.g., "Selected: 3/5")
  - Disabled merge button until exactly 5 selected
- **Merge Process**:
  - Replaces all children of existing parent with selected children
  - Deletes the current parent and all its children
  - Navigates to the merged parent after completion
  - Shows loading spinner during operation
  - Provides clear success/error feedback

### Search & Navigation

- **Search Parent**: Enter parent ID to navigate directly to specific parent
  - Located below the Roots section
  - Validates input and provides feedback
  - Clears search field on successful navigation
- **Navigation from Conflicts**: Click edit icon in conflicts list to navigate to parent in VM Builder

### EngineShortBow Integration

- **Navigation Button**: Click the navigation icon (🧭) in the VM Builder app bar to access ShortBow Navigator
- **ShortBow Navigator**: Dedicated screen for interactive symptom navigation with two main tabs:
  - **Import Data Tab**: Upload Excel symptom matrices and view statistics
  - **Navigate Tab**: Interactive symptom navigation with probability visualization
- **Symptom Navigation Workflow**:
  - **Starting Symptoms**: Dropdown shows top symptoms with highest average linkage
  - **Linked Symptoms**: After selecting a symptom, shows top 5 related symptoms with probabilities
  - **Selection Management**: Add symptoms to selection (max 5), remove with chip delete buttons
  - **Navigation History**: Save navigation sessions and view recent calculations
  - **Probability Display**: Clear percentage display of symptom linkage strengths

## API Configuration

### Switching API Targets

- Use Flutter define: `--dart-define=API_BASE_URL=http://127.0.0.1:8000/api/v1`
- Default when unset: `http://127.0.0.1:8000/api/v1`

## Home Dashboard

The Home pane serves as a comprehensive dashboard with three main sections:

### Conflicts Card

- **Scan Button**: Click to detect conflicts across the tree
- **Conflicts List**: Shows each conflict with:
  - Label name (e.g., "hypertension")
  - Occurrence count (e.g., "19 parents")
  - Union size (e.g., "union=10")
  - **Edit Button**: Click to navigate directly to the first parent in VM Builder for editing
- **Detail Panel**: When a conflict is selected:
  - **Header**: "Resolve: [label]" (e.g., "Resolve: hypertension")
  - **Occurrences List**: Shows each parent with:
    - Depth indicator (e.g., "D1 • Parent #12")
    - Current children list
  - **Union Children**: Selectable chips showing all possible children
    - Max 5 selection limit with error state
    - Visual feedback for selection count
  - **Actions**:
    - **Dry Run**: Shows diff dialog with changes that would be made
    - **Apply**: Commits selected children to all matching parents

### Export Card

- **Format Selection**: Radio buttons for CSV (default) and XLSX
- **Advanced Filters**:
  - **Max Depth**: Limit export depth (0 = unlimited)
  - **Only Red**: Export only red-flagged paths
  - **Include Meta**: Include metadata columns
  - **Root Filter**: Select specific roots to export
- **Export Methods**:
  - **Export Button**: Opens native file picker for download
  - **Copy URL**: Copies export URL to clipboard
- **Last Export**: Shows timestamp of most recent export

### New Submission Card

- Placeholder section for future bulk submission workflows

## Conflicts Resolution Workflow

### Scan Process

- Uses `GET /api/v1/conflicts/scan` to find parents with same label but different child sets
- Groups by normalized label (case-insensitive, trimmed) across all depths
- Detects conflicts when:
  - Same label has ≥2 occurrences with different child sets, OR
  - Union of all child labels across occurrences > 5

### Resolution Process

- **Detail Panel**: Shows union of all child labels as selectable chips (≤5 limit enforced)
- **Dry Run**: `POST /api/v1/conflicts/resolve` with `dry_run=true` shows changes without applying
- **Apply**: `POST /api/v1/conflicts/resolve` applies selected children to all matching parents
- **Cross-depth**: Resolution applies to all parents with matching label regardless of depth

## Export Actions

### Format Options

- **CSV**: Default format with canonical header
- **XLSX**: Excel-compatible spreadsheet format

### Filter Options

- **Max Depth**: Limit export to specific depth levels
- **Only Red**: Export only red-flagged paths
- **Include Meta**: Include metadata columns (D6, Notes)
- **Root Filter**: Export specific root trees only

### Export Methods

- **Native File Picker**: Save dialog with proper file extensions
- **URL Copy**: Shareable export links with current filter settings

## Technical Notes

### Core Constraints

- **Service-level ≤5 rule**: The editor enforces ≤5 children; DB remains flexible via unique `(parent_id, slot)`
- **Label-only conflicts**: Grouped by normalized label (case-insensitive, trimmed) across all depths
- **Max depth enforcement**: Prevents adding children to D6 parents (would exceed D6 limit)

### State Management

- **Riverpod**: Used for conflicts state management with `ChangeNotifierProvider`
- **Error Handling**: Comprehensive error states with user-friendly messages
- **Busy States**: Visual feedback during API operations
