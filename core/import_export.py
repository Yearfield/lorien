"""
Core import/export logic for decision tree data.
Implements deterministic algorithms for data transformation.
"""

import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import logging

from .constants import (
    CANON_HEADERS, ROOT_DEPTH, MAX_DEPTH, LEAF_DEPTH,
    ROOT_SLOT, MIN_CHILD_SLOT, MAX_CHILD_SLOT,
    STRATEGY_PLACEHOLDER, STRATEGY_PRUNE, PLACEHOLDER_TEXT
)
from .models import Node, Triaging
from .engine import DecisionTreeEngine

logger = logging.getLogger(__name__)

class ImportExportEngine:
    """
    Core engine for importing/exporting decision tree data.
    Implements deterministic algorithms with strict validation.
    """
    
    def __init__(self, tree_engine: DecisionTreeEngine):
        self.tree_engine = tree_engine
        
    def normalize_label(self, label: str) -> str:
        """
        Normalize label for identity comparison.
        
        Args:
            label: Original label text
            
        Returns:
            Normalized label for identity comparison
        """
        if not label:
            return ""
        return label.lower().strip()
    
    def store_label(self, label: str) -> str:
        """
        Store original label for display.
        
        Args:
            label: Original label text
            
        Returns:
            Label ready for storage (trimmed whitespace only)
        """
        if not label:
            return ""
        return label.strip()  # Only trim whitespace, preserve case
    
    def validate_headers(self, headers: List[str]) -> bool:
        """
        Validate that sheet headers match CANON_HEADERS exactly.
        Fail fast if mismatch.
        
        Args:
            headers: List of column headers from the sheet
            
        Returns:
            True if headers match exactly, False otherwise
            
        Raises:
            ValueError: If headers don't match canonical format
        """
        if len(headers) != len(CANON_HEADERS):
            raise ValueError(
                f"Expected {len(CANON_HEADERS)} columns, got {len(headers)}"
            )
        
        for i, (expected, actual) in enumerate(zip(CANON_HEADERS, headers)):
            if expected != actual:
                raise ValueError(
                    f"Column {i}: expected '{expected}', got '{actual}'"
                )
        
        return True
    
    def parse_row_as_path(self, row: pd.Series) -> Tuple[List[str], Optional[str], Optional[str]]:
        """
        Parse a row as a path from root to leaf.
        
        Args:
            row: Pandas Series representing one row of data
            
        Returns:
            Tuple of (node_labels, diagnostic_triage, actions)
            node_labels: List of 6 labels (root + 5 nodes)
            diagnostic_triage: Triage text from leaf
            actions: Actions text from leaf
        """
        # Extract node labels (Vital Measurement + Node 1-5)
        node_labels = []
        for i in range(6):  # 0=root, 1-5=nodes
            if i == 0:
                label = row["Vital Measurement"]
            else:
                label = row[f"Node {i}"]
            
            # Handle NaN/None values and normalize for storage
            if pd.isna(label) or str(label).strip() == "":
                node_labels.append("")
            else:
                node_labels.append(self.store_label(str(label)))
        
        # Extract triage data from leaf
        diagnostic_triage = row.get("Diagnostic Triage", "")
        actions = row.get("Actions", "")
        
        # Handle NaN/None values and normalize for storage
        if pd.isna(diagnostic_triage):
            diagnostic_triage = None
        elif str(diagnostic_triage).strip() == "":
            diagnostic_triage = None
        else:
            diagnostic_triage = self.store_label(str(diagnostic_triage))
            
        if pd.isna(actions):
            actions = None
        elif str(actions).strip() == "":
            actions = None
        else:
            actions = self.store_label(str(actions))
        
        return node_labels, diagnostic_triage, actions
    
    def import_path(self, node_labels: List[str], diagnostic_triage: Optional[str] = None, 
                   actions: Optional[str] = None, strategy: str = STRATEGY_PLACEHOLDER) -> Dict[str, Any]:
        """
        Import a single path into the decision tree.
        
        Args:
            node_labels: List of 6 labels (root + 5 nodes)
            diagnostic_triage: Optional triage text for leaf
            actions: Optional actions text for leaf
            strategy: How to handle missing nodes (placeholder/prune)
            
        Returns:
            Dict with import results and any violations
        """
        result = {
            "path_imported": False,
            "root_created": False,
            "nodes_created": 0,
            "violations": [],
            "missing_slots": []
        }
        
        try:
            # Validate path length
            if len(node_labels) != 6:
                result["violations"].append(f"Invalid path length: {len(node_labels)} (expected 6)")
                return result
            
            # Handle root node (depth 0, slot 0)
            root_label = node_labels[0]
            if not root_label:
                result["violations"].append("Root label cannot be empty")
                return result
            
            # Find or create root node
            root_node = self.tree_engine.find_or_create_root(root_label)
            if not root_node:
                result["violations"].append(f"Failed to create root node: {root_label}")
                return result
            
            if root_node.id is None:  # Newly created
                result["root_created"] = True
            
            # Process child nodes (depth 1-5)
            current_parent = root_node
            for depth in range(1, 6):
                slot = depth  # slot = depth for this structure
                label = node_labels[depth]
                
                if not label:  # Missing node
                    if strategy == STRATEGY_PLACEHOLDER:
                        label = PLACEHOLDER_TEXT
                        result["missing_slots"].append(f"Depth {depth}, Slot {slot}: placeholder created")
                    elif strategy == STRATEGY_PRUNE:
                        result["violations"].append(f"Missing node at depth {depth}, slot {slot}")
                        return result
                    else:  # STRATEGY_PROMPT
                        result["violations"].append(f"Missing node at depth {depth}, slot {slot} - requires user input")
                        return result
                
                # Find or create child node
                child_node = self.tree_engine.find_or_create_child(
                    parent_id=current_parent.id,
                    slot=slot,
                    label=label,
                    depth=depth
                )
                
                if not child_node:
                    result["violations"].append(f"Failed to create child at depth {depth}, slot {slot}")
                    return result
                
                if child_node.id is None:  # Newly created
                    result["nodes_created"] += 1
                
                current_parent = child_node
            
            # Attach triage data to leaf node if provided
            if diagnostic_triage or actions:
                leaf_node = current_parent
                triage = Triaging(
                    node_id=leaf_node.id,
                    diagnostic_triage=diagnostic_triage or "",
                    actions=actions or ""
                )
                self.tree_engine.create_or_update_triage(triage)
            
            result["path_imported"] = True
            return result
            
        except Exception as e:
            result["violations"].append(f"Import error: {str(e)}")
            logger.error(f"Error importing path: {e}")
            return result
    
    def import_dataframe(self, df: pd.DataFrame, strategy: str = STRATEGY_PLACEHOLDER) -> Dict[str, Any]:
        """
        Import a DataFrame into the decision tree.
        
        Args:
            df: DataFrame with canonical headers
            strategy: How to handle missing nodes
            
        Returns:
            Dict with import summary
        """
        # Validate headers first
        try:
            self.validate_headers(list(df.columns))
        except ValueError as e:
            return {
                "success": False,
                "error": f"Header validation failed: {str(e)}",
                "rows_processed": 0,
                "paths_imported": 0,
                "violations": [str(e)]
            }
        
        results = {
            "success": True,
            "rows_processed": len(df),
            "paths_imported": 0,
            "total_violations": 0,
            "violations": [],
            "missing_slots_created": 0
        }
        
        for idx, row in df.iterrows():
            try:
                # Parse row as path
                node_labels, diagnostic_triage, actions = self.parse_row_as_path(row)
                
                # Import the path
                path_result = self.import_path(
                    node_labels, diagnostic_triage, actions, strategy
                )
                
                if path_result["path_imported"]:
                    results["paths_imported"] += 1
                    results["missing_slots_created"] += len(path_result["missing_slots"])
                else:
                    results["total_violations"] += len(path_result["violations"])
                    results["violations"].extend([
                        f"Row {idx + 1}: {v}" for v in path_result["violations"]
                    ])
                    
            except Exception as e:
                results["total_violations"] += 1
                results["violations"].append(f"Row {idx + 1}: Import error - {str(e)}")
                logger.error(f"Error processing row {idx + 1}: {e}")
        
        return results
    
    def export_paths(self) -> List[Dict[str, str]]:
        """
        Export all complete root→leaf paths.
        Never shifts children below parent; never recomputes slot indices.
        
        Returns:
            List of dictionaries, each representing one row with canonical headers
        """
        paths = []
        
        try:
            # Get all root nodes
            root_nodes = self.tree_engine.get_all_roots()
            
            for root in root_nodes:
                # Walk each complete path from root to leaf
                path_data = self._walk_path_to_leaf(root)
                if path_data:
                    paths.append(path_data)
                    
        except Exception as e:
            logger.error(f"Error exporting paths: {e}")
            raise
        
        return paths
    
    def _walk_path_to_leaf(self, root_node: Node) -> Optional[Dict[str, str]]:
        """
        Walk a single path from root to leaf.
        
        Args:
            root_node: The root node to start from
            
        Returns:
            Dict with canonical headers, or None if path is incomplete
        """
        try:
            path_data = {
                "Vital Measurement": root_node.label,
                "Node 1": "",
                "Node 2": "",
                "Node 3": "",
                "Node 4": "",
                "Node 5": "",
                "Diagnostic Triage": "",
                "Actions": ""
            }
            
            current_node = root_node
            current_depth = 0
            
            # Walk down the path, one level at a time
            while current_depth < MAX_DEPTH and current_node:
                # Find child at next depth
                next_depth = current_depth + 1
                next_slot = next_depth
                
                children = self.tree_engine.get_children(current_node.id)
                child = next((c for c in children if c.slot == next_slot), None)
                
                if not child:
                    # Incomplete path - return None
                    return None
                
                # Add child to path data
                path_data[f"Node {next_depth}"] = child.label
                current_node = child
                current_depth = next_depth
            
            # If we reached a leaf, get triage data
            if current_depth == LEAF_DEPTH and current_node:
                triage = self.tree_engine.get_triage(current_node.id)
                if triage:
                    path_data["Diagnostic Triage"] = triage.diagnostic_triage
                    path_data["Actions"] = triage.actions
            
            # Only return complete paths
            if current_depth == LEAF_DEPTH:
                return path_data
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error walking path from root {root_node.id}: {e}")
            return None
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """
        Export all paths to a DataFrame with canonical headers.
        
        Returns:
            DataFrame with exact canonical column structure
        """
        paths = self.export_paths()
        
        if not paths:
            # Return empty DataFrame with correct headers
            return pd.DataFrame(columns=CANON_HEADERS)
        
        # Create DataFrame from paths
        df = pd.DataFrame(paths)
        
        # Ensure columns are in exact canonical order
        df = df[CANON_HEADERS]
        
        return df
