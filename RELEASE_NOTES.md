# Lorien Release Notes

## v6.8.0-beta.1 (Phase-6 Implementation)

**Release Date**: TBD  
**Commit SHA**: TBD  
**Phase**: 6 - Canon Guardrails & Feature Parity

### 🚀 Major Features

#### Canon Guardrails Enforcement
- **Exactly 5 Children Rule**: All parent nodes must have exactly 5 children. Import/create/update operations now enforce this rule with 422 responses for violations.
- **CSV V1 Contract**: Frozen 8-column format with exact header validation. Any header drift results in 422 with precise error context.
- **Outcomes Content Limits**: ≤7 words per field with regex validation `^[A-Za-z0-9 ,\-]+$`.
- **LLM Gating**: LLM integration is OFF by default and gated by `/api/v1/llm/health` endpoint.

#### Environment Configuration
- **LORIEN_DB_PATH**: Configurable database path with automatic parent directory creation.
- **LLM_ENABLED**: Environment toggle for LLM functionality (default: false).
- **CORS_ALLOW_ALL**: Toggle for development/LAN access (default: false).

#### API Dual-Mount
- **Health Endpoint**: Available at both `/health` and `/api/v1/health` for connectivity source of truth.
- **Versioned API**: All endpoints mounted under `/api/v1` prefix with root fallback.

### 🔧 Backend Improvements

#### Red-Flag Bulk Operations
- **Bulk Attach/Detach**: Atomic operations for managing multiple red flags per node.
- **Audit Trail**: Complete audit logging for all red flag operations.
- **Idempotent Operations**: Safe to retry without duplicate effects.

#### Import Job Management
- **Job States**: Track import jobs through queued → processing → done/failed states.
- **Structured Logging**: Replace print statements with proper logging throughout.
- **422 Hard-Reject**: Precise error responses for CSV header mismatches.

#### Database Enhancements
- **WAL Mode**: Write-Ahead Logging enabled by default for data integrity.
- **Foreign Key Constraints**: Enforced at connection level.
- **Import Jobs Table**: New table for tracking import operations.

### 🎨 Flutter UI Enhancements

#### Health & Connectivity
- **Health Badge**: Real-time API status indicator.
- **Settings/About**: Display tested URL and health response snippet.
- **LAN Helper Text**: Guidance for mobile/LAN development.

#### Outcomes Editor
- **Leaf-Only Access**: Editor visible only on leaf nodes with guard dialog for non-leaves.
- **Word Counter**: Live validation for ≤7 words per field.
- **Regex Enforcement**: Input validation with inline error display.
- **LLM Integration**: "LLM Fill" button gated by health endpoint status.

#### Navigation & Workflow
- **Skip to Incomplete**: Button to navigate to next incomplete parent.
- **Red-Flag Assigner**: Search, multi-select, and bulk operations interface.
- **Workspace Import/Export**: Excel import with precise error reporting and CSV export.

#### Accessibility
- **Small Screen Support**: All primary actions accessible at 320px width.
- **Screen Reader**: Proper semantic labels and field associations.
- **High Contrast**: Dark mode and 200% text scale support.

### 📊 Streamlit Parity

#### Admin Interface
- **Skip to Incomplete**: Button for navigating incomplete parents.
- **Red-Flag Management**: Search and bulk operations interface.
- **Export Functions**: CSV and XLSX export capabilities.
- **Performance**: Client-side filtering <100ms on ~5k rows.

### 🧪 Testing & Quality

#### Automated Tests
- **Health & LLM**: Environment-based testing for health endpoints.
- **Children Enforcement**: Validation of 5-children rule.
- **CSV Contract**: Header validation and error context testing.
- **Red-Flag Operations**: Bulk operations and audit verification.
- **Import Jobs**: State machine and failure handling tests.

#### Manual Verification
- **Health Endpoints**: Dual-mount verification.
- **LLM Gating**: Environment toggle testing.
- **CORS Behavior**: Origin restriction testing.
- **Import Validation**: Header mismatch error handling.

### 📚 Documentation

#### New Documentation
- **ENV.md**: Comprehensive environment configuration guide.
- **Makefile**: Development workflow automation.
- **Release Notes**: This document with implementation details.

#### Updated Documentation
- **API Endpoints**: New red-flag and import job endpoints.
- **Error Responses**: 422 validation error formats.
- **Environment Variables**: Complete configuration reference.

### 🔒 Security & Compliance

#### Data Validation
- **Input Sanitization**: Strict validation for all user inputs.
- **CSV Schema**: Enforced column structure prevents injection.
- **Content Limits**: Bounded field sizes and character sets.

#### Audit & Logging
- **Red-Flag Audit**: Complete trail of all flag operations.
- **Import Jobs**: Track all import operations with states.
- **Structured Logging**: Consistent log format across all components.

### 🚨 Breaking Changes

#### API Changes
- **Children Validation**: All children operations now require exactly 5 slots.
- **CSV Headers**: Import requires exact V1 contract headers.
- **LLM Endpoints**: Health endpoint now returns 503 when disabled.

#### Environment Variables
- **LORIEN_DB_PATH**: New required variable for database location.
- **LLM_ENABLED**: Must be explicitly set to true for LLM functionality.
- **CORS_ALLOW_ALL**: New variable for development/LAN access.

### 📋 Migration Guide

#### Database Migration
```bash
# Run migrations to add new tables
python storage/migrate.py

# Verify schema updates
sqlite3 your_database.db ".schema import_jobs"
```

#### Environment Setup
```bash
# Set required environment variables
export LORIEN_DB_PATH=/path/to/your/database.db
export LLM_ENABLED=false  # or true if using LLM
export CORS_ALLOW_ALL=false  # or true for development

# Start server
uvicorn api.app:app --host 127.0.0.1 --port 8000
```

#### Flutter App Updates
```bash
# Update API base URL in Flutter app
cd ui_flutter
flutter run -d linux --dart-define=API_BASE_URL=http://127.0.0.1:8000/api/v1
```

### 🔮 Future Directions

#### Phase 7 (Planned)
- **Mobile Support**: iOS and Android app builds.
- **Advanced LLM**: Enhanced triage suggestions and validation.
- **Performance**: Query optimization and caching improvements.
- **Analytics**: Enhanced metrics and reporting.

#### Beta Testing Goals
- **Multi-Device**: Test across different screen sizes and platforms.
- **Performance**: Validate <100ms response times for key operations.
- **Error Handling**: Verify 422 responses provide actionable feedback.
- **Accessibility**: Ensure compliance with WCAG guidelines.

### 🐛 Known Issues

#### Current Limitations
- **Import Processing**: Excel import validation only, full processing TBD.
- **LLM Integration**: Requires local model file when enabled.
- **Mobile**: Flutter app currently desktop-only.

#### Workarounds
- **Import Issues**: Use CSV format for immediate data import.
- **LLM Disabled**: Set `LLM_ENABLED=false` for production use.
- **CORS Issues**: Set `CORS_ALLOW_ALL=true` for development/LAN access.

### 📞 Support

#### Getting Help
- **Documentation**: Check `docs/` directory for detailed guides.
- **Issues**: Report bugs via GitHub issues with reproduction steps.
- **Discussions**: Use GitHub discussions for questions and feature requests.

#### Contributing
- **Development**: Follow the development workflow in `AGENTS.md`.
- **Testing**: Run `make test` before submitting changes.
- **Code Style**: Use `make format` and `make lint` for consistency.

---

**Note**: This is a beta release. Please report any issues or unexpected behavior. The API contract is stable for v6.8.0, but implementation details may change before final release.
