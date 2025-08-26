"""
Core validation rules for decision tree invariants.
"""

from typing import List, Dict, Any, Tuple, Optional
from collections import Counter, defaultdict
import pandas as pd

from .models import TreeValidationResult, Node, Parent


# Canonical column names (NON-NEGOTIABLE)
ROOT_COL = "Vital Measurement"
LEVEL_COLS = ["Node 1", "Node 2", "Node 3", "Node 4", "Node 5"]
MAX_LEVELS = 5
MAX_CHILDREN_PER_PARENT = 5
ROOT_PARENT_LABEL = "<ROOT>"


def validate_canonical_headers(df: pd.DataFrame) -> bool:
    """Validate that DataFrame has the required canonical headers."""
    required_cols = [ROOT_COL] + LEVEL_COLS + ["Diagnostic Triage", "Actions"]
    return all(col in df.columns for col in required_cols)


def find_parents_with_too_few_children(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Find parents that have fewer than 5 children.
    
    Args:
        df: DataFrame with decision tree data
        
    Returns:
        List of violations with parent info and child count
    """
    violations = []
    
    if not validate_canonical_headers(df):
        return violations
    
    # Level 1: Check ROOT (Vital Measurement) has 5 children in Node 1
    node1_values = df[LEVEL_COLS[0]].dropna().astype(str).str.strip()
    node1_values = node1_values[node1_values != ""]
    unique_node1 = set(node1_values)
    
    if len(unique_node1) < MAX_CHILDREN_PER_PARENT:
        violations.append({
            "level": 1,
            "parent_label": ROOT_PARENT_LABEL,
            "parent_path": ROOT_PARENT_LABEL,
            "current_children": list(unique_node1),
            "child_count": len(unique_node1),
            "expected_count": MAX_CHILDREN_PER_PARENT,
            "type": "too_few_children"
        })
    
    # Levels 2-5: Check each parent has 5 children
    for level in range(2, MAX_LEVELS + 1):
        parent_col = LEVEL_COLS[level - 2]  # Parent is at level-1
        child_col = LEVEL_COLS[level - 1]   # Children are at level
        
        # Group by parent values
        parent_child_groups = df.groupby(parent_col)[child_col].apply(
            lambda x: set(x.dropna().astype(str).str.strip()) - {""}
        )
        
        for parent_val, children_set in parent_child_groups.items():
            if parent_val and str(parent_val).strip():
                child_count = len(children_set)
                if child_count < MAX_CHILDREN_PER_PARENT:
                    # Build parent path
                    parent_path = _build_parent_path(df, level, parent_val)
                    
                    violations.append({
                        "level": level,
                        "parent_label": str(parent_val).strip(),
                        "parent_path": parent_path,
                        "current_children": list(children_set),
                        "child_count": child_count,
                        "expected_count": MAX_CHILDREN_PER_PARENT,
                        "type": "too_few_children"
                    })
    
    return violations


def find_parents_with_too_many_children(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Find parents that have more than 5 children.
    
    Args:
        df: DataFrame with decision tree data
        
    Returns:
        List of violations with parent info and child count
    """
    violations = []
    
    if not validate_canonical_headers(df):
        return violations
    
    # Level 1: Check ROOT (Vital Measurement) has <= 5 children in Node 1
    node1_values = df[LEVEL_COLS[0]].dropna().astype(str).str.strip()
    node1_values = node1_values[node1_values != ""]
    unique_node1 = set(node1_values)
    
    if len(unique_node1) > MAX_CHILDREN_PER_PARENT:
        violations.append({
            "level": 1,
            "parent_label": ROOT_PARENT_LABEL,
            "parent_path": ROOT_PARENT_LABEL,
            "current_children": list(unique_node1),
            "child_count": len(unique_node1),
            "expected_count": MAX_CHILDREN_PER_PARENT,
            "type": "too_many_children"
        })
    
    # Levels 2-5: Check each parent has <= 5 children
    for level in range(2, MAX_LEVELS + 1):
        parent_col = LEVEL_COLS[level - 2]  # Parent is at level-1
        child_col = LEVEL_COLS[level - 1]   # Children are at level
        
        # Group by parent values
        parent_child_groups = df.groupby(parent_col)[child_col].apply(
            lambda x: set(x.dropna().astype(str).str.strip()) - {""}
        )
        
        for parent_val, children_set in parent_child_groups.items():
            if parent_val and str(parent_val).strip():
                child_count = len(children_set)
                if child_count > MAX_CHILDREN_PER_PARENT:
                    # Build parent path
                    parent_path = _build_parent_path(df, level, parent_val)
                    
                    violations.append({
                        "level": level,
                        "parent_label": str(parent_val).strip(),
                        "parent_path": parent_path,
                        "current_children": list(children_set),
                        "child_count": child_count,
                        "expected_count": MAX_CHILDREN_PER_PARENT,
                        "type": "too_many_children"
                    })
    
    return violations


def find_mismatched_children_across_duplicates(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Find cases where the same parent label has different child sets across different paths.
    
    Args:
        df: DataFrame with decision tree data
        
    Returns:
        List of mismatches with parent info and variant child sets
    """
    mismatches = []
    
    if not validate_canonical_headers(df):
        return mismatches
    
    # Levels 2-5: Check for mismatched children across different parent paths
    for level in range(2, MAX_LEVELS + 1):
        parent_col = LEVEL_COLS[level - 2]  # Parent is at level-1
        child_col = LEVEL_COLS[level - 1]   # Children are at level
        
        # Group by parent values and collect all child sets
        parent_variants = defaultdict(list)
        
        for _, row in df.iterrows():
            parent_val = str(row[parent_col]).strip()
            child_val = str(row[child_col]).strip()
            
            if parent_val and child_val and parent_val != "" and child_val != "":
                # Build parent path for this row
                parent_path = _build_parent_path(df, level, parent_val, row)
                parent_variants[parent_val].append({
                    "parent_path": parent_path,
                    "children": [child_val]
                })
        
        # Check for mismatches within each parent label
        for parent_label, variants in parent_variants.items():
            # Collect all unique children for this parent label
            all_children = set()
            for variant in variants:
                all_children.update(variant["children"])
            
            # Check if all variants have the same children
            variant_children_sets = [set(v["children"]) for v in variants]
            if len(set(map(tuple, variant_children_sets))) > 1:
                mismatches.append({
                    "level": level,
                    "parent_label": parent_label,
                    "variants": variants,
                    "all_children": list(all_children),
                    "type": "mismatched_children"
                })
    
    return mismatches


def enforce_five_children(parent_id: int, df: pd.DataFrame, level: int, 
                         parent_label: str, new_children: List[str]) -> pd.DataFrame:
    """
    Enforce exactly 5 children for a parent, auto-filling placeholders and cascading to depth 5.
    
    Args:
        parent_id: ID of the parent to enforce
        df: DataFrame with decision tree data
        level: Level where children will be set
        parent_label: Label of the parent
        new_children: List of children to set (will be normalized to exactly 5)
        
    Returns:
        Updated DataFrame with enforced 5-children rule
    """
    if not validate_canonical_headers(df):
        return df
    
    # Normalize children to exactly 5
    normalized_children = _normalize_to_five_children(new_children)
    
    # Apply the 5-children set
    updated_df = df.copy()
    
    if level == 1:
        # Level 1: Update Node 1 column for all rows
        updated_df[LEVEL_COLS[0]] = ""
        for i, child in enumerate(normalized_children):
            if i == 0:
                # First child goes in existing rows
                updated_df.loc[updated_df[ROOT_COL].notna(), LEVEL_COLS[0]] = child
            else:
                # Additional children get new rows
                new_rows = []
                for _, row in updated_df[updated_df[ROOT_COL].notna()].iterrows():
                    new_row = row.copy()
                    new_row[LEVEL_COLS[0]] = child
                    # Clear deeper columns
                    for col in LEVEL_COLS[1:] + ["Diagnostic Triage", "Actions"]:
                        new_row[col] = ""
                    new_rows.append(new_row)
                
                if new_rows:
                    new_df = pd.DataFrame(new_rows)
                    updated_df = pd.concat([updated_df, new_df], ignore_index=True)
    else:
        # Levels 2-5: Update specific parent paths
        parent_col = LEVEL_COLS[level - 2]
        child_col = LEVEL_COLS[level - 1]
        
        # Find rows with this parent
        parent_mask = updated_df[parent_col] == parent_label
        
        if parent_mask.any():
            # Clear existing children at this level
            updated_df.loc[parent_mask, child_col] = ""
            
            # Apply first child to existing rows
            updated_df.loc[parent_mask, child_col] = normalized_children[0]
            
            # Add new rows for additional children
            for child in normalized_children[1:]:
                new_rows = []
                for _, row in updated_df[parent_mask].iterrows():
                    new_row = row.copy()
                    new_row[child_col] = child
                    # Clear deeper columns
                    for col in LEVEL_COLS[level:] + ["Diagnostic Triage", "Actions"]:
                        new_row[col] = ""
                    new_rows.append(new_row)
                
                if new_rows:
                    new_df = pd.DataFrame(new_rows)
                    updated_df = pd.concat([updated_df, new_df], ignore_index=True)
    
    return updated_df


def validate_tree_structure(df: pd.DataFrame) -> TreeValidationResult:
    """
    Comprehensive validation of the decision tree structure.
    
    Args:
        df: DataFrame with decision tree data
        
    Returns:
        TreeValidationResult with all violations and summary
    """
    violations = []
    
    # Check canonical headers
    if not validate_canonical_headers(df):
        violations.append({
            "type": "invalid_headers",
            "message": "DataFrame missing required canonical columns",
            "required": [ROOT_COL] + LEVEL_COLS + ["Diagnostic Triage", "Actions"]
        })
        return TreeValidationResult(
            is_valid=False,
            violations=violations,
            summary={"total_violations": len(violations)}
        )
    
    # Check for too few children
    too_few = find_parents_with_too_few_children(df)
    violations.extend(too_few)
    
    # Check for too many children
    too_many = find_parents_with_too_many_children(df)
    violations.extend(too_many)
    
    # Check for mismatched children
    mismatched = find_mismatched_children_across_duplicates(df)
    violations.extend(mismatched)
    
    # Build summary
    summary = {
        "total_violations": len(violations),
        "too_few_children": len(too_few),
        "too_many_children": len(too_many),
        "mismatched_children": len(mismatched),
        "is_valid": len(violations) == 0
    }
    
    return TreeValidationResult(
        is_valid=len(violations) == 0,
        violations=violations,
        summary=summary
    )


def _build_parent_path(df: pd.DataFrame, level: int, parent_label: str, 
                      row: Optional[pd.Series] = None) -> str:
    """Build parent path string for a given level and parent."""
    if level == 1:
        return ROOT_PARENT_LABEL
    
    path_parts = []
    for i in range(level - 1):
        if row is not None:
            path_parts.append(str(row[LEVEL_COLS[i]]).strip())
        else:
            # For general path building, use parent_label
            path_parts.append(parent_label)
    
    return ">".join(path_parts)


def _normalize_to_five_children(children: List[str]) -> List[str]:
    """Normalize children list to exactly 5 items."""
    # Remove empty/None values and normalize
    normalized = [str(c).strip() for c in children if c and str(c).strip()]
    
    # Pad with placeholders if less than 5
    while len(normalized) < MAX_CHILDREN_PER_PARENT:
        normalized.append(f"Option {len(normalized) + 1}")
    
    # Truncate if more than 5
    return normalized[:MAX_CHILDREN_PER_PARENT]
