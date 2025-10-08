"""
Path presentation for EngineLongBow.
Export current graph back to the frozen 8-column header as paths.
"""

import os
import sqlite3
from collections.abc import Iterable
from typing import Any, Optional

from .consts import FROZEN_HEADER


def export_paths(
    limit: Optional[int] = None,
    offset: int = 0,
    root_id: Optional[int] = None,
    conn: sqlite3.Connection = None,
) -> Iterable[list[str]]:
    """
    Export current graph as paths in frozen 8-column format.

    Args:
        limit: Maximum number of paths to return (None for all)
        offset: Number of paths to skip
        root_id: Optional root ID to filter paths to only those under this root
        conn: Database connection to use (if None, will create own connection)

    Yields:
        List of strings representing one row (D0..D6 + Notes)
    """
    # If no connection provided, create one (for backward compatibility)
    if conn is None:
        # Try to get from environment or use default
        db_path = os.environ.get(
            "LORIEN_DB_PATH", os.path.expanduser("~/.local/share/lorien/app.db")
        )
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        should_close = True
    else:
        should_close = False

    try:
        # Get all paths from root to leaves with metadata
        paths_with_meta = _get_all_paths_with_metadata(conn, limit, offset, root_id)

        for path_with_meta in paths_with_meta:
            # Convert path with metadata to 8-column row
            row = _path_to_row_with_metadata(path_with_meta)
            yield row

    finally:
        if should_close:
            conn.close()


def _get_all_paths_with_metadata(
    conn: sqlite3.Connection, limit: Optional[int], offset: int, root_id: Optional[int] = None
) -> list[dict[str, Any]]:
    """
    Get all paths from root to leaves with metadata using recursive CTE.

    Args:
        conn: Database connection
        limit: Maximum number of paths
        offset: Number of paths to skip
        root_id: Optional root ID to filter paths to only those under this root

    Returns:
        List of dicts with 'path' (list of labels) and 'metadata' (d6, notes)
    """
    # Build the recursive CTE to traverse from root to leaves with metadata
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
        WHERE parent_id IS NULL"""

    # Add root_id filter if specified
    if root_id is not None:
        sql += f" AND id = {root_id}"

    sql += """

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
        WHERE n.depth <= 5  -- Limit to max structural depth (D0..D5)
    )
    SELECT
        pt.path,
        pt.path_length,
        pt.id as leaf_id,
        pm.d6,
        pm.notes
    FROM path_traversal pt
    LEFT JOIN path_meta pm ON pm.leaf_id = pt.id
    WHERE pt.path_length <= 6  -- Only paths up to 6 levels (D0..D5)
    ORDER BY pt.path
    """

    if limit is not None:
        sql += f" LIMIT {limit}"
    if offset > 0:
        sql += f" OFFSET {offset}"

    cursor = conn.execute(sql)
    paths_with_meta = []

    for row in cursor.fetchall():
        path_str = row["path"]
        path_labels = path_str.split("|") if path_str else []

        paths_with_meta.append(
            {"path": path_labels, "metadata": {"d6": row["d6"], "notes": row["notes"]}}
        )

    return paths_with_meta


def _get_all_paths(conn: sqlite3.Connection, limit: Optional[int], offset: int) -> list[list[str]]:
    """
    Get all paths from root to leaves using recursive CTE.
    Legacy function for backward compatibility.

    Args:
        conn: Database connection
        limit: Maximum number of paths
        offset: Number of paths to skip

    Returns:
        List of paths, each path is a list of labels
    """
    paths_with_meta = _get_all_paths_with_metadata(conn, limit, offset)
    return [item["path"] for item in paths_with_meta]


def _path_to_row_with_metadata(path_with_meta: dict[str, Any]) -> list[str]:
    """
    Convert a path with metadata to a frozen 8-column row.

    Args:
        path_with_meta: Dict with 'path' (list of labels) and 'metadata' (d6, notes)

    Returns:
        List of 8 strings (D0..D6 + Notes)
    """
    path = path_with_meta["path"]
    metadata = path_with_meta["metadata"]

    row = []

    # Add structural path columns (D0..D5)
    for i in range(6):
        if i < len(path):
            row.append(path[i])
        else:
            row.append("")  # Pad with empty strings

    # Add D6 from metadata
    row.append(metadata.get("d6", ""))

    # Add Notes from metadata
    row.append(metadata.get("notes", ""))

    return row


def _path_to_row(path: list[str]) -> list[str]:
    """
    Convert a path to a frozen 8-column row.
    Legacy function for backward compatibility.

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


def export_paths_to_csv(
    limit: Optional[int] = None,
    offset: int = 0,
    root_id: Optional[int] = None,
    conn: sqlite3.Connection = None,
) -> str:
    """
    Export paths as CSV string with frozen header.

    Args:
        limit: Maximum number of paths to return
        offset: Number of paths to skip
        root_id: Optional root ID to filter paths to only those under this root

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
    for row in export_paths(limit, offset, root_id, conn):
        writer.writerow(row)

    return output.getvalue()


def export_paths_to_xlsx(
    limit: Optional[int] = None,
    offset: int = 0,
    root_id: Optional[int] = None,
    conn: sqlite3.Connection = None,
) -> bytes:
    """
    Export paths as XLSX bytes with frozen header.

    Args:
        limit: Maximum number of paths to return
        offset: Number of paths to skip
        root_id: Optional root ID to filter paths to only those under this root

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
    for row in export_paths(limit, offset, root_id, conn):
        ws.append(row)

    # Save to bytes
    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()
