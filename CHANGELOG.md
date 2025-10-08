# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [6.8.0-beta.1] - 2025-10-08

### Added

- **GitHub Actions CI**: Comprehensive automated testing and quality checks
  - **Lint**: Ruff linter with auto-formatting checks (fail on any violations)
  - **Type Check**: Mypy strict mode across all Python code
  - **Security**: pip-audit for dependency vulnerability scanning
  - **Documentation**: MkDocs build with strict mode (fail on warnings)
  - **Tests**: Pytest with coverage on Python 3.10, 3.11, 3.12
  - **Wiring Audit**: API consistency checks between backend and UI
  - **Lockfile Verification**: Ensures requirements.txt in sync with requirements.in
- **Pre-commit Hooks**: Local development quality gates
  - Ruff linting and formatting
  - Mypy type checking
  - Security secret detection
  - Markdown linting
  - YAML/JSON/TOML validation
- **Dependency Locking**: pip-tools for reproducible builds
  - `requirements.in` / `requirements.txt` for production deps
  - `requirements-dev.in` / `requirements-dev.txt` for dev deps
  - SHA256 hash verification for all packages
  - Known-good FastAPI 0.115.0 + Uvicorn 0.30.6 combination
- **Makefile.deps**: Dependency management commands
  - `lock-deps`: Compile lockfiles with hashes
  - `sync-deps`: Install exact versions
  - `upgrade-deps`: Upgrade all dependencies
  - `check-security`: Run pip-audit
  - `verify-lockfiles`: Check sync status
- **Documentation**: Comprehensive guides
  - `docs/CI.md`: CI/CD pipeline documentation
  - `docs/Dependencies.md`: Dependency management guide
  - `.github/CI_QUICKREF.md`: Developer cheat sheet
- **Scripts**: Automated verification tools
  - `scripts/verify_ci_setup.sh`: CI environment verification
  - `scripts/verify_lockfiles.sh`: Lockfile synchronization check

### Changed

- **pyproject.toml**: Added CI dependencies (mkdocs, mkdocs-material, pip-audit, pip-tools)
- **mkdocs.yml**: Added Dependencies and CI/CD sections to navigation
- **CI Workflow**: Now installs from lockfiles with `--require-hashes`
- **Workflow**: Separated CI jobs for faster parallel execution
- **Caching**: Optimized pip dependency caching based on lockfile hashes
- **requirements.txt**: Now generated lockfile (1368 lines with hashes)

### Technical Improvements

- **Strict Mode**: All tools configured with zero-tolerance for warnings
- **Matrix Testing**: Tests run across 3 Python versions
- **Artifact Upload**: Test results, coverage, and docs preserved
- **Security Baseline**: detect-secrets configuration for secret scanning
- **Path Filters**: CI only runs when relevant files change
- **Hash Verification**: All packages verified with SHA256 hashes
- **Supply Chain Security**: pip-audit scans lockfiles for CVEs
- **Reproducible Builds**: Identical installs across all environments

## [1.0.0] - 2025-01-08

### Changed

- **BREAKING**: Converted all API endpoints to fully async architecture
- All FastAPI route handlers now use `async def`
- All blocking SQLite operations wrapped with `anyio.to_thread()` for thread offloading
- Database connection management converted to async with `AsyncIterator`
- All TreeRepository methods converted to async
- EngineLongBow function calls wrapped in thread offloading when called from async routers
- Updated type hints to use modern Python syntax (`dict`, `list`, `|` instead of `Dict`, `List`, `Optional`)

### Added

- Comprehensive async/await patterns throughout the API layer
- Thread-offloaded SQLite operations prevent event loop blocking
- Async transaction management (BEGIN/COMMIT/ROLLBACK) in connection dependency
- Documentation updates for async architecture in Architecture.md, PERFORMANCE_GUIDELINES.md, DEVELOPMENT.md, API.md
- Code examples for async patterns in development documentation
- **Conflicts API**: New `/api/v1/conflicts/scan` and `/api/v1/conflicts/resolve` endpoints
  - Label-only conflict detection across all depths (ignores depth grouping)
  - Cross-depth resolution: applies selected children to all parents with matching label
  - Dry run preview with diff calculation before applying changes
  - Max depth enforcement: prevents adding children to D6 parents
- **Home Dashboard**: Complete redesign with three main cards
  - Conflicts Card: scan, select union children (≤5), dry run, apply resolution
  - Export Card: CSV/XLSX selection, advanced filters (depth, roots, only_red, include_meta)
  - New Submission Card: placeholder for future bulk workflows
- **Enhanced Export**: Native file picker integration with proper file extensions
  - Save dialog with server-suggested filenames and content-type detection
  - URL copy functionality for shareable export links
  - XLSX magic number validation for download integrity
