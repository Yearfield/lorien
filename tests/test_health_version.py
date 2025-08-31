"""
Test health endpoint version consistency.
"""

from tests.utils.api_client import get
from core.version import __version__


def test_health_has_version():
    """Test that health endpoint returns correct version."""
    r = get("/health")
    assert r.status_code == 200
    assert r.json().get("version") == __version__


def test_health_root_mount_has_version():
    """Test that root health endpoint returns correct version."""
    from fastapi.testclient import TestClient
    from api.app import app
    
    client = TestClient(app)
    r = client.get("/health")  # root mount
    assert r.status_code == 200
    assert r.json().get("version") == __version__


def test_health_api_v1_mount_has_version():
    """Test that API v1 health endpoint returns correct version."""
    r = get("/health")
    assert r.status_code == 200
    assert r.json().get("version") == __version__
