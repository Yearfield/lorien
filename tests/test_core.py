"""
Tests for core decision tree functionality.
"""

import pytest
import pandas as pd
from datetime import datetime

from core.models import Node, Parent, TreeValidationResult
from core.rules import (
    validate_canonical_headers,
    find_parents_with_too_few_children,
    find_parents_with_too_many_children,
    validate_tree_structure
)
from core.engine import DecisionTreeEngine


@pytest.fixture
def sample_df():
    """Create a sample DataFrame with decision tree data."""
    data = {
        "Vital Measurement": ["Hypertension", "Chest Pain", "Confusion"],
        "Node 1": ["Severe", "Mild", "Acute"],
        "Node 2": ["Emergency", "Monitor", "Urgent"],
        "Node 3": ["ICU", "Ward", "ER"],
        "Node 4": ["Ventilator", "Oxygen", "Medication"],
        "Node 5": ["Critical", "Stable", "Improving"],
        "Diagnostic Triage": ["Immediate", "Watch", "Treat"],
        "Actions": ["Call Code", "Monitor", "Medicate"]
    }
    return pd.DataFrame(data)


@pytest.fixture
def incomplete_df():
    """Create a DataFrame with incomplete parent-child relationships."""
    data = {
        "Vital Measurement": ["Hypertension", "Chest Pain"],
        "Node 1": ["Severe", "Mild"],
        "Node 2": ["Emergency", ""],  # Missing child for "Mild"
        "Node 3": ["ICU", ""],
        "Node 4": ["", ""],
        "Node 5": ["", ""],
        "Diagnostic Triage": ["", ""],
        "Actions": ["", ""]
    }
    return pd.DataFrame(data)


class TestCoreModels:
    """Test core domain models."""
    
    def test_node_creation(self):
        """Test Node model creation and validation."""
        node = Node(
            depth=1,
            slot=1,
            label="Test Node"
        )
        
        assert node.depth == 1
        assert node.slot == 1
        assert node.label == "Test Node"
        assert node.is_leaf is False
        assert isinstance(node.created_at, datetime)
        assert isinstance(node.updated_at, datetime)
    
    def test_node_validation(self):
        """Test Node model validation rules."""
        # Valid node
        valid_node = Node(depth=1, slot=1, label="Valid")
        assert valid_node is not None
        
        # Invalid depth
        with pytest.raises(ValueError):
            Node(depth=6, slot=1, label="Invalid")
        
        # Invalid slot for root
        with pytest.raises(ValueError):
            Node(depth=0, slot=1, label="Invalid")
        
        # Invalid slot for child
        with pytest.raises(ValueError):
            Node(depth=1, slot=0, label="Invalid")
    
    def test_parent_validation(self):
        """Test Parent model validation."""
        parent_node = Node(depth=1, slot=1, label="Parent")
        
        # Valid parent with 5 children
        children = [
            Node(depth=2, slot=i, label=f"Child {i}") 
            for i in range(1, 6)
        ]
        
        parent = Parent(node=parent_node, children=children)
        assert len(parent.children) == 5
        
        # Invalid parent with wrong number of children
        with pytest.raises(ValueError):
            Parent(node=parent_node, children=children[:3])


