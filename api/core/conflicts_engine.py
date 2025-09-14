"""
Core conflicts engine for variant-sets detection.

This module provides pure functions for detecting conflicts where duplicate parents
(same normalized label + same depth) have different 5-child label sets.
"""
import unicodedata
from typing import List, Dict, Any, Set, Tuple


def norm(s: str) -> str:
    """
    Normalize a string for consistent comparison.
    
    - Unicode NFKC normalization
    - Trim whitespace and collapse multiple spaces
    - Casefold for case-insensitive comparison
    - Handle None/empty strings
    """
    if s is None:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = " ".join(s.strip().split())  # trim and collapse spaces
    return s.casefold()


def signature(child_labels: List[str]) -> str:
    """
    Create a normalized signature for a set of child labels.
    
    - Normalizes each label
    - Removes empty/none labels
    - Deduplicates
    - Sorts for order independence
    - Joins with '|' separator
    """
    uniq = sorted({norm(x) for x in child_labels if norm(x)})
    return "|".join(uniq)


def find_variant_set_conflicts(parents: List[Dict[str, Any]], children: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Find conflicts where duplicate parents have different 5-child label sets.
    
    Args:
        parents: List of dicts with {id, depth, label}
        children: List of dicts with {parent_id, slot, label}
    
    Returns:
        List of conflict items with variant set information
    """
    # 1) Group children by parent_id, require exactly 5 unique non-empty labels
    children_by_parent = {}
    for child in children:
        parent_id = child["parent_id"]
        if parent_id not in children_by_parent:
            children_by_parent[parent_id] = []
        children_by_parent[parent_id].append(child)
    
    # Filter to parents with exactly 5 children
    valid_parents = []
    for parent in parents:
        parent_id = parent["id"]
        if parent_id in children_by_parent:
            child_labels = [c["label"] for c in children_by_parent[parent_id]]
            # Check for exactly 5 unique non-empty labels
            unique_labels = {norm(label) for label in child_labels if norm(label)}
            if len(unique_labels) == 5:
                valid_parents.append(parent)
    
    # 2) Group parents by (depth, normalized_label)
    parents_by_group = {}
    for parent in valid_parents:
        key = (parent["depth"], norm(parent["label"]))
        if key not in parents_by_group:
            parents_by_group[key] = []
        parents_by_group[key].append(parent)
    
    # 3) Within each group, compute signatures per parent
    conflicts = []
    for (depth, norm_label), group_parents in parents_by_group.items():
        if len(group_parents) < 2:
            continue  # Need at least 2 parents for a conflict
        
        # Compute signatures for each parent in the group
        signatures = {}
        parent_signatures = []
        
        for parent in group_parents:
            parent_id = parent["id"]
            child_labels = [c["label"] for c in children_by_parent[parent_id]]
            sig = signature(child_labels)
            signatures[str(parent_id)] = sig
            parent_signatures.append(sig)
        
        # Check if there are variant sets (different signatures)
        unique_signatures = set(parent_signatures)
        if len(unique_signatures) >= 2:
            # This is a conflict group with variant sets
            for parent in group_parents:
                conflicts.append({
                    "parent_id": parent["id"],
                    "label": parent["label"],
                    "depth": parent["depth"],
                    "child_count": 5,
                    "duplicate_parents": len(group_parents),
                    "variant_sets": len(unique_signatures),
                    "signatures": signatures
                })
    
    return conflicts


def get_conflict_group_data(parents: List[Dict[str, Any]], children: List[Dict[str, Any]], 
                           target_parent_id: int, target_label: str) -> Dict[str, Any]:
    """
    Get conflict group data for a specific parent.
    
    Args:
        parents: List of all parents
        children: List of all children
        target_parent_id: ID of the parent to find group for
        target_label: Label of the parent to find group for
    
    Returns:
        Group data with all parents in the same group and their children
    """
    # Find the target parent
    target_parent = None
    for parent in parents:
        if parent["id"] == target_parent_id and norm(parent["label"]) == norm(target_label):
            target_parent = parent
            break
    
    if not target_parent:
        return {"group": [], "children": [], "summary": {"unique_children": 0, "total_children": 0}}
    
    # Find all parents in the same group (same depth, normalized label)
    group_parents = []
    for parent in parents:
        if (parent["depth"] == target_parent["depth"] and 
            norm(parent["label"]) == norm(target_parent["label"])):
            group_parents.append(parent)
    
    # Get all children for parents in this group
    group_children = []
    for parent in group_parents:
        parent_id = parent["id"]
        for child in children:
            if child["parent_id"] == parent_id:
                group_children.append({
                    "child_id": child.get("id", 0),
                    "from_id": parent_id,
                    "slot": child.get("slot"),
                    "label": child["label"]
                })
    
    # Calculate summary
    unique_children = len({c["label"] for c in group_children})
    
    return {
        "group": [{"id": p["id"]} for p in group_parents],
        "children": group_children,
        "summary": {
            "unique_children": unique_children,
            "total_children": len(group_children)
        }
    }
