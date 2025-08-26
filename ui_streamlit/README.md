# Streamlit Adapter - Development UI

This is a **DEVELOPMENT ADAPTER** for the Decision Tree Manager, designed for quick demos and testing.

⚠️ **IMPORTANT**: This is NOT the production UI. Production UIs are Flutter/Kivy.

## Purpose

The Streamlit adapter provides a simple web interface for:
- Quick demos and presentations
- Development testing
- API exploration
- Data validation

## Architecture

The Streamlit adapter follows the **UI-agnostic core** principle:

- ✅ **Uses core/services** directly when running locally
- ✅ **Uses FastAPI API** when connecting to remote server
- ❌ **No direct database access** from Streamlit code
- ❌ **No direct Google Sheets access** from Streamlit code

## Features

### Connection Modes

1. **Local Services Mode**: Uses `core/services` and `storage/sqlite` directly
   - Triggered when `DB_PATH` environment variable is set
   - Triggered when API server is not available

2. **API Mode**: Uses FastAPI endpoints
   - Default: `http://localhost:8000`
   - Configurable via sidebar

### Pages

- **Overview**: System status and quick actions
- **Tree Editor**: Find and edit incomplete parents
- **Conflicts**: Validation and conflict detection (placeholder)
- **Calculator**: Export functionality (placeholder)
- **Settings**: Connection info and system details

### Health Information

Displays in sidebar:
- ✅ Connection status
- 📊 Version information
- 🗄️ Database configuration (WAL, foreign keys, path)
- 🔧 Connection mode (Local Services vs API)

## Usage

### Running the Adapter

```bash
# From the ui_streamlit directory
cd ui_streamlit
streamlit run app.py

# Or with custom API URL
streamlit run app.py --server.port 8501
```

### Configuration

The adapter uses `.streamlit/config.toml` for development settings:
- `fileWatcherType = "poll"` - Avoids inotify overload
- `runOnSave = false` - Prevents auto-reload issues
- `serverPort = 8501` - Default port

### Environment Variables

- `DB_PATH`: Forces local services mode
- `API_URL`: Default API base URL (configurable in UI)

## Development

### Testing

Run the smoke tests:
```bash
python -m pytest tests/ui/test_streamlit_adapter.py -v
```

### Adding Features

When adding new features:
1. Use `StreamlitAdapter` methods for data access
2. Implement both local services and API modes
3. Add appropriate error handling
4. Update tests

### Code Structure

```
ui_streamlit/
├── app.py              # Main Streamlit application
├── .streamlit/
│   └── config.toml     # Streamlit configuration
└── README.md           # This file
```

## Limitations

- **Development only**: Not for production use
- **Limited features**: Basic tree editing and health checks
- **No advanced UI**: Simple forms and displays
- **Placeholder pages**: Some features not fully implemented

## Production UIs

For production use, see:
- **Flutter**: `ui_flutter/` - Cross-platform mobile/desktop UI
- **Kivy**: Future implementation for desktop

## Troubleshooting

### Connection Issues

1. Check API server is running: `http://localhost:8000/api/v1/health`
2. Verify database path if using local services
3. Check firewall/network settings for remote API

### Performance Issues

1. Ensure `.streamlit/config.toml` has `fileWatcherType = "poll"`
2. Use `runOnSave = false` to prevent auto-reload
3. Consider using local services mode for better performance

### Import Errors

1. Ensure project root is in Python path
2. Install required dependencies: `pip install streamlit requests`
3. Check that core modules are available
