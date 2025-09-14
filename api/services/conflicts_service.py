"""
Conflicts service using the core conflicts engine.
"""
from typing import List, Dict, Any
import sqlite3
import os
import logging
from api.core.conflicts_engine import find_variant_set_conflicts, get_conflict_group_data, norm
from api.repositories.tree_repo import list_parents_with_exact_five, list_children_for_parents


def get_variant_conflicts(conn: sqlite3.Connection, limit: int, offset: int) -> Dict[str, Any]:
    """
    Get conflicts using the variant-sets engine.
    
    Args:
        conn: Database connection
        limit: Maximum number of results
        offset: Offset for pagination
        
    Returns:
        Dict with items, total, limit, offset
    """
    # Get parents with exactly 5 children
    parents = list_parents_with_exact_five(conn, limit, offset)
    
    if not parents:
        return {"items": [], "total": 0, "limit": limit, "offset": offset}
    
    # Get children for these parents
    parent_ids = [p["id"] for p in parents]
    children = list_children_for_parents(conn, parent_ids)
    
    # Use the engine to find conflicts
    conflicts = find_variant_set_conflicts(parents, children)
    
    # Ensure all integer fields are present and non-null
    for conflict in conflicts:
        conflict["parent_id"] = int(conflict.get("parent_id", 0))
        conflict["depth"] = int(conflict.get("depth", 0))
        conflict["child_count"] = int(conflict.get("child_count", 0))
        conflict["duplicate_parents"] = int(conflict.get("duplicate_parents", 0))
        conflict["variant_sets"] = int(conflict.get("variant_sets", 0))
        conflict["label"] = str(conflict.get("label", ""))
        conflict["signatures"] = conflict.get("signatures", {})
    
    out = {
        "items": conflicts,
        "total": len(conflicts),
        "limit": limit,
        "offset": offset
    }

    # Optional diagnostic: dump group -> signatures when enabled
    if os.getenv("LORIEN_DEBUG_CONFLICTS") == "1":
        logger = logging.getLogger(__name__)
        summary = {}
        for c in conflicts:
            key = (int(c.get("depth", 0)), norm(str(c.get("label", ""))))
            sigs = set(c.get("signatures", {}).values())
            if key in summary:
                summary[key].update(sigs)
            else:
                summary[key] = set(sigs)
        for (depth, nlabel), sigs in summary.items():
            logger.debug(f"conflicts group depth={depth} label='{nlabel}' signatures={len(sigs)}")

    return out


def get_conflict_group(conn: sqlite3.Connection, parent_id: int, label: str) -> Dict[str, Any]:
    """
    Get conflict group data using the engine.
    
    Args:
        conn: Database connection
        parent_id: ID of the parent to find group for
        label: Label of the parent to find group for
        
    Returns:
        Group data with all parents and children
    """
    # Get all parents (we need to find the group)
    parents = list_parents_with_exact_five(conn, 1000, 0)  # Large limit to get all
    
    # Get all children for these parents
    parent_ids = [p["id"] for p in parents]
    children = list_children_for_parents(conn, parent_ids)
    
    # Use the engine to get group data
    group_data = get_conflict_group_data(parents, children, parent_id, label)
    
    # Ensure integer fields are non-null
    if "summary" in group_data:
        group_data["summary"]["unique_children"] = int(group_data["summary"].get("unique_children", 0))
        group_data["summary"]["total_children"] = int(group_data["summary"].get("total_children", 0))
    
    return group_data
