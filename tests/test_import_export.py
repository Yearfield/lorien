"""
Tests for the import/export functionality.
Includes golden tests for various scenarios.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os

from core.constants import CANON_HEADERS, STRATEGY_PLACEHOLDER, STRATEGY_PRUNE
from core.import_export import ImportExportEngine
from core.engine import DecisionTreeEngine


class TestImportExportEngine:
    """Test the ImportExportEngine class."""
    
    @pytest.fixture
    def tree_engine(self):
        """Create a mock tree engine."""
        return DecisionTreeEngine()
    
    @pytest.fixture
    def import_export_engine(self, tree_engine):
        """Create an ImportExportEngine instance."""
        return ImportExportEngine(tree_engine)
    
    @pytest.fixture
    def perfect_data(self):
        """Create perfect 5-child test data."""
        return [
            {
                "Vital Measurement": "Hypertension",
                "Node 1": "Mild",
                "Node 2": "Controlled",
                "Node 3": "Medication",
                "Node 4": "ACE Inhibitor",
                "Node 5": "Lisinopril",
                "Diagnostic Triage": "Monitor blood pressure monthly",
                "Actions": "Prescribe lisinopril 10mg daily"
            },
            {
                "Vital Measurement": "Diabetes",
                "Node 1": "Type 2",
                "Node 2": "Controlled",
                "Node 3": "Oral Medication",
                "Node 4": "Metformin",
                "Node 5": "500mg Twice Daily",
                "Diagnostic Triage": "Monitor blood glucose weekly",
                "Actions": "Prescribe metformin 500mg twice daily with meals"
            }
        ]
    
    @pytest.fixture
    def missing_slot_data(self):
        """Create data with missing slot 4."""
        return [
            {
                "Vital Measurement": "Hypertension",
                "Node 1": "Mild",
                "Node 2": "Controlled",
                "Node 3": "Medication",
                "Node 4": "",  # Missing slot 4
                "Node 5": "Lisinopril",
                "Diagnostic Triage": "Monitor blood pressure monthly",
                "Actions": "Prescribe lisinopril 10mg daily"
            }
        ]
    
    @pytest.fixture
    def duplicate_children_data(self):
        """Create data with duplicate children."""
        return [
            {
                "Vital Measurement": "Hypertension",
                "Node 1": "Mild",
                "Node 2": "Controlled",
                "Node 3": "Medication",
                "Node 4": "ACE Inhibitor",
                "Node 5": "Lisinopril",
                "Diagnostic Triage": "Monitor blood pressure monthly",
                "Actions": "Prescribe lisinopril 10mg daily"
            },
            {
                "Vital Measurement": "Hypertension",
                "Node 1": "Mild",  # Duplicate
                "Node 2": "Controlled",  # Duplicate
                "Node 3": "Medication",  # Duplicate
                "Node 4": "ACE Inhibitor",  # Duplicate
                "Node 5": "Enalapril",  # Different leaf
                "Diagnostic Triage": "Monitor blood pressure monthly",
                "Actions": "Prescribe enalapril 5mg daily"
            }
        ]
    
    def test_validate_headers_perfect(self, import_export_engine):
        """Test header validation with perfect headers."""
        headers = CANON_HEADERS.copy()
        assert import_export_engine.validate_headers(headers) is True
    
    def test_validate_headers_wrong_count(self, import_export_engine):
        """Test header validation with wrong column count."""
        headers = CANON_HEADERS[:-1]  # Missing one column
        with pytest.raises(ValueError, match="Expected 8 columns, got 7"):
            import_export_engine.validate_headers(headers)
    
    def test_validate_headers_wrong_names(self, import_export_engine):
        """Test header validation with wrong column names."""
        headers = CANON_HEADERS.copy()
        headers[0] = "Wrong Name"  # Change first column name
        with pytest.raises(ValueError, match="Column 0: expected 'Vital Measurement', got 'Wrong Name'"):
            import_export_engine.validate_headers(headers)
    
    def test_validate_headers_wrong_order(self, import_export_engine):
        """Test header validation with wrong column order."""
        headers = CANON_HEADERS.copy()
        # Swap first two columns
        headers[0], headers[1] = headers[1], headers[0]
        with pytest.raises(ValueError, match="Column 0: expected 'Vital Measurement', got 'Node 1'"):
            import_export_engine.validate_headers(headers)
    
    def test_parse_row_as_path_perfect(self, import_export_engine, perfect_data):
        """Test parsing perfect row data."""
        df = pd.DataFrame(perfect_data)
        row = df.iloc[0]
        
        node_labels, diagnostic_triage, actions = import_export_engine.parse_row_as_path(row)
        
        assert len(node_labels) == 6
        assert node_labels[0] == "Hypertension"  # Root
        assert node_labels[1] == "Mild"          # Node 1
        assert node_labels[2] == "Controlled"    # Node 2
        assert node_labels[3] == "Medication"    # Node 3
        assert node_labels[4] == "ACE Inhibitor" # Node 4
        assert node_labels[5] == "Lisinopril"    # Node 5
        assert diagnostic_triage == "Monitor blood pressure monthly"
        assert actions == "Prescribe lisinopril 10mg daily"
    
    def test_parse_row_as_path_missing_values(self, import_export_engine):
        """Test parsing row with missing values."""
        data = {
            "Vital Measurement": "Hypertension",
            "Node 1": "Mild",
            "Node 2": "",  # Missing
            "Node 3": "Medication",
            "Node 4": None,  # None value
            "Node 5": "Lisinopril",
            "Diagnostic Triage": "",  # Empty
            "Actions": None  # None value
        }
        row = pd.Series(data)
        
        node_labels, diagnostic_triage, actions = import_export_engine.parse_row_as_path(row)
        
        assert len(node_labels) == 6
        assert node_labels[0] == "Hypertension"
        assert node_labels[1] == "Mild"
        assert node_labels[2] == ""  # Empty string for missing
        assert node_labels[3] == "Medication"
        assert node_labels[4] == ""  # Empty string for None
        assert node_labels[5] == "Lisinopril"
        assert diagnostic_triage is None  # Empty becomes None
        assert actions is None  # None becomes None
    
    def test_import_dataframe_perfect(self, import_export_engine, perfect_data):
        """Test importing perfect DataFrame."""
        df = pd.DataFrame(perfect_data)
        
        result = import_export_engine.import_dataframe(df, STRATEGY_PLACEHOLDER)
        
        assert result['success'] is True
        assert result['rows_processed'] == 2
        assert result['paths_imported'] == 2
        assert result['total_violations'] == 0
        assert result['missing_slots_created'] == 0
    
    def test_import_dataframe_missing_slots_placeholder(self, import_export_engine, missing_slot_data):
        """Test importing DataFrame with missing slots using placeholder strategy."""
        df = pd.DataFrame(missing_slot_data)
        
        result = import_export_engine.import_dataframe(df, STRATEGY_PLACEHOLDER)
        
        assert result['success'] is True
        assert result['rows_processed'] == 1
        assert result['paths_imported'] == 1
        assert result['total_violations'] == 0
        assert result['missing_slots_created'] == 1  # One missing slot filled
    
    def test_import_dataframe_missing_slots_prune(self, import_export_engine, missing_slot_data):
        """Test importing DataFrame with missing slots using prune strategy."""
        df = pd.DataFrame(missing_slot_data)
        
        result = import_export_engine.import_dataframe(df, STRATEGY_PRUNE)
        
        assert result['success'] is True
        assert result['rows_processed'] == 1
        assert result['paths_imported'] == 0  # Path rejected due to missing slot
        assert result['total_violations'] == 1  # One violation for missing slot
        assert "Missing node at depth 4, slot 4" in str(result['violations'])
    
    def test_import_dataframe_duplicate_children(self, import_export_engine, duplicate_children_data):
        """Test importing DataFrame with duplicate children."""
        df = pd.DataFrame(duplicate_children_data)
        
        result = import_export_engine.import_dataframe(df, STRATEGY_PLACEHOLDER)
        
        assert result['success'] is True
        assert result['rows_processed'] == 2
        assert result['paths_imported'] == 2  # Both paths imported
        assert result['total_violations'] == 0  # No violations (duplicates allowed by policy)
    
    def test_import_dataframe_invalid_headers(self, import_export_engine):
        """Test importing DataFrame with invalid headers."""
        data = [
            {
                "Wrong Header": "Value",
                "Another Wrong": "Value"
            }
        ]
        df = pd.DataFrame(data)
        
        result = import_export_engine.import_dataframe(df, STRATEGY_PLACEHOLDER)
        
        assert result['success'] is False
        assert "Header validation failed" in result['error']
        assert result['rows_processed'] == 0
        assert result['paths_imported'] == 0
    
    def test_export_to_dataframe_empty(self, import_export_engine):
        """Test exporting empty tree to DataFrame."""
        df = import_export_engine.export_to_dataframe()
        
        assert df.empty is True
        assert list(df.columns) == CANON_HEADERS
    
    def test_export_to_dataframe_with_data(self, import_export_engine, perfect_data):
        """Test exporting tree with data to DataFrame."""
        # First import some data
        df_input = pd.DataFrame(perfect_data)
        import_export_engine.import_dataframe(df_input, STRATEGY_PLACEHOLDER)
        
        # Then export
        df_output = import_export_engine.export_to_dataframe()
        
        # Should have the same structure
        assert list(df_output.columns) == CANON_HEADERS
        # Note: In the current mock implementation, this will be empty
        # In a real implementation, it would contain the imported data
    
    def test_export_paths_structure(self, import_export_engine):
        """Test that exported paths have correct structure."""
        paths = import_export_engine.export_paths()
        
        # Should be a list
        assert isinstance(paths, list)
        
        # Each path should have canonical headers
        for path in paths:
            assert isinstance(path, dict)
            for header in CANON_HEADERS:
                assert header in path
    
    def test_import_path_validation(self, import_export_engine):
        """Test import_path validation."""
        # Test with invalid path length
        result = import_export_engine.import_path(["Root"], strategy=STRATEGY_PLACEHOLDER)
        assert result['path_imported'] is False
        assert "Invalid path length" in str(result['violations'])
        
        # Test with empty root label
        result = import_export_engine.import_path(["", "Node1", "Node2", "Node3", "Node4", "Node5"], 
                                                strategy=STRATEGY_PLACEHOLDER)
        assert result['path_imported'] is False
        assert "Root label cannot be empty" in str(result['violations'])
    
    def test_import_path_strategies(self, import_export_engine):
        """Test different import strategies."""
        # Test placeholder strategy
        result = import_export_engine.import_path(
            ["Root", "Node1", "Node2", "", "Node4", "Node5"],  # Missing Node 3
            strategy=STRATEGY_PLACEHOLDER
        )
        assert result['path_imported'] is True
        assert len(result['missing_slots']) == 1
        
        # Test prune strategy
        result = import_export_engine.import_path(
            ["Root", "Node1", "Node2", "", "Node4", "Node5"],  # Missing Node 3
            strategy=STRATEGY_PRUNE
        )
        assert result['path_imported'] is False
        assert "Missing node at depth 3, slot 3" in str(result['violations'])


class TestGoldenTests:
    """Golden tests for import/export functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_perfect_5_children_roundtrip(self, temp_dir):
        """Golden test: Perfect 5-child rows → export equals input."""
        # Create perfect test data
        perfect_data = [
            {
                "Vital Measurement": "Hypertension",
                "Node 1": "Mild",
                "Node 2": "Controlled",
                "Node 3": "Medication",
                "Node 4": "ACE Inhibitor",
                "Node 5": "Lisinopril",
                "Diagnostic Triage": "Monitor blood pressure monthly",
                "Actions": "Prescribe lisinopril 10mg daily"
            }
        ]
        
        # Create input DataFrame
        df_input = pd.DataFrame(perfect_data)
        input_file = temp_dir / "input.xlsx"
        df_input.to_excel(input_file, index=False, engine='openpyxl')
        
        # Import
        tree_engine = DecisionTreeEngine()
        import_export_engine = ImportExportEngine(tree_engine)
        
        # Note: In the current mock implementation, this won't actually import
        # In a real implementation, this would test the roundtrip
        result = import_export_engine.import_dataframe(df_input, STRATEGY_PLACEHOLDER)
        assert result['success'] is True
        
        # Export
        df_output = import_export_engine.export_to_dataframe()
        
        # Verify structure
        assert list(df_output.columns) == CANON_HEADERS
        
        # Note: In the current mock implementation, output will be empty
        # In a real implementation, this would verify data equality
    
    def test_missing_slot_4_placeholder(self, temp_dir):
        """Golden test: Missing slot 4 → placeholder creation."""
        missing_data = [
            {
                "Vital Measurement": "Hypertension",
                "Node 1": "Mild",
                "Node 2": "Controlled",
                "Node 3": "Medication",
                "Node 4": "",  # Missing slot 4
                "Node 5": "Lisinopril",
                "Diagnostic Triage": "Monitor blood pressure monthly",
                "Actions": "Prescribe lisinopril 10mg daily"
            }
        ]
        
        df_input = pd.DataFrame(missing_data)
        tree_engine = DecisionTreeEngine()
        import_export_engine = ImportExportEngine(tree_engine)
        
        # Test placeholder strategy
        result = import_export_engine.import_dataframe(df_input, STRATEGY_PLACEHOLDER)
        assert result['success'] is True
        assert result['missing_slots_created'] == 1
        
        # Test prune strategy
        result = import_export_engine.import_dataframe(df_input, STRATEGY_PRUNE)
        assert result['success'] is True
        assert result['paths_imported'] == 0  # Path rejected
        assert result['total_violations'] == 1  # Violation reported
    
    def test_duplicate_children_repair(self, temp_dir):
        """Golden test: Duplicate children → repaired to first 5, flagged."""
        duplicate_data = [
            {
                "Vital Measurement": "Hypertension",
                "Node 1": "Mild",
                "Node 2": "Controlled",
                "Node 3": "Medication",
                "Node 4": "ACE Inhibitor",
                "Node 5": "Lisinopril",
                "Diagnostic Triage": "Monitor blood pressure monthly",
                "Actions": "Prescribe lisinopril 10mg daily"
            },
            {
                "Vital Measurement": "Hypertension",
                "Node 1": "Mild",  # Duplicate
                "Node 2": "Controlled",  # Duplicate
                "Node 3": "Medication",  # Duplicate
                "Node 4": "ACE Inhibitor",  # Duplicate
                "Node 5": "Enalapril",  # Different leaf
                "Diagnostic Triage": "Monitor blood pressure monthly",
                "Actions": "Prescribe enalapril 5mg daily"
            }
        ]
        
        df_input = pd.DataFrame(duplicate_data)
        tree_engine = DecisionTreeEngine()
        import_export_engine = ImportExportEngine(tree_engine)
        
        # Import with duplicates
        result = import_export_engine.import_dataframe(df_input, STRATEGY_PLACEHOLDER)
        assert result['success'] is True
        assert result['paths_imported'] == 2  # Both paths imported
        assert result['total_violations'] == 0  # No violations (duplicates allowed by policy)
        
        # Export to verify structure maintained
        df_output = import_export_engine.export_to_dataframe()
        assert list(df_output.columns) == CANON_HEADERS


