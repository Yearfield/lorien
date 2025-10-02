"""
Helper functions for import/export operations.
"""
from __future__ import annotations
import csv, io
from typing import List, Dict, Any, Iterable, Tuple
import re
from Engines.EngineLongBow.ingest import read_file

# Canonical header contract
CANONICAL_HEADER = ["D0","D1","D2","D3","D4","D5","D6","Notes"]

def _norm_header(name: str) -> str:
    """
    Normalize header names: strip, remove non-alnum, uppercase.
    '  depth 2 ' -> 'DEPTH2'
    """
    s = re.sub(r"[^A-Za-z0-9]+", "", (name or "").strip()).upper()
    return s

_SYN = {
    "D0":"D0","DEPTH0":"D0","LEVEL0":"D0","L0":"D0","R0":"D0","ROOT":"D0",
    "D1":"D1","DEPTH1":"D1","LEVEL1":"D1","L1":"D1","R1":"D1","CHILD1":"D1",
    "D2":"D2","DEPTH2":"D2","LEVEL2":"D2","L2":"D2","R2":"D2","CHILD2":"D2",
    "D3":"D3","DEPTH3":"D3","LEVEL3":"D3","L3":"D3","R3":"D3","CHILD3":"D3",
    "D4":"D4","DEPTH4":"D4","LEVEL4":"D4","L4":"D4","R4":"D4","CHILD4":"D4",
    "D5":"D5","DEPTH5":"D5","LEVEL5":"D5","L5":"D5","R5":"D5","CHILD5":"D5",
    "D6":"D6","DEPTH6":"D6","LEVEL6":"D6","L6":"D6","R6":"D6","CHILD6":"D6",
    "NOTES":"NOTES","NOTE":"NOTES","NOTESFIELD":"NOTES","COMMENT":"NOTES","COMMENTS":"NOTES",
}

def coerce_rows_to_canonical(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Accepts a list of dict rows (header -> value) and returns rows mapped to canonical
    keys D0..D6, Notes. We map by:
      1) Header synonyms (case-insensitive, space/char-insensitive).
      2) If still missing, fallback by POSITION: first 7 data-bearing columns -> D0..D6,
         and next column (if any) -> Notes.
    """
    if not rows:
        return rows
    raw_headers = list(rows[0].keys())
    # Build mapping using synonyms
    mapped = {}  # raw_header -> canonical or None
    for h in raw_headers:
        key = _norm_header(h)
        mapped[h] = _SYN.get(key)

    have = {v for v in mapped.values() if v}
    need = set(CANONICAL_HEADER)
    missing = [k for k in CANONICAL_HEADER if k not in have]

    if missing:
        # Fallback by position: consume headers left-to-right for D0..D6, then Notes
        # Find candidate headers with data-like names (exclude obvious non-data like EMPTY/UNNAMED)
        usable = [h for h in raw_headers]
        # Assign remaining D0..D6 first
        pos_idx = 0
        for dk in ["D0","D1","D2","D3","D4","D5","D6"]:
            if dk in have:
                continue
            if pos_idx < len(usable):
                mapped[usable[pos_idx]] = dk
                pos_idx += 1
        # If Notes is still missing, assign next position as Notes
        if "Notes" not in have:
            if pos_idx < len(usable):
                mapped[usable[pos_idx]] = "Notes"
                pos_idx += 1

    # Now produce canonical row dicts
    out: List[Dict[str, Any]] = []
    for r in rows:
        canon = {k: "" for k in CANONICAL_HEADER}
        for raw_h, val in r.items():
            ck = mapped.get(raw_h)
            if ck in canon:
                canon[ck] = val if val is not None else ""
        out.append(canon)
    return out

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
