"""
Test dual-mount API functionality.
"""
import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_dual_mount_stats():
    """Test that /tree/stats is available at both mounts."""
    # Test bare mount
    response_bare = client.get("/tree/stats")
    assert response_bare.status_code == 200
    
    # Test versioned mount
    response_v1 = client.get("/api/v1/tree/stats")
    assert response_v1.status_code == 200
    
    # Both should return the same data
    assert response_bare.json() == response_v1.json()

def test_dual_mount_health():
    """Test that /health is available at both mounts."""
    # Test bare mount
    response_bare = client.get("/health")
    assert response_bare.status_code == 200
    
    # Test versioned mount
    response_v1 = client.get("/api/v1/health")
    assert response_v1.status_code == 200
    
    # Both should return the same data
    assert response_bare.json() == response_v1.json()

def test_dual_mount_export():
    """Test that export endpoints are available at both mounts."""
    # Test CSV export
    response_bare = client.get("/tree/export")
    response_v1 = client.get("/api/v1/tree/export")
    
    assert response_bare.status_code == 200
    assert response_v1.status_code == 200
    assert response_bare.content == response_v1.content
    
    # Test XLSX export
    response_bare_xlsx = client.get("/tree/export.xlsx")
    response_v1_xlsx = client.get("/api/v1/tree/export.xlsx")
    
    assert response_bare_xlsx.status_code == 200
    assert response_v1_xlsx.status_code == 200
    assert response_bare_xlsx.content == response_v1_xlsx.content
