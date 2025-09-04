"""
Utility functions for the API layer.
"""

import csv
import io
from typing import List, Dict, Any
from datetime import datetime


def normalize_label(label: str) -> str:
    """
    Normalize a label by trimming whitespace, validating characters, and ensuring it's not empty.

    Args:
        label: Raw label string

    Returns:
        str: Normalized label

    Raises:
        ValueError: If label is empty after normalization or contains invalid characters
    """
    import re

    normalized = label.strip()
    if not normalized:
        raise ValueError("label cannot be empty")

    # Simple allowlist mirroring Outcomes (letters/digits/space/comma/hyphen)
    if not re.fullmatch(r"[A-Za-z0-9 ,\-]+", normalized):
        raise ValueError("label must be alnum/comma/hyphen/space")

    return normalized


def validate_unique_slots(children: List[Dict[str, Any]]) -> None:
    """
    Validate that all slots are unique within a children list.
    
    Args:
        children: List of child dictionaries with 'slot' keys
        
    Raises:
        ValueError: If duplicate slots are found
    """
    slots = [child['slot'] for child in children]
    if len(slots) != len(set(slots)):
        raise ValueError("Duplicate slots are not allowed")


def format_csv_export(data: List[Dict[str, Any]]) -> str:
    """
    Format data for CSV export with the specific 8-column header layout.
    
    Args:
        data: List of dictionaries containing tree data
        
    Returns:
        str: CSV-formatted string with proper headers
    """
    # Define the canonical 8-column headers (frozen contract)
    headers = ["Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5", "Diagnostic Triage", "Actions"]
    
    # Create CSV output with consistent line endings
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='\n')
    
    # Always write header
    writer.writerow(headers)
    
    # Write data rows if available
    if data:
        for row in data:
            csv_row = []
            for header in headers:
                if header == "Vital Measurement":
                    csv_row.append(row.get("Diagnosis", row.get("Vital Measurement", "")))
                elif header in ["Node 1", "Node 2", "Node 3", "Node 4", "Node 5"]:
                    csv_row.append(row.get(header, ""))
                elif header == "Diagnostic Triage":
                    csv_row.append(row.get("Diagnostic Triage", ""))
                elif header == "Actions":
                    csv_row.append(row.get("Actions", ""))
                else:
                    csv_row.append("")
            writer.writerow(csv_row)
    
    return output.getvalue()


def get_missing_slots(parent_id: int, existing_children: List[Dict[str, Any]]) -> List[int]:
    """
    Get list of missing slot numbers for a parent.
    
    Args:
        parent_id: ID of the parent node
        existing_children: List of existing children with slot information
        
    Returns:
        List[int]: List of missing slot numbers (1-5)
    """
    existing_slots = {child.get('slot') for child in existing_children if child.get('slot')}
    all_slots = set(range(1, 6))  # 1-5
    return sorted(list(all_slots - existing_slots))


def get_missing_slots_from_payload(children: List[Dict[str, Any]]) -> List[int]:
    """
    Get list of missing slot numbers from a children payload.
    
    Args:
        children: List of child dictionaries with 'slot' keys
        
    Returns:
        List[int]: List of missing slot numbers (1-5)
    """
    present = {c.get("slot") for c in children if c.get("slot") is not None}
    expected = {1, 2, 3, 4, 5}
    return sorted(list(expected - present))


def format_error_response(error: str, detail: str = None, code: str = None) -> Dict[str, Any]:
    """
    Format a standardized error response.
    
    Args:
        error: Error message
        detail: Additional error details
        code: Error code
        
    Returns:
        Dict[str, Any]: Formatted error response
    """
    response = {"error": error}
    if detail:
        response["detail"] = detail
    if code:
        response["code"] = code
    return response
