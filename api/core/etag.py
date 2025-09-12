"""
Enhanced ETag system for optimistic concurrency control.

Provides ETag generation, validation, and If-Match header handling
for all write operations to prevent lost updates.
"""

import hashlib
import json
from typing import Any, Dict, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ETagManager:
    """Manages ETag generation and validation."""
    
    @staticmethod
    def generate_etag(data: Union[Dict[str, Any], str, int, float]) -> str:
        """
        Generate ETag for data.
        
        Args:
            data: Data to generate ETag for
            
        Returns:
            ETag string
        """
        if isinstance(data, dict):
            # Sort keys for consistent hashing
            sorted_data = json.dumps(data, sort_keys=True, separators=(',', ':'))
        else:
            sorted_data = str(data)
        
        # Create hash
        hash_obj = hashlib.md5()
        hash_obj.update(sorted_data.encode('utf-8'))
        etag = hash_obj.hexdigest()
        
        # Add weak ETag prefix for compatibility
        return f'W/"{etag}"'
    
    @staticmethod
    def generate_version_etag(version: int, timestamp: Optional[str] = None) -> str:
        """
        Generate ETag for version-based concurrency.
        
        Args:
            version: Version number
            timestamp: Optional timestamp
            
        Returns:
            ETag string
        """
        data = {"version": version}
        if timestamp:
            data["timestamp"] = timestamp
        
        return ETagManager.generate_etag(data)
    
    @staticmethod
    def generate_node_etag(node_id: int, version: int, updated_at: str) -> str:
        """
        Generate ETag for a node.
        
        Args:
            node_id: Node ID
            version: Node version
            updated_at: Last update timestamp
            
        Returns:
            ETag string
        """
        data = {
            "node_id": node_id,
            "version": version,
            "updated_at": updated_at
        }
        return ETagManager.generate_etag(data)
    
    @staticmethod
    def generate_tree_etag(tree_data: Dict[str, Any]) -> str:
        """
        Generate ETag for tree structure.
        
        Args:
            tree_data: Tree data dictionary
            
        Returns:
            ETag string
        """
        # Normalize tree data for consistent hashing
        normalized_data = {
            "nodes": sorted(tree_data.get("nodes", []), key=lambda x: x.get("id", 0)),
            "triage": sorted(tree_data.get("triage", []), key=lambda x: x.get("node_id", 0)),
            "flags": sorted(tree_data.get("flags", []), key=lambda x: x.get("id", 0))
        }
        
        return ETagManager.generate_etag(normalized_data)
    
    @staticmethod
    def validate_etag(etag: str, expected_data: Union[Dict[str, Any], str, int, float]) -> bool:
        """
        Validate ETag against data.
        
        Args:
            etag: ETag to validate
            expected_data: Expected data
            
        Returns:
            True if ETag matches data
        """
        expected_etag = ETagManager.generate_etag(expected_data)
        return etag == expected_etag
    
    @staticmethod
    def parse_if_match_header(if_match: Optional[str]) -> Optional[str]:
        """
        Parse If-Match header value.
        
        Args:
            if_match: If-Match header value
            
        Returns:
            Cleaned ETag value or None
        """
        if not if_match:
            return None
        
        # Remove quotes and weak ETag prefix
        etag = if_match.strip()
        if etag.startswith('W/"') and etag.endswith('"'):
            etag = etag[3:-1]
        elif etag.startswith('"') and etag.endswith('"'):
            etag = etag[1:-1]
        
        return etag
    
    @staticmethod
    def check_etag_match(if_match: Optional[str], current_etag: str) -> bool:
        """
        Check if If-Match header matches current ETag.
        
        Args:
            if_match: If-Match header value
            current_etag: Current ETag
            
        Returns:
            True if ETags match
        """
        if not if_match:
            return True  # No If-Match header means no validation required
        
        parsed_etag = ETagManager.parse_if_match_header(if_match)
        if not parsed_etag:
            return False
        
        # Compare ETags (handle both weak and strong ETags)
        current_parsed = ETagManager.parse_if_match_header(current_etag)
        return parsed_etag == current_parsed
    
    @staticmethod
    def create_etag_response_headers(etag: str) -> Dict[str, str]:
        """
        Create response headers with ETag.
        
        Args:
            etag: ETag value
            
        Returns:
            Headers dictionary
        """
        return {
            "ETag": etag,
            "Cache-Control": "no-cache, must-revalidate"
        }
    
    @staticmethod
    def create_etag_error_response(if_match: Optional[str], current_etag: str) -> Dict[str, Any]:
        """
        Create error response for ETag mismatch.
        
        Args:
            if_match: If-Match header value
            current_etag: Current ETag
            
        Returns:
            Error response dictionary
        """
        return {
            "error": "etag_mismatch",
            "message": "Resource has been modified. Please refresh and try again.",
            "expected_etag": if_match,
            "current_etag": current_etag,
            "hint": "Use If-Match header with current ETag to resolve conflicts"
        }

class ConcurrencyError(Exception):
    """Exception raised for concurrency conflicts."""
    
    def __init__(self, message: str, expected_etag: Optional[str] = None, current_etag: Optional[str] = None):
        super().__init__(message)
        self.expected_etag = expected_etag
        self.current_etag = current_etag

def require_etag_match(if_match: Optional[str], current_etag: str) -> None:
    """
    Require ETag match or raise ConcurrencyError.
    
    Args:
        if_match: If-Match header value
        current_etag: Current ETag
        
    Raises:
        ConcurrencyError: If ETags don't match
    """
    if not ETagManager.check_etag_match(if_match, current_etag):
        raise ConcurrencyError(
            "ETag mismatch - resource has been modified",
            expected_etag=if_match,
            current_etag=current_etag
        )
