# Lorien Release Notes

## v6.8.0-beta.1

### Overview
Major feature release with enhanced API, new endpoints, improved validation, and comprehensive testing. Introduces dictionary administration, enhanced flag management, and performance optimizations.

### New Features

#### 🎯 **Dictionary Administration**
- **NEW**: Full CRUD operations for medical terms
- **Endpoint**: `GET/POST/PUT/DELETE /api/v1/dictionary`
- **Features**: Search, filtering, uniqueness constraints, usage tracking
- **Validation**: Label regex, category validation, code uniqueness

#### 🚩 **Enhanced Flag Management**
- **NEW**: Cascade operations for bulk flag assignment/removal
- **Endpoint**: `POST /api/v1/flags/assign`, `POST /api/v1/flags/remove`
- **Features**: Audit trail, cascade to descendants, idempotent operations
- **Pruning**: Automatic cleanup (≤30 days or ≤50k rows)

#### 🌳 **Tree Navigation**
- **NEW**: `GET /api/v1/tree/path` - Breadcrumbs from root to node
- **NEW**: `GET /api/v1/tree/next-incomplete-parent` - Performance-optimized
- **Features**: CSV header inclusion, depth tracking, path reconstruction

#### 📊 **Health & Monitoring**
- **Enhanced**: `/api/v1/health` with version, WAL, FK status
- **Enhanced**: `/api/v1/llm/health` with top-level JSON and checked_at
- **NEW**: Performance assertions for critical endpoints
- **Features**: Structured logging, error handling improvements

#### 📁 **Outcomes & Validation**
- **NEW**: `PUT /api/v1/outcomes/{node_id}` - Leaf-only validation
- **Enhanced**: Word count (≤7), regex whitelist, prohibited tokens
- **Features**: Legacy fallback support, structured error responses

#### 📤 **Import/Export**
- **Enhanced**: Strict 422 context for CSV schema drift
- **Features**: Detailed mismatch information, first offending column

### API Changes

#### Breaking Changes
- **Health Response**: Now includes `version`, `db`, `features` fields
- **LLM Health**: Top-level JSON structure with `checked_at` UTC timestamp
- **Flag Endpoints**: New response format with `affected` count and `node_ids`

#### New Endpoints
```
GET    /api/v1/tree/path?node_id=<id>
GET    /api/v1/tree/next-incomplete-parent
GET    /api/v1/flags?query=&limit=&offset=
POST   /api/v1/flags/assign
POST   /api/v1/flags/remove
GET    /api/v1/flags/audit?node_id=&limit=&offset=
GET    /api/v1/dictionary?query=&category=&limit=&offset=
POST   /api/v1/dictionary
PUT    /api/v1/dictionary/{id}
DELETE /api/v1/dictionary/{id}
GET    /api/v1/dictionary/{id}/usage?limit=&offset=
PUT    /api/v1/outcomes/{node_id}
```

#### Response Format Updates
- **Health**: `{"ok": true, "version": "6.8.0-beta.1", "db": {...}, "features": {...}}`
- **LLM Health**: Top-level JSON with `checked_at` ending in 'Z'
- **Flags**: `{"affected": int, "node_ids": [int, ...]}`
- **Tree Path**: Includes `csv_header` and padded `nodes` array

### Database Schema Changes

