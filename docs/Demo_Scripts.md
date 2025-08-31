# Demo Scripts (≤2 minutes each)

## Prerequisites
- API server running on `http://localhost:8000`
- Streamlit UI running on `http://localhost:8501`
- Flutter app configured with correct API base URL
- Sample data available in database

## Demo 1: Workspace Import/Export + Header Preview (2 min)

### Setup
1. Open Streamlit Workspace page
2. Ensure API server is running
3. Have a sample Excel file ready

### Demo Flow
1. **Show Header Preview** (30s)
   - Point to "CSV Header Preview" section
   - Highlight the frozen 8-column format
   - Explain this is the contract that cannot change

2. **Excel Import** (45s)
   - Upload sample Excel file
   - Show progress indicators (queued→processing→done)
   - Display detailed results (inserted, updated, skipped counts)
   - Show header validation results

3. **Export Functionality** (45s)
   - Click "Export Calculator (CSV)" - show download
   - Click "Export Tree (XLSX)" - show download
   - Verify files have correct headers

### Expected Results
- Progress indicators visible during import
- Success metrics displayed after import
- CSV/XLSX files download with correct headers
- Header preview shows exact 8-column format

## Demo 2: Conflicts → Jump → Fix → Re-validate (2 min)

### Setup
1. Open Streamlit Conflicts page
2. Ensure some conflicts exist in database
3. Have Editor page ready

### Demo Flow
1. **Show Conflicts Panel** (30s)
   - Display missing slots list
   - Show validation options expander
   - Highlight conflict counts

2. **Jump to Incomplete Parent** (45s)
   - Click "Jump to Next Incomplete Parent"
   - Navigate to Editor page
   - Show parent with missing children

3. **Fix and Re-validate** (45s)
   - Add missing child labels
   - Save changes
   - Return to Conflicts to show reduced count

### Expected Results
- Conflicts panel loads fast (<100ms)
- Jump navigation works seamlessly
- Editor shows correct parent context
- Conflict count decreases after fixes

## Demo 3: Outcomes Manual Edit (LLM Fill Hidden When OFF) (2 min)

### Setup
1. Open Streamlit Outcomes page
2. Ensure `LLM_ENABLED=false` in environment
3. Have leaf nodes with triage data

### Demo Flow
1. **Show Outcomes Grid** (30s)
   - Display triage records
   - Point out leaf-only editing rule
   - Show search/filter functionality

2. **Manual Triage Edit** (45s)
   - Select a leaf node
   - Edit triage text
   - Save changes
   - Verify data persists

3. **LLM Integration Hidden** (45s)
   - Point out no "Fill with LLM" button
   - Explain this is by design for safety
   - Show `/llm/health` returns 503

### Expected Results
- Outcomes grid loads with triage data
- Leaf nodes are editable, non-leaves disabled
- No LLM Fill button visible
- Manual edits save successfully
- LLM health endpoint shows disabled status

## Demo 4: Flutter Calculator & Exports (2 min)

### Setup
1. Flutter app running on target device/emulator
2. API base URL configured correctly
3. Sample data available

### Demo Flow
1. **Calculator Chained Dropdowns** (45s)
   - Show root selection dropdown
   - Navigate through Node1→Node5
   - Demonstrate reset behavior
   - Show outcomes at leaf

2. **Export Functionality** (45s)
   - Export Calculator as CSV
   - Export Tree as XLSX
   - Show platform-specific save/share
   - Verify file headers

3. **Workspace Integration** (30s)
   - Navigate to Workspace screen
   - Show health information
   - Demonstrate export buttons

### Expected Results
- Dropdowns chain correctly with reset behavior
- Helper text shows remaining levels
- Outcomes display at leaf nodes
- Exports work on all platforms
- Save/share functionality platform-appropriate

## Demo 5: Backup/Restore + Cache Management (2 min)

### Setup
1. Open Streamlit Workspace page
2. Ensure backup directory exists
3. Have some cached data

### Demo Flow
1. **Backup Operations** (45s)
   - Click "Create Backup"
   - Show backup file path
   - Display integrity check results
   - Show backup status

2. **Cache Management** (45s)
   - Refresh cache stats
   - Show cache size and TTL
   - Run performance test
   - Clear cache

3. **Restore Functionality** (30s)
   - Click "Restore Latest"
   - Show pre-restore backup creation
   - Display integrity check after restore

### Expected Results
- Backup creates timestamped files
- Integrity checks show database health
- Cache stats display current state
- Performance test shows cache improvement
- Restore creates safety backup

## Demo Tips

### Environment Setup
- **Base URL**: Show `http://localhost:8000` for local testing
- **Emulator IPs**: 
  - Android: `http://10.0.2.2:8000`
  - iOS: `http://localhost:8000`
  - Device: `http://<LAN-IP>:8000`

### Expected Screenshots
- Progress indicators during import
- CSV header preview showing 8 columns
- Conflicts panel with validation options
- Outcomes grid with leaf-only editing
- Flutter calculator with chained dropdowns
- Backup/restore with integrity results

### Common Issues & Solutions
- **CORS errors**: Set `CORS_ALLOW_ALL=true`
- **Slow responses**: Check cache performance test
- **Import failures**: Verify Excel file format
- **Navigation issues**: Use "Jump to Editor" buttons

### Demo Scripts for Different Audiences

#### **Stakeholders** (High-level)
- Focus on user experience improvements
- Show import/export efficiency
- Highlight mobile parity achievements

#### **Developers** (Technical)
- Show API endpoint structure
- Demonstrate caching effectiveness
- Explain architecture decisions

#### **QA/Testing** (Validation)
- Use acceptance checklist
- Test error scenarios
- Verify performance targets

## Demo Environment Checklist

- [ ] API server running and healthy
- [ ] Streamlit UI accessible
- [ ] Flutter app configured
- [ ] Sample data available
- [ ] Environment variables set
- [ ] Backup directory exists
- [ ] Test files ready
- [ ] Network connectivity verified
