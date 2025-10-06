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


def _clean(s: str) -> str:
    """Trim whitespace but preserve original casing."""
    return (s or "").strip()

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
    rows = conn.execute("SELECT id, depth, label FROM nodes").fetchall()
    grouped: Dict[str, Dict[str, Any]] = {}
    for pid, depth, label in rows:
        cleaned = _clean(label)
        norm_label = _norm(cleaned)
        if not norm_label:
            continue
        bucket = grouped.setdefault(norm_label, {"label": cleaned, "entries": []})
        if not bucket.get("label"):
            bucket["label"] = cleaned
        bucket["entries"].append({"parent_id": pid, "depth": depth})

    results: List[Dict[str, Any]] = []
    for norm_label, data in grouped.items():
        entries = data["entries"]
        if not entries:
            continue

        occurrences: List[Dict[str, Any]] = []
        skipped_occurrences: List[Dict[str, Any]] = []
        union_map: Dict[str, str] = {}
        child_sets: List[set] = []

        for entry in entries:
            pid = entry["parent_id"]
            depth = entry["depth"]
            child_rows = conn.execute(
                "SELECT label FROM nodes WHERE parent_id = ? ORDER BY slot ASC, id ASC",
                (pid,),
            ).fetchall()

            child_map: Dict[str, str] = {}
            ordered_children: List[str] = []
            for (child_label,) in child_rows:
                cleaned_child = _clean(child_label)
                if not cleaned_child:
                    continue
                norm_child = _norm(cleaned_child)
                if norm_child in child_map:
                    continue
                child_map[norm_child] = cleaned_child
                ordered_children.append(cleaned_child)
            depth_value = depth if depth is not None else 0
            base_payload: Dict[str, Any] = {
                "parent_id": pid,
                "depth": depth_value,
                "children": ordered_children,
            }

            if depth_value >= 6:
                skipped_occurrences.append({**base_payload, "reason": "max_depth"})
                continue

            occurrences.append(base_payload)
            child_sets.append(set(child_map.keys()))
            for norm_child, cleaned_child in child_map.items():
                union_map.setdefault(norm_child, cleaned_child)

        if not occurrences:
            continue

        # Determine if there is any divergence between occurrences
        has_diff = False
        if len(child_sets) >= 2:
            baseline = child_sets[0]
            has_diff = any(child_set != baseline for child_set in child_sets[1:])

        union_children = [union_map[key] for key in sorted(union_map.keys())]
        if has_diff or len(union_children) > 5:
            results.append({
                "label": data["label"],
                "occurrences": len(occurrences) + len(skipped_occurrences),
                "union_children": union_children,
                "parents": occurrences,
                "skipped_parents": skipped_occurrences,
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
    selected_pairs = []  # (normalized, cleaned)
    seen = set()
    for s in selected_raw:
        cleaned = _clean(str(s))
        normed = _norm(cleaned)
        if normed and normed not in seen:
            seen.add(normed)
            selected_pairs.append((normed, cleaned))

    selected = [clean for _, clean in selected_pairs]
    selected_norms = {norm for norm, _ in selected_pairs}
    
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
        SELECT id, depth FROM nodes 
        WHERE LOWER(TRIM(label)) = ?
    """, (label,)).fetchall()

    parent_depths: Dict[int, int] = {}
    parent_ids: List[int] = []
    skipped_parents: List[Dict[str, Any]] = []

    for pid, depth in parent_rows:
        depth_value = depth if depth is not None else 0
        parent_depths[pid] = depth_value
        if len(selected) > 0 and depth_value >= 6:
            skipped_parents.append({
                "parent_id": pid,
                "depth": depth_value,
                "reason": "max_depth",
            })
            continue
        parent_ids.append(pid)

    if not parent_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{
                "loc": ["label"],
                "msg": "all parents at max depth; cannot add children beyond D6",
                "type": "value_error.max_depth"
            }]
        )

    parents_diff = []

    # Calculate diffs for each parent
    for pid in parent_ids:
        current_rows = conn.execute("""
            SELECT label 
            FROM nodes 
            WHERE parent_id = ? AND label IS NOT NULL AND TRIM(label) != ''
        """, (pid,)).fetchall()

        current_map: Dict[str, str] = {}
        for (lab,) in current_rows:
            cleaned = _clean(lab)
            normed = _norm(cleaned)
            if normed and normed not in current_map:
                current_map[normed] = cleaned

        to_add = [clean for norm, clean in selected_pairs if norm not in current_map]
        to_remove = [current_map[norm] for norm in current_map if norm not in selected_norms]

        parents_diff.append({
            "parent_id": pid, 
            "removed": to_remove, 
            "added": to_add
        })
    
    if dry_run:
        return {
            "updated_parents": len(parent_ids),
            "children_per_parent": len(selected),
            "parents": parents_diff,
            "skipped_parents": skipped_parents,
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
        "parents": parents_diff,
        "skipped_parents": skipped_parents,
    }