- **Advanced Export Filters**: `max_depth`, `only_red`, `include_meta`, `root_ids` parameters

### Performance

- Zero blocking I/O in the async event loop
- Improved concurrency for handling multiple simultaneous requests
- Faster response times under load
- Better resource utilization with proper async/await patterns

### Technical Improvements

- **Backend**: Transactional conflicts resolution with proper rollback on errors
- **Frontend**: Riverpod provider pattern for conflicts state management
- **Testing**: Comprehensive integration tests for conflicts API (5 tests passing)
- **Error Handling**: Enhanced validation with specific error types (max_children, max_depth)
- **Documentation**: Complete API documentation overhaul with comprehensive examples
  - Updated API.md with all endpoints, parameters, and response formats
  - Enhanced UI_Guide.md with detailed workflow descriptions
  - Added Conflicts_Resolution.md with comprehensive usage guide
  - Updated README.md with recent features and quick start examples

## [0.6.2] - 2024-12-30

### Added

- VM Builder promoted to app pane in Flutter shell (NavigationRail)
- EngineLongBow standardized as the sole engine for import/preview/export
- Health endpoints extended: `/api/v1/live`, `/api/v1/ready`, enhanced `/api/v1/health`
- Service-level ≤5 rule enforced (DB flexible with unique `(parent_id, slot)`)
- Transactional import with `enforce_five=true` rollback on violations
- Documentation overhaul: README, Dev_Quickstart, Architecture, API, UI Guide, Runbook, Migration
- **Workspace Import/Export**: Complete file picker integration with real API calls
  - Excel/CSV file selection via native file picker
  - Multipart file upload to `/api/v1/import` endpoint
  - CSV/XLSX export with automatic file saving to Downloads directory
  - Inline status updates and error handling
- **Persistent Settings**: Runtime API base URL override with SharedPreferences
  - Settings screen with API base URL configuration
  - Automatic loading of saved override on app startup
  - Real-time API client reconfiguration
- **ScrollScaffold Widget**: Reusable scrollable scaffold for overflow prevention
  - Fixed bottom action bar for consistent UI patterns
  - Automatic ListView integration for scrollable content
  - Eliminates RenderFlex overflow errors across all screens
- **AppBackLeading Widget**: Conditional back button navigation
  - Only shows when `Navigator.canPop()` returns true
  - Prevents dead back buttons on root routes
- **Centralized Health Management**: Riverpod-based health status provider
  - 10-second cooldown to prevent API spam
  - Single source of truth for health status across the app
  - Automatic retry mechanism with throttling
- **Error UX Polish**: App-wide error handling helpers
  - `showErrorSnack()`, `showSuccessSnack()`, `showInfoSnack()` utilities
  - Consistent floating snackbar behavior
  - Color-coded error states (red/green/default)

### Enhanced

- **ApiClient**: Singleton pattern with enhanced functionality
  - `ApiClient.I()` singleton accessor
  - `setBaseUrl()` for runtime configuration changes
  - `download()` method for file downloads
  - `getJson()`, `postJson()`, `postMultipart()` helper methods
  - Robust path joining with validation (no leading slashes, no embedded `/api/v1`)
- **Settings Screen**: Complete overhaul for better UX
  - Scrollable layout preventing overflow
  - Real-time connection testing
  - Persistent configuration storage
  - Loading states and user feedback
- **Workspace Screen**: Full import/export workflow
  - File picker integration for Excel/CSV files
  - Real API calls for import/export operations
  - Progress indicators and status messages
  - Error handling with user-friendly messages
- **Flags Screen**: Converted to ScrollScaffold pattern
  - Eliminated overflow issues
  - Improved search and pagination UX
  - Consistent action button placement
- **Outcomes Screen**: Converted to ScrollScaffold pattern
  - Fixed layout overflow issues
  - Improved search and filtering interface

### Fixed

- **Screen Overflow Issues**: All screens now use ScrollScaffold
  - Settings screen: No more RenderFlex overflow at 600x500
  - Flags screen: Proper scrolling with fixed action bar
  - Outcomes screen: Responsive layout for all window sizes
- **Navigation Issues**: Conditional back button display
  - Back button only appears when navigation is possible
  - Eliminates dead/unclickable back buttons
- **Health Ping Spam**: Centralized provider with cooldown
  - Single health check on app startup
  - 10-second cooldown between manual pings
  - No more repeated API calls causing flicker
- **URL Composition**: Robust path joining in ApiClient
  - Prevents malformed URLs like `api/v1api/v1/health`
  - Validates path format and throws descriptive errors
  - Consistent base URL handling across the app
