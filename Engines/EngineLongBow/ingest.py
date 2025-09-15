"""
Path-based ingestion for EngineLongBow.
Reads CSV/XLSX files with frozen 8-column header and converts rows to paths.
"""

import csv
import io
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd

from .consts import FROZEN_HEADER, PATH_COLUMNS, NOTES_COLUMN

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


def validate_header(header: List[str]) -> Dict[str, Any]:
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
                    "row": 1
                }
            }
        }
    
    for i, (expected, received) in enumerate(zip(FROZEN_HEADER, header)):
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
                        "row": 1
                    }
                }
            }
    
    return {"valid": True}


def read_csv_file(file_content: bytes) -> List[List[str]]:
    """Read CSV file and return rows as list of lists."""
    content = file_content.decode('utf-8')
    reader = csv.reader(io.StringIO(content))
    return list(reader)


def read_xlsx_file(file_content: bytes) -> List[List[str]]:
    """Read XLSX file and return rows as list of lists."""
    if openpyxl is None:
        raise RuntimeError("openpyxl required for XLSX files")
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx') as tmp:
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


def read_file(file_content: bytes, filename: str) -> List[List[str]]:
    """
    Read file content and return rows as list of lists.
    
    Args:
        file_content: Raw file bytes
        filename: Original filename for format detection
        
    Returns:
        List of rows, each row is a list of 8 strings
    """
    file_path = Path(filename.lower())
    
    if file_path.suffix == '.csv':
        return read_csv_file(file_content)
    elif file_path.suffix in ['.xlsx', '.xls']:
        return read_xlsx_file(file_content)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")


def extract_paths(rows: List[List[str]]) -> List[List[str]]:
    """
    Extract path labels from rows, skipping blank rows.
    
    Args:
        rows: List of rows from file (including header)
        
    Returns:
        List of paths, each path is a list of up to 7 labels (D0..D6)
    """
    if not rows:
        return []
    
    # Skip header row
    data_rows = rows[1:] if len(rows) > 1 else []
    
    paths = []
    for row in data_rows:
        # Extract path columns (D0..D6)
        path_labels = []
        for i, col in enumerate(PATH_COLUMNS):
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
            paths.append(path_labels)
    
    return paths


def ingest_file(file_content: bytes, filename: str) -> Dict[str, Any]:
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
            return {
                "success": True,
                "paths": [],
                "total_rows": 0,
                "valid_rows": 0
            }
        
        # Validate header
        header = rows[0]
        validation = validate_header(header)
        
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"],
                "paths": [],
                "total_rows": len(rows) - 1,
                "valid_rows": 0
            }
        
        # Extract paths
        paths = extract_paths(rows)
        
        return {
            "success": True,
            "paths": paths,
            "total_rows": len(rows) - 1,  # Exclude header
            "valid_rows": len(paths)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": "value_error.file_processing",
                "loc": ["file"],
                "msg": f"Error processing file: {str(e)}",
                "ctx": {"filename": filename}
            },
            "paths": [],
            "total_rows": 0,
            "valid_rows": 0
        }
