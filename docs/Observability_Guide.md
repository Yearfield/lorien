# Lorien API Observability Guide

This guide explains the comprehensive observability and error handling improvements implemented in the Lorien API.

## Overview

The Lorien API now includes enterprise-grade observability features:

- **Centralized Error Handling**: Consistent error codes and production-safe messages
- **Structured Logging**: JSON logs with correlation IDs for request tracing
- **Error Tracking & Alerting**: Real-time error monitoring with configurable alerts
- **Comprehensive Metrics**: Performance monitoring and business metrics
- **Distributed Tracing**: OpenTelemetry integration for request flow tracking
- **Health Monitoring**: Detailed health status and observability endpoints

## Error Handling

### Centralized Error System

All errors now use a centralized system with consistent error codes and production-safe messages.

#### Error Codes

```python
from api.exceptions import ErrorCodes

# Common error codes
ErrorCodes.VALIDATION_ERROR          # 400 - Request validation failed
ErrorCodes.AUTHENTICATION_REQUIRED   # 401 - Authentication required
ErrorCodes.INSUFFICIENT_PERMISSIONS  # 403 - Insufficient permissions
ErrorCodes.RESOURCE_NOT_FOUND        # 404 - Resource not found
ErrorCodes.CONFLICT_ERROR            # 409 - Resource conflict
ErrorCodes.TOO_MANY_CHILDREN         # 422 - Business rule violation
ErrorCodes.INTERNAL_SERVER_ERROR     # 500 - Internal server error
```

#### Using Custom Exceptions

```python
from api.exceptions import ValidationError, NotFoundError, ConflictError

# Validation errors
raise ValidationError("Invalid input data", field="email")

# Not found errors
raise NotFoundError("user", resource_id="123")

# Conflict errors
raise ConflictError("User already exists", conflict_type="duplicate_email")
```

#### Error Response Format

All errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request data is invalid",
    "request_id": "req_abc123...",
    "trace_id": "trace_def456..."
  }
}
```

In development mode, additional details are included:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request data is invalid: Invalid email format",
    "detail": "Invalid email format",
    "context": {"field": "email"},
    "request_id": "req_abc123...",
    "trace_id": "trace_def456..."
  }
}
```

## Structured Logging

### Correlation IDs

Every request automatically gets correlation IDs that propagate through the entire request flow:

- `request_id`: Unique identifier for the request
- `trace_id`: Distributed tracing identifier
- `parent_span_id`: Parent span ID for distributed tracing

### Using Structured Logging

```python
from api.observability import get_logger

logger = get_logger(__name__)

# Basic logging
logger.info("User action completed")

# Logging with extra fields
logger.info(
    "User login successful",
    extra_fields={
        "user_id": 123,
        "action": "login",
        "ip_address": "192.168.1.1"
    }
)

# Error logging with context
logger.error(
    "Database operation failed",
    extra_fields={
        "operation": "create_user",
        "error_type": "IntegrityError",
        "retry_count": 3
    }
)
```

### Log Format

All logs are structured JSON with correlation IDs:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "api.routers.users",
  "message": "User login successful",
  "request_id": "req_abc123...",
  "trace_id": "trace_def456...",
  "location": {
    "file": "/app/api/routers/users.py",
    "line": 45,
    "function": "login_user"
  },
  "user_id": 123,
  "action": "login",
  "ip_address": "192.168.1.1"
}
```

## Error Tracking & Alerting

### Automatic Error Tracking

All errors are automatically tracked with:

- Error categorization by severity
- Pattern detection and analysis
- Real-time alerting based on thresholds
- Health status monitoring

### Alert Rules

Default alert rules are configured for:

- **Critical Server Errors**: 5+ 500 errors in 5 minutes
- **High Error Rate**: 50+ errors of any type in 5 minutes
- **Authentication Failures**: 10+ auth errors in 5 minutes
- **Database Errors**: 3+ database errors in 5 minutes
- **Rate Limiting**: 20+ rate limit hits in 5 minutes

### Custom Alert Rules

```python
from api.observability.error_tracking import ErrorTracker, AlertRule, ErrorSeverity, AlertChannel

tracker = get_error_tracker()

# Add custom alert rule
custom_rule = AlertRule(
    name="custom_business_errors",
    error_codes={"BUSINESS_RULE_VIOLATION"},
    threshold_count=10,
    time_window_seconds=300,
    severity=ErrorSeverity.MEDIUM,
    channels={AlertChannel.LOG, AlertChannel.WEBHOOK},
    cooldown_seconds=600
)

tracker._alert_rules.append(custom_rule)
```

### Health Status

The system automatically tracks health status:

- **healthy**: Normal operation
- **degraded**: Elevated error rates
- **unhealthy**: High error rates
- **critical**: Critical errors present

## Metrics & Monitoring

### Performance Metrics

Track performance with decorators:

```python
from api.observability import time_operation

@time_operation("user_creation")
async def create_user(user_data):
    # User creation logic
    pass
```

### Business Metrics

Track business-specific metrics:

```python
from api.observability import get_business_metrics

