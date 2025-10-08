# Observability Infrastructure

Comprehensive observability for the Lorien API, including request/trace IDs, structured logging, metrics collection, and OpenTelemetry integration.

## Features

### 1. Request & Trace IDs

Every HTTP request is assigned:

- **Request ID**: Unique identifier for the individual request (`req_xxxxxxxxxxxxxxxx`)
- **Trace ID**: Distributed tracing identifier compatible with OpenTelemetry (32 hex characters)
- **Parent Span ID**: Extracted from W3C `traceparent` header for distributed systems

These IDs are:

- Added to response headers (`X-Request-Id`, `X-Trace-Id`)
- Automatically included in all structured logs
- Propagated through async contexts
- Used for correlation across services

### 2. Structured JSON Logging

All logs are output as structured JSON with:

- ISO 8601 timestamps with timezone
- Log level (INFO, ERROR, etc.)
- Logger name
- Request/trace IDs (when available)
- File location (file, line, function)
- Custom fields via `extra_fields`
- Exception details with full traceback

**Example log entry:**

```json
{
  "timestamp": "2025-10-08T12:34:56.789Z",
  "level": "INFO",
  "logger": "api.routers.tree_basic",
  "message": "GET /api/v1/tree/123 -> 200 (45.23ms)",
  "request_id": "req_a1b2c3d4e5f6g7h8",
  "trace_id": "0af7651916cd43dd8448eb211c80319c",
  "location": {
    "file": "/home/user/api/routers/tree_basic.py",
    "line": 42,
    "function": "get_node"
  },
  "http": {
    "method": "GET",
    "path": "/api/v1/tree/123",
    "status_code": 200,
    "duration_ms": 45.23
  }
}
```

### 3. Metrics Collection

In-memory metrics collector tracks:

- **Counters**: Request counts, success/error rates
- **Gauges**: Current values (connections, queue sizes)
- **Histograms**: Value distributions
- **Timers**: Response times with percentiles (p50, p95, p99)

All metrics are:

- Tagged for grouping (method, path, status)
- Non-PHI (no patient data)
- Path-normalized (IDs replaced with placeholders)
- Limited in size to prevent memory growth

### 4. OpenTelemetry Integration

Optional integration with OpenTelemetry for:

- Distributed tracing (Jaeger, Zipkin, etc.)
- Metrics export (Prometheus, Datadog, etc.)
- Auto-instrumentation of FastAPI, HTTP requests, logging

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `JSON_LOGGING` | `true` | Enable JSON log output (false for text) |
| `ANALYTICS_ENABLED` | `false` | Enable metrics collection |
| `AUTH_TOKEN` | (none) | Token for metrics endpoint authentication |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | (none) | OpenTelemetry collector endpoint |
| `OTEL_EXPORTER_OTLP_HEADERS` | (none) | OTLP headers (format: `key1=value1,key2=value2`) |
| `OTEL_METRIC_EXPORT_INTERVAL` | `60000` | Metrics export interval in milliseconds |
| `OTEL_RESOURCE_ATTRIBUTES_*` | (none) | Custom resource attributes |

### Basic Setup

1. **Enable structured logging:**

```bash
export LOG_LEVEL=INFO
export JSON_LOGGING=true
```

2. **Enable metrics collection:**

```bash
export ANALYTICS_ENABLED=true
export AUTH_TOKEN=your-secret-token-here
```

3. **Enable OpenTelemetry (optional):**

```bash
# Install OpenTelemetry packages
pip install opentelemetry-distro opentelemetry-exporter-otlp

# Configure endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_RESOURCE_ATTRIBUTES_ENVIRONMENT=production
```

## Usage

### Structured Logging

```python
from api.observability import get_logger

logger = get_logger(__name__)

# Simple log
logger.info("User action completed")

# Log with extra fields
logger.info(
    "Data processed",
    extra_fields={
        "record_count": 150,
        "processing_time_ms": 234.5,
        "source": "import"
    }
)

# Log with context (request_id/trace_id automatically included)
logger.error(
    "Operation failed",
    extra_fields={
        "error_code": "DB_TIMEOUT",
        "retry_count": 3
    }
)
```

### Metrics

```python
from api.observability.metrics import (
    increment_counter,
    set_gauge,
    record_timer,
    record_histogram,
)

# Track events
increment_counter("imports.processed")
increment_counter("exports.failed", tags={"format": "csv"})

# Record current values
set_gauge("queue.size", 42)
set_gauge("active_connections", 8)

# Record timings
record_timer("db.query_time", 15.3, tags={"query": "select_nodes"})

# Record distributions
record_histogram("request.body_size", 1024, tags={"content_type": "json"})
```

### Custom Tracing (with OpenTelemetry)

```python
from api.observability.telemetry import get_tracer

tracer = get_tracer(__name__)

if tracer:
    with tracer.start_as_current_span("complex_operation") as span:
        span.set_attribute("user.action", "import")
        span.set_attribute("record.count", 100)

        # Your code here
        process_data()

        span.add_event("Processing complete")
```

