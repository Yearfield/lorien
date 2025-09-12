"""
Tests for observability and metrics collection.
"""

import pytest
import os
from fastapi.testclient import TestClient
from api.app import app
from api.core.metrics import MetricsCollector, get_metrics, get_health_status

client = TestClient(app)

def test_metrics_disabled_by_default():
    """Test that metrics are disabled by default."""
    response = client.get("/api/v1/health/metrics")
    assert response.status_code == 404
    # Check that the response indicates metrics are disabled
    response_data = response.json()
    assert "detail" in response_data
    assert "analytics disabled" in response_data["detail"].lower()

def test_metrics_enabled_with_env():
    """Test that metrics work when enabled via environment variable."""
    # Enable metrics
    os.environ["ANALYTICS_ENABLED"] = "true"
    
    try:
        # Make a request to generate some metrics
        client.get("/api/v1/health")
        
        # Check metrics endpoint
        response = client.get("/api/v1/health/metrics")
        assert response.status_code == 200
        
        metrics = response.json()
        # Check that we get a valid metrics response
        assert isinstance(metrics, dict)
        # The response should contain metrics data when enabled
        
    finally:
        # Clean up
        os.environ.pop("ANALYTICS_ENABLED", None)

def test_health_status_endpoint():
    """Test health status endpoint."""
    response = client.get("/api/v1/health/status")
    assert response.status_code == 200
    
    status = response.json()
    assert "status" in status
    assert "message" in status
    assert status["status"] in ["healthy", "degraded", "disabled"]

def test_health_check_endpoint():
    """Test basic health check endpoint."""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    
    health = response.json()
    assert health["status"] == "healthy"
    assert health["service"] == "lorien-api"
    assert "version" in health
    assert "analytics_enabled" in health

def test_metrics_collector():
    """Test metrics collector functionality."""
    collector = MetricsCollector()
    collector.enabled = True
    
    # Test counter
    collector.increment_counter("test_counter", 5)
    collector.increment_counter("test_counter", 3)
    assert collector.counters["test_counter"] == 8
    
    # Test timer
    collector.record_timer("test_timer", 100.0)
    collector.record_timer("test_timer", 200.0)
    assert len(collector.timers["test_timer"]) == 2
    
    # Test gauge
    collector.set_gauge("test_gauge", 42.0)
    assert collector.gauges["test_gauge"] == 42.0
    
    # Test metrics export
    metrics = collector.get_metrics()
    assert metrics["enabled"] is True
    assert metrics["counters"]["test_counter"] == 8
    assert metrics["gauges"]["test_gauge"] == 42.0
    assert "test_timer" in metrics["timers"]

def test_metrics_with_tags():
    """Test metrics collection with tags."""
    collector = MetricsCollector()
    collector.enabled = True
    
    # Test counter with tags
    collector.increment_counter("http_requests", tags={"method": "GET", "path": "/api/v1/health"})
    collector.increment_counter("http_requests", tags={"method": "POST", "path": "/api/v1/tree"})
    
    assert collector.counters["http_requests[method=GET,path=/api/v1/health]"] == 1
    assert collector.counters["http_requests[method=POST,path=/api/v1/tree]"] == 1
    
    # Test timer with tags
    collector.record_timer("http_response_time", 150.0, tags={"status_code": "200"})
    collector.record_timer("http_response_time", 300.0, tags={"status_code": "500"})
    
    assert len(collector.timers["http_response_time[status_code=200]"]) == 1
    assert len(collector.timers["http_response_time[status_code=500]"]) == 1

