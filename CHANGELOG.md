# Changelog

All notable changes to the Lorien project will be documented in this file.

## v6.8.0-beta.1 — 2025-09-01

### 🚀 New Features
- **Flutter Parity**: Complete calculator chained dropdowns and workspace export functionality
- **Enhanced Import UX**: Progress indicators, detailed error surfacing, and success metrics
- **Performance Improvements**: Comprehensive caching system with TTL and smart invalidation
- **Backup/Restore**: One-click database backup and restore with integrity checks
- **Audit Enhancement**: Branch-scoped audit history and retention management

### 🔧 API Enhancements
- **Flags Preview**: `GET /flags/preview-assign` for cascade effect preview
- **Audit Branch Scope**: `GET /flags/audit?branch=true` for descendant audit history
- **Backup Operations**: `POST /backup`, `POST /restore`, `GET /backup/status`
- **Health Metrics**: Optional non-PHI counters when `ANALYTICS_ENABLED=true`

### 🎨 UI Improvements
- **Streamlit Workspace**: Enhanced import/export, backup/restore, cache management
- **Progress Indicators**: Visual feedback during import operations
- **Error Surfacing**: Detailed validation errors and per-error counts
- **Cache Management**: Statistics, performance testing, and manual control

### 📱 Mobile Experience
- **Calculator Widget**: Chained dropdowns with reset-on-change behavior
- **Export Buttons**: Platform-specific save/share for CSV and XLSX
- **Workspace Screen**: Health information and export functionality
- **Platform Support**: Android emulator, iOS simulator, and physical devices

### 🏗️ Architecture
- **CSV Contract Frozen**: 8-column header format locked and enforced
- **Dual Mounts**: All endpoints available at `/` and `/api/v1`
- **LLM Safety**: OFF by default, guidance-only when enabled
- **Audit Retention**: 30-day/50k row cap with nightly rotation

### 🧪 Testing
- **Widget Tests**: Comprehensive Flutter component testing
- **API Tests**: Flags preview and audit branch endpoints
- **CSV Header Tests**: Contract enforcement validation
- **Performance Tests**: Cache effectiveness and endpoint response times

### 📚 Documentation
- **Pre-Beta Tracker**: Execution status and completion tracking
- **SLA Documentation**: Severity levels and response procedures
- **Rollback Plan**: Comprehensive recovery procedures
- **Demo Scripts**: Quick demonstration guides for stakeholders

### 🔒 Security & Compliance
- **No Direct DB Access**: Streamlit remains API-only adapter
- **Input Validation**: Enhanced validation on all endpoints
- **Audit Trail**: Comprehensive logging of flag operations
- **Medical Disclaimer**: LLM integration remains guidance-only

### 🚦 Performance Targets
- **Health Endpoint**: <100ms response time
- **Stats Endpoints**: <100ms response time
- **Import Operations**: <30s for typical files
- **Export Operations**: <10s for typical datasets

### 🌐 Platform Support
- **Web**: Streamlit UI with modern browser support
- **Desktop**: Flutter desktop application
- **Mobile**: Flutter iOS and Android applications
- **API**: RESTful endpoints with JSON responses

## v6.7.x — Previous Versions

[Previous changelog entries would go here]

---

## Release Notes

For detailed information about this release, see [docs/Release_Notes_v6.8.0-beta.1.md](docs/Release_Notes_v6.8.0-beta.1.md).

## Migration Guide

No database migrations are required for this release. The application will automatically create necessary backup directories and audit retention views.

## Known Issues

- [Document any known issues here]
- [Include workarounds if available]

## Support

- **Engineering**: Slack #lorien-engineering
- **Beta Users**: Slack #lorien-beta
- **Documentation**: [Link to docs]
- **Issues**: [Link to issue tracker]
