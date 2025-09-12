"""
Tests for data quality governance functionality.

Tests the central validators, data quality endpoints, and repair functionality.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sqlite3

from api.app import app
from api.repositories.validators import (
    normalize_label, validate_label, validate_outcome_text,
    validate_dictionary_term, validate_children_data, get_validation_rules
)

client = TestClient(app)

class TestCentralValidators:
    """Test central validation functions."""
    
    def test_normalize_label(self):
        """Test label normalization."""
        # Test basic normalization
        assert normalize_label("  chest pain  ") == "Chest Pain"
        assert normalize_label("multiple   spaces") == "Multiple Spaces"
        assert normalize_label("") == ""
        assert normalize_label("   ") == ""
        
        # Test title case conversion
        assert normalize_label("chest pain") == "Chest Pain"
        assert normalize_label("CHEST PAIN") == "Chest Pain"
    
    def test_validate_label_success(self):
        """Test successful label validation."""
        result = validate_label("Chest Pain", "label")
        assert result == "Chest Pain"
        
        result = validate_label("chest pain", "label")
        assert result == "Chest Pain"  # Normalized
    
    def test_validate_label_errors(self):
        """Test label validation errors."""
        # Empty label
        with pytest.raises(Exception) as exc_info:
            validate_label("", "label")
        assert exc_info.value.status_code == 422
        
        # Too long
        with pytest.raises(Exception) as exc_info:
            validate_label("x" * 101, "label")
        assert exc_info.value.status_code == 422
        
        # Invalid characters
        with pytest.raises(Exception) as exc_info:
            validate_label("chest@pain", "label")
        assert exc_info.value.status_code == 422
    
    def test_validate_outcome_text_success(self):
        """Test successful outcome validation."""
        result = validate_outcome_text("Monitor vital signs", "outcome")
        assert result == "Monitor Vital Signs"
        
        result = validate_outcome_text("assess patient condition", "outcome")
        assert result == "Assess Patient Condition"
    
    def test_validate_outcome_text_errors(self):
        """Test outcome validation errors."""
        # Empty outcome
        with pytest.raises(Exception) as exc_info:
            validate_outcome_text("", "outcome")
        assert exc_info.value.status_code == 422
        
        # Too many words
        with pytest.raises(Exception) as exc_info:
            validate_outcome_text("one two three four five six seven eight", "outcome")
        assert exc_info.value.status_code == 422
        
        # Prohibited tokens
        with pytest.raises(Exception) as exc_info:
            validate_outcome_text("give 10mg daily", "outcome")
        assert exc_info.value.status_code == 422
    
    def test_validate_dictionary_term(self):
        """Test dictionary term validation."""
        # Valid term
        result = validate_dictionary_term({
            "label": "Chest Pain",
            "category": "symptom",
            "code": "SYM001"
        })
        assert result["label"] == "Chest Pain"
        assert result["category"] == "Symptom"
        assert result["code"] == "SYM001"
        
        # Invalid category length
        with pytest.raises(Exception) as exc_info:
            validate_dictionary_term({
                "label": "Test",
                "category": "x" * 51
            })
        assert exc_info.value.status_code == 422
    
    def test_validate_children_data(self):
        """Test children data validation."""
        # Valid children data
        result = validate_children_data([
            {"label": "Option 1", "slot": 1, "depth": 1},
            {"label": "Option 2", "slot": 2, "depth": 1}
        ])
        assert len(result) == 2
        assert result[0]["label"] == "Option 1"
        assert result[0]["slot"] == 1
        
        # Invalid slot
        with pytest.raises(Exception) as exc_info:
            validate_children_data([
                {"label": "Option 1", "slot": 6, "depth": 1}
            ])
        assert exc_info.value.status_code == 422
        
        # Empty children
        with pytest.raises(Exception) as exc_info:
            validate_children_data([])
        assert exc_info.value.status_code == 422
    
    def test_get_validation_rules(self):
        """Test validation rules retrieval."""
        rules = get_validation_rules()
        assert "label_rules" in rules
        assert "outcome_rules" in rules
        assert "dictionary_rules" in rules
        assert "children_rules" in rules


class TestDataQualityEndpoints:
    """Test data quality API endpoints."""
    
    def test_get_data_quality_summary(self):
        """Test data quality summary endpoint."""
        response = client.get("/api/v1/admin/data-quality/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert "slot_gaps" in data
        assert "over_5_children" in data
        assert "orphans" in data
        assert "duplicate_labels" in data
        assert "total_nodes" in data
        assert "total_parents" in data
        assert "validation_rules" in data
        assert "status" in data
        
        # Check that all counts are non-negative
        assert data["slot_gaps"] >= 0
        assert data["over_5_children"] >= 0
        assert data["orphans"] >= 0
        assert data["duplicate_labels"] >= 0
        assert data["total_nodes"] >= 0
        assert data["total_parents"] >= 0
    
    def test_repair_slot_gaps(self):
        """Test slot gaps repair endpoint."""
        response = client.post("/api/v1/admin/data-quality/repair/slot-gaps")
        assert response.status_code == 200
        
        data = response.json()
        assert "repaired_count" in data
        assert "repair_details" in data
        assert "status" in data
        assert "message" in data
        
        # Check that repaired_count is non-negative
        assert data["repaired_count"] >= 0
        assert data["status"] == "completed"
    
    def test_repair_slot_gaps_idempotent(self):
        """Test that repair slot gaps is idempotent."""
        # Run repair twice
        response1 = client.post("/api/v1/admin/data-quality/repair/slot-gaps")
        response2 = client.post("/api/v1/admin/data-quality/repair/slot-gaps")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Second run should not repair anything new
        data1 = response1.json()
        data2 = response2.json()
        
        # If there were no gaps initially, both should return 0
        # If there were gaps, first run should repair them, second should return 0
        assert data2["repaired_count"] == 0
    
    def test_get_validation_rules_endpoint(self):
        """Test validation rules endpoint."""
        response = client.get("/api/v1/admin/data-quality/validation-rules")
        assert response.status_code == 200
        
        data = response.json()
        assert "validation_rules" in data
        assert "description" in data
        
        rules = data["validation_rules"]
        assert "label_rules" in rules
        assert "outcome_rules" in rules
        assert "dictionary_rules" in rules
        assert "children_rules" in rules


class TestDataQualityIntegration:
    """Test data quality integration with existing modules."""
    
    def test_dictionary_uses_central_validators(self):
        """Test that dictionary endpoints use central validators."""
        # This test would need to be implemented based on how the dictionary
        # router is updated to use central validators
        pass
    
    def test_children_upsert_uses_central_validators(self):
        """Test that children upsert uses central validators."""
        # This test would need to be implemented based on how the children
        # upsert endpoints are updated to use central validators
        pass
    
    def test_outcomes_put_uses_central_validators(self):
        """Test that outcomes PUT uses central validators."""
        # This test would need to be implemented based on how the outcomes
        # PUT endpoints are updated to use central validators
        pass


class TestDataQualityErrorHandling:
    """Test data quality error handling."""
    
    def test_summary_endpoint_error_handling(self):
        """Test data quality summary error handling."""
        # Mock database error
        with patch('api.routers.data_quality.get_repository') as mock_repo:
            mock_repo.side_effect = Exception("Database error")
            
            response = client.get("/api/v1/admin/data-quality/summary")
            assert response.status_code == 500
            
            data = response.json()
            assert "error" in data
            assert "Failed to get data quality summary" in data["error"]
    
    def test_repair_endpoint_error_handling(self):
        """Test repair endpoint error handling."""
        # Mock database error
        with patch('api.routers.data_quality.get_repository') as mock_repo:
            mock_repo.side_effect = Exception("Database error")
            
            response = client.post("/api/v1/admin/data-quality/repair/slot-gaps")
            assert response.status_code == 500
            
            data = response.json()
            assert "error" in data
            assert "Failed to repair slot gaps" in data["error"]


class TestDataQualityContractCompliance:
    """Test data quality contract compliance."""
    
    def test_422_error_structure(self):
        """Test that 422 errors follow the required structure."""
        # Test label validation error structure
        with pytest.raises(Exception) as exc_info:
            validate_label("", "test_field")
        
        error = exc_info.value
        assert error.status_code == 422
        assert isinstance(error.detail, list)
        
        detail = error.detail[0]
        assert "loc" in detail
        assert "msg" in detail
        assert "type" in detail
        assert detail["loc"] == ["body", "test_field"]
    
    def test_validation_rules_consistency(self):
        """Test that validation rules are consistent across the application."""
        rules = get_validation_rules()
        
        # Check that rules are properly structured
        assert isinstance(rules["label_rules"], dict)
        assert isinstance(rules["outcome_rules"], dict)
        assert isinstance(rules["dictionary_rules"], dict)
        assert isinstance(rules["children_rules"], dict)
        
        # Check that required fields are present
        assert "max_length" in rules["label_rules"]
        assert "max_words" in rules["outcome_rules"]
        assert "slot_range" in rules["children_rules"]