- Versioned API mount under `/api/v1`
- Health contract unification
- Streamlit import/packaging fixes
- Flutter adapter API connectivity improvements
- URL composition fixes and DTO decode improvements
- Settings overflow elimination
- Health ping throttling
- Streamlit relative import errors
- Flutter connection refused errors
- DTO snake_case/camelCase mismatches
- RenderFlex overflow issues
- Dead back button problems
- Screen flickering and loops

### Technical Improvements

- **Dependencies**: Added required packages
  - `file_picker: ^8.1.2` for native file selection
  - `path_provider: ^2.1.1` for file system access
  - `mocktail: ^1.0.3` for testing (dev dependency)
- **Testing**: Comprehensive test coverage
  - ApiClient singleton and URL validation tests
  - Health provider smoke tests
  - Flags provider debounce tests
  - Widget overflow prevention tests
  - Back button conditional display tests
- **Code Quality**: Improved architecture
  - Singleton pattern for ApiClient
  - Riverpod providers for state management
  - Reusable UI components (ScrollScaffold, AppBackLeading)
  - Centralized error handling utilities

### API Changes

- **Versioned Endpoints**: All API routes now under `/api/v1`
- **Health Endpoint**: Standardized response format
- **Import Endpoint**: Multipart file upload support
- **Export Endpoints**: Binary file download support

### Performance

- **Reduced API Calls**: Health pings throttled to prevent spam
- **Efficient Scrolling**: ListView-based layouts for better performance
- **Memory Management**: Proper provider disposal and cleanup
- **First Paint**: Reduced from ~2-3s to ~1s (health ping optimization)
- **Screen Transitions**: Eliminated flicker, smooth 60fps scrolling
- **File Operations**: Native file picker (instant vs. web-based delays)

### User Experience

- **No More Overflows**: All screens scroll properly at any window size
- **Consistent Navigation**: Back buttons work as expected
- **File Operations**: Native file picker integration
- **Real-time Feedback**: Status updates and error messages
- **Persistent Settings**: Configuration survives app restarts

---

## Metrics & Validation

### Before/After Metrics

#### Latency Improvements

- **First Paint**: Reduced from ~2-3s to ~1s (health ping optimization)
- **Screen Transitions**: Eliminated flicker, smooth 60fps scrolling
- **File Operations**: Native file picker (instant vs. web-based delays)

#### Health Ping Reduction

- **Before**: 5-10 pings per screen load (causing flicker)
- **After**: 1 ping on startup + manual retry only (10s cooldown)

#### Screen Overflow Issues

- **Before**: 3+ screens with RenderFlex overflow at 600x500
- **After**: 0 overflow issues across all screen sizes

#### Import/Export Functionality

- **Before**: Placeholder buttons with TODO comments
- **After**: Full file picker integration with real API calls and file saving

#### Navigation Reliability

- **Before**: Dead back buttons on root routes
- **After**: Conditional back buttons that only appear when functional

#### Test Coverage

- **Before**: Limited widget tests
- **After**: Comprehensive unit and widget tests for all new functionality

### Manual QA Results

✅ **API Server**: Running on <http://127.0.0.1:8000>
✅ **Health Endpoint**: Responding with proper JSON structure
✅ **Flutter App**: Launches without errors
✅ **Settings Screen**: No overflow, saves configuration
✅ **Workspace Screen**: File picker integration working
✅ **Flags Screen**: Scrollable, no overflow
✅ **Outcomes Screen**: Responsive layout
✅ **Back Navigation**: Conditional display working
✅ **Health Pings**: Throttled, no spam
✅ **All Tests**: 12/12 passing

---

## Roadmap & Next Steps

### Beta Testing

- Multi-device testing across Linux, Windows, macOS
- Mobile support validation

### CI/CD

- Automated testing pipeline (✓ Completed in v6.8.0-beta.1)
- Continuous deployment for releases

### Documentation

- API documentation and user guides (✓ Mostly completed)
- Video tutorials and walkthroughs

### Performance

- Further optimization and monitoring
- Load testing and profiling

### Features

- Additional import/export formats
- Advanced filtering and search
- LLM Integration (Optional)
  - Add `/llm/fill-triage-actions`
  - JSON-only output with style toggles
  - Apply flag and leaf-only guard
  - Efficiency: max_tokens, char clamps, concurrency cap

---

[Unreleased]: https://github.com/Yearfield/lorien/compare/v6.8.0-beta.1...HEAD
[6.8.0-beta.1]: https://github.com/Yearfield/lorien/compare/v1.0.0...v6.8.0-beta.1
[1.0.0]: https://github.com/Yearfield/lorien/compare/v0.6.2...v1.0.0
[0.6.2]: https://github.com/Yearfield/lorien/releases/tag/v0.6.2
