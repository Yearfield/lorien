"""
Google Sheets importer with strict header validation.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
import logging

from ..constants import CANON_HEADERS
from ..import_export import ImportExportEngine

logger = logging.getLogger(__name__)


class GoogleSheetsImporter:
    """Google Sheets importer with strict header validation."""
    
    def __init__(self, import_export_engine: ImportExportEngine):
        """
        Initialize Google Sheets importer.
        
        Args:
            import_export_engine: Core import/export engine
        """
        self.engine = import_export_engine
    
    def validate_headers_strict(self, headers: List[str]) -> None:
        """
        Validate headers with detailed error reporting.
        
        Args:
            headers: List of column headers from Google Sheets
            
        Raises:
            ValueError: If headers don't match canonical format with detailed error message
        """
        if not headers:
            raise ValueError("No headers found in Google Sheets")
        
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
    
    def import_gsheet_data(self, df: pd.DataFrame, strategy: str = "placeholder") -> Dict[str, Any]:
        """
        Import Google Sheets data with strict header validation.
        
        Args:
            df: Pandas DataFrame from Google Sheets
            strategy: Import strategy (placeholder/prune)
            
        Returns:
            Import results dictionary
            
        Raises:
            ValueError: If headers don't match canonical format
        """
        if df.empty:
            raise ValueError("Google Sheets data is empty")
        
        # Get headers
        headers = list(df.columns)
        
        # Validate headers strictly
        self.validate_headers_strict(headers)
        
        # Process rows
        results = {
            "source": "google_sheets",
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
    
    def validate_gsheet_headers_only(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate only the headers of Google Sheets data without importing.
        
        Args:
            df: Pandas DataFrame from Google Sheets
            
        Returns:
            Validation results dictionary
            
        Raises:
            ValueError: If headers don't match canonical format
        """
        if df.empty:
            raise ValueError("Google Sheets data is empty")
        
        # Get headers
        headers = list(df.columns)
        
        # Validate headers strictly
        self.validate_headers_strict(headers)
        
        return {
            "source": "google_sheets",
            "headers_valid": True,
            "total_rows": len(df),
            "headers": headers
        }
    
    def import_gsheet_url(self, url: str, strategy: str = "placeholder") -> Dict[str, Any]:
        """
        Import from Google Sheets URL with strict header validation.
        
        Args:
            url: Google Sheets URL
            strategy: Import strategy (placeholder/prune)
            
        Returns:
            Import results dictionary
            
        Raises:
            ValueError: If headers don't match canonical format or URL is invalid
        """
        try:
            # Convert Google Sheets URL to CSV export URL
            if "docs.google.com/spreadsheets" in url:
                # Extract sheet ID from URL
                if "/d/" in url:
                    sheet_id = url.split("/d/")[1].split("/")[0]
                else:
                    raise ValueError("Invalid Google Sheets URL format")
                
                # Create CSV export URL
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                
                # Read CSV data
                df = pd.read_csv(csv_url)
                
                return self.import_gsheet_data(df, strategy)
            else:
                raise ValueError("URL does not appear to be a Google Sheets URL")
                
        except pd.errors.EmptyDataError:
            raise ValueError("Google Sheets is empty")
        except pd.errors.ParserError as e:
            raise ValueError(f"Failed to parse Google Sheets data: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error importing from Google Sheets: {str(e)}")
    
    def validate_gsheet_url_headers_only(self, url: str) -> Dict[str, Any]:
        """
        Validate only the headers of Google Sheets URL without importing.
        
        Args:
            url: Google Sheets URL
            
        Returns:
            Validation results dictionary
            
        Raises:
            ValueError: If headers don't match canonical format or URL is invalid
        """
        try:
            # Convert Google Sheets URL to CSV export URL
            if "docs.google.com/spreadsheets" in url:
                # Extract sheet ID from URL
                if "/d/" in url:
                    sheet_id = url.split("/d/")[1].split("/")[0]
                else:
                    raise ValueError("Invalid Google Sheets URL format")
                
                # Create CSV export URL
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                
                # Read CSV data
                df = pd.read_csv(csv_url)
                
                return self.validate_gsheet_headers_only(df)
            else:
                raise ValueError("URL does not appear to be a Google Sheets URL")
                
        except pd.errors.EmptyDataError:
            raise ValueError("Google Sheets is empty")
        except pd.errors.ParserError as e:
            raise ValueError(f"Failed to parse Google Sheets data: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error validating Google Sheets: {str(e)}")
