# Observability Quick Reference

Fast reference for using Lorien's observability features.

## Setup (1 minute)

```bash
# Enable structured logging
export LOG_LEVEL=INFO
export JSON_LOGGING=true

# Enable metrics (optional)
export ANALYTICS_ENABLED=true
export AUTH_TOKEN=$(openssl rand -hex 32)

# Start API
uvicorn api.main:app
```

## Structured Logging

```python
from api.observability import get_logger

logger = get_logger(__name__)

# Log with context (request_id/trace_id auto-included)
logger.info("Action completed", extra_fields={"count": 42})

# Error with traceback
logger.error("Failed", extra_fields={"reason": "timeout"}, exc_info=True)
```

## Metrics

```python
from api.observability.metrics import increment_counter, record_timer

# Count events
increment_counter("events.processed", tags={"type": "import"})

# Measure timing
record_timer("operation.duration", duration_ms, tags={"op": "export"})
```

## View Metrics

```bash
# Access metrics endpoint (requires auth)
curl -H "Authorization: Bearer $AUTH_TOKEN" \
     http://localhost:8000/api/v1/health/metrics | jq
```

## OpenTelemetry (Optional)

```bash
# Install packages
pip install opentelemetry-distro opentelemetry-exporter-otlp

# Start Jaeger
docker run -d -p 4317:4317 -p 16686:16686 jaegertracing/all-in-one:latest

# Configure endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# View traces at http://localhost:16686
```

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `LOG_LEVEL` | `INFO` | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `JSON_LOGGING` | `true` | JSON output (true) or text (false) |
| `ANALYTICS_ENABLED` | `false` | Enable metrics collection |
| `AUTH_TOKEN` | - | Metrics endpoint auth token |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | - | OpenTelemetry collector URL |

## Response Headers

Every response includes:

- `X-Request-Id`: Unique request identifier
- `X-Trace-Id`: Distributed trace identifier

## Best Practices

✅ **DO:**

- Use structured fields: `extra_fields={"key": "value"}`
- Include relevant context: counts, durations, IDs
- Use appropriate log levels
- Authenticate metrics endpoint

❌ **DON'T:**

- Log PHI (patient data)
- Use string interpolation: `f"User {id}"`
- Log passwords or tokens
- Expose metrics without auth

## Troubleshooting

**Logs not JSON?**
→ Set `JSON_LOGGING=true`

**Metrics 404?**
→ Set `ANALYTICS_ENABLED=true` and restart

**Metrics 401?**
→ Include `Authorization: Bearer <token>` header

**OpenTelemetry not working?**
→ Install packages and set `OTEL_EXPORTER_OTLP_ENDPOINT`

## Full Documentation

- [Observability Guide](Observability.md) - Complete documentation
- [Module README](../api/observability/README.md) - API reference
- [Config Examples](../observability.env.example) - Configuration templates
