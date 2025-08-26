"""
Excel importer with strict header validation.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from ..constants import CANON_HEADERS
from ..import_export import ImportExportEngine

logger = logging.getLogger(__name__)


class ExcelImporter:
    """Excel importer with strict header validation."""
    
    def __init__(self, import_export_engine: ImportExportEngine):
        """
        Initialize Excel importer.
        
        Args:
            import_export_engine: Core import/export engine
        """
        self.engine = import_export_engine
    
    def validate_headers_strict(self, headers: List[str]) -> None:
        """
        Validate headers with detailed error reporting.
        
        Args:
            headers: List of column headers from Excel file
            
        Raises:
            ValueError: If headers don't match canonical format with detailed error message
        """
        if not headers:
            raise ValueError("No headers found in Excel file")
        
        # Check column count
        if len(headers) != len(CANON_HEADERS):
            raise ValueError(
                f"Header count mismatch: expected {len(CANON_HEADERS)} columns, got {len(headers)}\n"
                f"Expected: {CANON_HEADERS}\n"
                f"Found: {headers}"
            )
        
        # Check each header individually
        mismatches = []
        for i, (expected, actual) in enumerate(zip(CANON_HEADERS, headers)):
            if expected != actual:
                mismatches.append(f"Column {i+1}: expected '{expected}', got '{actual}'")
        
        if mismatches:
            error_msg = "Header validation failed:\n"
            error_msg += "\n".join(mismatches)
            error_msg += f"\n\nExpected headers: {CANON_HEADERS}"
            error_msg += f"\nFound headers: {headers}"
            raise ValueError(error_msg)
    
    def import_excel_file(self, file_path: str, strategy: str = "placeholder") -> Dict[str, Any]:
        """
        Import Excel file with strict header validation.
        
        Args:
            file_path: Path to Excel file
            strategy: Import strategy (placeholder/prune)
            
        Returns:
            Import results dictionary
            
        Raises:
            ValueError: If headers don't match canonical format
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=0)
            
            # Get headers
            headers = list(df.columns)
            
            # Validate headers strictly
            self.validate_headers_strict(headers)
            
            # Process rows
            results = {
                "file_path": str(file_path),
                "total_rows": len(df),
                "rows_processed": 0,
                "paths_imported": 0,
                "violations": [],
                "errors": []
            }
            
            for index, row in df.iterrows():
                try:
                    # Parse row as path
                    node_labels, diagnostic_triage, actions = self.engine.parse_row_as_path(row)
                    
                    # Import path
                    path_result = self.engine.import_path(
                        node_labels, diagnostic_triage, actions, strategy
                    )
                    
                    results["rows_processed"] += 1
                    
                    if path_result["path_imported"]:
                        results["paths_imported"] += 1
                    
                    if path_result.get("violations"):
                        results["violations"].extend(path_result["violations"])
                        
                except Exception as e:
                    error_msg = f"Row {index + 2}: {str(e)}"  # +2 for 1-based indexing and header row
                    results["errors"].append(error_msg)
                    logger.error(error_msg)
            
            return results
            
        except pd.errors.EmptyDataError:
            raise ValueError(f"Excel file is empty: {file_path}")
        except pd.errors.ParserError as e:
            raise ValueError(f"Failed to parse Excel file {file_path}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error importing Excel file {file_path}: {str(e)}")
    
    def validate_excel_headers_only(self, file_path: str) -> Dict[str, Any]:
        """
        Validate only the headers of an Excel file without importing data.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Validation results dictionary
            
        Raises:
            ValueError: If headers don't match canonical format
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=0)
            
            # Get headers
            headers = list(df.columns)
            
            # Validate headers strictly
            self.validate_headers_strict(headers)
            
            return {
                "file_path": str(file_path),
                "headers_valid": True,
                "total_rows": len(df),
                "headers": headers
            }
            
        except pd.errors.EmptyDataError:
            raise ValueError(f"Excel file is empty: {file_path}")
        except pd.errors.ParserError as e:
            raise ValueError(f"Failed to parse Excel file {file_path}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error validating Excel file {file_path}: {str(e)}")
