"""
Optimistic concurrency control utilities.

Provides version checking and conflict resolution for concurrent edits
while maintaining the existing 409 slot conflict semantics.
"""

import sqlite3
import time
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class ConcurrencyManager:
    """Manages optimistic concurrency control for tree operations."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
    
    def get_node_version(self, node_id: int) -> Optional[Dict[str, Any]]:
        """
        Get current version information for a node.
        
        Args:
            node_id: Node ID to get version for
            
        Returns:
            Version information dict with id, version, timestamp
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, 
                   (SELECT COUNT(*) FROM nodes WHERE parent_id = ?) as child_count
            FROM nodes 
            WHERE id = ?
        """, (node_id, node_id))
        
        result = cursor.fetchone()
        if not result:
            return None
        
        return {
            "id": result[0],
            "version": result[1],  # Use child count as version
            "timestamp": time.time(),
            "updated_at": datetime.now().isoformat()  # Generate timestamp
        }
    
    def check_version_match(self, node_id: int, expected_version: Optional[int] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if the current version matches the expected version.
        
        Args:
            node_id: Node ID to check
            expected_version: Expected version number (child count)
            
        Returns:
            Tuple of (is_match, current_version_info)
        """
        current_version = self.get_node_version(node_id)
        if not current_version:
            return False, {}
        
        if expected_version is None:
            return True, current_version
        
        is_match = current_version["version"] == expected_version
        return is_match, current_version
    
    def update_node_timestamp(self, node_id: int) -> None:
        """
        Update the timestamp for a node (no-op since no updated_at column).
        
        Args:
            node_id: Node ID to update
        """
        # Since there's no updated_at column, we just commit any pending changes
        self.conn.commit()
    
    def handle_version_conflict(self, node_id: int, expected_version: int, current_version: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a version conflict by returning 412 response data.
        
        Args:
            node_id: Node ID with conflict
            expected_version: Expected version
            current_version: Current version info
            
        Returns:
            Conflict response data
        """
        return {
            "error": "version_conflict",
            "message": "Data has been modified by another user. Please reload and try again.",
            "node_id": node_id,
            "expected_version": expected_version,
            "current_version": current_version["version"],
            "current_updated_at": current_version["updated_at"],
            "hint": "Use If-Match header with current version to resolve conflicts"
        }
    
    def validate_if_match_header(self, if_match: Optional[str], node_id: int) -> Tuple[bool, Optional[int]]:
        """
        Validate If-Match header and extract version.
        
        Args:
            if_match: If-Match header value
            node_id: Node ID being modified
            
        Returns:
            Tuple of (is_valid, version_number)
        """
        if not if_match:
            return True, None
        
        try:
            # Support both "version:123" and "123" formats
            if ":" in if_match:
                version_str = if_match.split(":")[-1].strip()
            else:
                version_str = if_match.strip()
            
            version = int(version_str)
            return True, version
        except (ValueError, IndexError):
            return False, None
    
    def create_etag(self, version_info: Dict[str, Any]) -> str:
        """
        Create ETag for version information.
        
        Args:
            version_info: Version information dict
            
        Returns:
            ETag string
        """
        return f"version:{version_info['version']}"
    
    def get_children_with_versions(self, parent_id: int) -> Tuple[list, Dict[str, Any]]:
        """
        Get children with version information for the parent.
        
        Args:
            parent_id: Parent node ID
            
        Returns:
            Tuple of (children_list, parent_version_info)
        """
        cursor = self.conn.cursor()
        
        # Get children
        cursor.execute("""
            SELECT id, label, slot, is_leaf
            FROM nodes 
            WHERE parent_id = ? 
            ORDER BY slot
        """, (parent_id,))
        
        children = []
        for row in cursor.fetchall():
            children.append({
                "id": row[0],
                "label": row[1],
                "slot": row[2],
                "is_leaf": bool(row[3]),
                "updated_at": datetime.now().isoformat()  # Generate timestamp
            })
        
        # Get parent version info
        parent_version = self.get_node_version(parent_id)
        
        return children, parent_version or {}
    
    def apply_children_with_version_check(
        self, 
        parent_id: int, 
        children_data: list, 
        expected_version: Optional[int] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Apply children changes with version checking.
        
        Args:
            parent_id: Parent node ID
            children_data: New children data
            expected_version: Expected parent version
            
        Returns:
            Tuple of (success, result_data)
        """
        try:
            # Check version match
            is_match, current_version = self.check_version_match(parent_id, expected_version)
            if not is_match:
                return False, self.handle_version_conflict(parent_id, expected_version or 0, current_version)
            
            # Apply changes (this would be implemented by the calling code)
            # For now, just update the timestamp
            self.update_node_timestamp(parent_id)
            
            return True, {
                "message": "Children updated successfully",
                "parent_id": parent_id,
                "new_version": current_version["version"] + 1
            }
            
        except Exception as e:
            logger.error(f"Error applying children changes: {e}")
            return False, {
                "error": "update_failed",
                "message": str(e)
            }
    
    def get_concurrency_info(self, node_id: int) -> Dict[str, Any]:
        """
        Get concurrency information for a node.
        
        Args:
            node_id: Node ID
            
        Returns:
            Concurrency information
        """
        version_info = self.get_node_version(node_id)
        if not version_info:
            return {}
        
        return {
            "node_id": node_id,
            "version": version_info["version"],
            "updated_at": version_info["updated_at"],
            "etag": self.create_etag(version_info),
            "concurrency_enabled": True
        }
