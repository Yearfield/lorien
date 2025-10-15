# Manual Testing Guide for Lorien API

## 🚀 Server Status

The Lorien API is currently running at:

- **URL**: <http://127.0.0.1:8000>
- **API Base**: <http://127.0.0.1:8000/api/v1>
- **Environment**: Development (authentication optional)
- **Status**: ✅ Running successfully

## 📋 Quick Test Commands

### Health Check

```bash
curl http://127.0.0.1:8000/api/v1/health | jq .
```

### Live Status

```bash
curl http://127.0.0.1:8000/api/v1/live | jq .
```

### Ready Status

```bash
curl http://127.0.0.1:8000/api/v1/ready | jq .
```

### List Root Nodes

```bash
curl http://127.0.0.1:8000/api/v1/tree/roots | jq .
```

### Create New Root Node

```bash
curl -X POST http://127.0.0.1:8000/api/v1/tree/roots \
  -H "Content-Type: application/json" \
  -d '{"label": "Test Node"}' | jq .
```

## 🔧 Testing Security Features

### Run Security Test Suite

```bash
python test_security_features.py
```

### Run Production Security Tests

```bash
python test_production_security.py
```

## 🌐 Browser Testing

### API Documentation

- **Swagger UI**: <http://127.0.0.1:8000/docs>
- **ReDoc**: <http://127.0.0.1:8000/redoc>

### Health Dashboard

- **Health Check**: <http://127.0.0.1:8000/api/v1/health>
- **Live Status**: <http://127.0.0.1:8000/api/v1/live>
- **Ready Status**: <http://127.0.0.1:8000/api/v1/ready>

## 🔐 Security Features to Test

### 1. Authentication (Development Mode)

- ✅ Read operations work without authentication
- ✅ Write operations work without authentication (development mode)
- ✅ Invalid tokens are ignored (development mode)

### 2. Security Headers

- ✅ Request ID tracking (`X-Request-ID`)
- ✅ Trace ID tracking (`X-Trace-ID`)
- ⚠️ Security headers disabled in development

### 3. CORS Configuration

- ✅ Allows all origins (`*`)
- ✅ Supports all HTTP methods
- ✅ Allows all headers

### 4. Rate Limiting

- ✅ Disabled in development mode
- ✅ No request limits applied

### 5. Input Validation

- ✅ JSON validation for request bodies
- ✅ Content-Type validation

## 🏭 Production Mode Testing

To test with full production security:

1. **Stop the current server** (Ctrl+C)

2. **Start with production settings**:

```bash
source .venv/bin/activate
export ENVIRONMENT=production
export AUTH_TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
export AUTH_REQUIRED=true
export RATE_LIMIT_ENABLED=true
export SECURITY_HEADERS_ENABLED=true
uvicorn api.app:app --host 127.0.0.1 --port 8000
```

3. **Test with authentication**:

```bash
# This will fail without token
curl -X POST http://127.0.0.1:8000/api/v1/tree/roots \
  -H "Content-Type: application/json" \
  -d '{"label": "Test"}'

# This will succeed with token
curl -X POST http://127.0.0.1:8000/api/v1/tree/roots \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{"label": "Test"}'
```

## 📊 Available Endpoints

### Health & Status

- `GET /api/v1/health` - Comprehensive health check
- `GET /api/v1/live` - Liveness probe
- `GET /api/v1/ready` - Readiness probe

### Tree Management

- `GET /api/v1/tree/roots` - List root nodes
- `POST /api/v1/tree/roots` - Create root node
- `GET /api/v1/tree/{id}` - Get node details
- `PUT /api/v1/tree/{id}` - Update node
- `DELETE /api/v1/tree/{id}` - Delete node

### Import/Export

- `POST /api/v1/import/preview` - Preview import
- `POST /api/v1/import` - Apply import
- `GET /api/v1/export` - Export data

### Conflicts Resolution

- `GET /api/v1/conflicts/scan` - Scan for conflicts
- `POST /api/v1/conflicts/resolve` - Resolve conflicts

## 🔍 Monitoring & Logs

### View Server Logs

The server is running with structured logging. Look for:

- ✅ Security events
- ✅ Request/response logging
- ✅ Error tracking
- ✅ Performance metrics

### Check Database

```bash
sqlite3 /tmp/lorien_test.db "SELECT COUNT(*) FROM nodes;"
```

## 🛠️ Development Tools

### Test Scripts Available

- `test_security_features.py` - Basic security testing
- `test_production_security.py` - Production security testing

### Environment Variables

- `ENVIRONMENT` - development/production
- `AUTH_REQUIRED` - true/false
- `AUTH_TOKEN` - Bearer token for authentication
- `RATE_LIMIT_ENABLED` - true/false
- `SECURITY_HEADERS_ENABLED` - true/false
- `CORS_ORIGINS` - Comma-separated origins

## 📝 Notes

- **Development Mode**: Authentication is optional, security features are relaxed
- **Production Mode**: Authentication required for write operations, full security enabled
- **Database**: Using `/tmp/lorien_test.db` for testing
- **Logging**: Structured JSON logging with request tracing
- **CORS**: Configured for cross-origin requests

## 🆘 Troubleshooting

### Server Not Starting

```bash
# Check if port is in use
lsof -i :8000

# Kill existing process
pkill -f "uvicorn api.app"
```

### Database Issues

```bash
# Check database file
ls -la /tmp/lorien_test.db

# Reset database
rm /tmp/lorien_test.db
```

### Authentication Issues

```bash
# Check environment variables
env | grep -E "(AUTH|ENVIRONMENT)"
```

Happy testing! 🎉
