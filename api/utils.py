"""
Utility functions for the API layer.
"""

import csv
import io
from typing import List, Dict, Any
from datetime import datetime


def normalize_label(label: str) -> str:
    """
    Normalize a label by trimming whitespace and ensuring it's not empty.
    
    Args:
        label: Raw label string
        
    Returns:
        str: Normalized label
        
    Raises:
        ValueError: If label is empty after normalization
    """
    normalized = label.strip()
    if not normalized:
        raise ValueError("Label cannot be empty")
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
    Format data for CSV export with the specific "Diagnosis" header layout.
    
    Args:
        data: List of dictionaries containing tree data
        
    Returns:
        str: CSV-formatted string with proper headers
    """
    if not data:
        return ""
    
    # Define the canonical headers
    headers = ["Diagnosis", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5"]
    
    # Create CSV output
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(headers)
    
    # Write data rows
    for row in data:
        csv_row = []
        for header in headers:
            if header == "Diagnosis":
                # Map "Diagnosis" to "Vital Measurement" or root value
                csv_row.append(row.get("Vital Measurement", row.get("Diagnosis", "")))
            else:
                csv_row.append(row.get(header, ""))
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
