# UI Guide (Flutter Shell)

## Navigation Structure

The app uses a `NavigationRail` with 5 main sections:

1. **Home** - Dashboard with conflicts resolution, export tools, and submission placeholders
2. **VM Builder** - Primary authoring pane (roots list, children editor, breadcrumbs)
3. **Outcomes** - Read-only outcomes view (future extensibility)
4. **Flags** - Filter and visualize red-flagged edges
5. **Settings** - Environment and diagnostics

## VM Builder Pane

### Core Behaviors
- **Import Panel**: Pick CSV/XLSX files, choose Append/Replace mode
  - Uses `POST /api/v1/import` with status feedback
  - Shows validation errors and warnings
- **Breadcrumbs**: Tap to jump to ancestor's children
- **Children Editor**: Add labels, drill into children to edit their children
- **Save Operation**: `PUT /api/v1/tree/children` atomically replaces children for current parent
- **Next Incomplete**: Uses `GET /api/v1/tree/next-underfilled` with snackbar feedback
- **State Management**: Busy overlay during long operations, navigation guarded during save/import
- **Error Handling**: 409 slot conflicts and 422 validation errors surface as inline messages

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
