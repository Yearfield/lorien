# Beta Acceptance Checklist (per drop)

## Pre-Deployment Checks

### Environment
- [ ] `ANALYTICS_ENABLED` environment variable set appropriately
- [ ] `DB_PATH` environment variable configured
- [ ] `CORS_ALLOW_ALL` set for LAN testing
- [ ] `LLM_ENABLED` set to false (default)

### Database
- [ ] Database file exists and accessible
- [ ] WAL mode enabled
- [ ] Foreign key constraints enabled
- [ ] No pending migrations

## Health & Infrastructure

### Health Endpoint
- [ ] `/health` returns 200 OK
- [ ] `/api/v1/health` returns identical response
- [ ] Version number matches expected (v6.8.0-beta.1)
- [ ] Database path displayed correctly
- [ ] WAL mode shows as true
- [ ] Foreign keys show as true
- [ ] LLM feature flag shows as false
- [ ] Metrics field present only when `ANALYTICS_ENABLED=true`

### Performance
- [ ] `/health` responds <100ms
- [ ] `/tree/stats` responds <100ms
- [ ] Conflicts endpoints respond <100ms

## Data Integrity

### CSV/XLSX Export Headers
- [ ] `/calc/export` header exact: `Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions`
- [ ] `/tree/export` header exact: `Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions`
- [ ] `/calc/export.xlsx` returns XLSX file with correct content-type
- [ ] `/tree/export.xlsx` returns XLSX file with correct content-type
- [ ] Both mounts (`/` and `/api/v1`) return identical headers

### Database Constraints
- [ ] Each parent has exactly 5 children (invariant enforced)
- [ ] Foreign key constraints working
- [ ] No orphaned records

## Core Functionality

### Import/Export
- [ ] Excel import accepts valid .xlsx files
- [ ] Import shows progress indicators (queued→processing→done)
- [ ] Import displays detailed results (inserted, updated, skipped counts)
- [ ] Import shows header validation errors with position details
- [ ] Import shows per-error counts
- [ ] CSV export downloads with correct filename
- [ ] XLSX export downloads with correct filename

### Outcomes
- [ ] Leaf-only triage editing works
- [ ] Non-leaf nodes show edit disabled
- [ ] LLM Fill button hidden when LLM disabled
- [ ] Triage data saves correctly
- [ ] Validation errors displayed clearly

### Conflicts
- [ ] Missing slots list displays correctly
- [ ] Jump to next incomplete parent works
- [ ] Conflicts panel loads fast (<100ms)
- [ ] Navigation to Editor works

### Calculator
- [ ] Chained dropdowns work (root → Node1..5)
- [ ] Deeper selections reset when higher selection changes
- [ ] Helper text shows remaining levels
- [ ] Outcomes display at leaf nodes
- [ ] Export buttons work for CSV and XLSX

## Flutter Parity

### Calculator Screen
- [ ] Chained dropdowns render correctly
- [ ] Reset behavior works as expected
- [ ] Helper text updates properly
- [ ] Outcomes display at leaf nodes
- [ ] Export buttons present and functional

### Workspace Screen
- [ ] Export buttons for CSV and XLSX
- [ ] Health information displays
- [ ] Navigation to other screens works

### Platform Testing
- [ ] Android emulator (10.0.2.2) works
- [ ] iOS simulator (localhost) works
- [ ] At least one physical device (LAN IP) works
- [ ] Export save/share functionality works per platform

## Backup & Restore

### Backup
- [ ] Create Backup button works
- [ ] Backup file created with timestamp
- [ ] Integrity check results displayed
- [ ] Backup file path shown

### Restore
- [ ] Restore Latest button works
- [ ] Pre-restore backup created
- [ ] Integrity check after restore
- [ ] Data restored correctly

### Status
- [ ] Show Backup Status button works
- [ ] Backup directory information displayed
- [ ] Available backups listed with details

## Cache Management

### Cache Operations
- [ ] Refresh Cache Stats shows current cache size and TTL
- [ ] Clear Cache button works
- [ ] Performance Test shows cache improvement
- [ ] Cache invalidation works on updates

## API Endpoints

### Flags
- [ ] `/flags/preview-assign` returns affected count
- [ ] `/flags/audit` with `branch=true` returns descendant audit
- [ ] Flag assignment/removal works with cascade

### Conflicts
- [ ] `/tree/conflicts/duplicate-labels` returns results
- [ ] `/tree/conflicts/orphans` returns results
- [ ] `/tree/conflicts/depth-anomalies` returns results

## Testing

### Automated Tests
- [ ] All API tests pass
- [ ] All Flutter widget tests pass
- [ ] CSV header freeze tests pass
- [ ] Health metrics toggle tests pass
- [ ] Test coverage ≥ previous version

### Manual Testing
- [ ] Streamlit UI loads without errors
- [ ] Flutter app builds and runs
- [ ] Critical user flows work end-to-end
- [ ] Error handling works as expected

## Documentation

### User Documentation
- [ ] PHASE6_README.md updated with new features
- [ ] API.md shows correct endpoints and contracts
- [ ] Dev_Quickstart.md includes LAN and CORS tips
- [ ] DesignDecisions.md reflects current architecture

### Operational Documentation
- [ ] Beta_SLA_Severity.md created
- [ ] Rollback_Plan.md created
- [ ] Beta_Acceptance_Checklist.md (this file) complete
- [ ] Demo scripts documented

## Final Verification

### Deployment
- [ ] All services running
- [ ] No error logs
- [ ] Health checks passing
- [ ] Performance targets met

### Communication
- [ ] Beta users notified
- [ ] Engineering team briefed
- [ ] Status page updated
- [ ] Rollback procedures documented

---

**Checklist Completed By**: _________________
**Date**: _________________
**Deployment Version**: _________________
**All Items Passed**: [ ] Yes [ ] No

**Notes**: _________________
