"""
Unit tests for header guard functionality.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile

from core.importers.excel_import import ExcelImporter
from core.importers.gsheet_import import GoogleSheetsImporter
from core.import_export import ImportExportEngine
from core.constants import CANON_HEADERS


@pytest.fixture
def mock_import_export_engine():
    """Create a mock import/export engine."""
    return Mock(spec=ImportExportEngine)


@pytest.fixture
def excel_importer(mock_import_export_engine):
    """Create Excel importer with mock engine."""
    return ExcelImporter(mock_import_export_engine)


@pytest.fixture
def gsheet_importer(mock_import_export_engine):
    """Create Google Sheets importer with mock engine."""
    return GoogleSheetsImporter(mock_import_export_engine)


@pytest.fixture
def valid_headers():
    """Valid canonical headers."""
    return CANON_HEADERS.copy()


@pytest.fixture
def invalid_headers():
    """Invalid headers for testing."""
    return ["Wrong Header", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5", "Diagnostic Triage", "Actions"]


class TestExcelImporterHeaderGuard:
    """Test Excel importer header validation."""
    
    def test_validate_headers_strict_valid(self, excel_importer, valid_headers):
        """Test that valid headers pass validation."""
        # Should not raise any exception
        excel_importer.validate_headers_strict(valid_headers)
    
    def test_validate_headers_strict_wrong_count(self, excel_importer):
        """Test that wrong column count fails validation."""
        wrong_headers = ["Vital Measurement", "Node 1", "Node 2"]  # Too few
        
        with pytest.raises(ValueError) as exc_info:
            excel_importer.validate_headers_strict(wrong_headers)
        
        error_msg = str(exc_info.value)
        assert "Header count mismatch" in error_msg
        assert "expected 8 columns, got 3" in error_msg
        assert "Expected:" in error_msg
        assert "Found:" in error_msg
    
    def test_validate_headers_strict_wrong_header(self, excel_importer, invalid_headers):
        """Test that wrong header names fail validation."""
        with pytest.raises(ValueError) as exc_info:
            excel_importer.validate_headers_strict(invalid_headers)
        
        error_msg = str(exc_info.value)
        assert "Header validation failed:" in error_msg
        assert "Column 1: expected 'Vital Measurement', got 'Wrong Header'" in error_msg
        assert "Expected headers:" in error_msg
        assert "Found headers:" in error_msg
    
    def test_validate_headers_strict_empty_headers(self, excel_importer):
        """Test that empty headers fail validation."""
        with pytest.raises(ValueError) as exc_info:
            excel_importer.validate_headers_strict([])
        
        error_msg = str(exc_info.value)
        assert "No headers found" in error_msg
    
    def test_validate_headers_strict_none_headers(self, excel_importer):
        """Test that None headers fail validation."""
        with pytest.raises(ValueError) as exc_info:
            excel_importer.validate_headers_strict(None)
        
        error_msg = str(exc_info.value)
        assert "No headers found" in error_msg
    
    def test_validate_headers_strict_multiple_mismatches(self, excel_importer):
        """Test that multiple header mismatches are all reported."""
        bad_headers = [
            "Wrong Vital", "Node 1", "Wrong Node 2", "Node 3", 
            "Node 4", "Node 5", "Wrong Triage", "Actions"
        ]
        
        with pytest.raises(ValueError) as exc_info:
            excel_importer.validate_headers_strict(bad_headers)
        
        error_msg = str(exc_info.value)
        assert "Column 1: expected 'Vital Measurement', got 'Wrong Vital'" in error_msg
        assert "Column 3: expected 'Node 2', got 'Wrong Node 2'" in error_msg
        assert "Column 7: expected 'Diagnostic Triage', got 'Wrong Triage'" in error_msg
    
    @patch('pandas.read_excel')
    def test_import_excel_file_valid_headers(self, mock_read_excel, excel_importer, valid_headers):
        """Test importing Excel file with valid headers."""
        # Create mock DataFrame
        mock_df = pd.DataFrame({
            'Vital Measurement': ['Test Vital'],
            'Node 1': ['Test Node 1'],
            'Node 2': ['Test Node 2'],
            'Node 3': ['Test Node 3'],
            'Node 4': ['Test Node 4'],
            'Node 5': ['Test Node 5'],
            'Diagnostic Triage': ['Test Triage'],
            'Actions': ['Test Actions']
        })
        mock_read_excel.return_value = mock_df
        
        # Mock the engine methods
        excel_importer.engine.parse_row_as_path.return_value = (
            ['Test Vital', 'Test Node 1', 'Test Node 2', 'Test Node 3', 'Test Node 4', 'Test Node 5'],
            'Test Triage',
            'Test Actions'
        )
        excel_importer.engine.import_path.return_value = {
            "path_imported": True,
            "violations": []
        }
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            tmp_file.write(b'dummy content')
            tmp_file_path = tmp_file.name
        
        try:
            result = excel_importer.import_excel_file(tmp_file_path, "placeholder")
            
            assert result["file_path"] == tmp_file_path
            assert result["total_rows"] == 1
            assert result["rows_processed"] == 1
            assert result["paths_imported"] == 1
            assert len(result["errors"]) == 0
            
        finally:
            Path(tmp_file_path).unlink(missing_ok=True)
    
    @patch('pandas.read_excel')
    def test_import_excel_file_invalid_headers(self, mock_read_excel, excel_importer, invalid_headers):
        """Test importing Excel file with invalid headers fails."""
        # Create mock DataFrame with invalid headers
        mock_df = pd.DataFrame({
            'Wrong Header': ['Test Vital'],
            'Node 1': ['Test Node 1'],
            'Node 2': ['Test Node 2'],
            'Node 3': ['Test Node 3'],
            'Node 4': ['Test Node 4'],
            'Node 5': ['Test Node 5'],
            'Diagnostic Triage': ['Test Triage'],
            'Actions': ['Test Actions']
        })
        mock_read_excel.return_value = mock_df
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            tmp_file.write(b'dummy content')
            tmp_file_path = tmp_file.name
        
        try:
            with pytest.raises(ValueError) as exc_info:
                excel_importer.import_excel_file(tmp_file_path, "placeholder")
            
            error_msg = str(exc_info.value)
            assert "Header validation failed:" in error_msg
            assert "Column 1: expected 'Vital Measurement', got 'Wrong Header'" in error_msg
            
        finally:
            Path(tmp_file_path).unlink(missing_ok=True)
    
    def test_import_excel_file_not_found(self, excel_importer):
        """Test that non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError) as exc_info:
            excel_importer.import_excel_file("nonexistent.xlsx", "placeholder")
        
        assert "Excel file not found" in str(exc_info.value)


