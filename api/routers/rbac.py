"""
RBAC management endpoints.

Provides user management, role assignment, and permission checking
for the RBAC system.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Dict, Any, Set
import logging

from ..core.rbac import rbac_manager, User, Role, Permission
from ..middleware.enhanced_auth import get_current_user, require_permission

logger = logging.getLogger(__name__)

router = APIRouter(tags=["rbac"])

@router.get("/rbac/status")
async def get_rbac_status():
    """Get RBAC system status."""
    return {
        "enabled": rbac_manager.is_enabled(),
        "total_users": len(rbac_manager.users),
        "active_sessions": len(rbac_manager.sessions),
        "available_roles": [role.value for role in Role],
        "available_permissions": [perm.value for perm in Permission]
    }

@router.get("/rbac/users")
async def list_users(
    current_user: User = Depends(require_permission(Permission.ADMIN_USERS))
):
    """List all users (admin only)."""
    users = []
    for user in rbac_manager.users.values():
        users.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": [role.value for role in user.roles],
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        })
    
    return {
        "users": users,
        "total": len(users)
    }

@router.get("/rbac/users/{user_id}")
async def get_user(
    user_id: str,
    current_user: User = Depends(require_permission(Permission.ADMIN_USERS))
):
    """Get user details (admin only)."""
    user = rbac_manager.users.get(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "user_not_found",
                "message": f"User {user_id} not found"
            }
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "roles": [role.value for role in user.roles],
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "permissions": [perm.value for perm in rbac_manager.get_user_permissions(user)]
    }

@router.post("/rbac/users")
async def create_user(
    user_data: Dict[str, Any],
    current_user: User = Depends(require_permission(Permission.ADMIN_USERS))
):
    """Create a new user (admin only)."""
    if not rbac_manager.is_enabled():
        raise HTTPException(
            status_code=400,
            detail={
                "error": "rbac_disabled",
                "message": "RBAC is not enabled"
            }
        )
    
    username = user_data.get("username")
    email = user_data.get("email")
    password = user_data.get("password")
    roles = user_data.get("roles", [])
    
    if not all([username, email, password]):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "missing_required_fields",
                "message": "username, email, and password are required"
            }
        )
    
    # Validate roles
    try:
        role_set = {Role(role) for role in roles}
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_roles",
                "message": f"Invalid roles: {e}"
            }
        )
    
    # Check if username already exists
    for user in rbac_manager.users.values():
        if user.username == username:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "username_exists",
                    "message": f"Username {username} already exists"
                }
            )
    
    # Create user
    try:
        user = rbac_manager.create_user(username, email, password, role_set)
        logger.info(f"Created user: {username} by {current_user.username}")
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": [role.value for role in user.roles],
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "user_creation_failed",
                "message": str(e)
            }
        )

@router.post("/rbac/auth/login")
async def login(credentials: Dict[str, str]):
    """Authenticate user and create session."""
    if not rbac_manager.is_enabled():
        raise HTTPException(
            status_code=400,
            detail={
                "error": "rbac_disabled",
                "message": "RBAC is not enabled"
            }
        )
    
    username = credentials.get("username")
    password = credentials.get("password")
    
    if not username or not password:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "missing_credentials",
                "message": "username and password are required"
            }
        )
    
    # Authenticate user
    user = rbac_manager.authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "invalid_credentials",
                "message": "Invalid username or password"
            }
        )
    
    # Create session
    session = rbac_manager.create_session(user)
    logger.info(f"User {username} logged in successfully")
    
    return {
        "token": session.token,
        "expires_at": session.expires_at.isoformat(),
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": [role.value for role in user.roles],
            "permissions": [perm.value for perm in rbac_manager.get_user_permissions(user)]
        }
    }

@router.post("/rbac/auth/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Logout user and revoke session."""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "not_authenticated",
                "message": "Not authenticated"
            }
        )
    
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        rbac_manager.revoke_session(token)
        logger.info(f"User {current_user.username} logged out")
    
    return {"message": "Logged out successfully"}

@router.get("/rbac/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "not_authenticated",
                "message": "Not authenticated"
            }
        )
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "roles": [role.value for role in current_user.roles],
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
        "permissions": [perm.value for perm in rbac_manager.get_user_permissions(current_user)]
    }

@router.get("/rbac/permissions")
async def get_permissions(
    current_user: User = Depends(get_current_user)
):
    """Get current user permissions."""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "not_authenticated",
                "message": "Not authenticated"
            }
        )
    
    permissions = rbac_manager.get_user_permissions(current_user)
    
    return {
        "permissions": [perm.value for perm in permissions],
        "total": len(permissions)
    }

@router.post("/rbac/users/{user_id}/roles")
async def assign_roles(
    user_id: str,
    roles_data: Dict[str, List[str]],
    current_user: User = Depends(require_permission(Permission.ADMIN_USERS))
):
    """Assign roles to user (admin only)."""
    user = rbac_manager.users.get(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "user_not_found",
                "message": f"User {user_id} not found"
            }
        )
    
    roles = roles_data.get("roles", [])
    try:
        role_set = {Role(role) for role in roles}
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_roles",
                "message": f"Invalid roles: {e}"
            }
        )
    
    # Update user roles
    user.roles = role_set
    logger.info(f"Updated roles for user {user.username}: {[r.value for r in role_set]}")
    
    return {
        "id": user.id,
        "username": user.username,
        "roles": [role.value for role in user.roles],
        "permissions": [perm.value for perm in rbac_manager.get_user_permissions(user)]
    }

@router.delete("/rbac/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_permission(Permission.ADMIN_USERS))
):
    """Delete user (admin only)."""
    user = rbac_manager.users.get(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "user_not_found",
                "message": f"User {user_id} not found"
            }
        )
    
    # Don't allow deleting self
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "cannot_delete_self",
                "message": "Cannot delete your own account"
            }
        )
    
    # Revoke all sessions for this user
    sessions_to_revoke = [
        token for token, session in rbac_manager.sessions.items()
        if session.user_id == user_id
    ]
    
    for token in sessions_to_revoke:
        rbac_manager.revoke_session(token)
    
    # Delete user
    del rbac_manager.users[user_id]
    logger.info(f"Deleted user {user.username} by {current_user.username}")
    
    return {"message": f"User {user.username} deleted successfully"}

@router.post("/rbac/sessions/cleanup")
async def cleanup_sessions(
    current_user: User = Depends(require_permission(Permission.ADMIN_SYSTEM))
):
    """Cleanup expired sessions (admin only)."""
    rbac_manager.cleanup_expired_sessions()
    
    return {
        "message": "Expired sessions cleaned up",
        "active_sessions": len(rbac_manager.sessions)
    }
