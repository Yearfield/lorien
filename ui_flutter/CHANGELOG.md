# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - Phase-6 UI Core

### Added
- Material 3 theme with brand slate color (#2E3B3D)
- GoRouter navigation with clean URL structure
- Riverpod state management
- Dio HTTP client with proper error handling
- Health service with /health connectivity SoT
- Settings screen with base URL configuration and connection testing
- Outcomes list and detail screens with validation (≤7 words + regex)
- Calculator screen with chained dropdowns and export functionality
- Flags screen with search and assigner sheet
- Workspace screen with import/export and header mismatch table
- Field validators with real-time word counting
- Error mapping for Pydantic 422 responses
- LLM gating with health probe
- Connected badge for real-time connection status
- Comprehensive test suite (unit, contract, widget tests)

### Changed
- Updated to Flutter 3.x compatibility
- Migrated from Provider to Riverpod
- Improved error handling and user feedback
- Enhanced accessibility and responsive design

### Fixed
- Async context safety issues
- Form validation and error display
- Navigation state management
- Theme consistency across light/dark modes

### Technical
- All non-negotiable contracts enforced:
  - 5 children exactly per parent
  - 8-column export header (Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions)
  - Client base path /api/v1
  - Connectivity SoT via /health endpoint
  - Outcomes fields ≤7 words with regex pattern
  - LLM OFF by default with suggestions-only workflow
