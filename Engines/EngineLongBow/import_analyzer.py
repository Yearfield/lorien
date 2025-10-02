from __future__ import annotations
from typing import Dict, List, Tuple, Any, Optional, Set
import sqlite3

# Input rows are already coerced to canonical: keys D0..D6, Notes

def _norm(s: str) -> str:
    return (s or "").strip()

def _chain(row: Dict[str, Any]) -> List[Tuple[int,str]]:
    out = []
    for d in range(7):
        k = f"D{d}"
        v = _norm(row.get(k, ""))
        if v:
            out.append((d, v))
    return out

def _path_key(parts: List[str]) -> str:
    # stable printable path for diagnostics
    return " > ".join(parts)

def analyze_max_children(
    conn: sqlite3.Connection,
    rows: List[Dict[str, Any]],
    mode: str = "append",
) -> List[Dict[str, Any]]:
    """
    Returns a list of violations. Each violation describes one parent path whose
    union of distinct immediate children (existing DB + file) would exceed five.
    In replace mode, 'existing DB' portion is treated as empty.
    """
    # 1) Build file-proposed children grouped by parent path
    proposed: Dict[str, Dict[str, Any]] = {}  # parent_key -> {children:set, rows:list, depth:int}
    for idx, r in enumerate(rows, start=2):
        chain = _chain(r)
        if not chain:
            continue
        # for each consecutive pair (parent -> child) in the chain, register the child under that parent
        for i in range(len(chain)-1):
            pdepth, plabel = chain[i]
            cdepth, clabel = chain[i+1]
            parent_parts = [lab for (_, lab) in chain[:i+1]]
            parent_key = _path_key(parent_parts)  # e.g., "Root A > cough"
            bucket = proposed.setdefault(parent_key, {"children": set(), "rows": [], "parent_depth": pdepth})
            bucket["children"].add(_norm(clabel).lower())
            bucket["rows"].append(idx)

    # 2) Merge with existing DB children when mode=append
    violations: List[Dict[str, Any]] = []
    for parent_key, info in proposed.items():
        children: Set[str] = set(info["children"])
        pdepth: int = int(info["parent_depth"])

        if mode == "append":
            # Resolve parent node in DB by traversing labels along the path
            labels = [seg.strip() for seg in parent_key.split(" > ")] if parent_key else []
            parent_ids = _resolve_parent_ids(conn, labels, pdepth)
            existing = set()
            for pid in parent_ids:
                for (lab,) in conn.execute(
                    "SELECT LOWER(TRIM(label)) FROM nodes WHERE parent_id=?", (pid,)
                ):
                    if lab: existing.add(lab)
            children |= existing

        if len(children) > 5:
            violations.append({
                "type": "value_error.max_children",
                "parent_path": parent_key,
                "parent_depth": pdepth,
                "unique_children": len(children),
                "children": sorted(children),
                "rows": sorted(set(info["rows"])),
            })
    return violations

def _resolve_parent_ids(conn: sqlite3.Connection, labels: List[str], pdepth: int) -> List[int]:
    """
    Traverse down by depth+label; returns candidate parent IDs at the indicated depth.
    We assume sibling duplicate labels are not present by policy; if they are,
    we include all matches (worst-case union).
    """
    if not labels:
        return []
    # depth 0 roots
    ids = [r[0] for r in conn.execute(
        "SELECT id FROM nodes WHERE depth=0 AND LOWER(TRIM(label))=?", (labels[0].lower(),)
    ).fetchall()]
    depth = 0
    for lab in labels[1:]:
        next_ids = []
        labn = lab.lower()
        for pid in ids:
            for (cid,) in conn.execute(
                "SELECT id FROM nodes WHERE parent_id=? AND LOWER(TRIM(label))=?", (pid, labn)
            ):
                next_ids.append(cid)
        ids = next_ids
        depth += 1
    # sanity: ensure depth matches
    if pdepth != len(labels)-1:
        # fall back: filter by recorded depth
        ids = [r[0] for r in conn.execute(
            "SELECT id FROM nodes WHERE id IN ({}) AND depth=?".format(
                ",".join("?" for _ in ids)
            ), tuple(ids) + (pdepth,)
        ).fetchall()] if ids else []
    return ids