business_metrics = get_business_metrics()

# Track tree operations
business_metrics.track_tree_operation(
    operation="create_node",
    success=True,
    duration_ms=150.5,
    node_type="decision"
)

# Track export operations
business_metrics.track_export_operations(
    format_type="csv",
    record_count=1000
)
```

### Manual Metrics

```python
from api.observability import increment_counter, record_timer, set_gauge

# Counters
increment_counter("api.requests", tags={"endpoint": "users"})

# Timers
record_timer("database.query_time", 45.2, tags={"query": "select_users"})

# Gauges
set_gauge("cache.size", 1024, tags={"cache": "user_cache"})
```

## Distributed Tracing

### OpenTelemetry Integration

The API integrates with OpenTelemetry for distributed tracing:

```bash
# Enable OpenTelemetry
export OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
export OTEL_RESOURCE_ATTRIBUTES_SERVICE_NAME=lorien-api
export OTEL_RESOURCE_ATTRIBUTES_SERVICE_VERSION=1.0.0
```

### Tracing Operations

```python
from api.observability import get_tracer, trace_async_operation, trace_database_operation

# Get tracer
tracer = get_tracer("api.users")

# Trace async operations
@trace_async_operation(tracer, "user_creation")
async def create_user(user_data):
    # User creation logic
    pass

# Trace database operations
@trace_database_operation(tracer, "select_users", "SELECT")
async def get_users():
    # Database query
    pass
```

### Manual Span Creation

```python
from api.observability import create_span, add_span_attributes, set_span_status

tracer = get_tracer("api.custom")

with create_span(tracer, "custom_operation", user_id=123) as span:
    try:
        # Operation logic
        add_span_attributes(span, operation_type="business_logic")
        set_span_status(span, success=True)
    except Exception as e:
        set_span_status(span, success=False, error_message=str(e))
        raise
```

## Health & Monitoring Endpoints

### Health Check

```bash
GET /api/v1/health
```

Returns comprehensive health status including:

- Database health
- Feature flags
- Error tracking status
- Metrics summary

### Detailed Metrics

```bash
GET /api/v1/metrics
```

Returns detailed metrics including:

- Performance counters
- Response time histograms
- Business metrics
- Recent performance profiles

### Error Status

```bash
GET /api/v1/errors
```

Returns error tracking information:

- Health status
- Recent error patterns
- Error severity breakdown

### Complete Observability

```bash
GET /api/v1/observability
```

Returns comprehensive observability data:

- Health status
- All metrics
- Error patterns and trends

## Configuration

### Environment Variables

```bash
# Logging
LOG_LEVEL=INFO
JSON_LOGGING=true

# OpenTelemetry
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
OTEL_RESOURCE_ATTRIBUTES_SERVICE_NAME=lorien-api

# Alerting
ALERT_WEBHOOK_URL=https://hooks.slack.com/services/...

# Environment
ENVIRONMENT=production  # Affects error message verbosity
```

### Production vs Development

- **Development**: Detailed error messages and stack traces
- **Production**: Sanitized error messages, no internal details

## Best Practices

### Error Handling

1. Use specific exception types for different error scenarios
2. Include context information in error details
3. Let the centralized system handle error responses
4. Don't expose internal implementation details

### Logging

1. Use structured logging with meaningful extra fields
2. Include correlation IDs for request tracing
3. Log at appropriate levels (INFO, WARNING, ERROR)
4. Avoid logging sensitive information

### Metrics

1. Use descriptive metric names with consistent naming
2. Include relevant tags for filtering and aggregation
3. Track both technical and business metrics
4. Monitor performance trends over time

### Tracing

1. Create spans for significant operations
2. Include relevant attributes for debugging
3. Set appropriate span status (success/error)
4. Use distributed tracing for microservices

## Integration Examples

### Grafana Dashboard

Create dashboards using the metrics endpoints:

```json
{
  "dashboard": {
    "title": "Lorien API Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [{
          "expr": "rate(api_requests_total[5m])"
        }]
      },
      {
        "title": "Error Rate",
        "targets": [{
          "expr": "rate(api_errors_total[5m])"
        }]
      }
    ]
  }
}
```

### Alerting Rules

Configure alerts based on error patterns:

```yaml
groups:
  - name: lorien-api
    rules:
      - alert: HighErrorRate
        expr: rate(api_errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
```

## Troubleshooting

### Common Issues

1. **Missing Correlation IDs**: Ensure ObservabilityMiddleware is registered first
2. **No OpenTelemetry Data**: Check OTEL_EXPORTER_OTLP_ENDPOINT configuration
3. **High Memory Usage**: Adjust metrics retention limits
4. **Alert Fatigue**: Tune alert thresholds and cooldowns

### Debugging

1. Check health endpoints for system status
2. Review error patterns in observability endpoint
3. Use correlation IDs to trace request flows
4. Monitor metrics for performance trends

This observability system provides comprehensive monitoring and debugging capabilities for the Lorien API, enabling proactive issue detection and efficient troubleshooting.
