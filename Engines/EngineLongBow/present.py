"""
Path presentation for EngineLongBow.
Export current graph back to the frozen 8-column header as paths.
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional, Iterable
from .consts import FROZEN_HEADER, PATH_COLUMNS, NOTES_COLUMN


def export_paths(limit: Optional[int] = None, offset: int = 0, db_path: Optional[str] = None) -> Iterable[List[str]]:
    """
    Export current graph as paths in frozen 8-column format.
    
    Args:
        limit: Maximum number of paths to return (None for all)
        offset: Number of paths to skip
        
    Yields:
        List of strings representing one row (D0..D6 + Notes)
    """
    # Get database connection
    if db_path is None:
        # Try to get from environment or use default
        db_path = os.environ.get("LORIEN_DB_PATH", os.path.expanduser("~/.local/share/lorien/app.db"))
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Get all paths from root to leaves
        paths = _get_all_paths(conn, limit, offset)
        
        for path in paths:
            # Convert path to 8-column row
            row = _path_to_row(path)
            yield row
            
    finally:
        conn.close()


def _get_all_paths(conn: sqlite3.Connection, limit: Optional[int], offset: int) -> List[List[str]]:
    """
    Get all paths from root to leaves using recursive CTE.
    
    Args:
        conn: Database connection
        limit: Maximum number of paths
        offset: Number of paths to skip
        
    Returns:
        List of paths, each path is a list of labels
    """
    # Build the recursive CTE to traverse from root to leaves
    sql = """
    WITH RECURSIVE path_traversal AS (
        -- Base case: root nodes
        SELECT 
            id,
            parent_id,
            label,
            depth,
            CAST(label AS TEXT) AS path,
            depth AS path_length
        FROM nodes 
        WHERE parent_id IS NULL
        
        UNION ALL
        
        -- Recursive case: children
        SELECT 
            n.id,
            n.parent_id,
            n.label,
            n.depth,
            pt.path || '|' || n.label AS path,
            pt.path_length + 1 AS path_length
        FROM nodes n
        JOIN path_traversal pt ON n.parent_id = pt.id
        WHERE n.depth <= 6  -- Limit to max depth
    )
    SELECT 
        path,
        path_length
    FROM path_traversal
    WHERE path_length <= 7  -- Only paths up to 7 levels (D0..D6)
    ORDER BY path
    """
    
    if limit is not None:
        sql += f" LIMIT {limit}"
    if offset > 0:
        sql += f" OFFSET {offset}"
    
    cur = conn.execute(sql)
    paths = []
    
    for row in cur.fetchall():
        path_str = row["path"]
        path_labels = path_str.split("|")
        paths.append(path_labels)
    
    return paths


def _path_to_row(path: List[str]) -> List[str]:
    """
    Convert a path to a frozen 8-column row.
    
    Args:
        path: List of labels representing the path
        
    Returns:
        List of 8 strings (D0..D6 + Notes)
    """
    row = []
    
    # Add path columns (D0..D6)
    for i in range(7):
        if i < len(path):
            row.append(path[i])
        else:
            row.append("")  # Pad with empty strings
    
    # Add Notes column (always empty for now)
    row.append("")
    
    return row


def export_paths_to_csv(limit: Optional[int] = None, offset: int = 0, db_path: Optional[str] = None) -> str:
    """
    Export paths as CSV string with frozen header.
    
    Args:
        limit: Maximum number of paths to return
        offset: Number of paths to skip
        
    Returns:
        CSV string with frozen header and path rows
    """
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(FROZEN_HEADER)
    
    # Write path rows
    for row in export_paths(limit, offset, db_path):
        writer.writerow(row)
    
    return output.getvalue()


def export_paths_to_xlsx(limit: Optional[int] = None, offset: int = 0, db_path: Optional[str] = None) -> bytes:
    """
    Export paths as XLSX bytes with frozen header.
    
    Args:
        limit: Maximum number of paths to return
        offset: Number of paths to skip
        
    Returns:
        XLSX bytes
    """
    try:
        import openpyxl
    except ImportError:
        raise RuntimeError("openpyxl required for XLSX export")
    
    wb = openpyxl.Workbook()
    ws = wb.active
    
    # Write header
    ws.append(FROZEN_HEADER)
    
    # Write path rows
    for row in export_paths(limit, offset, db_path):
        ws.append(row)
    
    # Save to bytes
    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()