class TestCoreRules:
    """Test core validation rules."""
    
    def test_validate_canonical_headers(self, sample_df):
        """Test canonical header validation."""
        assert validate_canonical_headers(sample_df) is True
        
        # Test with missing columns
        incomplete_df = sample_df.drop(columns=["Diagnostic Triage"])
        assert validate_canonical_headers(incomplete_df) is False
    
    def test_find_parents_with_too_few_children(self, incomplete_df):
        """Test finding parents with too few children."""
        violations = find_parents_with_too_few_children(incomplete_df)
        
        # Should find violations for incomplete parents
        assert len(violations) > 0
        
        # Check that violations have expected structure
        for violation in violations:
            assert "level" in violation
            assert "parent_label" in violation
            assert "child_count" in violation
            assert "expected_count" in violation
            assert violation["expected_count"] == 5
    
    def test_find_parents_with_too_many_children(self, sample_df):
        """Test finding parents with too many children."""
        # Create a DataFrame with too many children
        many_children_df = sample_df.copy()
        # Add 3 more rows to create >5 children for Hypertension at level 1
        for i in range(3):
            many_children_df.loc[len(many_children_df)] = {
                "Vital Measurement": "Hypertension",
                "Node 1": f"Very Severe {i+1}",  # This creates >5 children for Hypertension
                "Node 2": "",
                "Node 3": "",
                "Node 4": "",
                "Node 5": "",
                "Diagnostic Triage": "",
                "Actions": ""
            }
        
        violations = find_parents_with_too_many_children(many_children_df)
        assert len(violations) > 0
    
    def test_validate_tree_structure(self, sample_df):
        """Test comprehensive tree structure validation."""
        result = validate_tree_structure(sample_df)
        
        assert isinstance(result, TreeValidationResult)
        assert "total_violations" in result.summary
        assert "too_few_children" in result.summary
        assert "too_many_children" in result.summary
        assert "mismatched_children" in result.summary


class TestDecisionTreeEngine:
    """Test the decision tree engine."""
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = DecisionTreeEngine()
        assert engine is not None
    
    def test_analyze_tree_structure(self, sample_df):
        """Test tree structure analysis."""
        engine = DecisionTreeEngine()
        result = engine.analyze_tree_structure(sample_df)
        
        assert isinstance(result, TreeValidationResult)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'violations')
        assert hasattr(result, 'summary')
    
    def test_find_violations(self, incomplete_df):
        """Test violation detection."""
        engine = DecisionTreeEngine()
        violations = engine.find_violations(incomplete_df)
        
        assert "too_few_children" in violations
        assert "too_many_children" in violations
        assert "mismatched_children" in violations
        assert isinstance(violations, dict)
    
    def test_get_next_incomplete_parent(self, incomplete_df):
        """Test finding next incomplete parent."""
        engine = DecisionTreeEngine()
        next_parent = engine.get_next_incomplete_parent(incomplete_df)
        
        if next_parent:
            assert "level" in next_parent
            assert "parent_label" in next_parent
            assert "child_count" in next_parent
    
    def test_get_tree_statistics(self, sample_df):
        """Test tree statistics generation."""
        engine = DecisionTreeEngine()
        stats = engine.get_tree_statistics(sample_df)
        
        assert "total_rows" in stats
        assert "total_columns" in stats
        assert "validation" in stats
        assert isinstance(stats["validation"], dict)
    
    def test_export_calculator_csv(self, sample_df):
        """Test calculator CSV export."""
        engine = DecisionTreeEngine()
        selected_rows = [0, 1]  # Select first two rows
        
        csv_output = engine.export_calculator_csv(sample_df, selected_rows)
        
        assert csv_output is not None
        assert isinstance(csv_output, str)
        assert "Diagnosis" in csv_output
        assert "Node 1" in csv_output
        assert "Node 5" in csv_output
        
        # Check that we have the expected number of lines
        lines = csv_output.split('\n')
        assert len(lines) == 3  # Header + 2 data rows


class TestIntegration:
    """Test integration between core components."""
    
    def test_end_to_end_validation(self, sample_df):
        """Test end-to-end validation workflow."""
        # Validate headers
        assert validate_canonical_headers(sample_df)
        
        # Find violations
        violations = find_parents_with_too_few_children(sample_df)
        too_many = find_parents_with_too_many_children(sample_df)
        
        # Use engine to analyze
        engine = DecisionTreeEngine()
        result = engine.analyze_tree_structure(sample_df)
        
        # Verify consistency
        assert len(violations) == result.summary["too_few_children"]
        assert len(too_many) == result.summary["too_many_children"]
    
    def test_model_serialization(self):
        """Test that models can be serialized/deserialized."""
        node = Node(
            depth=1,
            slot=1,
            label="Test Node"
        )
        
        # Convert to dict
        node_dict = node.model_dump()
        
        # Recreate from dict
        recreated_node = Node(**node_dict)
        
        assert recreated_node.depth == node.depth
        assert recreated_node.slot == node.slot
        assert recreated_node.label == node.label
