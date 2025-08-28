# Phase 6 Run Instructions

## 🚀 Quick Start

### 1) Apply Database Migration
```bash
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

### 2) Start the API Server
```bash
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

### 3) Start Streamlit Adapter
```bash
# In a new terminal
cd /home/jharm/Lorien
source venv/bin/activate
streamlit run ui_streamlit/app.py
```

**Expected Output:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

## 🧪 Testing

### Run All Tests
```bash
source venv/bin/activate
python -m pytest tests/ -v
```

### Run Phase 6 Specific Tests
```bash
# Forbidden imports test
python -m pytest tests/test_streamlit_forbidden_imports.py -v

# E2E smoke test
python -m pytest tests/test_tree_upsert_smoke.py -v

# CSV contract test
python -m pytest tests/test_csv_contract.py -v
```

## 🌐 LAN Configuration

### Enable LAN Access
```bash
export CORS_ALLOW_ALL=true
python main.py
```

### Test LAN Connectivity
```bash
# From another device on the same network
curl http://<your-lan-ip>:8000/api/v1/health
```

### Android Emulator
```
API Base URL: http://10.0.2.2:8000
```

### Physical Device
```
API Base URL: http://<your-lan-ip>:8000
```

## 📱 Flutter Integration

### Set Base URL
```bash
# In your Flutter app's .env file
LORIEN_API_BASE=http://localhost:8000
# or for LAN
LORIEN_API_BASE=http://192.168.1.100:8000
```

### Test Flutter Connection
```bash
# Verify API is accessible
curl http://localhost:8000/api/v1/health
```

## 🔍 Verification Checklist

### API Endpoints
- [ ] `GET /api/v1/health` returns version and db_path
- [ ] `GET /llm/health` returns 503 (LLM disabled)
- [ ] `GET /flags/audit/` returns empty array initially
- [ ] `POST /flags/audit/` creates audit records
- [ ] `GET /calc/export` returns CSV with canonical headers

### Streamlit Pages
- [ ] Editor: 5 child slots with atomic upsert
- [ ] Parent Detail: missing slots display and next-incomplete jump
- [ ] Flags: search and assign with user tracking
- [ ] Calculator: CSV export with header preview
- [ ] Settings: API base URL config and health viewer
- [ ] Triage: leaf-only editing enforcement

### Database
- [ ] `red_flag_audit` table exists with proper indexes
- [ ] Foreign key constraints are enabled
- [ ] Exactly 5 children invariant enforced

## 🚨 Troubleshooting

### Common Issues

1. **Migration Fails**
   ```bash
   # Check database path
   echo $DB_PATH
   # Ensure database directory exists
   mkdir -p ~/.local/share/lorien
   ```

2. **API Won't Start**
   ```bash
   # Check port availability
   netstat -tlnp | grep :8000
   # Kill existing process if needed
   pkill -f "python main.py"
   ```

3. **CORS Issues**
   ```bash
   # Verify CORS setting
   echo $CORS_ALLOW_ALL
   # Set if needed
   export CORS_ALLOW_ALL=true
   ```

4. **Streamlit Import Errors**
   ```bash
   # Check Python path
   python -c "import sys; print(sys.path)"
   # Install missing dependencies
   pip install -r requirements.txt
   ```

### Debug Commands

```bash
# Check API health
curl -s http://localhost:8000/health | jq .

# Test audit endpoint
curl -s http://localhost:8000/flags/audit/ | jq .

# Test CSV export
curl -s http://localhost:8000/calc/export | head -1

# Check database schema
sqlite3 ~/.local/share/lorien/app.db ".schema red_flag_audit"
```

## 📊 Performance Monitoring

### API Response Times
```bash
# Test endpoint performance
time curl -s http://localhost:8000/health > /dev/null
time curl -s http://localhost:8000/flags/audit/ > /dev/null
```

### Database Performance
```bash
# Check database size
ls -lh ~/.local/share/lorien/app.db

# Check audit table size
sqlite3 ~/.local/share/lorien/app.db "SELECT COUNT(*) FROM red_flag_audit;"
```

## 🎯 Phase 6 Success Criteria

- [ ] `/health` and `/api/v1/health` show {status, version, db_path}
- [ ] CORS_ALLOW_ALL=true enables LAN access
- [ ] Streamlit pages perform only API calls
- [ ] Editor supports exactly 5 child slots with atomic upsert
- [ ] Parent Detail shows missing slots and next-incomplete jump
- [ ] Flags search + assign works with audit logging
- [ ] Calculator export shows canonical CSV headers
- [ ] Triage editing is leaf-only enforced
- [ ] All new tests pass
- [ ] E2E smoke test confirms upsert readback

**Phase 6 is complete when all checkboxes are checked!** ✅
