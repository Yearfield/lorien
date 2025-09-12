"""
Role-Based Access Control (RBAC) system for Lorien.

Provides user management, role assignment, and permission checking
for fine-grained access control to API endpoints.
"""

import os
import hashlib
import secrets
from typing import Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)

class Permission(str, Enum):
    """System permissions."""
    # Read permissions
    READ_TREE = "read:tree"
    READ_TRIAGE = "read:triage"
    READ_FLAGS = "read:flags"
    READ_DICTIONARY = "read:dictionary"
    READ_EXPORT = "read:export"
    READ_HEALTH = "read:health"
    
    # Write permissions
    WRITE_TREE = "write:tree"
    WRITE_TRIAGE = "write:triage"
    WRITE_FLAGS = "write:flags"
    WRITE_DICTIONARY = "write:dictionary"
    WRITE_EXPORT = "write:export"
    
    # Admin permissions
    ADMIN_USERS = "admin:users"
    ADMIN_ROLES = "admin:roles"
    ADMIN_SYSTEM = "admin:system"
    ADMIN_AUDIT = "admin:audit"

class Role(str, Enum):
    """System roles."""
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

# Role to permissions mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.VIEWER: {
        Permission.READ_TREE,
        Permission.READ_TRIAGE,
        Permission.READ_FLAGS,
        Permission.READ_DICTIONARY,
        Permission.READ_EXPORT,
        Permission.READ_HEALTH,
    },
    Role.EDITOR: {
        Permission.READ_TREE,
        Permission.READ_TRIAGE,
        Permission.READ_FLAGS,
        Permission.READ_DICTIONARY,
        Permission.READ_EXPORT,
        Permission.READ_HEALTH,
        Permission.WRITE_TREE,
        Permission.WRITE_TRIAGE,
        Permission.WRITE_FLAGS,
        Permission.WRITE_DICTIONARY,
        Permission.WRITE_EXPORT,
    },
    Role.ADMIN: {
        Permission.READ_TREE,
        Permission.READ_TRIAGE,
        Permission.READ_FLAGS,
        Permission.READ_DICTIONARY,
        Permission.READ_EXPORT,
        Permission.READ_HEALTH,
        Permission.WRITE_TREE,
        Permission.WRITE_TRIAGE,
        Permission.WRITE_FLAGS,
        Permission.WRITE_DICTIONARY,
        Permission.WRITE_EXPORT,
        Permission.ADMIN_USERS,
        Permission.ADMIN_ROLES,
        Permission.ADMIN_AUDIT,
    },
    Role.SUPER_ADMIN: {
        # All permissions
        *[p for p in Permission],
    }
}

@dataclass
class User:
    """User model for RBAC."""
    id: str
    username: str
    email: str
    roles: Set[Role]
    is_active: bool = True
    created_at: datetime = None
    last_login: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

@dataclass
class Session:
    """User session for authentication."""
    token: str
    user_id: str
    expires_at: datetime
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.now(timezone.utc) > self.expires_at

