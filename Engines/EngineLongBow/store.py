"""
Path storage for EngineLongBow.
Idempotent, transactional store of edges implied by paths.
Contextual node creation: unique by (parent_id, depth, norm(label)).
"""

import sqlite3
import os
from typing import List, Dict, Any, Literal, Optional
from contextlib import contextmanager

from .consts import FROZEN_HEADER
from .utils import norm


def _get_conn(db_path: str):
    """Get database connection using provided path"""
    return sqlite3.connect(db_path)


def _get_or_create_node(conn: sqlite3.Connection, parent_id: int | None, depth: int, raw_label: str) -> int:
    """
    Get or create a node contextually by parent using provided connection.
    Roots (depth==0): unique by (parent_id IS NULL, depth=0, norm(label))
    Non-roots: unique by (parent_id=<prev_id>, depth=d, norm(label))
    """
    nlabel = norm(raw_label)
    cur = conn.cursor()
    
    if parent_id is None:
        # Root node - compare column label to normalized param
        cur.execute("""
          SELECT id FROM nodes
          WHERE parent_id IS NULL AND depth=? AND lower(trim(label)) = ?
        """, (depth, nlabel))
        row = cur.fetchone()
        if row:
            nid = row[0]
        else:
            cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (NULL, ?, NULL, ?)",
                        (depth, raw_label))
            nid = cur.lastrowid
    else:
        # Child node - contextual by parent, compare column label to normalized param
        cur.execute("""
          SELECT id FROM nodes
          WHERE parent_id=? AND depth=? AND lower(trim(label)) = ?
        """, (parent_id, depth, nlabel))
        row = cur.fetchone()
        if row:
            nid = row[0]
        else:
            # Assign slot before inserting to satisfy constraint
            slot = _get_next_slot(conn, parent_id)
            cur.execute("INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?, ?, ?, ?)",
                        (parent_id, depth, slot, raw_label))
            nid = cur.lastrowid
    
    return nid


def _get_next_slot(conn: sqlite3.Connection, parent_id: int) -> int:
    """Get the next available slot for a child under parent_id"""
    cur = conn.cursor()
    # Deterministic: next available slot = max(slot)+1 for this parent, gaps allowed
    cur.execute("SELECT COALESCE(MAX(slot), 0) FROM nodes WHERE parent_id=?", (parent_id,))
    next_slot = (cur.fetchone()[0] or 0) + 1
    return next_slot


def _assign_slot_if_needed(conn: sqlite3.Connection, parent_id: int, child_id: int) -> None:
    """Assign deterministic slot for child node (legacy function)"""
    cur = conn.cursor()
    # If slot already set, do nothing
    cur.execute("SELECT slot FROM nodes WHERE id=?", (child_id,))
    if cur.fetchone()[0] is not None:
        return
    # Deterministic: next available slot = max(slot)+1 for this parent, gaps allowed
    cur.execute("SELECT COALESCE(MAX(slot), 0) FROM nodes WHERE parent_id=?", (parent_id,))
    next_slot = (cur.fetchone()[0] or 0) + 1
    cur.execute("UPDATE nodes SET slot=? WHERE id=?", (next_slot, child_id))


def _ensure_indexes(conn: sqlite3.Connection) -> None:
    """Ensure required indexes exist for EngineLongBow operations."""
    cur = conn.cursor()
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_parent_slot_unique
        ON nodes(parent_id, slot) WHERE parent_id IS NOT NULL;
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_nodes_parent_depth
        ON nodes(parent_id, depth);
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_nodes_label_depth
        ON nodes(label, depth);
    """)
    conn.commit()


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Ensure database schema exists - relies on migrations for schema creation."""
    # Just ensure indexes exist - schema should be created by migrations
    _ensure_indexes(conn)


class ImportResult:
    """Result of import operation."""
    def __init__(self):
        self.inserted_nodes = 0
        self.inserted_edges = 0
        self.parents_touched = 0
        self.preview = False
        self.errors = []


def get_or_create_node(conn: sqlite3.Connection, parent_id: Optional[int], depth: int, 
                      label_norm: str, label_raw: str) -> int:
    """
    Get or create a node with the given properties.
    
    Args:
        conn: Database connection
        parent_id: Parent node ID (None for root)
        depth: Node depth
        label_norm: Normalized label for grouping
        label_raw: Raw label for display
        slot: Slot number (1-5 for children, None for root)
        
    Returns:
        Node ID
    """
    # Check if node already exists
    if parent_id is None:
        # Root node
        cur = conn.execute(
            "SELECT id FROM nodes WHERE parent_id IS NULL AND depth = ? AND label = ?",
            (depth, label_raw)
        )
    else:
        # Child node
        cur = conn.execute(
            "SELECT id FROM nodes WHERE parent_id = ? AND depth = ? AND label = ?",
            (parent_id, depth, label_raw)
        )
    
    row = cur.fetchone()
    if row:
        return row["id"]
    
    # Create new node
    if parent_id is None:
        # Root node
        cur = conn.execute(
            "INSERT INTO nodes (parent_id, label, depth, slot, is_leaf) VALUES (NULL, ?, ?, NULL, ?)",
            (label_raw, depth, 1 if depth == 5 else 0)
        )
    else:
        # Child node - assign slot
        slot = assign_slot_if_new(conn, parent_id)
        if slot is None:
            raise RuntimeError(f"Parent {parent_id} is full (5 children)")
        
        cur = conn.execute(
            "INSERT INTO nodes (parent_id, label, depth, slot, is_leaf) VALUES (?, ?, ?, ?, ?)",
            (parent_id, label_raw, depth, slot, 1 if depth == 5 else 0)
        )
    
    return cur.lastrowid


