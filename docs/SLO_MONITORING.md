# Service Level Objectives (SLO) and Monitoring

This document defines the Service Level Objectives (SLOs) and monitoring strategy for the Lorien application.

## Service Level Objectives

### Availability SLO

- **Target**: 99.9% uptime (8.76 hours downtime per year)
- **Measurement**: Successful health check responses
- **Monitoring**: `/api/v1/health` endpoint
- **Alerting**: < 99.9% availability over 24-hour window

### Performance SLOs

#### Response Time Targets

| Endpoint Category | p95 Target | p99 Target | Measurement |
|------------------|------------|------------|-------------|
| Health checks | 50ms | 100ms | `/api/v1/health` |
| Navigate queries | 150ms | 300ms | `/api/v1/tree/next-incomplete-parent` |
| Children upsert | 200ms | 500ms | `/api/v1/tree/{id}/children` |
| CSV export | 2s | 5s | `/api/v1/tree/export` |
| Dictionary lookups | 100ms | 200ms | `/api/v1/dictionary/*` |
| Outcomes updates | 150ms | 300ms | `/api/v1/triage/*` |

#### Error Rate Targets

- **Target**: < 0.1% error rate (4xx + 5xx responses)
- **Measurement**: HTTP response status codes
- **Alerting**: > 0.1% error rate over 1-hour window

#### Conflict Rate Targets

- **Target**: < 5% conflict rate (409 responses)
- **Measurement**: 409 responses as percentage of total requests
- **Alerting**: > 5% conflict rate over 1-hour window

## Monitoring Strategy

### Metrics Collection

#### Request Metrics

- **Request count**: Total requests by endpoint, method, status code
- **Response time**: p50, p95, p99 latencies by endpoint
- **Error rate**: 4xx and 5xx responses as percentage
- **Conflict rate**: 409 responses as percentage

#### System Metrics

- **Database performance**: Query execution times, connection pool usage
- **Memory usage**: Peak memory consumption, garbage collection
- **CPU usage**: Average and peak CPU utilization
- **Disk usage**: Database file size, log file sizes

#### Business Metrics

- **Tree operations**: Create, update, delete operations
- **Import/export**: Success/failure rates, processing times
- **User activity**: Active sessions, feature usage

### Alerting Rules

#### Critical Alerts (Immediate Response)

1. **Service Down**: Health check failing for > 5 minutes
2. **High Error Rate**: > 1% error rate for > 10 minutes
3. **Database Unavailable**: Database connection failures
4. **Memory Exhaustion**: > 90% memory usage

#### Warning Alerts (Response within 1 hour)

1. **Performance Degradation**: p95 latency > 2x target for > 15 minutes
2. **High Conflict Rate**: > 10% conflict rate for > 30 minutes
3. **Disk Space Low**: < 20% free disk space
4. **High CPU Usage**: > 80% CPU usage for > 30 minutes

#### Info Alerts (Response within 24 hours)

1. **SLO Breach**: Any SLO target missed
2. **Unusual Traffic**: > 2x normal request volume
3. **New Error Types**: Previously unseen error patterns

### Monitoring Tools

#### Built-in Metrics

- **FastAPI Metrics**: Request/response metrics via middleware
- **Health Endpoints**: `/api/v1/health` and `/api/v1/health/metrics`
- **Database Metrics**: SQLite performance analysis

#### External Monitoring (Recommended)

- **Application Performance Monitoring (APM)**: New Relic, DataDog, or similar
- **Log Aggregation**: ELK stack, Splunk, or similar
- **Infrastructure Monitoring**: Prometheus + Grafana, or cloud provider tools
- **Uptime Monitoring**: Pingdom, UptimeRobot, or similar

## SLO Implementation

### Metrics Collection

```python
# Example metrics collection
from api.core.metrics import increment_counter, record_timer

# Count requests
increment_counter("http_requests", tags={"endpoint": "/api/v1/tree/children"})

# Record response time
record_timer("http_response_time", duration_ms, tags={"endpoint": "/api/v1/tree/children"})

# Count errors
increment_counter("http_errors", tags={"status_code": "409"})
```

### Health Checks

```bash
# Basic health check
curl -f http://localhost:8000/api/v1/health

# Detailed metrics (when enabled)
curl http://localhost:8000/api/v1/health/metrics
```

### SLO Validation

```python
# Example SLO validation
def validate_slo_metrics(metrics):
    """Validate that metrics meet SLO targets."""
    issues = []
    
    # Check response time SLOs
    for endpoint, latency_p95 in metrics.get("response_times", {}).items():
        if latency_p95 > SLO_TARGETS[endpoint]["p95"]:
            issues.append(f"{endpoint} p95 latency {latency_p95}ms exceeds target")
    
    # Check error rate SLO
    error_rate = metrics.get("error_rate", 0)
    if error_rate > 0.001:  # 0.1%
        issues.append(f"Error rate {error_rate:.2%} exceeds 0.1% target")
    
    return issues
```

## Alerting Configuration

### Alert Channels

1. **Critical**: Slack #alerts, PagerDuty, SMS
2. **Warning**: Slack #warnings, Email
3. **Info**: Slack #notifications, Email digest

### Alert Escalation

1. **Level 1**: On-call engineer (0-15 minutes)
2. **Level 2**: Senior engineer (15-60 minutes)
3. **Level 3**: Engineering manager (60+ minutes)

### Runbook Integration

Each alert should link to a runbook with:
- **Problem description**
- **Immediate actions**
- **Diagnostic steps**
- **Resolution procedures**
- **Post-incident follow-up**

## SLO Reporting

### Daily Reports

- **SLO compliance**: Current vs target metrics
- **Performance trends**: Response time and error rate trends
- **Incident summary**: Any SLO breaches and resolutions

### Weekly Reports

- **SLO performance**: Weekly SLO compliance rates
- **Capacity planning**: Traffic growth and resource usage
- **Improvement opportunities**: Areas for optimization

### Monthly Reports

- **SLO review**: Overall SLO performance and adjustments
- **Incident analysis**: Root cause analysis of SLO breaches
- **Capacity planning**: Resource scaling recommendations

## SLO Maintenance

### Regular Reviews

- **Monthly**: Review SLO targets and adjust as needed
- **Quarterly**: Comprehensive SLO and monitoring review
- **Annually**: Strategic SLO and monitoring roadmap

### SLO Updates

- **Target adjustments**: Based on business requirements and technical capabilities
- **New SLOs**: As new features and endpoints are added
- **Retired SLOs**: For deprecated features and endpoints

### Continuous Improvement

- **Monitoring optimization**: Improve alerting and dashboards
- **SLO refinement**: Better alignment with business objectives
- **Tool evaluation**: Assess and upgrade monitoring tools

## Emergency Procedures

### SLO Breach Response

1. **Immediate**: Acknowledge alert and assess impact
2. **Short-term**: Implement workaround if available
3. **Medium-term**: Root cause analysis and fix
4. **Long-term**: Process improvement to prevent recurrence

### Communication

- **Internal**: Notify team and stakeholders
- **External**: Update status page if applicable
- **Post-incident**: Conduct post-mortem and document lessons learned

### Recovery

- **Service restoration**: Restore service to normal operation
- **SLO validation**: Confirm SLO compliance is restored
- **Monitoring**: Enhanced monitoring during recovery period
