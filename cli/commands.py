"""
CLI command implementations for decision tree operations.
"""

import sys
import logging
from pathlib import Path
from typing import Optional
import pandas as pd

from core.constants import (
    EXIT_SUCCESS, EXIT_VALIDATION_ERROR, EXIT_IMPORT_ERROR, 
    EXIT_EXPORT_ERROR, EXIT_SYSTEM_ERROR, CANON_HEADERS
)


logger = logging.getLogger(__name__)

def validate_tree(repo, exit_on_violations: bool = False) -> int:
    """
    Validate tree structure and print counts.
    
    Args:
        import_export_engine: Import/export engine instance
        exit_on_violations: Whether to exit with error code if violations found
        
    Returns:
        Exit code
    """
    try:
        print("🔍 Validating decision tree structure...")
        
        # Get tree statistics from the repository
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            # Count total nodes
            cursor.execute("SELECT COUNT(*) FROM nodes")
            total_nodes = cursor.fetchone()[0]
            
            # Count leaf nodes (depth 5)
            cursor.execute("SELECT COUNT(*) FROM nodes WHERE depth = 5")
            leaf_nodes = cursor.fetchone()[0]
            
            # Count root nodes (depth 0)
            cursor.execute("SELECT COUNT(*) FROM nodes WHERE depth = 0")
            root_nodes = cursor.fetchone()[0]
            
            # Count complete paths (using the view)
            cursor.execute("SELECT COUNT(*) FROM v_paths_complete")
            complete_paths = cursor.fetchone()[0]
            
            # Count incomplete parents
            cursor.execute("SELECT COUNT(*) FROM v_next_incomplete_parent")
            incomplete_parents = cursor.fetchone()[0]
        
        stats = {
            "total_nodes": total_nodes,
            "root_nodes": root_nodes,
            "leaf_nodes": leaf_nodes,
            "complete_paths": complete_paths,
            "incomplete_parents": incomplete_parents
        }
        
        print(f"📊 Tree Statistics:")
        print(f"   Total nodes: {stats['total_nodes']}")
        print(f"   Root nodes: {stats['root_nodes']}")
        print(f"   Leaf nodes: {stats['leaf_nodes']}")
        print(f"   Complete paths: {stats['complete_paths']}")
        print(f"   Incomplete parents: {stats['incomplete_parents']}")
        
        if stats['incomplete_parents'] > 0:
            print(f"⚠️  Found {stats['incomplete_parents']} incomplete parents")
            if exit_on_violations:
                print("❌ Validation failed - incomplete parents found")
                return EXIT_VALIDATION_ERROR
            else:
                print("⚠️  Validation completed with incomplete parents (non-fatal)")
        else:
            print("✅ Validation passed - all parents are complete")
        
        return EXIT_SUCCESS
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        print(f"❌ Validation error: {e}")
        return EXIT_VALIDATION_ERROR

