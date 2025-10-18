"""
Utility functions for EngineShelob pathogen data normalization.
"""

from typing import Any, Optional

from .consts import PROPERTY_COLUMNS


def normalize_pathogen_name(name: Any) -> Optional[str]:
    """
    Normalize a pathogen name for consistent storage.

    Args:
        name: Raw pathogen name from spreadsheet

    Returns:
        Normalized name or None if empty/invalid
    """
    if name is None:
        return None

    s = str(name).strip()
    if s == "" or s.lower() in ["nan", "null", "none"]:
        return None

    # Basic normalization: trim whitespace, preserve case
    return s


def normalize_value(value: Any) -> Optional[str]:
    """
    Normalize a property value for storage.

    Args:
        value: Raw value from spreadsheet

    Returns:
        Normalized value or None if empty/invalid
    """
    if value is None:
        return None

    s = str(value).strip()
    if s == "" or s.lower() in ["nan", "null", "none"]:
        return None

    # Preserve case for property values
    return s


def normalize_association_value(value: Any) -> Optional[int]:
    """
    Normalize an association value to binary (0/1).

    Args:
        value: Raw association value from spreadsheet

    Returns:
        0, 1, or None if invalid
    """
    if value is None:
        return None

    s = str(value).strip().lower()

    # Handle various representations of "true"
    if s in ["1", "yes", "true", "present", "y"]:
        return 1

    # Handle various representations of "false"
    if s in ["0", "no", "false", "absent", "n"]:
        return 0

    # Try to parse as integer
    try:
        int_val = int(s)
        return 1 if int_val != 0 else 0
    except ValueError:
        pass

    return None


def is_association_column(column_name: str, sample_values: list[Any]) -> bool:
    """
    Determine if a column contains association data based on name and sample values.

    Args:
        column_name: Name of the column
        sample_values: Sample values from the column

    Returns:
        True if this appears to be an association column
    """
    # Check column name patterns
    name_lower = column_name.lower()
    for indicator in ["meningitis", "headache", "photophobia", "pneumonia", "fever", "cough"]:
        if indicator in name_lower:
            return True

    # Check if most values are binary
    binary_count = 0
    total_count = 0

    for value in sample_values[:10]:  # Check first 10 values
        if value is not None and str(value).strip():
            total_count += 1
            normalized = normalize_association_value(value)
            if normalized is not None:
                binary_count += 1

    # If more than 70% of non-empty values are binary, consider it an association column
    if total_count > 0 and (binary_count / total_count) > 0.7:
        return True

    return False


def detect_property_association_breakpoint(headers: list[str], sample_rows: list[list[Any]]) -> int:
    """
    Detect where property columns end and association columns begin.

    Args:
        headers: List of column headers
        sample_rows: Sample data rows for analysis

    Returns:
        Index where association columns begin (0-based)
    """
    # Look for "Notes" column as a strong indicator
    for i, header in enumerate(headers):
        if header.lower().strip() in ["notes", "note"]:
            # Check if the next columns look like associations
            if i + 1 < len(headers):
                next_samples = [row[i + 1] for row in sample_rows if i + 1 < len(row)]
                if is_association_column(headers[i + 1], next_samples):
                    return i + 1

    # Fallback: analyze each column for binary patterns
    for i, header in enumerate(headers):
        if i >= len(PROPERTY_COLUMNS):  # Beyond expected property columns
            column_samples = [row[i] for row in sample_rows if i < len(row)]
            if is_association_column(header, column_samples):
                return i

    # Default: assume all columns are properties if no clear breakpoint
    return len(headers)