class TestGoogleSheetsImporterHeaderGuard:
    """Test Google Sheets importer header validation."""
    
    def test_validate_headers_strict_valid(self, gsheet_importer, valid_headers):
        """Test that valid headers pass validation."""
        # Should not raise any exception
        gsheet_importer.validate_headers_strict(valid_headers)
    
    def test_validate_headers_strict_wrong_count(self, gsheet_importer):
        """Test that wrong column count fails validation."""
        wrong_headers = ["Vital Measurement", "Node 1", "Node 2"]  # Too few
        
        with pytest.raises(ValueError) as exc_info:
            gsheet_importer.validate_headers_strict(wrong_headers)
        
        error_msg = str(exc_info.value)
        assert "Header count mismatch" in error_msg
        assert "expected 8 columns, got 3" in error_msg
        assert "Expected:" in error_msg
        assert "Found:" in error_msg
    
    def test_validate_headers_strict_wrong_header(self, gsheet_importer, invalid_headers):
        """Test that wrong header names fail validation."""
        with pytest.raises(ValueError) as exc_info:
            gsheet_importer.validate_headers_strict(invalid_headers)
        
        error_msg = str(exc_info.value)
        assert "Header validation failed:" in error_msg
        assert "Column 1: expected 'Vital Measurement', got 'Wrong Header'" in error_msg
        assert "Expected headers:" in error_msg
        assert "Found headers:" in error_msg
    
    def test_validate_headers_strict_empty_headers(self, gsheet_importer):
        """Test that empty headers fail validation."""
        with pytest.raises(ValueError) as exc_info:
            gsheet_importer.validate_headers_strict([])
        
        error_msg = str(exc_info.value)
        assert "No headers found" in error_msg
    
    def test_import_gsheet_data_valid_headers(self, gsheet_importer, valid_headers):
        """Test importing Google Sheets data with valid headers."""
        # Create DataFrame with valid headers
        df = pd.DataFrame({
            'Vital Measurement': ['Test Vital'],
            'Node 1': ['Test Node 1'],
            'Node 2': ['Test Node 2'],
            'Node 3': ['Test Node 3'],
            'Node 4': ['Test Node 4'],
            'Node 5': ['Test Node 5'],
            'Diagnostic Triage': ['Test Triage'],
            'Actions': ['Test Actions']
        })
        
        # Mock the engine methods
        gsheet_importer.engine.parse_row_as_path.return_value = (
            ['Test Vital', 'Test Node 1', 'Test Node 2', 'Test Node 3', 'Test Node 4', 'Test Node 5'],
            'Test Triage',
            'Test Actions'
        )
        gsheet_importer.engine.import_path.return_value = {
            "path_imported": True,
            "violations": []
        }
        
        result = gsheet_importer.import_gsheet_data(df, "placeholder")
        
        assert result["source"] == "google_sheets"
        assert result["total_rows"] == 1
        assert result["rows_processed"] == 1
        assert result["paths_imported"] == 1
        assert len(result["errors"]) == 0
    
    def test_import_gsheet_data_invalid_headers(self, gsheet_importer, invalid_headers):
        """Test importing Google Sheets data with invalid headers fails."""
        # Create DataFrame with invalid headers
        df = pd.DataFrame({
            'Wrong Header': ['Test Vital'],
            'Node 1': ['Test Node 1'],
            'Node 2': ['Test Node 2'],
            'Node 3': ['Test Node 3'],
            'Node 4': ['Test Node 4'],
            'Node 5': ['Test Node 5'],
            'Diagnostic Triage': ['Test Triage'],
            'Actions': ['Test Actions']
        })
        
        with pytest.raises(ValueError) as exc_info:
            gsheet_importer.import_gsheet_data(df, "placeholder")
        
        error_msg = str(exc_info.value)
        assert "Header validation failed:" in error_msg
        assert "Column 1: expected 'Vital Measurement', got 'Wrong Header'" in error_msg
    
    def test_import_gsheet_data_empty(self, gsheet_importer):
        """Test that empty DataFrame raises error."""
        empty_df = pd.DataFrame()
        
        with pytest.raises(ValueError) as exc_info:
            gsheet_importer.import_gsheet_data(empty_df, "placeholder")
        
        assert "Google Sheets data is empty" in str(exc_info.value)
    
    def test_validate_gsheet_headers_only_valid(self, gsheet_importer, valid_headers):
        """Test header-only validation with valid headers."""
        df = pd.DataFrame({
            'Vital Measurement': ['Test Vital'],
            'Node 1': ['Test Node 1'],
            'Node 2': ['Test Node 2'],
            'Node 3': ['Test Node 3'],
            'Node 4': ['Test Node 4'],
            'Node 5': ['Test Node 5'],
            'Diagnostic Triage': ['Test Triage'],
            'Actions': ['Test Actions']
        })
        
        result = gsheet_importer.validate_gsheet_headers_only(df)
        
        assert result["source"] == "google_sheets"
        assert result["headers_valid"] is True
        assert result["total_rows"] == 1
        assert result["headers"] == valid_headers
    
    def test_validate_gsheet_headers_only_invalid(self, gsheet_importer, invalid_headers):
        """Test header-only validation with invalid headers fails."""
        df = pd.DataFrame({
            'Wrong Header': ['Test Vital'],
            'Node 1': ['Test Node 1'],
            'Node 2': ['Test Node 2'],
            'Node 3': ['Test Node 3'],
            'Node 4': ['Test Node 4'],
            'Node 5': ['Test Node 5'],
            'Diagnostic Triage': ['Test Triage'],
            'Actions': ['Test Actions']
        })
        
        with pytest.raises(ValueError) as exc_info:
            gsheet_importer.validate_gsheet_headers_only(df)
        
        error_msg = str(exc_info.value)
        assert "Header validation failed:" in error_msg
        assert "Column 1: expected 'Vital Measurement', got 'Wrong Header'" in error_msg


