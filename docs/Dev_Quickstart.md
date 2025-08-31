# Developer Quickstart Guide

## Prerequisites
- Python 3.12+
- SQLite 3
- Flutter 3.16+ (for mobile development)
- Git

## Setup

### 1. Clone and Setup
```bash
git clone <repository-url>
cd Lorien
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
DB_PATH=lorien.db
CORS_ALLOW_ALL=false  # Set to true for LAN testing
LLM_ENABLED=false     # Keep disabled for safety
ANALYTICS_ENABLED=false  # Set to true for metrics collection
```

### 3. Database Setup
```bash
# Initialize database
python -m storage.init_db

# Run migrations (if any)
python -m storage.run_migrations
```

## Development

### API Development
```bash
# Start FastAPI server
uvicorn api.main:app --reload --port 8000

# Health check
curl http://localhost:8000/health
```

### Streamlit Development
```bash
# Start Streamlit UI
streamlit run Home.py

# With custom port
streamlit run Home.py --server.port 8501
```

### Flutter Development
```bash
# Navigate to Flutter directory
cd ui_flutter

# Get dependencies
flutter pub get

# Run tests
flutter test

# Start development server
flutter run -d linux  # or -d chrome for web
```

## LAN & CORS
- Set `CORS_ALLOW_ALL=true` for LAN/mobile testing
- Configure API base in UI settings; verify with `/health` JSON
- Android emulator: use `http://10.0.2.2:<port>`
- iOS simulator: use `http://localhost:<port>`
- Physical devices: use `http://<LAN-IP>:<port>`

## Testing

### API Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=api tests/
```

### Flutter Tests
```bash
cd ui_flutter
flutter test
```

### Integration Tests
```bash
# Start API server
uvicorn api.main:app --port 8000

# Run integration tests
pytest tests/test_integration.py
```

## Database Operations

### Backup
```bash
# Via API
curl -X POST http://localhost:8000/backup

# Via UI: Use "Create Backup" button in Workspace
```

### Restore
```bash
# Via API
curl -X POST http://localhost:8000/restore

# Via UI: Use "Restore Latest" button in Workspace
```

### Integrity Check
```bash
# Check database health
curl http://localhost:8000/health | jq '.db'
```

## Performance Monitoring

### Cache Management
- Cache statistics available in Workspace page
- TTL: 5 minutes default
- Performance tests show cache effectiveness
- Clear cache when debugging

### Endpoint Performance
- `/health`: <100ms target
- `/tree/stats`: <100ms target
- Conflicts endpoints: <100ms target
- Import operations: <30s target
- Export operations: <10s target

## Telemetry (beta)
- `ANALYTICS_ENABLED=true` surfaces non-PHI counters in `health.metrics`
- Metrics include table counts, audit retention status, cache info
- No PHI data collected
- Toggle available in environment configuration

## Troubleshooting

### Common Issues
1. **CORS errors**: Set `CORS_ALLOW_ALL=true`
2. **Database locked**: Check WAL mode and foreign keys
3. **Import failures**: Verify 8-column CSV headers
4. **Cache issues**: Clear cache via UI or restart server

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Start with verbose output
uvicorn api.main:app --reload --log-level debug
```

### Health Checks
```bash
# Basic health
curl http://localhost:8000/health

# Database info
curl http://localhost:8000/health | jq '.db'

# Feature flags
curl http://localhost:8000/health | jq '.features'

# Metrics (if enabled)
curl http://localhost:8000/health | jq '.metrics'
```

## Deployment

### Production
```bash
# Set production environment
export ENV=production
export DB_PATH=/var/lib/lorien/lorien.db

# Start production server
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Docker (if available)
```bash
# Build image
docker build -t lorien .

# Run container
docker run -p 8000:8000 lorien
```

## Contributing

### Code Style
- Follow PEP 8 for Python
- Use type hints
- Document functions and classes
- Write tests for new features

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature
```

## Support
- **Documentation**: Check docs/ directory
- **Issues**: Create GitHub issue
- **Discussions**: Use GitHub Discussions
- **Engineering**: Slack #lorien-engineering
