# Observability Guide

This guide covers the observability infrastructure in Lorien, including logging, metrics, tracing, and monitoring.

## Overview

Lorien's observability stack provides:

1. **Request/Trace IDs** - Unique identifiers for request correlation
2. **Structured JSON Logging** - Machine-parseable logs with context
3. **Metrics Collection** - Performance and usage statistics
4. **OpenTelemetry Integration** - Distributed tracing and export

## Quick Start

### Enable Basic Observability

```bash
# Enable structured logging
export LOG_LEVEL=INFO
export JSON_LOGGING=true

# Enable metrics
export ANALYTICS_ENABLED=true
export AUTH_TOKEN=your-secret-token

# Start the API
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Enable OpenTelemetry (Optional)

```bash
# Install OpenTelemetry packages
pip install opentelemetry-distro opentelemetry-exporter-otlp

# Configure OTLP endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Start with OpenTelemetry
uvicorn api.main:app
```

## Request & Trace IDs

Every request automatically receives:

- **Request ID**: `req_xxxxxxxxxxxxxxxx`
- **Trace ID**: 32-character hex string (OpenTelemetry compatible)

### Response Headers

```http
HTTP/1.1 200 OK
X-Request-Id: req_a1b2c3d4e5f6g7h8
X-Trace-Id: 0af7651916cd43dd8448eb211c80319c
Content-Type: application/json
```

### Distributed Tracing

Lorien supports W3C Trace Context for distributed systems:

```bash
# Send traceparent header
curl -H "traceparent: 00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01" \
     http://localhost:8000/api/v1/tree/1
```

The trace ID will be extracted and propagated through all services.

## Structured Logging

### Log Format

All logs are JSON-structured:

```json
{
  "timestamp": "2025-10-08T12:34:56.789Z",
  "level": "INFO",
  "logger": "api.routers.tree_basic",
  "message": "Node retrieved successfully",
  "request_id": "req_a1b2c3d4e5f6g7h8",
  "trace_id": "0af7651916cd43dd8448eb211c80319c",
  "location": {
    "file": "/home/user/api/routers/tree_basic.py",
    "line": 42,
    "function": "get_node"
  },
  "node_id": 123,
  "depth": 2
}
```

### Using Structured Logging

```python
from api.observability import get_logger

logger = get_logger(__name__)

# Simple log
logger.info("Operation started")

# Log with structured fields
logger.info(
    "Import completed",
    extra_fields={
        "records_imported": 150,
        "duration_ms": 234.5,
        "source_format": "excel"
    }
)

# Error logging with context
try:
    process_data()
except Exception as exc:
    logger.error(
        "Processing failed",
        extra_fields={
            "error_type": type(exc).__name__,
            "retry_count": 3
        },
        exc_info=True  # Include full traceback
    )
```

### Log Levels

| Level | When to Use |
|-------|-------------|
| DEBUG | Detailed diagnostic information |
| INFO | General informational messages |
| WARNING | Warning messages (degraded state) |
| ERROR | Error messages (operation failed) |
| CRITICAL | Critical errors (system unstable) |

### Best Practices

1. **Use structured fields** instead of string interpolation:

   ```python
   # Good
   logger.info("User action", extra_fields={"user_id": 123, "action": "login"})

   # Bad
   logger.info(f"User {user_id} performed {action}")
   ```

2. **Include relevant context**:
   - IDs (node_id, parent_id, etc.)
   - Counts (record_count, error_count)
   - Timings (duration_ms, response_time)
   - States (status, phase, stage)

3. **Never log PHI** (Protected Health Information):
   - No patient names, dates of birth, etc.
   - Use IDs instead of identifiable information
   - Review logs for compliance

4. **Use appropriate levels**:
   - Don't log INFO for every database query
   - Don't log ERROR for expected validation failures
   - Use WARNING for degraded but functional states

## Metrics Collection

### Available Metrics

The system automatically collects:

**HTTP Metrics:**

- `http.requests` - Request count by method, path, status
- `http.response_time` - Response times with percentiles
- `http.success` - Successful requests (2xx)
- `http.client_errors` - Client errors (4xx) by status
- `http.server_errors` - Server errors (5xx) by status

**Application Metrics:**

- `app.startup` - Application start count
- `app.shutdown` - Application shutdown count

### Custom Metrics

```python
from api.observability.metrics import (
    increment_counter,
    set_gauge,
    record_timer,
    record_histogram,
)

# Count events
increment_counter("imports.processed")
increment_counter("exports.failed", tags={"format": "csv"})

# Track current values
set_gauge("active_connections", 42)
set_gauge("queue.size", 15)

# Measure duration
start = time.time()
do_work()
duration_ms = (time.time() - start) * 1000
record_timer("work.duration", duration_ms, tags={"work_type": "import"})

# Track distributions
record_histogram("import.record_count", 1500, tags={"source": "excel"})
```

### Metrics Endpoint

Access metrics via the authenticated endpoint:

```bash
curl -H "Authorization: Bearer your-token" \
     http://localhost:8000/api/v1/health/metrics
