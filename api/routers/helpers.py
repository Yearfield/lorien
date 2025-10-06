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
    "D0":"D0","DEPTH0":"D0","LEVEL0":"D0","L0":"D0","R0":"D0","ROOT":"D0","VITALMEASUREMENT":"D0",
    "D1":"D1","DEPTH1":"D1","LEVEL1":"D1","L1":"D1","R1":"D1","CHILD1":"D1","NODE1":"D1",
    "D2":"D2","DEPTH2":"D2","LEVEL2":"D2","L2":"D2","R2":"D2","CHILD2":"D2","NODE2":"D2",
    "D3":"D3","DEPTH3":"D3","LEVEL3":"D3","L3":"D3","R3":"D3","CHILD3":"D3","NODE3":"D3",
    "D4":"D4","DEPTH4":"D4","LEVEL4":"D4","L4":"D4","R4":"D4","CHILD4":"D4","NODE4":"D4",
    "D5":"D5","DEPTH5":"D5","LEVEL5":"D5","L5":"D5","R5":"D5","CHILD5":"D5","NODE5":"D5",
    "D6":"D6","DEPTH6":"D6","LEVEL6":"D6","L6":"D6","R6":"D6","CHILD6":"D6","NODE6":"D6","DIAGNOSTICTRIAGE":"D6","DIAGTRIAGE":"D6",
    # Map all note-like headers to canonical 'Notes' (proper case)
    "NOTES":"Notes","NOTE":"Notes","NOTESFIELD":"Notes","COMMENT":"Notes","COMMENTS":"Notes","ACTIONS":"Notes","ACTION":"Notes",
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
        # Fallback by position: assign only from headers that did not map via synonyms
        usable = [h for h in raw_headers if not mapped.get(h)]
        # Assign remaining D0..D6 first
        pos_idx = 0
        for dk in ["D0","D1","D2","D3","D4","D5","D6"]:
            if dk in have:
                continue
            if pos_idx < len(usable):
                mapped[usable[pos_idx]] = dk
                have.add(dk)
                pos_idx += 1
        # If Notes is still missing, assign next available unmapped header as Notes
        if "Notes" not in have and pos_idx < len(usable):
            mapped[usable[pos_idx]] = "Notes"
            have.add("Notes")
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

def parse_csv_or_xlsx(file_content: bytes, filename: str) -> Tuple[List[List[str]], List[Dict[str, Any]]]:
    """
    Parse CSV or XLSX file content and return both raw rows and header-mapped dictionaries.
    
    Args:
        file_content: Raw file bytes
        filename: Original filename for format detection
        
    Returns:
        Tuple of (raw_rows, list of dictionaries with column headers as keys)
    """
    rows = read_file(file_content, filename)

    if not rows:
        return [], []

    header = rows[0]

    mapped: List[Dict[str, Any]] = []
    for row in rows[1:]:
        padded_row = row + [''] * (len(header) - len(row))
        mapped.append(dict(zip(header, padded_row)))

    return rows, mapped
