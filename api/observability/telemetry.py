"""
OpenTelemetry integration for distributed tracing and metrics.

Provides hooks for OTLP export to observability backends like:
- Jaeger
- Zipkin
- Prometheus
- Grafana
- Datadog
- New Relic
- etc.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def is_otel_enabled() -> bool:
    """
    Check if OpenTelemetry is enabled.

    Enabled when OTEL_EXPORTER_OTLP_ENDPOINT is set.
    """
    return bool(os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"))


def setup_opentelemetry(
    service_name: str = "lorien-api",
    service_version: Optional[str] = None,
) -> bool:
    """
    Initialize OpenTelemetry instrumentation.

    This function sets up:
    - Tracer provider with OTLP exporter
    - Metrics provider with OTLP exporter
    - FastAPI auto-instrumentation
    - SQLite instrumentation (if available)

    Args:
        service_name: Name of the service
        service_version: Version of the service

    Returns:
        True if successfully initialized, False if disabled or failed
    """
    if not is_otel_enabled():
        logger.info("OpenTelemetry disabled (OTEL_EXPORTER_OTLP_ENDPOINT not set)")
        return False

    try:
        # Import OpenTelemetry packages (optional dependencies)
        from opentelemetry import metrics, trace
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.logging import LoggingInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        # Create resource attributes
        resource_attributes = {
            "service.name": service_name,
            "service.instance.id": os.getenv("HOSTNAME", "unknown"),
        }

        if service_version:
            resource_attributes["service.version"] = service_version

        # Add custom attributes from environment
        env_prefix = "OTEL_RESOURCE_ATTRIBUTES_"
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                attr_name = key[len(env_prefix) :].lower().replace("_", ".")
                resource_attributes[attr_name] = value

        resource = Resource.create(resource_attributes)

        # ========== TRACING SETUP ==========

        # Get OTLP endpoint
        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

        # Configure trace exporter
        trace_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            headers=_get_otlp_headers(),
        )

        # Create tracer provider
        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))

        # Set global tracer provider
        trace.set_tracer_provider(tracer_provider)

        # ========== METRICS SETUP ==========

        # Configure metric exporter
        metric_exporter = OTLPMetricExporter(
            endpoint=otlp_endpoint,
            headers=_get_otlp_headers(),
        )

        # Create metrics reader
        metric_reader = PeriodicExportingMetricReader(
            exporter=metric_exporter,
            export_interval_millis=int(os.getenv("OTEL_METRIC_EXPORT_INTERVAL", "60000")),
        )

        # Create meter provider
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader],
        )

        # Set global meter provider
        metrics.set_meter_provider(meter_provider)

        # ========== AUTO-INSTRUMENTATION ==========

        # Instrument FastAPI
        FastAPIInstrumentor.instrument()

        # Instrument logging to add trace context
        LoggingInstrumentor().instrument()

        # Instrument HTTP requests
        RequestsInstrumentor().instrument()

        logger.info(
            f"✓ OpenTelemetry initialized - exporting to {otlp_endpoint}",
            extra={
                "service_name": service_name,
                "service_version": service_version,
                "endpoint": otlp_endpoint,
            },
        )

        return True

    except ImportError as e:
        logger.warning(
            f"OpenTelemetry packages not installed: {e}. "
            "Install with: pip install opentelemetry-distro opentelemetry-exporter-otlp"
        )
        return False

    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry: {e}", exc_info=True)
        return False


def _get_otlp_headers() -> dict[str, str]:
    """
    Get OTLP headers from environment.

    Supports format: key1=value1,key2=value2
    """
    headers_str = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")
    if not headers_str:
        return {}

    headers = {}
    for pair in headers_str.split(","):
        if "=" in pair:
            key, value = pair.split("=", 1)
            headers[key.strip()] = value.strip()

    return headers


def shutdown_opentelemetry():
    """
    Gracefully shutdown OpenTelemetry providers.

    Call this on application shutdown to flush pending telemetry.
    """
    if not is_otel_enabled():
        return

    try:
        from opentelemetry import metrics, trace

        # Get providers
        tracer_provider = trace.get_tracer_provider()
        meter_provider = metrics.get_meter_provider()

        # Shutdown (flush pending data)
        if hasattr(tracer_provider, "shutdown"):
            tracer_provider.shutdown()

        if hasattr(meter_provider, "shutdown"):
            meter_provider.shutdown()

        logger.info("✓ OpenTelemetry shutdown complete")

    except Exception as e:
        logger.warning(f"Error during OpenTelemetry shutdown: {e}")


# Convenience functions for creating spans and metrics


def get_tracer(name: str):
    """Get a tracer for creating custom spans."""
    if not is_otel_enabled():
        return None

    try:
        from opentelemetry import trace

        return trace.get_tracer(name)
    except ImportError:
        return None


def get_meter(name: str):
    """Get a meter for creating custom metrics."""
    if not is_otel_enabled():
        return None

    try:
        from opentelemetry import metrics

        return metrics.get_meter(name)
    except ImportError:
        return None
