# Phase 6: Red-Flag Audit + CSV Export Implementation

## 🎯 Overview

This phase implements an append-only Red-Flag Audit system and CSV export functionality for the Lorien decision tree application. The audit system tracks all flag assignments and removals, while CSV export provides data export capabilities for both Symptoms and Calculator screens.

## 📦 Features Implemented

### 1. Red-Flag Audit System
- **Append-only audit table** with proper indexing
- **Dual-mount API endpoints** at `/flags/audit` and `/api/v1/flags/audit`
- **Internal audit calls** integrated into flag assignment/removal services
- **Comprehensive filtering** by node, flag, user, and time

### 2. CSV Export System
- **API endpoints** for calculator and tree data export
- **Flutter UI components** with platform-specific behavior
- **Desktop save** and **mobile share sheet** support
- **Frozen header contract** ensuring consistency

### 3. Enhanced API
- **Dual-mount support** for all endpoints
- **Improved CORS configuration** with environment toggle
- **Better error handling** and validation

## 🛠 Installation & Setup

### Prerequisites
- Python 3.8+
- Flutter SDK
- SQLite3

### 1. Apply Database Migration

```bash
# Run the migration script
cd /home/jharm/Lorien
source venv/bin/activate
python storage/migrate.py
```

**Expected Output:**
```
🔄 Lorien Database Migration Runner
========================================
Database: /home/jharm/.local/share/lorien/app.db
Found 1 migration(s) to apply
Running migration: 001_add_red_flag_audit.sql
✅ Migration 001_add_red_flag_audit.sql applied successfully
========================================
Migration Summary: 1/1 successful
🎉 All migrations completed successfully!
```

### 2. Start the API Server

```bash
# Start the FastAPI server
cd /home/jharm/Lorien
source venv/bin/activate
python main.py
```

**Expected Output:**
```
Starting Decision Tree API server...
Host: 127.0.0.1
Port: 8000
Reload: true
Version: v6.7.0
Docs: http://127.0.0.1:8000/docs
API v1 Health: http://127.0.0.1:8000/api/v1/health
```

## 🧪 Testing & Verification

### 1. Run All Tests

```bash
# Run the complete test suite
cd /home/jharm/Lorien
source venv/bin/activate
python -m pytest tests/ -v
```

### 2. Test Audit Endpoints

```bash
# Test audit list (should be empty initially)
curl -s http://localhost:8000/flags/audit/ | jq .
curl -s http://localhost:8000/api/v1/flags/audit/ | jq .

# Create an audit record
curl -s -X POST http://localhost:8000/flags/audit/ \
  -H 'Content-Type: application/json' \
  -d '{"node_id":1,"flag_id":1,"action":"assign","user":"test"}' | jq .

# Verify the record was created
curl -s "http://localhost:8000/flags/audit/?node_id=1&limit=5" | jq .
```

### 3. Test CSV Export

```bash
# Test calculator export
curl -s http://localhost:8000/calc/export -o calc_export.csv
head -5 calc_export.csv

# Test tree export
curl -s http://localhost:8000/tree/export -o tree_export.csv
head -5 tree_export.csv

# Verify headers
grep "Diagnosis,Node 1,Node 2,Node 3,Node 4,Node 5" *.csv
```

## 📱 Flutter Integration

### 1. Dependencies

Add these to your `pubspec.yaml`:

```yaml
dependencies:
  http: ^1.1.0
  path_provider: ^2.1.1
  share_plus: ^7.2.1
```

### 2. Usage Example

```dart
import 'package:your_app/widgets/csv_export_button.dart';

// Calculator export
final calcEndpoint = Uri.parse('$baseUrl/calc/export');
CsvExportButton(
  endpoint: calcEndpoint,
  fileName: 'lorien_calc_export.csv',
  label: 'Export Calculator CSV',
);

// Tree export
final treeEndpoint = Uri.parse('$baseUrl/tree/export');
CsvExportButton(
  endpoint: treeEndpoint,
  fileName: 'lorien_tree_export.csv',
  label: 'Export Tree CSV',
);
```

### 3. Platform Behavior

- **Desktop**: Files saved to temporary directory with success dialog
- **Mobile**: Opens native share sheet for file sharing
- **Error Handling**: Shows error messages for failed exports

## 🌐 LAN Configuration Tips

### Android Emulator
```
API Base URL: http://10.0.2.2:8000
```

