"""
Path-based ingestion for EngineLongBow.
Reads CSV/XLSX files with frozen 8-column header and converts rows to paths.
"""

import csv
import io
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Optional

from .consts import FROZEN_HEADER

# Header synonyms for user-friendly import
CANON = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "Notes"]
HEADER_SYNONYMS = {
    "d0": "D0",
    "vitalmeasurement": "D0",
    "vital measurement": "D0",
    "d1": "D1",
    "node1": "D1",
    "node 1": "D1",
    "d2": "D2",
    "node2": "D2",
    "node 2": "D2",
    "d3": "D3",
    "node3": "D3",
    "node 3": "D3",
    "d4": "D4",
    "node4": "D4",
    "node 4": "D4",
    "d5": "D5",
    "node5": "D5",
    "node 5": "D5",
    # IMPORTANT CHANGE: diagnostic triage is NOT a node; normalize to Notes
    "d6": "D6",  # keep canonical name available if already provided
    "diagnostictriage": "Notes",
    "diagnostic triage": "Notes",
    "notes": "Notes",
    "actions": "Notes",
}


class HeaderMismatchError(Exception):
    """Exception for header validation failures with hint support."""

    def __init__(self, expected, received, hint=None):
        self.expected = expected
        self.received = received
        self.hint = hint
        super().__init__(f"Header mismatch: expected {expected}, got {received}")


def _key(s: str) -> str:
    return " ".join(s.strip().split()).lower()


def normalize_header(cols: list[str]) -> list[str]:
    mapped = []
    notes_count = 0

    # First, check if this is already the canonical header
    if cols == CANON:
        return cols

    for raw in cols:
        k = _key(raw)
        canon = HEADER_SYNONYMS.get(k)
        if not canon:
            # allow already-canonical names
            if raw in CANON:
                canon = raw
        if not canon:
            # fail fast
            raise HeaderMismatchError(
                expected=CANON,
                received=cols,
                hint="Accepted synonyms: " + ", ".join(sorted(set(HEADER_SYNONYMS.keys()))),
            )

        # Handle multiple Notes columns (Diagnostic Triage + Actions both map to Notes)
        if canon == "Notes":
            notes_count += 1
            if notes_count == 1:
                mapped.append("D6")  # First Notes synonym becomes D6
            else:
                mapped.append("Notes")  # Subsequent Notes synonyms stay as Notes
        else:
            mapped.append(canon)

    # Ensure we have exactly 8 columns
    if len(mapped) != 8:
        raise HeaderMismatchError(
            expected=CANON, received=cols, hint=f"Expected exactly 8 columns, got {len(mapped)}"
        )

    # Verify we have the right structure: D0..D5, D6, Notes
    expected_structure = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "Notes"]
    if mapped != expected_structure:
        raise HeaderMismatchError(
            expected=expected_structure,
            received=cols,
            hint="Columns must map to D0..D5, D6, Notes structure",
        )

    return mapped


try:
    import openpyxl
except ImportError:
    openpyxl = None


def normalize_label(label: Any) -> Optional[str]:
    """
    Normalize a label for grouping (casefolding, whitespace collapse, Unicode NFKC).
    Returns None for blank/empty labels.
    """
    if label is None:
        return None

    s = str(label).strip()
    if s == "" or s.lower() == "nan":
        return None

    # Basic normalization (can be enhanced with proper Unicode NFKC)
    return s.lower().strip()


def _normalize_metadata_value(value: Any) -> Optional[str]:
    """
    Normalize a metadata value (preserve case, only trim whitespace).
    Returns None for blank/empty values.
    """
    if value is None:
        return None

    s = str(value).strip()
    if s == "" or s.lower() == "nan":
        return None

    # Only trim whitespace, preserve case for metadata
    return s


def validate_header(header: list[str]) -> dict[str, Any]:
    """
    Validate that the header matches the frozen 8-column header exactly.

    Returns:
        Dict with validation result and error details if mismatch
    """
    if len(header) != len(FROZEN_HEADER):
        return {
            "valid": False,
            "error": {
                "type": "value_error.header_mismatch",
                "loc": ["header"],
                "msg": "Frozen 8-column header mismatch",
                "ctx": {
                    "expected": FROZEN_HEADER,
                    "received": header,
                    "col_index": len(header),
                    "row": 1,
                },
            },
        }

    for i, (expected, received) in enumerate(zip(FROZEN_HEADER, header, strict=False)):
        if expected != received:
            return {
                "valid": False,
                "error": {
                    "type": "value_error.header_mismatch",
                    "loc": ["header"],
                    "msg": "Frozen 8-column header mismatch",
                    "ctx": {
                        "expected": FROZEN_HEADER,
                        "received": header,
                        "col_index": i,
                        "row": 1,
                    },
                },
            }

    return {"valid": True}


def read_csv_file(file_content: bytes) -> list[list[str]]:
    """Read CSV file and return rows as list of lists."""
    content = file_content.decode("utf-8")
    reader = csv.reader(io.StringIO(content))
    return list(reader)


