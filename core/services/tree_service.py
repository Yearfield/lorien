"""
Tree service for managing decision tree operations.
"""

from typing import List, Optional, Dict, Any
from sqlite3 import Connection

from storage.sqlite import SQLiteRepository
from core.models import Node


class TreeService:
    """Service for tree-related operations."""
    
    def __init__(self, repository: Optional[SQLiteRepository] = None):
        """
        Initialize tree service.
        
        Args:
            repository: SQLite repository instance. If None, creates a new one.
        """
        self.repository = repository or SQLiteRepository()
    
    def get_next_incomplete_parent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the next incomplete parents using the optimized view.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of incomplete parents with their missing slots
        """
        with self.repository._get_connection() as conn:
            cursor = conn.cursor()
            
            # Use the optimized view with stable ordering
            query = """
                SELECT 
                    parent_id,
                    missing_slots,
                    (SELECT label FROM nodes WHERE id = parent_id) as parent_label,
                    (SELECT depth FROM nodes WHERE id = parent_id) as parent_depth
                FROM v_next_incomplete_parent
                ORDER BY parent_depth ASC, parent_id ASC
                LIMIT ?
            """
            
            cursor.execute(query, (limit,))
            results = []
            
            for row in cursor.fetchall():
                results.append({
                    "parent_id": row[0],
                    "missing_slots": row[1],
                    "parent_label": row[2],
                    "parent_depth": row[3]
                })
            
            return results
    
    def get_incomplete_parents_count(self) -> int:
        """
        Get the total count of incomplete parents.
        
        Returns:
            Number of incomplete parents
        """
        with self.repository._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) FROM v_next_incomplete_parent"
            cursor.execute(query)
            
            return cursor.fetchone()[0]
    
    def get_parent_children(self, parent_id: int) -> List[Node]:
        """
        Get all children of a parent node.
        
        Args:
            parent_id: ID of the parent node
            
        Returns:
            List of child nodes
        """
        return self.repository.get_children(parent_id)
    
    def get_parent_missing_slots(self, parent_id: int) -> List[int]:
        """
        Get the missing slots for a specific parent.
        
        Args:
            parent_id: ID of the parent node
            
        Returns:
            List of missing slot numbers (1-5)
        """
        with self.repository._get_connection() as conn:
            cursor = conn.cursor()
            
            # Use the missing slots view for this specific parent
            query = """
                SELECT missing_slots
                FROM v_missing_slots
                WHERE parent_id = ?
            """
            
            cursor.execute(query, (parent_id,))
            result = cursor.fetchone()
            
            if result and result[0]:
                # Convert comma-separated string to list of integers
                return [int(slot) for slot in result[0].split(',')]
            
            return []
    
    def is_parent_complete(self, parent_id: int) -> bool:
        """
        Check if a parent has all 5 children.
        
        Args:
            parent_id: ID of the parent node
            
        Returns:
            True if parent has exactly 5 children, False otherwise
        """
        children = self.get_parent_children(parent_id)
        return len(children) == 5
    
    def get_tree_statistics(self) -> Dict[str, Any]:
        """
        Get overall tree statistics.
        
        Returns:
            Dictionary with tree statistics
        """
        with self.repository._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get coverage statistics
            cursor.execute("SELECT * FROM v_tree_coverage ORDER BY depth")
            coverage = []
            for row in cursor.fetchall():
                coverage.append({
                    "depth": row[0],
                    "total_nodes": row[1],
                    "leaf_count": row[2]
                })
            
            # Get incomplete parents count
            incomplete_count = self.get_incomplete_parents_count()
            
            # Get total parents count
            cursor.execute("""
                SELECT COUNT(*) FROM nodes 
                WHERE depth BETWEEN 0 AND 4
            """)
            total_parents = cursor.fetchone()[0]
            
            return {
                "coverage": coverage,
                "incomplete_parents": incomplete_count,
                "total_parents": total_parents,
                "completion_rate": (total_parents - incomplete_count) / total_parents if total_parents > 0 else 0
            }
