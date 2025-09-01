# Release Notes - Version 0.6.1

## Overview
Phase-6 UI Core has been successfully merged to main with comprehensive API integration, file handling, and production-ready features.

## What's New
- **Complete API Integration**: All features now have strongly-typed API clients
- **File Operations**: Import/export functionality with proper error handling
- **Settings Persistence**: Base URL configuration saved via SharedPreferences
- **About/Status Page**: Real-time connection status and contract verification
- **Form Validation**: Comprehensive field validation with real-time feedback
- **LLM Integration**: Health-gated AI suggestions with proper error handling
- **CI/CD Pipeline**: GitHub Actions workflow for automated testing

## Technical Improvements
- **Dio Interceptors**: Dynamic base URL handling for all API calls
- **Error Mapping**: Pydantic 422 responses properly mapped to UI fields
- **State Management**: Riverpod with proper persistence and reactivity
- **Navigation**: GoRouter with clean URL structure and deep linking
- **Testing**: 37 comprehensive tests covering contracts, widgets, and units

## Contracts Enforced
- ✅ 5 children exactly per parent (never coerced/hidden)
- ✅ 8-column export header (Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions)
- ✅ Client base path: /api/v1 via Dio interceptor
- ✅ Connectivity SoT: GET /health only (200 ⇒ Connected)
- ✅ Outcomes: ≤7 words; regex ^[A-Za-z0-9 ,\-]+$; 422 surfaced under fields
- ✅ LLM: OFF by default; Fill suggests only; apply=true on non-leaf ⇒ 422 + suggestions at top level

## Build Artifacts
- Android APK ready for distribution
- Linux desktop build available
- Web build (optional) for browser access

## Next Steps
- Backend integration testing
- User acceptance testing
- Production deployment preparation

## Breaking Changes
None - this is a feature-complete implementation that maintains all existing contracts.

## Known Issues
- Placeholder logo file needs to be replaced with actual JAD branding
- Some deprecated Flutter APIs (will be addressed in future updates)

## Support
For issues or questions, please refer to the project documentation or create an issue in the repository.