class RBACManager:
    """Manages RBAC operations."""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self._rbac_enabled = None  # Cache for enabled state
        self._initialize_default_users()
    
    def _initialize_default_users(self):
        """Initialize default users if RBAC is enabled."""
        if not self.is_enabled():
            return
        
        # Create default admin user
        admin_user = User(
            id="admin",
            username="admin",
            email="admin@lorien.local",
            roles={Role.SUPER_ADMIN}
        )
        self.users["admin"] = admin_user
        
        # Create default editor user
        editor_user = User(
            id="editor",
            username="editor",
            email="editor@lorien.local",
            roles={Role.EDITOR}
        )
        self.users["editor"] = editor_user
        
        # Create default viewer user
        viewer_user = User(
            id="viewer",
            username="viewer",
            email="viewer@lorien.local",
            roles={Role.VIEWER}
        )
        self.users["viewer"] = viewer_user
        
        logger.info("Initialized default RBAC users: admin, editor, viewer")
    
    def is_enabled(self) -> bool:
        """Check if RBAC is enabled."""
        if self._rbac_enabled is None:
            self._rbac_enabled = os.getenv("RBAC_ENABLED", "false").lower() == "true"
        return self._rbac_enabled
    
    def force_enable(self) -> None:
        """Force enable RBAC (for testing)."""
        self._rbac_enabled = True
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256()
        hash_obj.update(f"{password}{salt}".encode())
        return f"{salt}:{hash_obj.hexdigest()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        try:
            salt, hash_value = hashed.split(":", 1)
            hash_obj = hashlib.sha256()
            hash_obj.update(f"{password}{salt}".encode())
            return hash_obj.hexdigest() == hash_value
        except ValueError:
            return False
    
    def create_user(self, username: str, email: str, password: str, roles: Set[Role]) -> User:
        """Create a new user."""
        if not self.is_enabled():
            raise ValueError("RBAC is not enabled")
        
        user_id = secrets.token_urlsafe(16)
        hashed_password = self.hash_password(password)
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            roles=roles
        )
        
        # Store password hash (in real implementation, this would be in database)
        user._password_hash = hashed_password
        
        self.users[user_id] = user
        logger.info(f"Created user: {username} with roles: {[r.value for r in roles]}")
        
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        if not self.is_enabled():
            return None
        
        # Find user by username
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break
        
        if not user or not user.is_active:
            return None
        
        # In real implementation, verify password against stored hash
        # For now, use simple password matching for demo
        if hasattr(user, '_password_hash'):
            if not self.verify_password(password, user._password_hash):
                return None
        else:
            # Default passwords for demo users
            default_passwords = {
                "admin": "admin123",
                "editor": "editor123",
                "viewer": "viewer123"
            }
            if password != default_passwords.get(username):
                return None
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        
        return user
    
    def create_session(self, user: User, duration_hours: int = 24) -> Session:
        """Create a new session for a user."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=duration_hours)
        
        session = Session(
            token=token,
            user_id=user.id,
            expires_at=expires_at
        )
        
        self.sessions[token] = session
        logger.info(f"Created session for user: {user.username}")
        
        return session
    
    def get_session(self, token: str) -> Optional[Session]:
        """Get a session by token."""
        session = self.sessions.get(token)
        if session and not session.is_expired:
            return session
        elif session:
            # Remove expired session
            del self.sessions[token]
        return None
    
    def get_user_by_session(self, token: str) -> Optional[User]:
        """Get user by session token."""
        session = self.get_session(token)
        if not session:
            return None
        
        return self.users.get(session.user_id)
    
    def has_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        if not user or not user.is_active:
            return False
        
        # Super admin has all permissions
        if Role.SUPER_ADMIN in user.roles:
            return True
        
        # Check if any of user's roles have the permission
        for role in user.roles:
            if permission in ROLE_PERMISSIONS.get(role, set()):
                return True
        
        return False
    
    def has_any_permission(self, user: User, permissions: Set[Permission]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(self.has_permission(user, perm) for perm in permissions)
    
    def has_all_permissions(self, user: User, permissions: Set[Permission]) -> bool:
        """Check if user has all of the specified permissions."""
        return all(self.has_permission(user, perm) for perm in permissions)
    
    def get_user_permissions(self, user: User) -> Set[Permission]:
        """Get all permissions for a user."""
        if not user or not user.is_active:
            return set()
        
        permissions = set()
        for role in user.roles:
            permissions.update(ROLE_PERMISSIONS.get(role, set()))
        
        return permissions
    
    def revoke_session(self, token: str) -> bool:
        """Revoke a session."""
        if token in self.sessions:
            del self.sessions[token]
            logger.info(f"Revoked session: {token}")
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        expired_tokens = [
            token for token, session in self.sessions.items()
            if session.is_expired
        ]
        
        for token in expired_tokens:
            del self.sessions[token]
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired sessions")

# Global RBAC manager instance
rbac_manager = RBACManager()