class TestHeaderGuardErrorMessages:
    """Test that header guard provides helpful error messages."""
    
    def test_error_message_includes_expected_and_found(self, excel_importer):
        """Test that error messages include both expected and found headers."""
        wrong_headers = ["Wrong Vital", "Node 1", "Node 2", "Node 3", 
                        "Node 4", "Node 5", "Diagnostic Triage", "Actions"]
        
        with pytest.raises(ValueError) as exc_info:
            excel_importer.validate_headers_strict(wrong_headers)
        
        error_msg = str(exc_info.value)
        
        # Should include expected headers
        assert "Vital Measurement" in error_msg
        assert "Node 1" in error_msg
        assert "Diagnostic Triage" in error_msg
        assert "Actions" in error_msg
        
        # Should include found headers
        assert "Wrong Vital" in error_msg
        
        # Should include specific mismatch
        assert "Column 1: expected 'Vital Measurement', got 'Wrong Vital'" in error_msg
    
    def test_error_message_multiple_mismatches(self, excel_importer):
        """Test that multiple mismatches are all reported clearly."""
        wrong_headers = ["Wrong Vital", "Wrong Node 1", "Node 2", "Node 3", 
                        "Node 4", "Node 5", "Wrong Triage", "Actions"]
        
        with pytest.raises(ValueError) as exc_info:
            excel_importer.validate_headers_strict(wrong_headers)
        
        error_msg = str(exc_info.value)
        
        # Should report all mismatches
        assert "Column 1: expected 'Vital Measurement', got 'Wrong Vital'" in error_msg
        assert "Column 2: expected 'Node 1', got 'Wrong Node 1'" in error_msg
        assert "Column 7: expected 'Diagnostic Triage', got 'Wrong Triage'" in error_msg
        
        # Should not report correct headers
        assert "Column 3: expected 'Node 2', got 'Node 2'" not in error_msg
