"""
Pathogen data ingestion for EngineShelob.
Reads CSV/XLSX files and extracts pathogen properties and associations.
"""

import csv
import io
import tempfile
from pathlib import Path
from typing import Any

from .consts import PROPERTY_COLUMNS
from .utils import (
    detect_property_association_breakpoint,
    normalize_association_value,
    normalize_pathogen_name,
    normalize_value,
)

try:
    import openpyxl
except ImportError:
    openpyxl = None


class PathogenDataError(Exception):
    """Exception for pathogen data processing errors."""

    pass


def read_csv_file(file_content: bytes) -> list[list[str]]:
    """Read CSV file and return rows as list of lists."""
    content = file_content.decode("utf-8")
    reader = csv.reader(io.StringIO(content))
    return list(reader)


def read_xlsx_file(file_content: bytes) -> list[list[str]]:
    """Read XLSX file and return rows as list of lists."""
    if openpyxl is None:
        raise PathogenDataError("openpyxl required for XLSX files")

    with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
        tmp.write(file_content)
        tmp.flush()

        wb = openpyxl.load_workbook(tmp.name)
        ws = wb.active

        rows = []
        for row in ws.iter_rows(values_only=True):
            # Convert None values to empty strings
            row_data = [str(cell) if cell is not None else "" for cell in row]
            rows.append(row_data)

        return rows


def read_file(file_content: bytes, filename: str) -> list[list[str]]:
    """
    Read file content and return rows as list of lists.

    Args:
        file_content: Raw file bytes
        filename: Original filename for format detection

    Returns:
        List of rows, each row is a list of strings

    Raises:
        PathogenDataError: If file format is unsupported
    """
    file_path = Path(filename.lower())

    if file_path.suffix == ".csv":
        return read_csv_file(file_content)
    elif file_path.suffix in [".xlsx", ".xls"]:
        return read_xlsx_file(file_content)
    else:
        raise PathogenDataError(f"Unsupported file format: {file_path.suffix}")


def extract_pathogen_data(rows: list[list[str]]) -> dict[str, Any]:
    """
    Extract pathogen data from spreadsheet rows.

    Args:
        rows: List of rows from file (including header)

    Returns:
        Dict with extracted data structure:
        {
            "pathogens": [{"properties": {...}, "associations": {...}}],
            "association_types": [...],
            "breakpoint": int
        }
    """
    if not rows:
        return {"pathogens": [], "association_types": [], "breakpoint": 0}

    # Get headers and data rows
    headers = rows[0]
    data_rows = rows[1:] if len(rows) > 1 else []

    # Detect breakpoint between properties and associations
    breakpoint = detect_property_association_breakpoint(
        headers, data_rows[:5]
    )  # Use first 5 rows for analysis

    # Extract association type names
    association_types = []
    if breakpoint < len(headers):
        association_types = headers[breakpoint:]

    # Extract pathogen data
    pathogens = []
    for row in data_rows:
        if not row or all(not str(cell).strip() for cell in row):
            continue  # Skip empty rows

        # Extract properties (columns 0 to breakpoint-1)
        properties = {}
        for i, prop_name in enumerate(PROPERTY_COLUMNS):
            if i < breakpoint and i < len(row):
                if prop_name == "pathogen_name":
                    properties[prop_name] = normalize_pathogen_name(row[i])
                else:
                    properties[prop_name] = normalize_value(row[i])
            else:
                properties[prop_name] = None

        # Extract associations (columns breakpoint onwards)
        associations = {}
        for i, assoc_type in enumerate(association_types):
            col_index = breakpoint + i
            if col_index < len(row):
                value = normalize_association_value(row[col_index])
                if value is not None:  # Only store non-null associations
                    associations[assoc_type] = value

        # Only include pathogens with at least a name
        if properties.get("pathogen_name"):
            pathogens.append({"properties": properties, "associations": associations})

    return {
        "pathogens": pathogens,
        "association_types": association_types,
        "breakpoint": breakpoint,
    }


def ingest_file(file_content: bytes, filename: str) -> dict[str, Any]:
    """
    Main ingestion function that reads file and extracts pathogen data.

    Args:
        file_content: Raw file bytes
        filename: Original filename

    Returns:
        Dict with extracted data and metadata:
        {
            "success": bool,
            "data": {...},  # From extract_pathogen_data
            "total_rows": int,
            "valid_pathogens": int,
            "errors": List[str]
        }
    """
    try:
        # Read file
        rows = read_file(file_content, filename)

        if not rows:
            return {
                "success": True,
                "data": {"pathogens": [], "association_types": [], "breakpoint": 0},
                "total_rows": 0,
                "valid_pathogens": 0,
                "errors": [],
            }

        # Extract pathogen data
        data = extract_pathogen_data(rows)

        return {
            "success": True,
            "data": data,
            "total_rows": len(rows) - 1,  # Exclude header
            "valid_pathogens": len(data["pathogens"]),
            "errors": [],
        }

    except Exception as e:
        return {
            "success": False,
            "data": {"pathogens": [], "association_types": [], "breakpoint": 0},
            "total_rows": 0,
            "valid_pathogens": 0,
            "errors": [f"Error processing file: {str(e)}"],
        }
