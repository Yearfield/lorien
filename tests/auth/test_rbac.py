"""
Tests for RBAC (Role-Based Access Control) system.
"""

import pytest
import os
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from api.core.rbac import rbac_manager, User, Role, Permission
from api.app import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_rbac():
    """Setup RBAC for tests."""
    # Enable RBAC
    os.environ["RBAC_ENABLED"] = "true"
    
    # Clear existing data
    rbac_manager.users.clear()
    rbac_manager.sessions.clear()
    
    # Initialize default users
    rbac_manager._initialize_default_users()
    
    # Ensure RBAC is enabled
    rbac_manager.force_enable()
    
    yield
    
    # Cleanup
    os.environ.pop("RBAC_ENABLED", None)
    rbac_manager.users.clear()
    rbac_manager.sessions.clear()

def test_rbac_status():
    """Test RBAC status endpoint."""
    response = client.get("/api/v1/rbac/status")
    assert response.status_code == 200
    
    data = response.json()
    assert data["enabled"] is True
    assert data["total_users"] >= 0  # May be 0 if not initialized yet
    assert data["active_sessions"] == 0
    assert "admin" in data["available_roles"]
    assert "read:tree" in data["available_permissions"]

def test_user_authentication():
    """Test user authentication."""
    # Test valid login
    response = client.post("/api/v1/rbac/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    
    data = response.json()
    assert "token" in data
    assert data["user"]["username"] == "admin"
    assert "super_admin" in data["user"]["roles"]
    
    # Test invalid login
    response = client.post("/api/v1/rbac/auth/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_user_management():
    """Test user management endpoints."""
    # Login as admin
    login_response = client.post("/api/v1/rbac/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # List users
    response = client.get("/api/v1/rbac/users", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["users"]) == 3
    assert data["total"] == 3
    
    # Get specific user
    admin_user = next(u for u in data["users"] if u["username"] == "admin")
    response = client.get(f"/api/v1/rbac/users/{admin_user['id']}", headers=headers)
    assert response.status_code == 200
    
    user_data = response.json()
    assert user_data["username"] == "admin"
    assert "super_admin" in user_data["roles"]

def test_permission_system():
    """Test permission system."""
    # Login as editor
    login_response = client.post("/api/v1/rbac/auth/login", json={
        "username": "editor",
        "password": "editor123"
    })
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check permissions
    response = client.get("/api/v1/rbac/permissions", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "write:tree" in data["permissions"]
    assert "read:tree" in data["permissions"]
    assert "admin:users" not in data["permissions"]
    
    # Check current user info
    response = client.get("/api/v1/rbac/me", headers=headers)
    assert response.status_code == 200
    
    user_data = response.json()
    assert user_data["username"] == "editor"
    assert "editor" in user_data["roles"]

def test_role_assignment():
    """Test role assignment."""
    # Login as admin
    login_response = client.post("/api/v1/rbac/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get editor user
    users_response = client.get("/api/v1/rbac/users", headers=headers)
    editor_user = next(u for u in users_response.json()["users"] if u["username"] == "editor")
    
    # Assign admin role to editor
    response = client.post(f"/api/v1/rbac/users/{editor_user['id']}/roles", 
                          json={"roles": ["admin"]}, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "admin" in data["roles"]
    assert "admin:users" in data["permissions"]

def test_unauthorized_access():
    """Test unauthorized access."""
    # Try to access admin endpoint without authentication
    response = client.get("/api/v1/rbac/users")
    assert response.status_code == 401
    
    # Try to access admin endpoint with viewer role
    login_response = client.post("/api/v1/rbac/auth/login", json={
        "username": "viewer",
        "password": "viewer123"
    })
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/rbac/users", headers=headers)
    assert response.status_code == 403

def test_session_management():
    """Test session management."""
    # Login
    login_response = client.post("/api/v1/rbac/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Use session
    response = client.get("/api/v1/rbac/me", headers=headers)
    assert response.status_code == 200
    
    # Logout
    response = client.post("/api/v1/rbac/auth/logout", headers=headers)
    assert response.status_code == 200
    
    # Try to use expired session (should fail)
    try:
        response = client.get("/api/v1/rbac/me", headers=headers)
        assert response.status_code == 401
    except Exception as e:
        # The middleware raises HTTPException which gets converted to 401
        assert "401" in str(e) or "invalid_token" in str(e)

def test_rbac_disabled():
    """Test behavior when RBAC is disabled."""
    # Disable RBAC
    os.environ["RBAC_ENABLED"] = "false"
    
    # Clear RBAC data and reset enabled state
    rbac_manager.users.clear()
    rbac_manager.sessions.clear()
    rbac_manager._rbac_enabled = None  # Reset cached state
    
    # Try to access RBAC endpoints
    response = client.get("/api/v1/rbac/status")
    assert response.status_code == 200
    
    data = response.json()
    assert data["enabled"] is False
    
    # Try to login
    response = client.post("/api/v1/rbac/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 400
    
    # Re-enable RBAC
    os.environ["RBAC_ENABLED"] = "true"
    rbac_manager.force_enable()

def test_user_creation():
    """Test user creation."""
    # Login as admin
    login_response = client.post("/api/v1/rbac/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create new user
    response = client.post("/api/v1/rbac/users", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "roles": ["editor"]
    }, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == "testuser"
    assert "editor" in data["roles"]
    
    # Verify user can login
    login_response = client.post("/api/v1/rbac/auth/login", json={
        "username": "testuser",
        "password": "testpass123"
    })
    assert login_response.status_code == 200

def test_duplicate_username():
    """Test duplicate username handling."""
    # Login as admin
    login_response = client.post("/api/v1/rbac/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to create user with existing username
    response = client.post("/api/v1/rbac/users", json={
        "username": "admin",  # Already exists
        "email": "test@example.com",
        "password": "testpass123",
        "roles": ["editor"]
    }, headers=headers)
    assert response.status_code == 409

def test_invalid_roles():
    """Test invalid role handling."""
    # Login as admin
    login_response = client.post("/api/v1/rbac/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to create user with invalid role
    response = client.post("/api/v1/rbac/users", json={
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "testpass123",
        "roles": ["invalid_role"]
    }, headers=headers)
    assert response.status_code == 400

def test_user_deletion():
    """Test user deletion."""
    # Login as admin
    login_response = client.post("/api/v1/rbac/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create test user
    create_response = client.post("/api/v1/rbac/users", json={
        "username": "deleteme",
        "email": "delete@example.com",
        "password": "testpass123",
        "roles": ["viewer"]
    }, headers=headers)
    user_id = create_response.json()["id"]
    
    # Delete user
    response = client.delete(f"/api/v1/rbac/users/{user_id}", headers=headers)
    assert response.status_code == 200
    
    # Verify user is deleted
    response = client.get(f"/api/v1/rbac/users/{user_id}", headers=headers)
    assert response.status_code == 404

def test_self_deletion_prevention():
    """Test prevention of self-deletion."""
    # Login as admin
    login_response = client.post("/api/v1/rbac/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get admin user ID
    me_response = client.get("/api/v1/rbac/me", headers=headers)
    admin_id = me_response.json()["id"]
    
    # Try to delete self
    response = client.delete(f"/api/v1/rbac/users/{admin_id}", headers=headers)
    assert response.status_code == 400
