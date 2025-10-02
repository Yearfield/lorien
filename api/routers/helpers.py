"""
Helper functions for import/export operations.
"""
from typing import List, Dict, Any
from Engines.EngineLongBow.ingest import read_file

def parse_csv_or_xlsx(file_content: bytes, filename: str) -> List[Dict[str, Any]]:
    """
    Parse CSV or XLSX file content and return as list of dictionaries.
    
    Args:
        file_content: Raw file bytes
        filename: Original filename for format detection
        
    Returns:
        List of dictionaries with column headers as keys
    """
    # Use existing read_file function to get rows as list of lists
    rows = read_file(file_content, filename)
    
    if not rows:
        return []
    
    # First row is header
    header = rows[0]
    
    # Convert remaining rows to dictionaries
    result = []
    for row in rows[1:]:
        # Pad row to match header length
        padded_row = row + [''] * (len(header) - len(row))
        row_dict = dict(zip(header, padded_row))
        result.append(row_dict)
    
    return result