def import_excel(repo, file_path: str, strategy: str) -> int:
    """
    Import decision tree from Excel file.
    
    Args:
        import_export_engine: Import/export engine instance
        file_path: Path to Excel file
        strategy: Strategy for handling missing nodes
        
    Returns:
        Exit code
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return EXIT_IMPORT_ERROR
        
        if not file_path.suffix.lower() in ['.xlsx', '.xls']:
            print(f"❌ Invalid file extension: {file_path.suffix}")
            return EXIT_IMPORT_ERROR
        
        print(f"📥 Importing from Excel: {file_path}")
        print(f"🔧 Strategy: {strategy}")
        
        # Read Excel file
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            print(f"❌ Failed to read Excel file: {e}")
            return EXIT_IMPORT_ERROR
        
        print(f"📊 Read {len(df)} rows, {len(df.columns)} columns")
        
        # Validate headers
        try:
            # Validate headers manually
            if len(df.columns) != len(CANON_HEADERS):
                raise ValueError(f"Expected {len(CANON_HEADERS)} columns, got {len(df.columns)}")
            
            for i, (expected, actual) in enumerate(zip(CANON_HEADERS, df.columns)):
                if expected != actual:
                    raise ValueError(f"Column {i}: expected '{expected}', got '{actual}'")
            
            print("✅ Headers validated successfully")
        except ValueError as e:
            print(f"❌ Header validation failed: {e}")
            print(f"   Expected: {CANON_HEADERS}")
            print(f"   Got: {list(df.columns)}")
            return EXIT_IMPORT_ERROR
        
        # Import data using repository
        print("🔄 Importing data...")
        
        rows_processed = 0
        paths_imported = 0
        
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                try:
                    # Extract data from row
                    vital_measurement = str(row["Vital Measurement"]).strip()
                    node_1 = str(row["Node 1"]).strip()
                    node_2 = str(row["Node 2"]).strip()
                    node_3 = str(row["Node 3"]).strip()
                    node_4 = str(row["Node 4"]).strip()
                    node_5 = str(row["Node 5"]).strip()
                    diagnostic_triage = str(row.get("Diagnostic Triage", "")).strip()
                    actions = str(row.get("Actions", "")).strip()
                    
                    # Create root node (Vital Measurement)
                    cursor.execute("""
                        INSERT INTO nodes (parent_id, depth, slot, label, is_leaf, created_at, updated_at)
                        VALUES (NULL, 0, 0, ?, 0, strftime('%Y-%m-%dT%H:%M:%fZ','now'), strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                    """, (vital_measurement,))
                    root_id = cursor.lastrowid
                    
                    # Create child nodes
                    nodes = [node_1, node_2, node_3, node_4, node_5]
                    parent_id = root_id
                    
                    for depth, (node_label, slot) in enumerate(zip(nodes, range(1, 6)), 1):
                        if node_label:  # Only create if label is not empty
                            cursor.execute("""
                                INSERT INTO nodes (parent_id, depth, slot, label, is_leaf, created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ','now'), strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                            """, (parent_id, depth, slot, node_label, depth == 5))
                            parent_id = cursor.lastrowid
                    
                    # Create triage for leaf node if it exists
                    if diagnostic_triage or actions:
                        cursor.execute("""
                            INSERT INTO triage (node_id, diagnostic_triage, actions, created_at, updated_at)
                            VALUES (?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ','now'), strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                        """, (parent_id, diagnostic_triage, actions))
                    
                    rows_processed += 1
                    paths_imported += 1
                    
                except Exception as e:
                    print(f"⚠️  Failed to import row {rows_processed + 1}: {e}")
                    continue
            
            conn.commit()
        
        print(f"✅ Import completed successfully")
        print(f"   Rows processed: {rows_processed}")
        print(f"   Paths imported: {paths_imported}")
        
        return EXIT_SUCCESS
        
        return EXIT_SUCCESS
        
    except Exception as e:
        logger.error(f"Import error: {e}")
        print(f"❌ Import error: {e}")
        return EXIT_IMPORT_ERROR

def import_gsheet(repo, sheet_id: str, worksheet: str, strategy: str) -> int:
    """
    Import decision tree from Google Sheets.
    
    Args:
        import_export_engine: Import/export engine instance
        sheet_id: Google Sheets ID
        worksheet: Worksheet name
        strategy: Strategy for handling missing nodes
        
    Returns:
        Exit code
    """
    try:
        print(f"📥 Importing from Google Sheets")
        print(f"   Sheet ID: {sheet_id}")
        print(f"   Worksheet: {worksheet}")
        print(f"   Strategy: {strategy}")
        
        # This would require Google Sheets API integration
        # For now, we'll show a placeholder message
        print("❌ Google Sheets import not yet implemented")
        print("   This feature requires Google Sheets API setup")
        print("   Use 'import-excel' for local Excel files instead")
        
        return EXIT_IMPORT_ERROR
        
    except Exception as e:
        logger.error(f"Google Sheets import error: {e}")
        print(f"❌ Google Sheets import error: {e}")
        return EXIT_IMPORT_ERROR

def export_excel(repo, file_path: str) -> int:
    """
    Export decision tree to Excel file.
    
    Args:
        import_export_engine: Import/export engine instance
        file_path: Output file path
        
    Returns:
        Exit code
    """
    try:
        file_path = Path(file_path)
        
        # Ensure .xlsx extension
        if file_path.suffix.lower() != '.xlsx':
            file_path = file_path.with_suffix('.xlsx')
        
        print(f"📤 Exporting to Excel: {file_path}")
        
        # Export data using repository
        print("🔄 Exporting data...")
        
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get complete paths using the view
            cursor.execute("""
                SELECT vital_measurement, node_1, node_2, node_3, node_4, node_5, 
                       diagnostic_triage, actions
                FROM v_paths_complete
            """)
            
            rows = cursor.fetchall()
            
            if not rows:
                print("⚠️  No data to export")
                # Create empty file with headers
                df = pd.DataFrame(columns=CANON_HEADERS)
            else:
                # Convert to DataFrame
                df = pd.DataFrame(rows, columns=CANON_HEADERS)
        
        # Write to Excel
        try:
            df.to_excel(file_path, index=False, engine='openpyxl')
            print(f"✅ Export completed successfully")
            print(f"   Rows exported: {len(df)}")
            print(f"   Columns: {list(df.columns)}")
        except Exception as e:
            print(f"❌ Failed to write Excel file: {e}")
            return EXIT_EXPORT_ERROR
        
        return EXIT_SUCCESS
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        print(f"❌ Export error: {e}")
        return EXIT_EXPORT_ERROR

def export_csv(repo, file_path: str) -> int:
    """
    Export decision tree to CSV file.
    
    Args:
        import_export_engine: Import/export engine instance
        file_path: Output file path
        
    Returns:
        Exit code
    """
    try:
        file_path = Path(file_path)
        
        # Ensure .csv extension
        if file_path.suffix.lower() != '.csv':
            file_path = file_path.with_suffix('.csv')
        
        print(f"📤 Exporting to CSV: {file_path}")
        
        # Export data using repository
        print("🔄 Exporting data...")
        
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get complete paths using the view
            cursor.execute("""
                SELECT vital_measurement, node_1, node_2, node_3, node_4, node_5, 
                       diagnostic_triage, actions
                FROM v_paths_complete
            """)
            
            rows = cursor.fetchall()
            
            if not rows:
                print("⚠️  No data to export")
                # Create empty file with headers
                df = pd.DataFrame(columns=CANON_HEADERS)
            else:
                # Convert to DataFrame
                df = pd.DataFrame(rows, columns=CANON_HEADERS)
        
        # Write to CSV
        try:
            df.to_csv(file_path, index=False, encoding='utf-8')
            print(f"✅ Export completed successfully")
            print(f"   Rows exported: {len(df)}")
            print(f"   Columns: {list(df.columns)}")
        except Exception as e:
            print(f"❌ Failed to write CSV file: {e}")
            return EXIT_EXPORT_ERROR
        
        return EXIT_SUCCESS
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        print(f"❌ Export error: {e}")
        return EXIT_EXPORT_ERROR

def fix_tree(repo, enforce_five: bool, strategy: str) -> int:
    """
    Fix tree violations.
    
    Args:
        import_export_engine: Import/export engine instance
        enforce_five: Whether to enforce exactly 5 children per parent
        strategy: Strategy for fixing violations
        
    Returns:
        Exit code
    """
    try:
        print(f"🔧 Fixing tree violations")
        print(f"   Enforce five children: {enforce_five}")
        print(f"   Strategy: {strategy}")
        
        if enforce_five:
            print("🔄 Enforcing exactly 5 children per parent...")
            # This would need to be implemented in the engine
            # For now, we'll show a placeholder message
            print("⚠️  Five-children enforcement not yet implemented")
            print("   This feature requires additional engine methods")
        else:
            print("ℹ️  No specific fixes requested")
        
        print("✅ Fix operation completed")
        return EXIT_SUCCESS
        
    except Exception as e:
        logger.error(f"Fix error: {e}")
        print(f"❌ Fix error: {e}")
        return EXIT_SYSTEM_ERROR