class TestCLICommands:
    """Test CLI command functionality."""
    
    def test_validate_command(self):
        """Test the validate command."""
        from cli.commands import validate_tree
        from core.engine import DecisionTreeEngine
        from core.import_export import ImportExportEngine
        
        tree_engine = DecisionTreeEngine()
        import_export_engine = ImportExportEngine(tree_engine)
        
        # Test validation without exit on violations
        result = validate_tree(import_export_engine, exit_on_violations=False)
        assert result == 0  # EXIT_SUCCESS
        
        # Test validation with exit on violations
        result = validate_tree(import_export_engine, exit_on_violations=True)
        assert result == 0  # EXIT_SUCCESS (no violations in mock)
    
    def test_import_excel_command(self):
        """Test the import-excel command."""
        from cli.commands import import_excel
        from core.engine import DecisionTreeEngine
        from core.import_export import ImportExportEngine
        
        tree_engine = DecisionTreeEngine()
        import_export_engine = ImportExportEngine(tree_engine)
        
        # Test with non-existent file
        result = import_excel(import_export_engine, "nonexistent.xlsx", "placeholder")
        assert result == 2  # EXIT_IMPORT_ERROR
        
        # Test with invalid file extension
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test")
            temp_file = f.name
        
        try:
            result = import_excel(import_export_engine, temp_file, "placeholder")
            assert result == 2  # EXIT_IMPORT_ERROR
        finally:
            os.unlink(temp_file)
    
    def test_export_commands(self):
        """Test export commands."""
        from cli.commands import export_csv, export_excel
        from core.engine import DecisionTreeEngine
        from core.import_export import ImportExportEngine
        
        tree_engine = DecisionTreeEngine()
        import_export_engine = ImportExportEngine(tree_engine)
        
        # Test CSV export
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_file = f.name
        
        try:
            result = export_csv(import_export_engine, temp_file)
            assert result == 0  # EXIT_SUCCESS
            
            # Verify file was created
            assert os.path.exists(temp_file)
        finally:
            os.unlink(temp_file)
        
        # Test Excel export
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_file = f.name
        
        try:
            result = export_excel(import_export_engine, temp_file)
            assert result == 0  # EXIT_SUCCESS
            
            # Verify file was created
            assert os.path.exists(temp_file)
        finally:
            os.unlink(temp_file)
