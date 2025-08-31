# Beta Severity & SLAs

## Severity Levels

### P0 — Critical (Fix <24h; hotfix permitted)
- **Data loss/corruption**: Database integrity issues, import/export data corruption
- **Import/export broken**: CSV/XLSX endpoints returning errors, wrong headers
- **5-children invariant breach**: Database allowing parents with ≠5 children
- **Authentication bypass**: Security vulnerabilities allowing unauthorized access
- **Service unavailable**: API completely down, health endpoint failing

**Escalation**: Immediate on-call engineer + Slack #lorien-beta
**Response**: Acknowledge within 1 hour, fix within 24 hours
**Communication**: Update status every 4 hours until resolved

### P1 — High (Fix <72h)
- **Major feature unusable**: Conflicts/Outcomes/Calculator common paths broken
- **Performance degradation**: Endpoints responding >5s, cache not working
- **UI critical flows**: Import/export buttons not working, navigation broken
- **Data inconsistency**: Audit trail missing, flag assignments not persisting
- **Mobile parity broken**: Flutter app not working on target devices

**Escalation**: On-call engineer + daily status updates
**Response**: Acknowledge within 4 hours, fix within 72 hours
**Communication**: Update status every 12 hours until resolved

### P2 — Medium (Batch to next patch)
- **Cosmetic issues**: UI alignment, color mismatches, minor text issues
- **Minor performance**: Endpoints responding 1-5s, acceptable but not optimal
- **Documentation**: Outdated docs, missing examples, unclear instructions
- **Non-critical features**: Advanced filters, bulk actions, optional integrations
- **Platform-specific**: Issues affecting only one platform/device type

**Escalation**: Regular development cycle
**Response**: Acknowledge within 24 hours, fix in next scheduled release
**Communication**: Weekly status updates

## SLA Targets

| Severity | Response Time | Resolution Time | Escalation |
|----------|---------------|-----------------|------------|
| P0       | 1 hour       | 24 hours        | Immediate  |
| P1       | 4 hours      | 72 hours        | Daily      |
| P2       | 24 hours     | Next release     | Weekly     |

## Escalation Matrix

### P0 Escalation
1. **Immediate**: On-call engineer + Slack #lorien-beta
2. **1 hour**: Engineering manager + product owner
3. **4 hours**: CTO + customer success
4. **24 hours**: Executive escalation

### P1 Escalation
1. **4 hours**: Engineering manager
2. **24 hours**: Product owner
3. **72 hours**: CTO

### P2 Escalation
1. **24 hours**: Engineering manager
2. **Weekly**: Product owner review

## Communication Channels

- **Primary**: Slack #lorien-beta
- **Escalation**: Slack #lorien-engineering
- **Customer**: Email + status page
- **Internal**: Daily standup + weekly review

## Status Page Updates

- **P0**: Update every 2 hours
- **P1**: Update every 8 hours
- **P2**: Update every 24 hours

## Post-Incident

- **P0/P1**: Post-mortem within 48 hours
- **P2**: Retrospective in next sprint
- **All**: Update runbooks and procedures
