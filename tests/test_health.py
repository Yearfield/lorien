"""Minimal health endpoint checks for the trimmed API surface."""


def test_health_endpoint_ok(client_db):
    client, _ = client_db
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert "version" in data
    assert "db" in data
    assert "features" in data
    # Metrics should be omitted when analytics are disabled
    assert "metrics" not in data


def test_health_metrics_disabled(client_db):
    client, _ = client_db
    response = client.get("/api/v1/health/metrics")
    assert response.status_code == 404