```

Response:

```json
{
  "timestamp": 1696776896.789,
  "uptime_seconds": 3600.5,
  "observability": {
    "counters": {
      "http.requests{method=GET,path=/api/v1/tree/{id},status=200}": 1234
    },
    "timers": {
      "http.response_time{method=GET,path=/api/v1/tree/{id},status=200}": {
        "count": 1234,
        "mean": 45.67,
        "p50": 42.3,
        "p95": 89.2,
        "p99": 156.7
      }
    }
  }
}
```

### Authentication

The metrics endpoint requires authentication when `AUTH_TOKEN` is set:

```bash
# Set auth token
export AUTH_TOKEN=your-secret-token-here

# Access metrics
curl -H "Authorization: Bearer your-secret-token-here" \
     http://localhost:8000/api/v1/health/metrics
```

## OpenTelemetry Integration

### Setup

1. **Install dependencies:**

   ```bash
   pip install opentelemetry-distro opentelemetry-exporter-otlp
   ```

2. **Configure endpoint:**

   ```bash
   export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
   ```

3. **Start the application:**

   ```bash
   uvicorn api.main:app
   ```

### Jaeger (Tracing)

```bash
# Start Jaeger
docker run -d --name jaeger \
  -p 4317:4317 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest

# Configure Lorien
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# View traces at http://localhost:16686
```

### Custom Spans

```python
from api.observability.telemetry import get_tracer

tracer = get_tracer(__name__)

if tracer:
    with tracer.start_as_current_span("import_excel") as span:
        span.set_attribute("file.size_bytes", file_size)
        span.set_attribute("file.format", "xlsx")

        # Import logic here
        records = parse_excel(file)

        span.set_attribute("records.count", len(records))
        span.add_event("Parsing complete")
```

### Resource Attributes

Add custom resource attributes:

```bash
export OTEL_RESOURCE_ATTRIBUTES_ENVIRONMENT=production
export OTEL_RESOURCE_ATTRIBUTES_DATACENTER=us-east-1
export OTEL_RESOURCE_ATTRIBUTES_VERSION=1.0.0
```

## Production Deployment

### Log Aggregation

Use log aggregation tools to collect and analyze logs:

**ELK Stack (Elasticsearch, Logstash, Kibana):**

```bash
# Ship logs to Logstash
uvicorn api.main:app | nc logstash.example.com 5000
```

**Grafana Loki:**

```bash
# Use Promtail to ship logs
# See: https://grafana.com/docs/loki/latest/clients/promtail/
```

**Cloud Logging:**

- **AWS CloudWatch**: Use AWS CloudWatch Logs agent
- **GCP Cloud Logging**: Use Google Cloud Logging agent
- **Azure Monitor**: Use Azure Monitor agent

### Metrics Monitoring

**Prometheus:**

```yaml
# Use OpenTelemetry Collector with Prometheus exporter
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

exporters:
  prometheus:
    endpoint: 0.0.0.0:9090

service:
  pipelines:
    metrics:
      receivers: [otlp]
      exporters: [prometheus]
```

**Datadog:**

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=https://api.datadoghq.com
export OTEL_EXPORTER_OTLP_HEADERS="api-key=YOUR_API_KEY"
```

### Performance Tuning

1. **Log Level**: Use `INFO` in production, `DEBUG` only for troubleshooting
2. **Sampling**: Consider sampling high-volume traces
3. **Batch Size**: Adjust OTLP batch size for high throughput
4. **Metric Intervals**: Increase export interval to reduce overhead

```bash
# Production settings
export LOG_LEVEL=INFO
export OTEL_METRIC_EXPORT_INTERVAL=60000  # 60 seconds
```

## Security Considerations

### Metrics Authentication

Always enable authentication for the metrics endpoint:

```bash
# Generate a strong token
export AUTH_TOKEN=$(openssl rand -hex 32)

# Restrict endpoint access via firewall
sudo ufw allow from 10.0.0.0/8 to any port 8000
```

### Log Security

1. **Never log sensitive data** (passwords, tokens, PHI)
2. **Use log rotation** to prevent disk exhaustion
3. **Encrypt logs in transit** (TLS for log shipping)
4. **Control log access** (RBAC for log viewers)

### Network Isolation

Restrict observability endpoints:

```bash
# Allow metrics only from monitoring network
iptables -A INPUT -p tcp --dport 8000 -s 10.0.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 8000 -j DROP
```

## Troubleshooting

### Logs Not Appearing

1. Check log level: `export LOG_LEVEL=DEBUG`
2. Verify JSON logging: `export JSON_LOGGING=true`
3. Check stdout/stderr redirection
4. Review uvicorn logging config

### Metrics Endpoint 404

1. Enable analytics: `export ANALYTICS_ENABLED=true`
2. Restart the application
3. Verify endpoint: `curl http://localhost:8000/api/v1/health/metrics`

### Metrics Endpoint 401

1. Set auth token: `export AUTH_TOKEN=your-token`
2. Include header: `Authorization: Bearer your-token`
3. Verify token matches

### OpenTelemetry Not Working

1. Install dependencies: `pip install opentelemetry-distro opentelemetry-exporter-otlp`
2. Set endpoint: `export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317`
3. Check connectivity: `nc -zv localhost 4317`
4. Review startup logs for errors

## References

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [W3C Trace Context Specification](https://www.w3.org/TR/trace-context/)
- [Structured Logging Best Practices](https://www.honeycomb.io/blog/structured-logging-best-practices)
- [The Twelve-Factor App: Logs](https://12factor.net/logs)
- [Observability Engineering Book](https://www.oreilly.com/library/view/observability-engineering/9781492076438/)