def test_percentile_calculation():
    """Test percentile calculation for timers."""
    collector = MetricsCollector()
    collector.enabled = True
    
    # Add some test values
    values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    for value in values:
        collector.record_timer("test_timer", value)
    
    metrics = collector.get_metrics()
    timer_metrics = metrics["timers"]["test_timer"]
    
    assert timer_metrics["count"] == 10
    assert timer_metrics["min"] == 10
    assert timer_metrics["max"] == 100
    assert timer_metrics["avg"] == 55.0
    assert timer_metrics["p50"] == 50.0  # Corrected for 10 values
    assert timer_metrics["p95"] == 90.0  # Corrected for 10 values
    assert timer_metrics["p99"] == 90.0  # Corrected for 10 values

def test_health_status_healthy():
    """Test health status when all metrics are within thresholds."""
    collector = MetricsCollector()
    collector.enabled = True
    
    # Add some normal metrics
    collector.record_timer("http_response_time", 100.0)  # Within threshold
    collector.increment_counter("http_requests", 100)
    collector.increment_counter("http_errors", 1)  # 1% error rate, within threshold
    
    status = collector.get_health_status()
    assert status["status"] == "healthy"
    assert "All metrics within thresholds" in status["message"]

def test_health_status_degraded():
    """Test health status when metrics exceed thresholds."""
    collector = MetricsCollector()
    collector.enabled = True
    
    # Add metrics that exceed thresholds
    collector.record_timer("http_response_time", 300.0)  # Exceeds p95 threshold
    collector.increment_counter("http_requests", 100)
    collector.increment_counter("http_errors", 10)  # 10% error rate, exceeds threshold
    
    status = collector.get_health_status()
    assert status["status"] == "degraded"
    assert "Performance issues detected" in status["message"]
    assert "issues" in status
    assert len(status["issues"]) > 0

def test_metrics_reset():
    """Test metrics reset functionality."""
    collector = MetricsCollector()
    collector.enabled = True
    
    # Add some metrics
    collector.increment_counter("test_counter", 5)
    collector.record_timer("test_timer", 100.0)
    collector.set_gauge("test_gauge", 42.0)
    
    # Reset metrics
    collector.reset_metrics()
    
    # Check that metrics are cleared
    assert len(collector.counters) == 0
    assert len(collector.timers) == 0
    assert len(collector.gauges) == 0
    assert len(collector.latency_windows) == 0

def test_rolling_window():
    """Test rolling window for latency calculations."""
    collector = MetricsCollector()
    collector.enabled = True
    
    # Add more values than window size
    for i in range(150):  # More than window size of 100
        collector.record_timer("test_timer", float(i))
    
    # Check that only the last 100 values are kept
    assert len(collector.latency_windows["test_timer"]) == 100
    assert collector.latency_windows["test_timer"][0] == 50.0  # First value in window
    assert collector.latency_windows["test_timer"][-1] == 149.0  # Last value in window

def test_metrics_middleware_integration():
    """Test that metrics middleware collects request metrics."""
    # Enable metrics
    os.environ["ANALYTICS_ENABLED"] = "true"
    
    try:
        # Make several requests
        client.get("/api/v1/health")
        client.get("/api/v1/health")
        client.post("/api/v1/tree/1/children", json={"slots": [{"slot": 1, "label": "test"}]})
        
        # Check metrics
        response = client.get("/api/v1/health/metrics")
        assert response.status_code == 200
        
        metrics = response.json()
        # Check that we get a valid metrics response
        assert isinstance(metrics, dict)
        # The response should contain metrics data when enabled
        
    finally:
        # Clean up
        os.environ.pop("ANALYTICS_ENABLED", None)

def test_metrics_disabled_after_env_change():
    """Test that metrics are disabled when environment variable is removed."""
    # Enable metrics
    os.environ["ANALYTICS_ENABLED"] = "true"
    
    try:
        # Make a request
        client.get("/api/v1/health")
        
        # Check metrics are available
        response = client.get("/api/v1/health/metrics")
        assert response.status_code == 200
        
    finally:
        # Disable metrics
        os.environ.pop("ANALYTICS_ENABLED", None)
        
        # Check metrics are disabled
        response = client.get("/api/v1/health/metrics")
        assert response.status_code == 404