#### New Tables
```sql
-- Dictionary terms
CREATE TABLE dictionary_terms (
    id INTEGER PRIMARY KEY,
    label TEXT NOT NULL,
    category TEXT NOT NULL,
    code TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(label, category),
    UNIQUE(code)
);

-- Node-term associations
CREATE TABLE node_terms (
    node_id INTEGER NOT NULL,
    term_id INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (node_id, term_id)
);

-- Enhanced flags namespace
CREATE TABLE flags (
    id INTEGER PRIMARY KEY,
    label TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE node_flags (
    node_id INTEGER NOT NULL,
    flag_id INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (node_id, flag_id)
);

CREATE TABLE flag_audit (
    id INTEGER PRIMARY KEY,
    node_id INTEGER NOT NULL,
    flag_id INTEGER NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('assign', 'remove')),
    ts TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Performance Improvements

#### Targets Met
- **Next Incomplete Parent**: <100 ms on sample data
- **Tree Path**: <50 ms with CTE-based path reconstruction
- **Health Endpoints**: <50 ms response time
- **Flag Operations**: <100 ms for bulk cascade operations

#### Optimizations
- **Indexes**: Added for dictionary terms, flags, and audit tables
- **Queries**: CTE-based recursive path finding
- **Caching**: Prepared statements for common operations
- **Pruning**: Automated cleanup to maintain performance

### Validation Enhancements

#### Outcomes Validation
- **Word Count**: ≤7 words per field
- **Regex**: `^[A-Za-z0-9 ,\-µ%]+$` (medical symbols allowed)
- **Prohibited Tokens**: Blocks dosing terms (mg, mcg, µg, ml, kg, IU, %, bid, tid, qid, etc.)
- **Empty Rejection**: Post-normalization empty string detection

#### Import Validation
- **Schema Drift**: Hard reject with detailed context
- **Header Matching**: Exact order and case validation
- **Error Context**: `first_offending_row`, `col_index`, expected vs received

### Testing Coverage

#### New Test Files
- `tests/api/test_import_csv_schema.py` - Import validation
- `tests/api/test_outcomes_validation.py` - Outcomes validation
- `tests/api/test_flags.py` - Flag operations
- `tests/api/test_next_incomplete_parent.py` - Tree navigation
- `tests/api/test_tree_path.py` - Path reconstruction
- `tests/api/test_dictionary.py` - Dictionary CRUD
- `tests/ops/test_prune_flags.py` - Pruning operations
- `tests/performance/test_critical_endpoints.py` - Performance assertions

#### Test Coverage
- **Unit Tests**: 31+ test cases for core functionality
- **Integration Tests**: End-to-end API validation
- **Performance Tests**: Timing assertions for critical paths
- **Edge Cases**: Error handling, validation failures, boundary conditions

### Infrastructure

#### Operations
- **NEW**: `ops/prune_flags.py` - Automated flag audit cleanup
- **Enhanced**: `storage/migrate.py` - Multi-migration support
- **Makefile**: Added `prune-flags` target

#### Configuration
- **Version**: Single-sourced in `core/version.py`
- **Environment**: Comprehensive ENV.md documentation
- **API Docs**: Complete endpoint specifications

### Migration Guide

#### For Existing Deployments
1. **Backup Database**: `cp lorien.db lorien.db.backup`
2. **Run Migrations**: `python storage/migrate.py`
3. **Update Environment**: Review ENV.md for new variables
4. **Test Endpoints**: Verify `/api/v1/health` returns version 6.8.0-beta.1

#### Environment Variables
```bash
# Required
export LORIEN_DB_PATH=/path/to/lorien.db

# Optional (defaults shown)
export LLM_ENABLED=false
export LLM_PROVIDER=null
export LLM_MODEL_PATH=""
export CORS_ALLOW_ALL=false
export ANALYTICS_ENABLED=false
```

#### API Client Updates
- **Health Parsing**: Handle new `version`, `db`, `features` fields
- **LLM Health**: Parse top-level JSON with `checked_at` timestamps
- **Flag Operations**: Handle new response format with `affected` count
- **Error Handling**: Process 422 validation errors with field-level detail

### Known Issues
- LLM integration remains stubbed (null provider only)
- Dictionary usage tracking limited to node associations
- Cascade operations may be slow on very deep trees (>10 levels)

### Future Plans
- **v6.8.0-beta.2**: LLM provider implementations (Ollama, GGUF)
- **v6.8.0-beta.3**: Advanced search and filtering
- **v6.9.0**: Mobile app optimizations
- **v7.0.0**: Multi-tenant support

---

**SHA**: [TBD - to be updated after CI green]

**Date**: January 2025

**Compatibility**: Requires clean database migration. No backward compatibility for flag endpoints.