### Physical Device (Same Network)
```
API Base URL: http://<LAN-IP>:8000
```

### iOS Simulator
```
API Base URL: http://localhost:8000
```

### Physical iOS Device (Same Network)
```
API Base URL: http://<LAN-IP>:8000
```

## 🔧 Configuration

### Environment Variables

```bash
# CORS Configuration
CORS_ALLOW_ALL=true  # Allow all origins (development)
CORS_ALLOW_ALL=false # Restrict to localhost (production)

# LLM Configuration
LLM_ENABLED=true     # Enable LLM features
LLM_ENABLED=false    # Disable LLM features

# Database Configuration
LORIEN_DB_PATH=/path/to/custom/database.db
```

### API Base URL Configuration

The Flutter app can be configured with different API base URLs:

1. **Development**: `http://localhost:8000`
2. **Android Emulator**: `http://10.0.2.2:8000`
3. **Physical Device**: `http://<your-lan-ip>:8000`

## 📊 API Endpoints

### Health & Status
- `GET /health` - Root health check
- `GET /api/v1/health` - API v1 health check
- `GET /llm/health` - LLM health check
- `GET /api/v1/llm/health` - API v1 LLM health check

### Red Flag Audit
- `GET /flags/audit/` - List audit records
- `POST /flags/audit/` - Create audit record
- `GET /api/v1/flags/audit/` - API v1 list audit records
- `POST /api/v1/flags/audit/` - API v1 create audit record

### CSV Export
- `GET /calc/export` - Calculator CSV export
- `GET /tree/export` - Tree data CSV export
- `GET /api/v1/calc/export` - API v1 calculator export
- `GET /api/v1/tree/export` - API v1 tree export

### Flag Management
- `POST /flags/assign` - Assign red flag to node
- `DELETE /flags/remove` - Remove red flag from node
- `GET /flags/search?q=<query>` - Search red flags
- `POST /api/v1/flags/assign` - API v1 assign flag
- `DELETE /api/v1/flags/remove` - API v1 remove flag

## 🚨 Troubleshooting

### Common Issues

1. **Migration Fails**
   - Ensure database exists and is writable
   - Check SQLite version compatibility
   - Verify migration file exists

2. **API Endpoints Return 404**
   - Check if server is running
   - Verify endpoint paths are correct
   - Check router mounting in `api/app.py`

3. **CSV Export Fails**
   - Verify database has data
   - Check file permissions for temporary directory
   - Ensure proper content-type headers

4. **Flutter Export Issues**
   - Verify API base URL configuration
   - Check network connectivity
   - Ensure proper permissions for file access

### Debug Commands

```bash
# Check database schema
sqlite3 /home/jharm/.local/share/lorien/app.db ".schema red_flag_audit"

# Check audit records
sqlite3 /home/jharm/.local/share/lorien/app.db "SELECT * FROM red_flag_audit LIMIT 5;"

# Check API routes
curl -s http://localhost:8000/docs | grep -i "flags/audit"

# Test CORS
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: X-Requested-With" \
  -X OPTIONS http://localhost:8000/health
```

## 📈 Performance Considerations

### Audit Table
- **Indexes**: Optimized for node_id, flag_id, and timestamp queries
- **Retention**: Consider implementing cleanup for old audit records
- **Bulk Operations**: Audit logging adds minimal overhead

### CSV Export
- **Streaming Response**: Large exports don't consume memory
- **Caching**: Consider implementing response caching for static data
- **Compression**: Large exports can benefit from gzip compression

## 🔒 Security Notes

- **Audit Trail**: All flag operations are logged for compliance
- **Input Validation**: All endpoints validate input data
- **CORS**: Configurable CORS policy for different environments
- **User Tracking**: Audit records include user identification when provided

## 📝 Future Enhancements

1. **Audit Cleanup**: Automated cleanup of old audit records
2. **Export Formats**: Additional export formats (Excel, JSON)
3. **Bulk Operations**: Batch flag assignments with audit logging
4. **User Management**: Enhanced user authentication and authorization
5. **Audit Reports**: Web-based audit report generation

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the test output for specific error messages
3. Verify all prerequisites are met
4. Check the API documentation at `/docs` endpoint

---

**Phase 6 Complete!** 🎉

The Lorien application now has comprehensive audit logging and CSV export capabilities, making it ready for production use with proper compliance tracking.
