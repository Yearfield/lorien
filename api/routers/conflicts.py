"""
Conflicts router for detecting and resolving tree conflicts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
import sqlite3
from typing import List, Dict, Any
from ..dependencies import get_db_connection

router = APIRouter(tags=["conflicts"])

def _norm(s: str) -> str:
    """Normalize string: trim whitespace and convert to lowercase."""
    return (s or "").strip().lower()

@router.get("/conflicts/scan")
def scan_conflicts(conn: sqlite3.Connection = Depends(get_db_connection)) -> List[Dict[str, Any]]:
    """
    Group conflicts by normalized label ONLY (ignore depth). Each conflict entry appears once per label,
    with all occurrences across all depths included in `parents[]` (each with its depth).
    A label is a conflict if either:
      - it has >=2 occurrences AND their child sets differ, OR
      - the union of all immediate child labels across occurrences is > 5.
    """
    # Load all parents (id, depth, label)
    rows = conn.execute("SELECT id, depth, LOWER(TRIM(label)) AS parent_label FROM nodes").fetchall()
    by_label: Dict[str, List[Dict[str, int]]] = {}
    for pid, depth, plab in rows:
        if not plab:
            continue
        by_label.setdefault(plab, []).append({"parent_id": pid, "depth": depth})

    results: List[Dict[str, Any]] = []
    for plab, entries in by_label.items():
        if not entries:
            continue
        occ = []
        union = set()
        for e in entries:
            pid = e["parent_id"]
            depth = e["depth"]
            kids = conn.execute(
                "SELECT LOWER(TRIM(label)) FROM nodes WHERE parent_id=?", (pid,)
            ).fetchall()
            childset = sorted({r[0] for r in kids if r[0]})
            if childset:
                union.update(childset)
            occ.append({"parent_id": pid, "depth": depth, "children": childset})

        # Non-conflict quick exit
        if len(occ) <= 1 and len(union) <= 5:
            continue

        # Detect any difference across occurrences
        diff = False
        if len(occ) >= 2:
            s0 = set(occ[0]["children"])
            for o in occ[1:]:
                if set(o["children"]) != s0:
                    diff = True
                    break
        union_children = sorted(list(union))
        if diff or len(union_children) > 5:
            results.append({
                "label": plab,
                "occurrences": len(occ),
                "union_children": union_children,
                "parents": occ,  # each has parent_id, depth, children[]
            })
    # Sort by label for deterministic UI
    results.sort(key=lambda x: x["label"])
    return results

@router.post("/conflicts/resolve")
def resolve_conflict(
    payload: Dict[str, Any], 
    conn: sqlite3.Connection = Depends(get_db_connection)
) -> Dict[str, Any]:
    """
    Apply the selected children to all parents with the given label across ALL depths.
    'depth' in the payload is accepted but ignored for backward compatibility.
    """
    # depth is accepted but not used anymore
    _ = payload.get("depth", None)
    label = _norm(str(payload.get("label", "")))
    selected_raw = payload.get("selected_children", [])
    
    # Normalize and dedupe selected children while preserving order
    selected = []
    seen = set()
    for s in selected_raw:
        normalized = _norm(str(s))
        if normalized and normalized not in seen:
            seen.add(normalized)
            selected.append(normalized)
    
    # Enforce ≤5 children limit
    if len(selected) > 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{
                "loc": ["selected_children"],
                "msg": f"too many children: {len(selected)}>5",
                "type": "value_error.max_children"
            }]
        )
    
    dry_run = bool(payload.get("dry_run", False))
    
    # All parents across ALL depths matching the label
    parent_rows = conn.execute("""
        SELECT id FROM nodes 
        WHERE LOWER(TRIM(label)) = ?
    """, (label,)).fetchall()
    
    parent_ids = [r[0] for r in parent_rows]
    
    # Pre-read parent depths for max-depth guard
    parent_depths = {}
    for pid in parent_ids:
        depth_row = conn.execute("SELECT depth FROM nodes WHERE id = ?", (pid,)).fetchone()
        parent_depths[pid] = depth_row[0] if depth_row else None
    
    # Check if any parent is at max depth (D6) and would need D7 children
    for pid in parent_ids:
        pdepth = parent_depths.get(pid)
        if pdepth is not None and pdepth >= 6 and len(selected) > 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[{
                    "loc": ["label"],
                    "msg": "parent at max depth; cannot add children beyond D6",
                    "type": "value_error.max_depth"
                }]
            )
    
    parents_diff = []
    
    # Calculate diffs for each parent
    for pid in parent_ids:
        current_rows = conn.execute("""
            SELECT LOWER(TRIM(label)) 
            FROM nodes 
            WHERE parent_id = ? AND label IS NOT NULL AND TRIM(label) != ''
        """, (pid,)).fetchall()
        
        current_children = sorted({r[0] for r in current_rows if r[0]})
        to_add = [s for s in selected if s not in current_children]
        to_remove = [s for s in current_children if s not in selected]
        
        parents_diff.append({
            "parent_id": pid, 
            "removed": to_remove, 
            "added": to_add
        })
    
    if dry_run:
        return {
            "updated_parents": len(parent_ids),
            "children_per_parent": len(selected),
            "parents": parents_diff
        }
    
    # Apply changes transactionally
    conn.isolation_level = None
    conn.execute("BEGIN IMMEDIATE")
    try:
        for pid in parent_ids:
            # Delete existing children
            conn.execute("DELETE FROM nodes WHERE parent_id = ?", (pid,))
            
            # Insert new children at depth+1 with sequential slots
            # Get the parent's depth first
            parent_depth_row = conn.execute("SELECT depth FROM nodes WHERE id = ?", (pid,)).fetchone()
            parent_depth = parent_depth_row[0] if parent_depth_row else 0
            child_depth = parent_depth + 1
            
            # Additional guard: ensure we don't exceed max depth
            if child_depth > 6:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=[{
                        "loc": ["label"],
                        "msg": "would exceed max depth D6",
                        "type": "value_error.max_depth"
                    }]
                )
            
            for i, child_label in enumerate(selected, start=1):
                conn.execute("""
                    INSERT INTO nodes (parent_id, depth, slot, label) 
                    VALUES (?, ?, ?, ?)
                """, (pid, child_depth, i, child_label))
        
        conn.execute("COMMIT")
    except Exception as e:
        conn.execute("ROLLBACK")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve conflict: {str(e)}"
        )
    
    return {
        "updated_parents": len(parent_ids),
        "children_per_parent": len(selected),
        "parents": parents_diff
    }
