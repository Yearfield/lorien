"""
Core decision tree engine for business logic operations.
No I/O side effects - pure domain logic.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import pandas as pd

from .models import Node, Parent, Path, RedFlag, Triaging, TreeValidationResult
from .rules import (
    validate_tree_structure, 
    find_parents_with_too_few_children,
    find_parents_with_too_many_children,
    find_mismatched_children_across_duplicates,
    enforce_five_children
)


class DecisionTreeEngine:
    """Core engine for decision tree operations."""
    
    def __init__(self):
        """Initialize the decision tree engine."""
        pass
    
    # Import/Export Support Methods
    
    def find_or_create_root(self, label: str) -> Optional[Node]:
        """
        Find or create a root node with the given label.
        
        Args:
            label: Label for the root node
            
        Returns:
            Node object (existing or newly created)
        """
        # This is a placeholder - in the real implementation, this would
        # interact with the storage layer to find or create nodes
        # For now, return a mock node with a proper ID
        return Node(
            id=1,  # Mock ID for testing
            parent_id=None,
            depth=0,
            slot=0,
            label=label,
            is_leaf=False
        )
    
    def find_or_create_child(self, parent_id: int, slot: int, label: str, depth: int) -> Optional[Node]:
        """
        Find or create a child node with the given parameters.
        
        Args:
            parent_id: ID of the parent node
            slot: Slot number (1-5)
            label: Label for the child node
            depth: Depth of the child node
            
        Returns:
            Node object (existing or newly created)
        """
        # This is a placeholder - in the real implementation, this would
        # interact with the storage layer to find or create nodes
        # For now, return a mock node with a proper ID
        return Node(
            id=parent_id * 10 + slot,  # Mock ID based on parent and slot
            parent_id=parent_id,
            depth=depth,
            slot=slot,
            label=label,
            is_leaf=(depth == 5)
        )
    
    def get_all_roots(self) -> List[Node]:
        """
        Get all root nodes (depth 0).
        
        Returns:
            List of root nodes
        """
        # This is a placeholder - in the real implementation, this would
        # query the storage layer
        # For now, return a mock root node
        return [
            Node(
                id=1,
                parent_id=None,
                depth=0,
                slot=0,
                label="Hypertension",
                is_leaf=False
            )
        ]
    
    def get_children(self, parent_id: int) -> List[Node]:
        """
        Get all children of a parent node.
        
        Args:
            parent_id: ID of the parent node
            
        Returns:
            List of child nodes
        """
        # This is a placeholder - in the real implementation, this would
        # query the storage layer
        # For now, return mock children
        if parent_id == 1:  # Root node
            return [
                Node(
                    id=11,  # parent_id * 10 + slot
                    parent_id=parent_id,
                    depth=1,
                    slot=1,
                    label="Mild",
                    is_leaf=False
                ),
                Node(
                    id=12,
                    parent_id=parent_id,
                    depth=1,
                    slot=2,
                    label="Severe",
                    is_leaf=False
                )
            ]
        elif parent_id == 11:  # Level 1 child
            return [
                Node(
                    id=111,
                    parent_id=parent_id,
                    depth=2,
                    slot=1,
                    label="Controlled",
                    is_leaf=False
                )
            ]
        return []
    
    def get_triage(self, node_id: int) -> Optional[Triaging]:
        """
        Get triage information for a node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            Triaging object if found, None otherwise
        """
        # This is a placeholder - in the real implementation, this would
        # query the storage layer
        # For now, return None (no triage data in mock)
        return None
    
    def create_or_update_triage(self, triage: Triaging) -> bool:
        """
        Create or update triage information for a node.
        
        Args:
            triage: Triaging object to create or update
            
        Returns:
            True if successful, False otherwise
        """
        # This is a placeholder - in the real implementation, this would
        # interact with the storage layer
        # For now, return True
        return True

    # Tree Analysis Methods
    
    def analyze_tree_structure(self, df: pd.DataFrame) -> TreeValidationResult:
        """
        Analyze the decision tree structure for violations.
        
        Args:
            df: DataFrame with decision tree data
            
        Returns:
            TreeValidationResult with all violations and summary
        """
        return validate_tree_structure(df)
    
    def find_violations(self, df: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find all rule violations in the tree.
        
        Args:
            df: DataFrame with decision tree data
            
        Returns:
            Dictionary with violation types as keys and lists of violations as values
        """
        violations = {
            "too_few_children": find_parents_with_too_few_children(df),
            "too_many_children": find_parents_with_too_many_children(df),
            "mismatched_children": find_mismatched_children_across_duplicates(df)
        }
        
        return violations
    
    def get_next_incomplete_parent(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Find the next incomplete parent for the "Skip to next incomplete parent" feature.
        
        Args:
            df: DataFrame with decision tree data
            
        Returns:
            Information about the next incomplete parent, or None if all complete
        """
        violations = find_parents_with_too_few_children(df)
        
        if not violations:
            return None
        
        # Sort by level (ascending) and return the first one
        violations.sort(key=lambda x: x["level"])
        return violations[0]
    
    # Tree Manipulation Methods
    
    def add_child_to_parent(self, df: pd.DataFrame, level: int, parent_label: str, 
                           child_label: str, slot: Optional[int] = None) -> pd.DataFrame:
        """
        Add a child to a parent at a specific level.
        
        Args:
            df: DataFrame with decision tree data
            level: Level where child will be added (1-5)
            parent_label: Label of the parent
            child_label: Label of the child to add
            slot: Specific slot (1-5) for the child. If None, auto-assign.
            
        Returns:
            Updated DataFrame with the new child
        """
        if level < 1 or level > 5:
            raise ValueError("Level must be between 1 and 5")
        
        updated_df = df.copy()
        
        if level == 1:
            # Level 1: Add to Node 1 column
            if slot is None:
                # Find next available slot
                existing_values = set(updated_df["Node 1"].dropna().astype(str).str.strip())
                existing_values = existing_values - {""}
                
                if len(existing_values) >= 5:
                    raise ValueError("Level 1 already has 5 children")
                
                # Add child to existing rows
                updated_df.loc[updated_df["Vital Measurement"].notna(), "Node 1"] = child_label
            else:
                if slot < 1 or slot > 5:
                    raise ValueError("Slot must be between 1 and 5")
                
                # Add child to specific slot (this would require row manipulation)
                # For now, just add to existing rows
                updated_df.loc[updated_df["Vital Measurement"].notna(), "Node 1"] = child_label
        else:
            # Levels 2-5: Add to specific Node column
            parent_col = f"Node {level - 1}"
            child_col = f"Node {level}"
            
            if parent_col not in updated_df.columns or child_col not in updated_df.columns:
                raise ValueError(f"Required columns not found: {parent_col}, {child_col}")
            
            # Find rows with this parent
            parent_mask = updated_df[parent_col] == parent_label
            
            if not parent_mask.any():
                raise ValueError(f"Parent '{parent_label}' not found at level {level}")
            
            if slot is None:
                # Find next available slot
                existing_values = set(updated_df.loc[parent_mask, child_col].dropna().astype(str).str.strip())
                existing_values = existing_values - {""}
                
                if len(existing_values) >= 5:
                    raise ValueError(f"Parent '{parent_label}' already has 5 children")
                
                # Add child to existing rows
                updated_df.loc[parent_mask, child_col] = child_label
            else:
                if slot < 1 or slot > 5:
                    raise ValueError("Slot must be between 1 and 5")
                
                # Add child to specific slot
                updated_df.loc[parent_mask, child_col] = child_label
        
        return updated_df
    
    def enforce_five_children_rule(self, df: pd.DataFrame, level: int, parent_label: str, 
                                 new_children: List[str]) -> pd.DataFrame:
        """
        Enforce exactly 5 children for a parent, auto-filling placeholders.
        
        Args:
            df: DataFrame with decision tree data
            level: Level where children will be set
            parent_label: Label of the parent
            new_children: List of children to set (will be normalized to exactly 5)
            
        Returns:
            Updated DataFrame with enforced 5-children rule
        """
        # Use the rules module function
        return enforce_five_children(0, df, level, parent_label, new_children)
    
    def propagate_changes_to_depth_5(self, df: pd.DataFrame, level: int, 
                                   parent_label: str) -> pd.DataFrame:
        """
        Propagate changes from a parent to ensure all paths are complete to depth 5.
        
        Args:
            df: DataFrame with decision tree data
            level: Level where the parent is located
            parent_label: Label of the parent
            
        Returns:
            Updated DataFrame with propagated changes
        """
        if level >= 5:
            return df  # Already at max depth
        
        updated_df = df.copy()
        
        # For each level from current + 1 to 5, ensure children exist
        for current_level in range(level + 1, 6):
            parent_col = f"Node {current_level - 1}"
            child_col = f"Node {current_level}"
            
            if parent_col not in updated_df.columns or child_col not in updated_df.columns:
                continue
            
            # Find all unique parent values at this level
            parent_values = set(updated_df[parent_col].dropna().astype(str).str.strip())
            parent_values = parent_values - {""}
            
            for parent_val in parent_values:
                # Check if this parent has children
                parent_mask = updated_df[parent_col] == parent_val
                existing_children = set(updated_df.loc[parent_mask, child_col].dropna().astype(str).str.strip())
                existing_children = existing_children - {""}
                
                if len(existing_children) < 5:
                    # Auto-fill with placeholders
                    missing_count = 5 - len(existing_children)
                    placeholders = [f"Option {i+1}" for i in range(missing_count)]
                    
                    # Add placeholders to existing rows
                    for i, placeholder in enumerate(placeholders):
                        if i == 0:
                            # First placeholder goes in existing rows
                            updated_df.loc[parent_mask, child_col] = placeholder
                        else:
                            # Additional placeholders get new rows
                            new_rows = []
                            for _, row in updated_df[parent_mask].iterrows():
                                new_row = row.copy()
                                new_row[child_col] = placeholder
                                # Clear deeper columns
                                for col in [f"Node {j}" for j in range(current_level + 1, 6)] + ["Diagnostic Triage", "Actions"]:
                                    if col in new_row.index:
                                        new_row[col] = ""
                                new_rows.append(new_row)
                            
                            if new_rows:
                                new_df = pd.DataFrame(new_rows)
                                updated_df = pd.concat([updated_df, new_df], ignore_index=True)
        
        return updated_df
    
    # Red Flag Methods
    
    def assign_red_flag(self, df: pd.DataFrame, node_label: str, red_flag_name: str, 
                       level: Optional[int] = None) -> pd.DataFrame:
        """
        Assign a red flag to a node.
        
        Args:
            df: DataFrame with decision tree data
            node_label: Label of the node to flag
            red_flag_name: Name of the red flag
            level: Specific level to search (if None, search all levels)
            
        Returns:
            Updated DataFrame with red flag assignment
        """
        updated_df = df.copy()
        
        # Add red flag column if it doesn't exist
        if "Red Flags" not in updated_df.columns:
            updated_df["Red Flags"] = ""
        
        if level is None:
            # Search all Node columns
            node_cols = ["Node 1", "Node 2", "Node 3", "Node 4", "Node 5"]
        else:
            if level < 1 or level > 5:
                raise ValueError("Level must be between 1 and 5")
            node_cols = [f"Node {level}"]
        
        # Find rows with the specified node label
        for col in node_cols:
            if col in updated_df.columns:
                node_mask = updated_df[col] == node_label
                
                # Update red flags for matching rows
                for idx in updated_df[node_mask].index:
                    current_flags = updated_df.loc[idx, "Red Flags"]
                    if pd.isna(current_flags) or str(current_flags).strip() == "":
                        updated_df.loc[idx, "Red Flags"] = red_flag_name
                    else:
                        # Append to existing flags
                        existing_flags = str(current_flags).strip()
                        if red_flag_name not in existing_flags:
                            updated_df.loc[idx, "Red Flags"] = f"{existing_flags}, {red_flag_name}"
        
        return updated_df
    
    def search_red_flags(self, df: pd.DataFrame, query: str) -> List[Dict[str, Any]]:
        """
        Search for red flags in the tree.
        
        Args:
            df: DataFrame with decision tree data
            query: Search query
            
        Returns:
            List of nodes with matching red flags
        """
        if "Red Flags" not in df.columns:
            return []
        
        results = []
        
        # Search in all Node columns
        node_cols = ["Node 1", "Node 2", "Node 3", "Node 4", "Node 5"]
        
        for col in node_cols:
            if col in df.columns:
                # Find rows where red flags column contains the query
                red_flag_mask = df["Red Flags"].astype(str).str.contains(query, case=False, na=False)
                
                for idx in df[red_flag_mask].index:
                    node_label = df.loc[idx, col]
                    red_flags = df.loc[idx, "Red Flags"]
                    
                    if pd.notna(node_label) and str(node_label).strip():
                        results.append({
                            "level": int(col.split()[-1]),
                            "node_label": str(node_label).strip(),
                            "red_flags": str(red_flags).strip(),
                            "row_index": idx
                        })
        
        return results
    
    # Calculator Export Methods
    
    def export_calculator_csv(self, df: pd.DataFrame, selected_rows: List[int]) -> str:
        """
        Export selected rows to calculator CSV format.
        
        Args:
            df: DataFrame with decision tree data
            selected_rows: List of row indices to export
            
        Returns:
            CSV string in calculator format
        """
        if not selected_rows:
            return ""
        
        # Filter to selected rows
        selected_df = df.iloc[selected_rows].copy()
        
        # Build calculator format
        # Header: Diagnosis (from the selected rows)
        # Rows: Node 1-5 selections with quality/metadata
        
        csv_lines = []
        
        # Add header row
        header = ["Diagnosis"] + [f"Node {i}" for i in range(1, 6)] + ["Quality", "Metadata"]
        csv_lines.append(",".join(header))
        
        # Add data rows
        for _, row in selected_df.iterrows():
            # Build diagnosis from the path
            path_parts = []
            for col in ["Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5"]:
                if col in row.index and pd.notna(row[col]) and str(row[col]).strip():
                    path_parts.append(str(row[col]).strip())
            
            diagnosis = " > ".join(path_parts) if path_parts else "Unknown"
            
            # Get Node 1-5 values
            node_values = []
            for i in range(1, 6):
                col = f"Node {i}"
                if col in row.index and pd.notna(row[col]) and str(row[col]).strip():
                    node_values.append(str(row[col]).strip())
                else:
                    node_values.append("")
            
            # Add quality and metadata (placeholder for now)
            quality = "High"  # Could be calculated based on data completeness
            metadata = f"Row {row.name + 1}"  # Could include more metadata
            
            # Build CSV row
            csv_row = [diagnosis] + node_values + [quality, metadata]
            csv_lines.append(",".join(csv_row))
        
        return "\n".join(csv_lines)
    
    # Utility Methods
    
    def get_tree_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive tree statistics.
        
        Args:
            df: DataFrame with decision tree data
            
        Returns:
            Dictionary with tree statistics
        """
        stats = {}
        
        # Basic counts
        stats["total_rows"] = len(df)
        stats["total_columns"] = len(df.columns)
        
        # Node counts by level
        node_cols = ["Node 1", "Node 2", "Node 3", "Node 4", "Node 5"]
        for i, col in enumerate(node_cols, 1):
            if col in df.columns:
                non_empty = df[col].dropna().astype(str).str.strip()
                non_empty = non_empty[non_empty != ""]
                stats[f"level_{i}_nodes"] = len(non_empty)
                stats[f"level_{i}_unique_nodes"] = len(set(non_empty))
        
        # Root level (Vital Measurement)
        if "Vital Measurement" in df.columns:
            non_empty = df["Vital Measurement"].dropna().astype(str).str.strip()
            non_empty = non_empty[non_empty != ""]
            stats["root_nodes"] = len(non_empty)
            stats["root_unique_nodes"] = len(set(non_empty))
        
        # Red flags
        if "Red Flags" in df.columns:
            red_flag_rows = df["Red Flags"].dropna().astype(str).str.strip()
            red_flag_rows = red_flag_rows[red_flag_rows != ""]
            stats["rows_with_red_flags"] = len(red_flag_rows)
        
        # Validation results
        validation = self.analyze_tree_structure(df)
        stats["validation"] = validation.summary
        
        return stats
    
    def find_orphan_nodes(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Find orphan nodes (nodes without proper parent relationships).
        
        Args:
            df: DataFrame with decision tree data
            
        Returns:
            List of orphan node information
        """
        orphans = []
        
        # Check each level for orphans
        for level in range(2, 6):  # Start from level 2 (level 1 has ROOT as parent)
            parent_col = f"Node {level - 1}"
            child_col = f"Node {level}"
            
            if parent_col not in df.columns or child_col not in df.columns:
                continue
            
            # Find rows where child exists but parent is missing
            child_mask = (df[child_col].notna()) & (df[child_col].astype(str).str.strip() != "")
            parent_mask = (df[parent_col].isna()) | (df[parent_col].astype(str).str.strip() == "")
            
            orphan_mask = child_mask & parent_mask
            
            for idx in df[orphan_mask].index:
                child_label = df.loc[idx, child_col]
                orphans.append({
                    "level": level,
                    "child_label": str(child_label).strip(),
                    "row_index": idx,
                    "issue": "Missing parent"
                })
        
        return orphans
