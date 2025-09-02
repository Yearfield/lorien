"""
SQLite repository for decision tree data persistence.
Implements repository pattern with transaction support and WAL mode.
"""

import sqlite3
import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

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
        logger.debug(f"SQLiteRepository: Initializing with resolved DB path: {self._db_path}")
        logger.debug(f"SQLiteRepository: Path exists: {os.path.exists(self._db_path)}")
        
        self._ensure_db_directory()
        self._init_database()
        
        logger.debug(f"SQLiteRepository: After init, DB size: {os.path.getsize(self._db_path)} bytes")
    
    def _get_default_db_path(self) -> str:
        """Get default database path from environment or OS-appropriate app data directory."""
        db_path = os.getenv("LORIEN_DB_PATH")
        if db_path:
            return db_path
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
        Path(db_dir).mkdir(parents=True, exist_ok=True)
    
    def _init_database(self):
        """Initialize database with schema."""
        logger.debug("_init_database: Starting database initialization")
        schema_path = Path(__file__).parent / 'schema.sql'
        logger.debug(f"_init_database: Schema path: {schema_path}")
        logger.debug(f"_init_database: Schema file exists: {schema_path.exists()}")
        
        with self._get_connection() as conn:
            # Read and execute schema
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            logger.debug(f"_init_database: Schema SQL length: {len(schema_sql)} characters")
            conn.executescript(schema_sql)
            conn.commit()
            logger.debug("_init_database: Schema executed and committed")
    
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
        """Assign a red flag to a node (idempotent - won't fail if already assigned)."""
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO node_red_flags (node_id, red_flag_id, created_at)
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

    def search_red_flags_by_id(self, flag_id: int) -> List[RedFlag]:
        """Search red flags by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM red_flags
                WHERE id = ?
                ORDER BY name ASC
            """, (flag_id,))
            
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
    
    def update_triage(self, node_id: int, diagnostic_triage: Optional[str], actions: Optional[str]) -> bool:
        """Update triage for a node."""
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO triage (node_id, diagnostic_triage, actions, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    node_id,
                    diagnostic_triage,
                    actions,
                    self._datetime_to_iso(datetime.now())
                ))
                
                conn.commit()
                return True
                
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise ValueError(f"Triage update failed: {e}")

    def get_parents_with_missing_slots(self) -> List[Dict[str, Any]]:
        """Get all parents with missing child slots."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.label, p.depth,
                       GROUP_CONCAT(c.slot ORDER BY c.slot) as existing_slots
                FROM nodes p
                LEFT JOIN nodes c ON p.id = c.parent_id
                WHERE p.parent_id IS NOT NULL
                GROUP BY p.id
                HAVING COUNT(c.id) < 5 OR COUNT(c.id) IS NULL
            """)
            
            results = []
            for row in cursor.fetchall():
                existing_slots = [int(s) for s in row['existing_slots'].split(',') if s] if row['existing_slots'] else []
                missing_slots = [i for i in range(1, 6) if i not in existing_slots]
                
                results.append({
                    "parent_id": row['id'],
                    "label": row['label'],
                    "depth": row['depth'],
                    "existing_slots": existing_slots,
                    "missing_slots": missing_slots
                })
            
            return results

    def search_triage_records(self, leaf_only: bool = True, query: Optional[str] = None, 
                             vm: Optional[str] = None, sort: Optional[str] = None, 
                             limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search triage records with optional filtering."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            sql = """
                SELECT n.id, n.label, n.depth, n.is_leaf,
                       t.diagnostic_triage, t.actions, t.updated_at,
                       p.label as parent_label,
                       vm.label as vital_measurement
                FROM nodes n
                LEFT JOIN triage t ON n.id = t.node_id
                LEFT JOIN nodes p ON n.parent_id = p.id
                LEFT JOIN nodes vm ON vm.id = (
                    SELECT root_id FROM (
                        WITH RECURSIVE path AS (
                            SELECT id, parent_id, label, depth
                            FROM nodes
                            WHERE id = n.id
                            UNION ALL
                            SELECT n.id, n.parent_id, n.label, n.depth
                            FROM nodes n
                            JOIN path p ON n.id = p.parent_id
                        )
                        SELECT id as root_id FROM path WHERE depth = 0 LIMIT 1
                    )
                )
                WHERE 1=1
            """
            params = []
            
            if leaf_only:
                sql += " AND n.is_leaf = 1"
            
            if query:
                sql += " AND (t.diagnostic_triage LIKE ? OR t.actions LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])
            
            if vm:
                sql += " AND vm.label LIKE ?"
                params.append(f"%{vm}%")
            
            # Handle sorting
            if sort:
                if sort == "updated_at:desc":
                    sql += " ORDER BY t.updated_at DESC"
                elif sort == "updated_at:asc":
                    sql += " ORDER BY t.updated_at ASC"
                else:
                    sql += " ORDER BY n.id"  # default fallback
            else:
                sql += " ORDER BY n.id"
            
            # Handle limit
            if limit:
                sql += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(sql, params)
            
            results = []
            for row in cursor.fetchall():
                # Build path for display
                path_parts = [row['vital_measurement'] if row['vital_measurement'] else 'Root']
                if row['parent_label'] and row['parent_label'] != row['vital_measurement']:
                    path_parts.append(row['parent_label'])
                if row['label']:
                    path_parts.append(row['label'])
                path = " → ".join(path_parts)
                
                results.append({
                    "node_id": row['id'],
                    "label": row['label'],
                    "depth": row['depth'],
                    "is_leaf": bool(row['is_leaf']),
                    "path": path,
                    "vital_measurement": row['vital_measurement'],
                    "diagnostic_triage": row['diagnostic_triage'],
                    "actions": row['actions'],
                    "updated_at": row['updated_at']
                })
            
            return results
    
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
    
    # Red Flag Audit operations
    
    def create_red_flag_audit(self, node_id: int, flag_id: int, action: str, user: Optional[str] = None) -> int:
        """Create a new red flag audit record."""
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO red_flag_audit (node_id, flag_id, action, user, ts)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    node_id,
                    flag_id,
                    action,
                    user,
                    self._datetime_to_iso(datetime.now())
                ))
                
                audit_id = cursor.lastrowid
                conn.commit()
                return audit_id
                
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise ValueError(f"Red flag audit creation failed: {e}")
    
    def get_red_flag_audit(
        self, 
        node_id: Optional[int] = None,
        flag_id: Optional[int] = None,
        user: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get red flag audit records with optional filtering."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Build query dynamically based on filters
            query = """
                SELECT id, node_id, flag_id, action, user, ts
                FROM red_flag_audit
                WHERE 1=1
            """
            params = []
            
            if node_id is not None:
                query += " AND node_id = ?"
                params.append(node_id)
            
            if flag_id is not None:
                query += " AND flag_id = ?"
                params.append(flag_id)
            
            if user is not None:
                query += " AND user = ?"
                params.append(user)
            
            query += " ORDER BY ts DESC, id DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row[0],
                    "node_id": row[1],
                    "flag_id": row[2],
                    "action": row[3],
                    "user": row[4],
                    "ts": row[5]
                }
                for row in rows
            ]

    def get_red_flag_audit_with_branch(
        self, 
        node_id: Optional[int] = None,
        flag_id: Optional[int] = None,
        user: Optional[str] = None,
        branch: bool = False,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get red flag audit records with optional filtering and branch scope support."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Build WHERE clause
            where_conditions = []
            params = []
            
            if node_id is not None:
                if branch:
                    # Get descendants using recursive CTE
                    descendants = self.get_descendant_nodes(node_id)
                    node_ids = [node_id] + descendants
                    placeholders = ','.join(['?' for _ in node_ids])
                    where_conditions.append(f"rfa.node_id IN ({placeholders})")
                    params.extend(node_ids)
                else:
                    where_conditions.append("rfa.node_id = ?")
                    params.append(node_id)
            
            if flag_id is not None:
                where_conditions.append("rfa.flag_id = ?")
                params.append(flag_id)
            
            if user is not None:
                where_conditions.append("rfa.user = ?")
                params.append(user)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Build query
            query = f"""
                SELECT rfa.id, rfa.node_id, rfa.flag_id, rfa.action, rfa.user, rfa.ts,
                       rf.name as flag_name, n.label as node_label
                FROM red_flag_audit rfa
                JOIN red_flags rf ON rfa.flag_id = rf.id
                JOIN nodes n ON rfa.node_id = n.id
                WHERE {where_clause}
                ORDER BY rfa.ts DESC
                LIMIT ?
            """
            
            params.append(limit)
            cursor.execute(query, params)
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    "id": row[0],
                    "node_id": row[1],
                    "flag_id": row[2],
                    "action": row[3],
                    "user": row[4],
                    "ts": row[5],
                    "flag_name": row[6],
                    "node_label": row[7]
                })
            
            return records
    
    def get_red_flag_audit_by_id(self, audit_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific red flag audit record by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, node_id, flag_id, action, user, ts
                FROM red_flag_audit
                WHERE id = ?
            """, (audit_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "node_id": row[1],
                    "flag_id": row[2],
                    "action": row[3],
                    "user": row[4],
                    "ts": row[5]
                }
            return None

    def check_integrity(self) -> Dict[str, Any]:
        """Check database integrity and return results."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Run PRAGMA integrity_check
                cursor.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()
                
                # Check foreign key constraints
                cursor.execute("PRAGMA foreign_key_check")
                fk_errors = cursor.fetchall()
                
                # Check WAL mode
                cursor.execute("PRAGMA journal_mode")
                journal_mode = cursor.fetchone()
                
                # Check foreign keys are enabled
                cursor.execute("PRAGMA foreign_keys")
                fk_enabled = cursor.fetchone()
                
                # Count records in main tables
                cursor.execute("SELECT COUNT(*) FROM nodes")
                node_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM red_flags")
                flag_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM red_flag_audit")
                audit_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM triage")
                triage_count = cursor.fetchone()[0]
                
                return {
                    "ok": integrity_result[0] == "ok" and len(fk_errors) == 0,
                    "integrity_check": integrity_result[0] if integrity_result else "unknown",
                    "foreign_key_errors": len(fk_errors),
                    "foreign_key_details": fk_errors if fk_errors else [],
                    "journal_mode": journal_mode[0] if journal_mode else "unknown",
                    "foreign_keys_enabled": bool(fk_enabled[0]) if fk_enabled else False,
                    "table_counts": {
                        "nodes": node_count,
                        "red_flags": flag_count,
                        "red_flag_audit": audit_count,
                        "triage": triage_count
                    }
                }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "integrity_check": "failed",
                "foreign_key_errors": -1,
                "foreign_key_details": [],
                "journal_mode": "unknown",
                "foreign_keys_enabled": False,
                "table_counts": {}
            }
    
    def get_red_flag(self, flag_id: int) -> Optional[RedFlag]:
        """Get a red flag by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, severity, created_at
                FROM red_flags
                WHERE id = ?
            """, (flag_id,))
            
            row = cursor.fetchone()
            if row:
                return RedFlag(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    severity=row[3],
                    created_at=self._iso_to_datetime(row[4])
                )
            return None
    
    def get_tree_data_for_csv(self) -> List[Dict[str, Any]]:
        """
        Get all tree data formatted for CSV export.
        
        Returns:
            List of dictionaries with exactly 5 children per parent,
            formatted for CSV export with Diagnosis header.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all parent nodes (nodes with depth 0)
            cursor.execute("""
                SELECT id, label FROM nodes 
                WHERE depth = 0 
                ORDER BY id
            """)
            parents = cursor.fetchall()
            
            csv_data = []
            
            for parent in parents:
                parent_id = parent['id']
                vital_measurement = parent['label']
                
                # Get children for this parent, ordered by slot
                cursor.execute("""
                    SELECT slot, label FROM nodes 
                    WHERE parent_id = ? 
                    ORDER BY slot
                """, (parent_id,))
                children = cursor.fetchall()
                
                # Create row with exactly 5 slots
                row = {
                    "Diagnosis": vital_measurement,
                    "Node 1": "",
                    "Node 2": "",
                    "Node 3": "",
                    "Node 4": "",
                    "Node 5": ""
                }
                
                # Fill in existing children
                for child in children:
                    slot = child['slot']
                    if 1 <= slot <= 5:
                        row[f"Node {slot}"] = child['label']
                
                csv_data.append(row)
            
            return csv_data
    
    def get_descendant_nodes(self, root_id: int) -> List[int]:
        """Get all descendant node IDs using recursive CTE."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                WITH RECURSIVE subtree(id) AS (
                    SELECT ? 
                    UNION ALL
                    SELECT n.id FROM nodes n JOIN subtree s ON n.parent_id = s.id
                )
                SELECT id FROM subtree WHERE id != ?
            """, (root_id, root_id))
            
            return [row[0] for row in cursor.fetchall()]
    
    def remove_red_flag_from_node(self, node_id: int, red_flag_id: int) -> bool:
        """Remove a red flag from a node."""
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM node_red_flags 
                    WHERE node_id = ? AND red_flag_id = ?
                """, (node_id, red_flag_id))
                
                conn.commit()
                return True
                
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise ValueError(f"Red flag removal failed: {e}")
    
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

    def create_root_node(self, label: str) -> int:
        """Create a new root node (depth=0, no parent)."""
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO nodes (label, parent_id, slot, depth, is_leaf, created_at, updated_at)
                    VALUES (?, NULL, 0, 0, 0, ?, ?)
                """, (
                    label,
                    self._datetime_to_iso(datetime.now()),
                    self._datetime_to_iso(datetime.now())
                ))
                
                root_id = cursor.lastrowid
                conn.commit()
                return root_id
                
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise ValueError(f"Failed to create root node: {e}")

    def create_child_node(self, parent_id: int, slot: int, label: str, depth: int) -> int:
        """Create a child node under a parent."""
        with self._get_connection() as conn:
            try:
                cursor = conn.cursor()
                
                # Determine if this will be a leaf (depth 5)
                is_leaf = 1 if depth == 5 else 0
                
                cursor.execute("""
                    INSERT INTO nodes (label, parent_id, slot, depth, is_leaf, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    label,
                    parent_id,
                    slot,
                    depth,
                    is_leaf,
                    self._datetime_to_iso(datetime.now()),
                    self._datetime_to_iso(datetime.now())
                ))
                
                child_id = cursor.lastrowid
                conn.commit()
                return child_id
                
            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise ValueError(f"Failed to create child node: {e}")

    def get_tree_stats(self) -> Dict[str, Any]:
        """Get tree completeness statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get node counts
            cursor.execute("SELECT COUNT(*) FROM nodes")
            total_nodes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM nodes WHERE parent_id IS NULL")
            total_roots = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM nodes WHERE is_leaf = 1")
            total_leaves = cursor.fetchone()[0]
            
            # Get complete paths (roots that have complete paths to leaves)
            cursor.execute("""
                WITH RECURSIVE path_check AS (
                    SELECT id, label, 0 as depth
                    FROM nodes 
                    WHERE parent_id IS NULL
                    
                    UNION ALL
                    
                    SELECT n.id, n.label, pc.depth + 1
                    FROM nodes n
                    JOIN path_check pc ON n.parent_id = pc.id
                    WHERE pc.depth < 5
                )
                SELECT COUNT(DISTINCT pc.id) 
                FROM path_check pc
                WHERE pc.depth = 0
                AND EXISTS (
                    SELECT 1 FROM path_check pc2 
                    WHERE pc2.depth = 5 
                    AND pc2.id IN (
                        SELECT n5.id FROM nodes n1
                        JOIN nodes n2 ON n2.parent_id = n1.id
                        JOIN nodes n3 ON n3.parent_id = n2.id  
                        JOIN nodes n4 ON n4.parent_id = n3.id
                        JOIN nodes n5 ON n5.parent_id = n4.id
                        WHERE n1.parent_id = pc.id
                    )
                )
            """)
            complete_paths = cursor.fetchone()[0]
            
            # Get incomplete parents (have fewer than 5 children)
            cursor.execute("""
                SELECT COUNT(*)
                FROM (
                    SELECT p.id
                    FROM nodes p
                    LEFT JOIN nodes c ON p.id = c.parent_id
                    WHERE p.parent_id IS NOT NULL
                    GROUP BY p.id
                    HAVING COUNT(c.id) < 5
                )
            """)
            incomplete_parents = cursor.fetchone()[0]
            
            return {
                "nodes": total_nodes,
                "roots": total_roots,
                "leaves": total_leaves,
                "complete_paths": complete_paths,
                "incomplete_parents": incomplete_parents
            }

    def get_duplicate_labels(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get nodes with duplicate labels under the same parent."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT n.parent_id, p.label AS parent_label, n.label, COUNT(*) AS cnt,
                       GROUP_CONCAT(n.id) AS child_ids
                FROM nodes n
                JOIN nodes p ON p.id = n.parent_id
                GROUP BY n.parent_id, n.label
                HAVING COUNT(*) > 1
                ORDER BY cnt DESC, n.parent_id ASC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            rows = cursor.fetchall()
            result = []
            for row in rows:
                parent_id, parent_label, label, count, child_ids_str = row
                child_ids = [int(id_str) for id_str in child_ids_str.split(',') if id_str] if child_ids_str else []
                result.append({
                    "parent_id": parent_id,
                    "parent_label": parent_label,
                    "label": label,
                    "count": count,
                    "child_ids": child_ids
                })
            return result

    def get_orphan_nodes(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get orphan nodes with invalid parent_id references."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT n.id, n.parent_id, n.label, n.depth
                FROM nodes n
                LEFT JOIN nodes p ON p.id = n.parent_id
                WHERE n.parent_id IS NOT NULL AND p.id IS NULL
                ORDER BY n.id
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            rows = cursor.fetchall()
            result = []
            for row in rows:
                node_id, parent_id, label, depth = row
                result.append({
                    "id": node_id,
                    "parent_id": parent_id,
                    "label": label,
                    "depth": depth
                })
            return result

    def get_depth_anomalies(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get nodes with invalid depth values."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                -- roots with depth != 0
                SELECT id, parent_id, label, depth, 'ROOT_DEPTH' AS anomaly
                FROM nodes WHERE parent_id IS NULL AND depth != 0
                UNION ALL
                -- non-roots where depth != parent.depth + 1
                SELECT c.id, c.parent_id, c.label, c.depth, 'PARENT_CHILD_DEPTH' AS anomaly
                FROM nodes c
                JOIN nodes p ON p.id = c.parent_id
                WHERE c.depth != p.depth + 1
                ORDER BY id
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            rows = cursor.fetchall()
            result = []
            for row in rows:
                node_id, parent_id, label, depth, anomaly = row
                result.append({
                    "id": node_id,
                    "parent_id": parent_id,
                    "label": label,
                    "depth": depth,
                    "anomaly": anomaly
                })
            return result

    # Import job methods
    def create_import_job(self, state: str, filename: str = None, size_bytes: int = None) -> int:
        """Create a new import job."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO import_jobs (state, filename, size_bytes)
                VALUES (?, ?, ?)
            """, (state, filename, size_bytes))
            conn.commit()
            return cursor.lastrowid

    def update_import_job(self, job_id: int, **kwargs) -> None:
        """Update an import job with the given fields."""
        if not kwargs:
            return
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Build dynamic UPDATE query
            fields = []
            values = []
            for key, value in kwargs.items():
                if key in ['state', 'message', 'filename', 'size_bytes']:
                    fields.append(f"{key} = ?")
                    values.append(value)
                elif key == 'finished_at':
                    fields.append("finished_at = ?")
                    values.append(value)
            
            if fields:
                values.append(job_id)
                query = f"UPDATE import_jobs SET {', '.join(fields)} WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()

    def get_import_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific import job by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, state, created_at, finished_at, message, filename, size_bytes
                FROM import_jobs WHERE id = ?
            """, (job_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "state": row[1],
                    "created_at": row[2],
                    "finished_at": row[3],
                    "message": row[4],
                    "filename": row[5],
                    "size_bytes": row[6]
                }
            return None

    def get_import_jobs(self) -> List[Dict[str, Any]]:
        """Get all import jobs ordered by creation time."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, state, created_at, finished_at, message, filename, size_bytes
                FROM import_jobs
                ORDER BY created_at
                LIMIT 100
            """, ())
            
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append({
                    "id": row[0],
                    "state": row[1],
                    "created_at": row[2],
                    "finished_at": row[3],
                    "message": row[4],
                    "filename": row[5],
                    "size_bytes": row[6]
                })
            return result
