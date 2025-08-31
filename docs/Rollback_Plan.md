# Rollback Plan

## Overview
This document outlines the rollback procedures for Lorien v6.8.0-beta.1 in case of critical issues during the beta window.

## Pre-Rollback Checklist

### 1. Pre-Drop Backup
- [ ] Create database snapshot: `POST /backup`
- [ ] Verify backup integrity: Check backup file exists and integrity check passes
- [ ] Tag current state: `git tag v6.8.0-beta.1-rollback-$(date +%Y%m%d-%H%M%S)`
- [ ] Document current issues: Record specific problems and affected users

### 2. Communication
- [ ] Notify beta users of potential rollback
- [ ] Update status page to "Investigating"
- [ ] Alert engineering team via Slack #lorien-beta

## Rollback Procedures

### Option 1: One-Click Restore (Recommended)
**Use when**: Database corruption, data loss, or critical API issues

1. **Execute Restore**:
   ```bash
   # Via UI: Click "Restore Latest" button
   # Via API: POST /restore
   ```

2. **Verify Integrity**:
   - Check `/health` endpoint returns OK
   - Verify database integrity check passes
   - Confirm critical data is restored

3. **Test Critical Paths**:
   - CSV/XLSX export headers are correct
   - Import functionality works
   - Basic navigation functions

### Option 2: Git Revert
**Use when**: Code-level issues, deployment problems, or configuration errors

1. **Revert to Previous Tag**:
   ```bash
   git checkout v6.7.x  # Previous stable version
   git tag v6.8.0-beta.1-rollback-$(date +%Y%m%d-%H%M%S)
   ```

2. **Redeploy**:
   ```bash
   # Restart API server
   uvicorn api.main:app --reload --port 8000
   
   # Restart Streamlit
   streamlit run Home.py
   ```

3. **Verify Deployment**:
   - Check `/health` endpoint
   - Verify version number is correct
   - Test critical functionality

### Option 3: Database-Only Rollback
**Use when**: Data issues but code is stable

1. **Restore Database**:
   ```bash
   # Stop application
   # Replace current database with backup
   cp backups/lorien_backup_YYYYMMDD_HHMMSS.db sqlite.db
   # Restart application
   ```

2. **Verify Data**:
   - Check record counts
   - Verify relationships are intact
   - Test critical queries

## Post-Rollback Verification

### Health Checks
- [ ] `/health` endpoint returns OK
- [ ] Version number is correct
- [ ] Database path is accessible
- [ ] WAL mode and foreign keys are enabled

### Functional Tests
- [ ] CSV/XLSX header exact (8 columns)
- [ ] Outcomes save (leaf-only) works
- [ ] Conflicts lists load fast
- [ ] Import: valid fixture works, invalid shows errors
- [ ] Flutter: Calculator and exports work
- [ ] Backup/Restore UI buttons work

### Performance Checks
- [ ] `/tree/stats` responds <100ms
- [ ] Conflicts endpoints respond <100ms
- [ ] Import operations complete <30s
- [ ] Export operations complete <10s

## Rollback Decision Matrix

| Issue Type | Severity | Rollback Option | Decision Maker |
|------------|----------|-----------------|----------------|
| Data corruption | P0 | Option 1 (Restore) | On-call engineer |
| API down | P0 | Option 2 (Git revert) | Engineering manager |
| Performance >5s | P1 | Option 2 (Git revert) | Engineering manager |
| UI broken | P1 | Option 2 (Git revert) | Product owner |
| Minor bugs | P2 | No rollback | Engineering manager |

## Communication Plan

### During Rollback
- **Immediate**: Slack #lorien-beta + #lorien-engineering
- **15 minutes**: Status page update
- **1 hour**: Email to beta users
- **4 hours**: Detailed incident report

### After Rollback
- **24 hours**: Post-mortem meeting
- **48 hours**: Rollback report to stakeholders
- **1 week**: Lessons learned document

## Recovery Steps

### 1. Immediate Recovery
- [ ] Restore service to working state
- [ ] Verify critical functionality
- [ ] Communicate status to users

### 2. Root Cause Analysis
- [ ] Investigate what caused the issue
- [ ] Document findings
- [ ] Identify preventive measures

### 3. Fix and Redeploy
- [ ] Develop fix for the issue
- [ ] Test thoroughly
- [ ] Deploy with monitoring
- [ ] Consider re-enabling beta features

## Contact Information

- **On-call Engineer**: [Contact info]
- **Engineering Manager**: [Contact info]
- **Product Owner**: [Contact info]
- **Emergency**: [Emergency contact]

## Rollback History

| Date | Version | Reason | Rollback Method | Resolution Time |
|------|---------|--------|-----------------|-----------------|
| [To be filled during beta] | | | | |
