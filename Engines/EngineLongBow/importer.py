from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Any
import sqlite3

CANONICAL_HEADER = ["D0","D1","D2","D3","D4","D5","D6","Notes"]

@dataclass
class ImportOptions:
    mode: str = "append"  # "append" | "replace"
    enforce_five: bool = True

def _norm(s: str) -> str:
    return (s or "").strip()

def _find_path_cells(row: Dict[str, Any]) -> List[str]:
    # Extract D0..D6 in order, trimmed
    return [_norm(row.get(h, "")) for h in CANONICAL_HEADER[:7]]

def _first_nonempty_idx(cells: List[str]) -> Optional[int]:
    for i, v in enumerate(cells):
        if v:
            return i
    return None

def _parent_chain(cells: List[str]) -> List[Tuple[int,str]]:
    """
    Returns list of (depth,label) for all non-empty cells in D0..D6.
    For example: ["Root","A","","","",..] -> [(0,"Root"), (1,"A")]
    """
    out = []
    last_label = None
    for d, v in enumerate(cells):
        if v:
            out.append((d, v))
            last_label = v
        else:
            # keep scanning; blanks allowed
            pass
    return out

def import_rows(conn: sqlite3.Connection, rows: List[Dict[str, Any]], opts: ImportOptions) -> Dict[str, Any]:
    """
    Import CSV/XLSX rows with header D0..D6, Notes.
    - Transactional: BEGIN IMMEDIATE ... COMMIT; on failure ROLLBACK.
    - mode=replace -> clears all nodes before importing.
    Returns summary {inserted, updated, roots, parents_touched}
    """
    conn.isolation_level = None
    conn.execute("BEGIN IMMEDIATE")
    try:
        if opts.mode == "replace":
            # wipe all nodes
            conn.execute("DELETE FROM nodes")

        # caches: label -> node id at each depth for current row
        # and parent_id -> {label_norm: slot}
        slot_cache: Dict[int, Dict[str,int]] = {}

        def ensure_root(label: str) -> int:
            labn = label.lower().strip()
            row = conn.execute(
                "SELECT id FROM nodes WHERE depth=0 AND LOWER(TRIM(label))=?",
                (labn,)
            ).fetchone()
            if row:
                return row[0]
            # Insert root: parent_id=NULL, slot=NULL
            cur = conn.execute(
                "INSERT INTO nodes (parent_id, depth, slot, label) VALUES (NULL, 0, NULL, ?)",
                (label,)
            )
            return cur.lastrowid

        def ensure_child(parent_id: int, parent_depth: int, label: str) -> int:
            # depth = parent_depth + 1 must be <= 6
            depth = parent_depth + 1
            if depth > 6:
                raise ValueError(f"max depth exceeded for parent {parent_id}: {label}")
            labn = label.lower().strip()
            row = conn.execute(
                "SELECT id, slot FROM nodes WHERE parent_id=? AND LOWER(TRIM(label))=?",
                (parent_id, labn)
            ).fetchone()
            if row:
                return row[0]
            # compute slot deterministically 1..N (no hard cap)
            if parent_id not in slot_cache:
                # initialize from DB
                slot_cache[parent_id] = {}
                for srow in conn.execute(
                    "SELECT LOWER(TRIM(label)) AS labn, slot FROM nodes WHERE parent_id=? ORDER BY slot",
                    (parent_id,)
                ):
                    if srow[0] and srow[1] is not None:
                        slot_cache[parent_id][srow[0]] = int(srow[1])
            mapping = slot_cache[parent_id]
            if labn in mapping:
                slot = mapping[labn]
            else:
                # next available = 1 + max used (or 1)
                used = [v for v in mapping.values() if isinstance(v, int)]
                slot = (max(used) + 1) if used else 1
                mapping[labn] = slot
            cur = conn.execute(
                "INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?, ?, ?, ?)",
                (parent_id, depth, slot, label)
            )
            return cur.lastrowid

        inserted = 0
        roots_seen = set()
        parents_touched = set()

        for idx, r in enumerate(rows, start=2):  # 1-based header -> data starts at row 2
            cells = _find_path_cells(r)
            chain = _parent_chain(cells)  # [(depth,label), ...]
            if not chain:
                # skip empty line
                continue
            # enforce monotonic depth chain like D0 -> D1 -> D2...
            # tolerate gaps (e.g., D0,D2) by computing depth from position, not count
            node_id = None
            parent_id = None
            parent_depth = -1
            for d, label in chain:
                if d == 0:
                    # root
                    rid = ensure_root(label)
                    roots_seen.add(rid)
                    node_id = rid
                    parent_id = rid
                    parent_depth = 0
                else:
                    # child under last node
                    if parent_id is None:
                        # malformed row (no earlier parent but depth>0)
                        raise RuntimeError(f"value_error.malformed_path: row {idx} has D{d} but no parent")
                    node_id = ensure_child(parent_id, parent_depth, label)
                    parents_touched.add(parent_id)
                    parent_id = node_id
                    parent_depth = d
                inserted += 1  # counter kept simple; can be enhanced to track new vs existing

        conn.execute("COMMIT")
        return {
            "ok": True,
            "inserted": inserted,
            "roots": len(roots_seen),
            "parents_touched": len(parents_touched),
        }
    except Exception as e:
        conn.execute("ROLLBACK")
        raise