def assign_slot_if_new(conn: sqlite3.Connection, parent_id: int) -> Optional[int]:
    """
    Assign the next available slot for a new child under parent_id.
    
    Args:
        conn: Database connection
        parent_id: Parent node ID
        
    Returns:
        Next available slot (1-5) or None if parent is full
    """
    # Get used slots
    cur = conn.execute(
        "SELECT slot FROM nodes WHERE parent_id = ? AND slot IS NOT NULL ORDER BY slot",
        (parent_id,)
    )
    used_slots = {row["slot"] for row in cur.fetchall()}
    
    # Find first available slot
    for slot in range(1, 6):
        if slot not in used_slots:
            return slot
    
    return None  # Parent is full


def delete_all_nodes(conn: sqlite3.Connection) -> None:
    """Delete all nodes (for replace mode)."""
    conn.execute("DELETE FROM nodes")
    conn.execute("DELETE FROM outcomes")


def list_direct_children(conn: sqlite3.Connection, parent_ids: List[int]) -> List[Dict[str, Any]]:
    """
    List direct children for the given parent IDs.
    
    Args:
        conn: Database connection
        parent_ids: List of parent node IDs
        
    Returns:
        List of child dicts with {id, parent_id, slot, label, depth}
    """
    if not parent_ids:
        return []
    
    placeholders = ",".join("?" * len(parent_ids))
    sql = f"""
    SELECT id, parent_id, slot, label, depth
    FROM nodes
    WHERE parent_id IN ({placeholders})
    ORDER BY parent_id, slot
    """
    
    cur = conn.execute(sql, parent_ids)
    return [dict(row) for row in cur.fetchall()]


@contextmanager
def transaction(conn: sqlite3.Connection):
    """Context manager for database transactions."""
    try:
        conn.execute("BEGIN")
        yield
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


def apply_import(paths: List[List[str]], mode: Literal["replace", "append", "preview"], db_path: Optional[str] = None) -> ImportResult:
    """
    Apply import of paths to the database using contextual node creation.
    
    Args:
        paths: List of paths, each path is a list of labels (D0..D6)
        mode: Import mode (replace/append/preview)
        
    Returns:
        ImportResult with operation details
    """
    result = ImportResult()
    result.preview = (mode == "preview")
    
    if not paths:
        return result
    
    # Get database connection
    if db_path is None:
        # Use environment variable or default path
        db_path = os.environ.get("LORIEN_DB_PATH", os.path.expanduser("~/.local/share/lorien/app.db"))
    
    # Apply migrations first
    from api.db.migrate import apply_migrations
    apply_migrations(db_path)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    
    try:
        # Ensure indexes exist
        _ensure_schema(conn)
        
        if mode == "replace":
            with transaction(conn):
                delete_all_nodes(conn)
                result = _process_paths_contextual(conn, paths, result)
        elif mode == "append":
            with transaction(conn):
                result = _process_paths_contextual(conn, paths, result)
        elif mode == "preview":
            # Preview mode - don't actually write to database
            result = _preview_paths(paths, result)
        else:
            raise ValueError(f"Invalid mode: {mode}")
            
    finally:
        conn.close()
    
    return result


def _process_paths_contextual(conn: sqlite3.Connection, paths: List[List[str]], result: ImportResult) -> ImportResult:
    """Process paths using contextual node creation with single connection."""
    for path in paths:
        if not path:
            continue
            
        parent_id = None
        for depth, label in enumerate(path):
            # Create or get node contextually
            node_id = _get_or_create_node(conn, parent_id, depth, label)
            result.inserted_nodes += 1
            
            # Update parent for next iteration
            parent_id = node_id
            
            # Count edges (parent -> child relationships)
            if parent_id is not None:
                result.inserted_edges += 1
        
        # Count parents touched
        if parent_id is not None:
            result.parents_touched += 1
    
    return result


def _process_paths(conn: sqlite3.Connection, paths: List[List[str]], result: ImportResult) -> ImportResult:
    """Process paths and create nodes/edges (legacy method)."""
    node_cache = {}  # (parent_id, depth, label) -> node_id
    
    for path in paths:
        if not path:
            continue
            
        parent_id = None
        for depth, label in enumerate(path):
            # Create or get node
            cache_key = (parent_id, depth, label)
            if cache_key in node_cache:
                node_id = node_cache[cache_key]
            else:
                node_id = get_or_create_node(conn, parent_id, depth, label, label)
                node_cache[cache_key] = node_id
                result.inserted_nodes += 1
            
            # Update parent for next iteration
            parent_id = node_id
            
            # Count edges (parent -> child relationships)
            if parent_id is not None:
                result.inserted_edges += 1
        
        # Count parents touched
        if parent_id is not None:
            result.parents_touched += 1
    
    return result


def _preview_paths(paths: List[List[str]], result: ImportResult) -> ImportResult:
    """Preview mode - just count what would be created."""
    for path in paths:
        if not path:
            continue
            
        # Count nodes that would be created
        result.inserted_nodes += len(path)
        
        # Count edges that would be created
        result.inserted_edges += len(path) - 1  # n nodes = n-1 edges
        
        # Count parents touched
        result.parents_touched += 1
    
    return result