def read_xlsx_file(file_content: bytes) -> list[list[str]]:
    """Read XLSX file and return rows as list of lists."""
    if openpyxl is None:
        raise RuntimeError("openpyxl required for XLSX files")

    with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
        tmp.write(file_content)
        tmp.flush()

        wb = openpyxl.load_workbook(tmp.name)
        ws = wb.active

        rows = []
        for row in ws.iter_rows(values_only=True):
            # Convert None values to empty strings and ensure we have exactly 8 columns
            row_data = [str(cell) if cell is not None else "" for cell in row]
            # Pad or truncate to exactly 8 columns
            while len(row_data) < 8:
                row_data.append("")
            if len(row_data) > 8:
                row_data = row_data[:8]
            rows.append(row_data)

        return rows


def read_file(file_content: bytes, filename: str) -> list[list[str]]:
    """
    Read file content and return rows as list of lists.

    Args:
        file_content: Raw file bytes
        filename: Original filename for format detection

    Returns:
        List of rows, each row is a list of 8 strings
    """
    file_path = Path(filename.lower())

    if file_path.suffix == ".csv":
        return read_csv_file(file_content)
    elif file_path.suffix in [".xlsx", ".xls"]:
        return read_xlsx_file(file_content)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")


def extract_paths_with_metadata(rows: list[list[str]]) -> list[dict[str, Any]]:
    """
    Extract path labels and metadata from rows, skipping blank rows.

    Args:
        rows: List of rows from file (including header)

    Returns:
        List of dicts with 'path' (D0..D5 labels) and 'metadata' (D6, Notes values)
        Note: D6/Notes are stored as metadata, not used for structural node creation
    """
    if not rows:
        return []

    # Skip header row
    data_rows = rows[1:] if len(rows) > 1 else []

    paths_with_meta = []
    for row in data_rows:
        # Extract structural path columns (D0..D5 only) to prevent depth=6 nodes
        path_labels = []
        for i in range(6):  # Only D0..D5, not D6
            if i < len(row):
                label = normalize_label(row[i])
                if label is not None:
                    path_labels.append(label)
                else:
                    break  # Stop at first blank label
            else:
                break

        # Only include non-empty paths
        if path_labels:
            # Extract metadata from D6 and Notes columns (preserve case)
            d6_value = None
            notes_value = None

            if len(row) > 6:  # D6 column exists
                d6_value = _normalize_metadata_value(row[6])
            if len(row) > 7:  # Notes column exists
                notes_value = _normalize_metadata_value(row[7])

            paths_with_meta.append(
                {"path": path_labels, "metadata": {"d6": d6_value, "notes": notes_value}}
            )

    return paths_with_meta


def _upsert_path_meta(
    conn: sqlite3.Connection, leaf_id: int, d6_value: Optional[str], notes_value: Optional[str]
) -> None:
    """
    Upsert path metadata for a leaf node.

    Args:
        conn: SQLite connection
        leaf_id: ID of the leaf node
        d6_value: D6 (Diagnostic Triage) value, may be None
        notes_value: Notes (Actions) value, may be None
    """
    conn.execute(
        """
        INSERT INTO path_meta(leaf_id, d6, notes)
        VALUES(?, ?, ?)
        ON CONFLICT(leaf_id) DO UPDATE SET
          d6 = COALESCE(excluded.d6, path_meta.d6),
          notes = COALESCE(excluded.notes, path_meta.notes)
    """,
        (leaf_id, d6_value, notes_value),
    )


def extract_paths(rows: list[list[str]]) -> list[list[str]]:
    """
    Extract path labels from rows, skipping blank rows.
    Legacy function for backward compatibility.

    Args:
        rows: List of rows from file (including header)

    Returns:
        List of paths, each path is a list of up to 6 labels (D0..D5)
        Note: D6/Notes are not used for structural node creation
    """
    paths_with_meta = extract_paths_with_metadata(rows)
    return [item["path"] for item in paths_with_meta]


def ingest_file(file_content: bytes, filename: str) -> dict[str, Any]:
    """
    Main ingestion function that reads file and extracts paths.

    Args:
        file_content: Raw file bytes
        filename: Original filename

    Returns:
        Dict with paths and validation results
    """
    try:
        # Read file
        rows = read_file(file_content, filename)

        if not rows:
            return {"success": True, "paths": [], "total_rows": 0, "valid_rows": 0}

        # Validate and normalize header
        header = rows[0]
        try:
            normalized_header = normalize_header(header)
            # Replace the header row with normalized version for processing
            rows[0] = normalized_header
        except HeaderMismatchError as e:
            return {
                "success": False,
                "error": {
                    "type": "value_error.header_mismatch",
                    "loc": ["header"],
                    "msg": "Frozen 8-column header mismatch",
                    "ctx": {"expected": e.expected, "received": e.received, "hint": e.hint},
                },
                "paths": [],
                "total_rows": len(rows) - 1,
                "valid_rows": 0,
            }

        # Extract paths with metadata
        paths_with_meta = extract_paths_with_metadata(rows)

        return {
            "success": True,
            "paths": paths_with_meta,
            "total_rows": len(rows) - 1,  # Exclude header
            "valid_rows": len(paths_with_meta),
        }

    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": "value_error.file_processing",
                "loc": ["file"],
                "msg": f"Error processing file: {str(e)}",
                "ctx": {"filename": filename},
            },
            "paths": [],
            "total_rows": 0,
            "valid_rows": 0,
        }