## Metrics Endpoint

The `/api/v1/health/metrics` endpoint provides access to all collected metrics.

### Authentication

The metrics endpoint **requires authentication** when `AUTH_TOKEN` is set:

```bash
# Access metrics
curl -H "Authorization: Bearer your-token" \
     http://localhost:8000/api/v1/health/metrics
```

Response structure:

```json
{
  "timestamp": 1696776896.789,
  "uptime_seconds": 3600.5,
  "observability": {
    "counters": {
      "http.requests{method=GET,path=/api/v1/tree/{id},status=200}": 1234,
      "http.success": 1200,
      "http.client_errors{status=404}": 34
    },
    "timers": {
      "http.response_time{method=GET,path=/api/v1/tree/{id},status=200}": {
        "count": 1234,
        "mean": 45.67,
        "p50": 42.3,
        "p95": 89.2,
        "p99": 156.7,
        "min": 12.1,
        "max": 234.5
      }
    }
  },
  "database": {
    "node_count": 5678,
    "max_depth": 4
  }
}
```

### Security Considerations

1. **Authentication Required**: Metrics may reveal system internals
2. **Non-PHI Only**: No patient or sensitive data in metrics
3. **Rate Limiting**: Consider adding rate limits in production
4. **Network Isolation**: Restrict metrics endpoint access via firewall

## OpenTelemetry Exporters

### Jaeger (Distributed Tracing)

```bash
# Start Jaeger all-in-one
docker run -d --name jaeger \
  -p 4317:4317 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest

# Configure Lorien
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# View traces at http://localhost:16686
```

### Prometheus (Metrics)

```bash
# Use OpenTelemetry Collector with Prometheus exporter
# See: https://opentelemetry.io/docs/collector/

export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

### Cloud Providers

#### Datadog

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=https://api.datadoghq.com
export OTEL_EXPORTER_OTLP_HEADERS="api-key=YOUR_API_KEY"
```

#### New Relic

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.nr-data.net:4317
export OTEL_EXPORTER_OTLP_HEADERS="api-key=YOUR_LICENSE_KEY"
```

#### Grafana Cloud

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp-gateway-prod-us-central-0.grafana.net/otlp
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Basic YOUR_BASE64_CREDENTIALS"
```

## Performance Considerations

### Memory Usage

- Histograms and timers are limited to 1,000 values each
- Older values are automatically dropped (FIFO)
- Metrics reset on application restart

### CPU Impact

- Structured logging has minimal overhead (~2-5% typical)
- Metrics collection is lock-protected and fast
- OpenTelemetry uses batching to minimize impact

### Recommendations

- Use `INFO` level in production (not `DEBUG`)
- Enable OpenTelemetry only when needed
- Consider log aggregation for high-volume systems

## Troubleshooting

### Logs not appearing

1. Check `LOG_LEVEL` is set correctly
2. Verify stdout/stderr are not being redirected
3. Ensure `JSON_LOGGING` matches your log parser

### Metrics endpoint returns 404

1. Set `ANALYTICS_ENABLED=true`
2. Restart the application

### Metrics endpoint returns 401

1. Set `AUTH_TOKEN` environment variable
2. Include token in `Authorization: Bearer <token>` header

### OpenTelemetry not working

1. Install dependencies: `pip install opentelemetry-distro opentelemetry-exporter-otlp`
2. Set `OTEL_EXPORTER_OTLP_ENDPOINT`
3. Check collector/backend is reachable
4. Review startup logs for OpenTelemetry initialization messages

## Testing

### Unit Tests

```python
from api.observability import get_logger, set_request_context
from api.observability.metrics import increment_counter, get_metrics_snapshot, reset_metrics

# Test logging with context
set_request_context(request_id="test-req-123")
logger = get_logger(__name__)
logger.info("Test message")

# Test metrics
reset_metrics()
increment_counter("test.counter", 5)
snapshot = get_metrics_snapshot()
assert snapshot["counters"]["test.counter"] == 5
```

### Integration Tests

```bash
# Start the API
export ANALYTICS_ENABLED=true
export AUTH_TOKEN=test-token
uvicorn api.main:app

# Test metrics endpoint
curl -H "Authorization: Bearer test-token" \
     http://localhost:8000/api/v1/health/metrics

# Generate test traffic
for i in {1..100}; do
  curl http://localhost:8000/api/v1/health
done

# Verify metrics
curl -H "Authorization: Bearer test-token" \
     http://localhost:8000/api/v1/health/metrics | jq '.observability.counters'
```

## Migration from Legacy Logging

The observability system is backward compatible with existing logging:

```python
# Old style (still works)
import logging
logger = logging.getLogger(__name__)
logger.info("Simple log")

# New style (structured)
from api.observability import get_logger
logger = get_logger(__name__)
logger.info("Structured log", extra_fields={"key": "value"})
```

Both styles produce structured JSON output when `JSON_LOGGING=true`.

## See Also

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- [Structured Logging Best Practices](https://www.honeycomb.io/blog/structured-logging-best-practices)
