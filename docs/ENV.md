# Lorien Environment Configuration

This document describes the environment variables used by Lorien and their configuration options.

## Server Environment Variables

### Database Configuration

#### `LORIEN_DB_PATH`
- **Purpose**: Path to the SQLite database file
- **Type**: String (absolute or relative path)
- **Default**: `~/.local/share/lorien/app.db` (OS-appropriate app data directory)
- **Examples**:
  ```bash
  # Absolute path
  export LORIEN_DB_PATH=/var/lib/lorien/production.db
  
  # Relative path (relative to current working directory)
  export LORIEN_DB_PATH=./data/lorien.db
  
  # Test database in temporary directory
  export LORIEN_DB_PATH=$PWD/.tmp/lorien.db
  ```
- **Notes**: 
  - Parent directory will be created automatically if it doesn't exist
  - Database will be initialized with schema if it doesn't exist
  - WAL mode and foreign key constraints are automatically enabled

### Feature Flags

#### `LLM_ENABLED`
- **Purpose**: Enable/disable Local LLM integration
- **Type**: Boolean string
- **Default**: `false`
- **Values**: `true` or `false`
- **Examples**:
  ```bash
  # Enable LLM
  export LLM_ENABLED=true
  
  # Disable LLM (default)
  export LLM_ENABLED=false
  ```
- **Notes**:
  - When disabled, `/api/v1/llm/health` returns 503
  - When enabled, requires `LLM_MODEL_PATH` to point to valid model file
  - UI will show/hide LLM-related features based on this setting

#### `LLM_MODEL_PATH`
- **Purpose**: Path to the LLM model file (when LLM_ENABLED=true)
- **Type**: String (file path)
- **Default**: `""` (empty)
- **Examples**:
  ```bash
  export LLM_MODEL_PATH=/opt/lorien/models/llama-2-7b.gguf
  export LLM_MODEL_PATH=./models/mistral-7b-instruct.gguf
  export LLM_MODEL_PATH=/tmp/fake-model.gguf  # For testing
  ```
- **Notes**:
  - File must exist and be readable when `LLM_ENABLED=true`
  - Health check validates file existence
  - Leave empty for null provider

#### `LLM_PROVIDER`
- **Purpose**: Specify which LLM provider to use
- **Type**: String
- **Default**: `null`
- **Examples**:
  ```bash
  # Use null provider (default, no-op for testing)
  export LLM_PROVIDER=null

  # Use Ollama provider (when implemented)
  export LLM_PROVIDER=ollama

  # Use custom provider
  export LLM_PROVIDER=custom
  ```
- **Notes**:
  - `null`: Always-ready provider for testing/development
  - `ollama`: Local Ollama instance (future implementation)
  - Provider must be available in `core/llm/providers/`

### CORS Configuration

#### `CORS_ALLOW_ALL`
- **Purpose**: Allow all origins for CORS (useful for development/LAN)
- **Type**: Boolean string
- **Default**: `false`
- **Values**: `true` or `false`
- **Examples**:
  ```bash
  # Allow all origins (development/LAN)
  export CORS_ALLOW_ALL=true
  
  # Restrict to specific origins (production)
  export CORS_ALLOW_ALL=false
  ```
- **Notes**:
  - When `false`: restricts to localhost, emulator IPs, and common dev ports
  - When `true`: allows any origin (`*`)
  - Useful for mobile development and LAN access

### Analytics (Optional)

#### `ANALYTICS_ENABLED`
- **Purpose**: Enable runtime metrics collection
- **Type**: Boolean string
- **Default**: `false`
- **Values**: `true` or `false`
- **Notes**: When enabled, `/health` endpoint includes table counts and cache metrics

## UI-Only Environment Variables

**Note**: These variables are used by Flutter/Streamlit clients and should NOT be set on the server.

#### `BASE_URL`
- **Purpose**: Base URL for API endpoints
- **Type**: String (URL)
- **Examples**:
  ```bash
  # Local development
  export BASE_URL=http://127.0.0.1:8000/api/v1
  
  # LAN access
  export BASE_URL=http://192.168.1.100:8000/api/v1
  
  # Production
  export BASE_URL=https://api.lorien.example.com/api/v1
  ```
- **Notes**:
  - Must include `/api/v1` suffix
  - Used by Flutter app for API communication
  - Do not set this on the server side

## Development Environment Setup

### Quick Start
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set up test database
export LORIEN_DB_PATH=$PWD/.tmp/lorien.db

# Start server
uvicorn api.app:app --host 127.0.0.1 --port 8000 --reload
```

### Testing Configuration
```bash
# Test database in temporary directory
export LORIEN_DB_PATH=$PWD/.tmp/lorien.db

# Enable LLM for testing
export LLM_ENABLED=true

# Allow all CORS for testing
export CORS_ALLOW_ALL=true
```

### Production Configuration
```bash
# Production database
export LORIEN_DB_PATH=/var/lib/lorien/production.db

# Disable LLM (unless specifically needed)
export LLM_ENABLED=false

# Restrict CORS
export CORS_ALLOW_ALL=false

# Optional: Enable analytics
export ANALYTICS_ENABLED=true
```

## Mobile Development

### Android Emulator
- CORS automatically includes `http://10.0.2.2` (emulator host)
- Use `BASE_URL=http://10.0.2.2:8000/api/v1` in Flutter app

### iOS Simulator
- CORS automatically includes localhost variants
- Use `BASE_URL=http://127.0.0.1:8000/api/v1` in Flutter app

### Physical Device (LAN)
```bash
# Allow all CORS for LAN access
export CORS_ALLOW_ALL=true

# Use your computer's LAN IP
export BASE_URL=http://192.168.1.100:8000/api/v1
```

## Troubleshooting

### Database Issues
```bash
# Check database path
echo $LORIEN_DB_PATH

# Verify database exists and is accessible
ls -la $LORIEN_DB_PATH

# Check database health
curl http://127.0.0.1:8000/api/v1/health | jq '.db'
```

### LLM Issues
```bash
# Check LLM status
curl http://127.0.0.1:8000/api/v1/llm/health

# Verify model file exists
ls -la $LLM_MODEL_PATH
```

### CORS Issues
```bash
# Check CORS configuration
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS http://127.0.0.1:8000/api/v1/health
```

## Environment File Example

Create a `.env` file for local development:
```bash
# .env
LORIEN_DB_PATH=./.tmp/lorien.db
LLM_ENABLED=false
CORS_ALLOW_ALL=true
ANALYTICS_ENABLED=false
```

**Note**: Lorien doesn't automatically load `.env` files. You must export these variables or use a tool like `direnv`.
