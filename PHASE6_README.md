# Phase 6 README - Lorien Decision Tree Platform

## Quick Commands

### API Server
```bash
# Start the API server
cd /home/jharm/Lorien
source venv/bin/activate
python main.py

# Or use uvicorn directly
uvicorn api.app:app --host 127.0.0.1 --port 8000 --reload
```

### Streamlit UI
```bash
# Start Streamlit interface
cd /home/jharm/Lorien
source venv/bin/activate
streamlit run ui_streamlit/main.py --server.port 8501
```

### Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test suites
python -m pytest tests/test_phase6b.py -v
python -m pytest tests/test_ui_parity.py -v
```

## LAN Testing Tips

### CORS Configuration
```bash
# Allow all origins for LAN testing
export CORS_ALLOW_ALL=true

# Start server with CORS enabled
python main.py
```

### Emulator & Device IPs
- **Android Emulator**: `10.0.2.2:8000`
- **iOS Simulator**: `127.0.0.1:8000`
- **LAN Devices**: Use your machine's LAN IP (e.g., `192.168.1.100:8000`)
- **WSL2**: Use `localhost:8000` from Windows, or your WSL2 IP

### Health Check
```bash
# Check API health
curl http://localhost:8000/health | jq .
curl http://localhost:8000/api/v1/health | jq .

# Check LLM status
curl http://localhost:8000/api/v1/llm/health | jq .
```

## New Phase 6B Endpoints

### Excel Export
```bash
# Calculator data as Excel
GET /calc/export.xlsx
GET /api/v1/calc/export.xlsx

# Tree data as Excel  
GET /tree/export.xlsx
GET /api/v1/tree/export.xlsx
```

### Root Management
```bash
# Create new vital measurement with 5 child slots
POST /tree/roots
POST /api/v1/tree/roots

# Request body
{
  "label": "Blood Pressure",
  "children": ["High", "Normal", "Low"]
}
```

### Tree Statistics
```bash
# Get completeness metrics
GET /tree/stats
GET /api/v1/tree/stats

# Response includes: nodes, roots, leaves, complete_paths, incomplete_parents
```

### LLM Integration
```bash
# Fill triage actions (feature-flagged)
POST /llm/fill-triage-actions
POST /api/v1/llm/fill-triage-actions

# Check LLM status
GET /llm/health
GET /api/v1/llm/health
```

### Conflict Validation
```bash
# Duplicate labels under same parent
GET /tree/conflicts/duplicate-labels?limit=100&offset=0

# Orphan nodes with invalid parent references
GET /tree/conflicts/orphans?limit=100&offset=0

# Depth anomalies (invalid depth values)
GET /tree/conflicts/depth-anomalies?limit=100&offset=0
```

## The 8-Column Contract

**CSV/Excel headers are frozen at exactly 8 columns:**

```
Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions
```

**Column Details:**
- **Vital Measurement**: Root node label (depth=0)
- **Node 1-5**: Child node labels (depth=1-5)
- **Diagnostic Triage**: Clinical assessment for leaf nodes
- **Actions**: Recommended actions for leaf nodes

**Export Formats:**
- CSV: `/calc/export` and `/tree/export`
- Excel: `/calc/export.xlsx` and `/tree/export.xlsx`

## Feature Flags

### LLM Integration
- **Default**: OFF (disabled)
- **Control**: `LLM_ENABLED=true` environment variable
- **Health Check**: `/llm/health` returns 503 when disabled
- **Safety**: AI suggestions are guidance-only; no auto-apply

### CORS
- **Default**: Restricted origins
- **LAN Mode**: `CORS_ALLOW_ALL=true` for cross-device testing

## Streamlit "Where to Click"

### 🏢 Workspace Page
- **Excel Import**: Upload `.xlsx` files for bulk data import
- **New Vital Measurement**: Create root nodes with 5 child slots
- **Export Buttons**: Download CSV/XLSX with 8-column headers
- **Completeness Summary**: View tree statistics and jump to incomplete parents
- **Health Check**: Monitor API status and database path

### ⚠️ Conflicts Page  
- **Validation Options**: Toggle duplicate labels, orphans, depth anomalies
- **Conflict Tables**: Paginated results with search/filter
- **Jump Links**: Navigate directly to problematic nodes/parents
- **Missing Slots**: Find parents needing more children
- **Next Incomplete**: Jump to next parent requiring attention

### 📋 Outcomes Page
- **Search & Filter**: Find triage records by criteria
- **LLM Fill**: AI-powered triage suggestions (when enabled)
- **Inline Editing**: Edit triage data for leaf nodes only
- **Multi-Select**: Compare multiple outcomes side-by-side
- **Safety Notice**: AI guidance-only warnings

### 🧮 Calculator Page
- **Chained Dropdowns**: Root → Node1 → Node2 → Node3 → Node4 → Node5
- **Path Selection**: Navigate tree structure sequentially
- **Outcomes Display**: Show triage data when leaf is reached
- **Path Export**: Download single path as CSV/XLSX
- **Header Preview**: Verify 8-column canonical format

## Architecture Notes

### Dual Mount Strategy
- **Root Paths**: All endpoints at `/` (e.g., `/calc/export.xlsx`)
- **Versioned Paths**: Same endpoints at `/api/v1` (e.g., `/api/v1/calc/export.xlsx`)
- **Consistency**: Identical responses and behavior at both paths

### Streamlit Adapter Pattern
- **API-Only**: No direct database access
- **HTTP Client**: Uses `ui_streamlit/api_client.py` for all backend communication
- **State Management**: Session state for navigation and selections

### Database Constraints
- **5 Children Rule**: Each parent must have exactly 5 children
- **Depth Validation**: Nodes must have depth = parent.depth + 1
- **Foreign Keys**: Maintained with CASCADE operations

## Troubleshooting

### Common Issues
1. **CORS Errors**: Set `CORS_ALLOW_ALL=true` for LAN testing
2. **LLM 503**: Normal when `LLM_ENABLED=false` (default)
3. **Import Failures**: Check Excel file format and 8-column headers
4. **Navigation Issues**: Use "Jump to Editor" buttons for direct navigation

### Performance
- **Pagination**: Use `limit` and `offset` for large datasets
- **Search**: Client-side filtering for small result sets
- **Caching**: Streamlit session state for user selections

### Development
- **Hot Reload**: Both API (`--reload`) and Streamlit support hot reloading
- **Logs**: Check terminal output for detailed error messages
- **Database**: SQLite file location shown in `/health` response
