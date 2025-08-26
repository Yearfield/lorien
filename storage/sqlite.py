"""
SQLite repository for decision tree data persistence.
Implements repository pattern with transaction support and WAL mode.
"""

import sqlite3
import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import pandas as pd

from core.models import Node, Parent, RedFlag, Triaging, TreeValidationResult
from core.rules import validate_tree_structure
from core.storage.path import get_db_path


class SQLiteRepository:
    """Repository for SQLite-based decision tree storage."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize SQLite repository.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default app data location.
        """
        if db_path is None:
            db_path = self._get_default_db_path()
        
        # Always resolve to absolute path
        self._db_path = str(Path(db_path).resolve())
        print(f"[DEBUG] SQLiteRepository: Initializing with resolved DB path: {self._db_path}")
        print(f"[DEBUG] SQLiteRepository: Path exists: {os.path.exists(self._db_path)}")
        
        self._ensure_db_directory()
        self._init_database()
        
        print(f"[DEBUG] SQLiteRepository: After init, DB size: {os.path.getsize(self._db_path)} bytes")
    
    def _get_default_db_path(self) -> str:
        """Get default database path in OS-appropriate app data directory."""
        return str(get_db_path())
    
    @property
    def db_path(self) -> str:
        """Get the resolved database path (for health endpoint)."""
        return self._db_path
    
    def get_resolved_db_path(self) -> str:
        """Get the resolved database path (for health endpoint)."""
        return self.db_path
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self._db_path)
        os.makedirs(db_dir, exist_ok=True)
    
    def _init_database(self):
        """Initialize database with schema."""
        print(f"[DEBUG] _init_database: Starting database initialization")
        schema_path = Path(__file__).parent / 'schema.sql'
        print(f"[DEBUG] _init_database: Schema path: {schema_path}")
        print(f"[DEBUG] _init_database: Schema file exists: {schema_path.exists()}")
        
        with self._get_connection() as conn:
            # Read and execute schema
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            print(f"[DEBUG] _init_database: Schema SQL length: {len(schema_sql)} characters")
            conn.executescript(schema_sql)
            conn.commit()
            print(f"[DEBUG] _init_database: Schema executed and committed")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper configuration."""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        
        return conn
    
    def _datetime_to_iso(self, dt: datetime) -> str:
        """Convert datetime to ISO format string."""
        return dt.isoformat()
    
    def _iso_to_datetime(self, iso_str: str) -> datetime:
        """Convert ISO format string to datetime."""
        return datetime.fromisoformat(iso_str)
    
    # Node operations
    
    def create_node(self, node: Node) -> int:
        """
        Create a new node.
        
        Args:
            node: Node to create
            
        Returns:
            ID of the created node
            
        Raises:
            ValueError: If node violates constraints
        """
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO nodes (parent_id, depth, slot, label, is_leaf, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    node.parent_id,
                    node.depth,
                    node.slot,
                    node.label,
                    1 if node.is_leaf else 0,
                    self._datetime_to_iso(node.created_at),
                    self._datetime_to_iso(node.updated_at)
                ))
                
                node_id = cursor.lastrowid
                conn.commit()
                return node_id
                
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise ValueError(f"Node creation failed: {e}")
    
    def get_node(self, node_id: int) -> Optional[Node]:
        """Get node by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM nodes WHERE id = ?", (node_id,))
            row = cursor.fetchone()
            
            if row:
                return Node(
                    id=row['id'],
                    parent_id=row['parent_id'],
                    depth=row['depth'],
                    slot=row['slot'],
                    label=row['label'],
                    is_leaf=bool(row['is_leaf']),
                    created_at=self._iso_to_datetime(row['created_at']),
                    updated_at=self._iso_to_datetime(row['updated_at'])
                )
            return None
    
    def update_node(self, node: Node) -> bool:
        """Update an existing node."""
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE nodes 
                    SET parent_id = ?, depth = ?, slot = ?, label = ?, is_leaf = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    node.parent_id,
                    node.depth,
                    node.slot,
                    node.label,
                    1 if node.is_leaf else 0,
                    self._datetime_to_iso(datetime.now()),
                    node.id
                ))
                
                success = cursor.rowcount > 0
                conn.commit()
                return success
                
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise ValueError(f"Node update failed: {e}")
    
    def delete_node(self, node_id: int) -> bool:
        """Delete a node and all its descendants."""
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
                
                success = cursor.rowcount > 0
                conn.commit()
                return success
                
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise ValueError(f"Node deletion failed: {e}")
    
    def get_children(self, parent_id: int) -> List[Node]:
        """Get all children of a parent node."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM nodes 
                WHERE parent_id = ? 
                ORDER BY slot
            """, (parent_id,))
            
            children = []
            for row in cursor.fetchall():
                children.append(Node(
                    id=row['id'],
                    parent_id=row['parent_id'],
                    depth=row['depth'],
                    slot=row['slot'],
                    label=row['label'],
                    is_leaf=bool(row['is_leaf']),
                    created_at=self._iso_to_datetime(row['created_at']),
                    updated_at=self._iso_to_datetime(row['updated_at'])
                ))
            
            return children
    
    def get_parent(self, node_id: int) -> Optional[Node]:
        """Get parent of a node."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT n.* FROM nodes n
                JOIN nodes c ON n.id = c.parent_id
                WHERE c.id = ?
            """, (node_id,))
            
            row = cursor.fetchone()
            if row:
                return Node(
                    id=row['id'],
                    parent_id=row['parent_id'],
                    depth=row['depth'],
                    slot=row['slot'],
                    label=row['label'],
                    is_leaf=bool(row['is_leaf']),
                    created_at=self._iso_to_datetime(row['created_at']),
                    updated_at=self._iso_to_datetime(row['updated_at'])
                )
            return None
    
    # Parent operations
    
    def get_parent_with_children(self, parent_id: int) -> Optional[Parent]:
        """Get a parent node with all its children."""
        parent_node = self.get_node(parent_id)
        if not parent_node:
            return None
        
        children = self.get_children(parent_id)
        return Parent(node=parent_node, children=children)
    
    def find_parents_with_too_few_children(self) -> List[Dict[str, Any]]:
        """Find parents with fewer than 5 children."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT parent_id, child_count, children
                FROM v_parents_too_few
            """)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "parent_id": row['parent_id'],
                    "child_count": row['child_count'],
                    "children": row['children'].split(', ') if row['children'] else []
                })
            
            return results
    
    def find_parents_with_too_many_children(self) -> List[Dict[str, Any]]:
        """Find parents with more than 5 children."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT parent_id, child_count, children
                FROM v_parents_too_many
            """)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "parent_id": row['parent_id'],
                    "child_count": row['child_count'],
                    "children": row['children'].split(', ') if row['children'] else []
                })
            
            return results
    
    def get_next_incomplete_parent(self) -> Optional[Dict[str, Any]]:
        """Get the next incomplete parent for the 'Skip to next incomplete parent' feature."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT parent_id, missing_slots
                FROM v_next_incomplete_parent
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if row:
                return {
                    "parent_id": row['parent_id'],
                    "missing_slots": row['missing_slots']
                }
            return None
    
    # Tree operations
    
    def upsert_children_atomic(self, parent_id: int, children_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Atomic upsert of multiple children for a parent.
        
        Args:
            parent_id: ID of the parent node
            children_data: List of dicts with 'slot' and 'label' keys
            
        Returns:
            Dict with results of the operation
            
        Raises:
            ValueError: If validation fails
            sqlite3.IntegrityError: If UNIQUE constraint is violated
        """
        with self._get_connection() as conn:
            try:
                # Start immediate transaction
                conn.execute("BEGIN IMMEDIATE")
                
                # Get parent info
                parent = self.get_node(parent_id)
                if not parent:
                    raise ValueError(f"Parent node {parent_id} not found")
                
                if parent.depth >= 5:
                    raise ValueError(f"Parent node {parent_id} is a leaf node and cannot have children")
                
                results = {
                    "parent_id": parent_id,
                    "children_processed": 0,
                    "children_created": 0,
                    "children_updated": 0,
                    "errors": []
                }
                
                # Process each child
                for child_data in children_data:
                    slot = child_data["slot"]
                    label = child_data["label"]
                    
                    # Validate slot
                    if slot < 1 or slot > 5:
                        results["errors"].append(f"Invalid slot {slot}: must be between 1 and 5")
                        continue
                    
                    # Validate label
                    if not label or not label.strip():
                        results["errors"].append(f"Invalid label for slot {slot}: cannot be empty")
                        continue
                    
                    try:
                        # Check if child already exists in this slot
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT id, label FROM nodes 
                            WHERE parent_id = ? AND slot = ?
                        """, (parent_id, slot))
                        
                        existing = cursor.fetchone()
                        
                        if existing:
                            # Update existing child
                            cursor.execute("""
                                UPDATE nodes 
                                SET label = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
                                WHERE id = ?
                            """, (label.strip(), existing['id']))
                            results["children_updated"] += 1
                        else:
                            # Create new child
                            cursor.execute("""
                                INSERT INTO nodes (parent_id, depth, slot, label, is_leaf, created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ','now'), strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                            """, (parent_id, parent.depth + 1, slot, label.strip(), parent.depth + 1 == 5))
                            results["children_created"] += 1
                        
                        results["children_processed"] += 1
                        
                    except sqlite3.IntegrityError as e:
                        # Handle UNIQUE constraint violations
                        if "UNIQUE constraint failed" in str(e):
                            results["errors"].append(f"Slot {slot} conflict: {str(e)}")
                        else:
                            raise
                    except Exception as e:
                        results["errors"].append(f"Error processing slot {slot}: {str(e)}")
                
                # Commit transaction
                conn.commit()
                
                return results
                
            except Exception as e:
                # Rollback on any error
                conn.rollback()
                raise
    
    def get_tree_coverage(self) -> Dict[str, Any]:
        """Get tree coverage summary."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM v_tree_coverage")
            
            coverage = {}
            for row in cursor.fetchall():
                coverage[row['depth']] = {
                    "parent_count": row['parent_count'],
                    "leaf_count": row['leaf_count'],
                    "total_nodes": row['total_nodes']
                }
            
            return coverage
    
    def validate_tree(self) -> TreeValidationResult:
        """Validate the entire tree structure."""
        # Get violations from database views
        too_few = self.find_parents_with_too_few_children()
        too_many = self.find_parents_with_too_many_children()
        
        violations = []
        
        # Convert database results to violation format
        for item in too_few:
            violations.append({
                "type": "too_few_children",
                "parent_id": item["parent_id"],
                "child_count": item["child_count"],
                "expected_count": 5
            })
        
        for item in too_many:
            violations.append({
                "type": "too_many_children",
                "parent_id": item["parent_id"],
                "child_count": item["child_count"],
                "expected_count": 5
            })
        
        summary = {
            "total_violations": len(violations),
            "too_few_children": len(too_few),
            "too_many_children": len(too_many),
            "is_valid": len(violations) == 0
        }
        
        return TreeValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            summary=summary
        )
    
    # Red flag operations
    
    def create_red_flag(self, red_flag: RedFlag) -> int:
        """Create a new red flag."""
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO red_flags (name, description, severity, created_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    red_flag.name,
                    red_flag.description,
                    red_flag.severity,
                    self._datetime_to_iso(red_flag.created_at)
                ))
                
                flag_id = cursor.lastrowid
                conn.commit()
                return flag_id
                
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise ValueError(f"Red flag creation failed: {e}")
    
    def assign_red_flag_to_node(self, node_id: int, red_flag_id: int) -> bool:
        """Assign a red flag to a node."""
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO node_red_flags (node_id, red_flag_id, created_at)
                    VALUES (?, ?, ?)
                """, (
                    node_id,
                    red_flag_id,
                    self._datetime_to_iso(datetime.now())
                ))
                
                conn.commit()
                return True
                
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise ValueError(f"Red flag assignment failed: {e}")
    
    def search_red_flags(self, query: str) -> List[RedFlag]:
        """Search red flags by name."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM red_flags 
                WHERE name LIKE ?
                ORDER BY name
            """, (f"%{query}%",))
            
            red_flags = []
            for row in cursor.fetchall():
                red_flags.append(RedFlag(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    severity=row['severity'],
                    created_at=self._iso_to_datetime(row['created_at'])
                ))
            
            return red_flags
    
    # Triage operations
    
    def create_triage(self, triage: Triaging) -> bool:
        """Create or update triage for a node."""
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO triage (node_id, diagnostic_triage, actions, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    triage.node_id,
                    triage.diagnostic_triage,
                    triage.actions,
                    self._datetime_to_iso(triage.created_at),
                    self._datetime_to_iso(triage.updated_at)
                ))
                
                conn.commit()
                return True
                
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise ValueError(f"Triage creation failed: {e}")
    
    def get_triage(self, node_id: int) -> Optional[Triaging]:
        """Get triage for a node."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM triage WHERE node_id = ?
            """, (node_id,))
            
            row = cursor.fetchone()
            if row:
                return Triaging(
                    node_id=row['node_id'],
                    diagnostic_triage=row['diagnostic_triage'],
                    actions=row['actions'],
                    created_at=self._iso_to_datetime(row['created_at']),
                    updated_at=self._iso_to_datetime(row['updated_at'])
                )
            return None
    
    # Utility operations
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get table counts
            cursor.execute("SELECT COUNT(*) FROM nodes")
            node_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM red_flags")
            red_flag_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM triage")
            triage_count = cursor.fetchone()[0]
            
            # Get database file size
            db_size = os.path.getsize(self._db_path) if os.path.exists(self._db_path) else 0
            
            return {
                "db_path": self._db_path,
                "db_size_bytes": db_size,
                "node_count": node_count,
                "red_flag_count": red_flag_count,
                "triage_count": triage_count,
                "created_at": datetime.now().isoformat()
            }
    
    def clear_database(self):
        """Clear all data from the database (for testing/reset)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM node_red_flags")
            cursor.execute("DELETE FROM triage")
            cursor.execute("DELETE FROM red_flags")
            cursor.execute("DELETE FROM nodes")
            conn.commit()
    
    def close(self):
        """Flush and close the underlying SQLite connection."""
        try:
            # Force WAL checkpoint to flush data to main database file
            with self._get_connection() as conn:
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                conn.commit()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                # Force WAL checkpoint to flush data to main database file
                with self._get_connection() as conn:
                    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                    conn.commit()
            else:
                # Let caller control rollback granularity; at minimum ensure close
                pass
        finally:
            pass  # SQLite connections are automatically closed when using context manager
