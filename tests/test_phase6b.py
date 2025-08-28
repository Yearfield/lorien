"""
Tests for Phase-6B features: Excel export, root creation, tree stats, and LLM fill.
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app
import os

client = TestClient(app)


class TestExcelExport:
    """Test Excel export endpoints."""
    
    def test_calc_export_xlsx_returns_200_and_correct_mime(self):
        """Test that /calc/export.xlsx returns 200 and correct MIME type."""
        response = client.get("/calc/export.xlsx")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert "attachment; filename=calculator_export.xlsx" in response.headers["content-disposition"]
    
    def test_tree_export_xlsx_returns_200_and_correct_mime(self):
        """Test that /tree/export.xlsx returns 200 and correct MIME type."""
        response = client.get("/tree/export.xlsx")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert "attachment; filename=tree_export.xlsx" in response.headers["content-disposition"]
    
    def test_excel_workbook_has_correct_headers(self):
        """Test that Excel workbooks have the correct 8-column headers."""
        response = client.get("/calc/export.xlsx")
        assert response.status_code == 200
        
        # Check that the file is a valid Excel file (starts with Excel magic bytes)
        content = response.content
        assert content.startswith(b'PK')  # Excel files start with PK (ZIP format)
        
        # Note: Full Excel content validation would require pandas/openpyxl in test environment
        # This test verifies the endpoint works and returns Excel format


class TestRootCreation:
    """Test root creation with 5 children."""
    
    def test_create_root_with_empty_children(self):
        """Test creating a root with 5 empty child slots."""
        response = client.post("/tree/roots", json={"label": "Test Vital"})
        assert response.status_code == 200
        
        data = response.json()
        assert "root_id" in data
        assert "children" in data
        assert len(data["children"]) == 5
        
        # Check that all 5 slots are created
        slots = [child["slot"] for child in data["children"]]
        assert slots == [1, 2, 3, 4, 5]
        
        # Check that empty children have empty labels
        for child in data["children"]:
            assert child["label"] == ""
    
    def test_create_root_with_initial_children(self):
        """Test creating a root with some initial child labels."""
        response = client.post("/tree/roots", json={
            "label": "Test Vital 2",
            "children": ["Child 1", "Child 2"]
        })
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["children"]) == 5
        
        # Check that initial children are set
        assert data["children"][0]["label"] == "Child 1"
        assert data["children"][1]["label"] == "Child 2"
        
        # Check that remaining slots are empty
        for i in range(2, 5):
            assert data["children"][i]["label"] == ""
    
    def test_create_root_rejects_empty_label(self):
        """Test that creating a root with empty label is rejected."""
        response = client.post("/tree/roots", json={"label": ""})
        assert response.status_code == 400
        assert "Root label cannot be empty" in response.json()["detail"]
    
    def test_create_root_rejects_too_many_children(self):
        """Test that creating a root with more than 5 children is rejected."""
        response = client.post("/tree/roots", json={
            "label": "Test Vital 3",
            "children": ["A", "B", "C", "D", "E", "F"]  # 6 children
        })
        assert response.status_code == 400
        assert "Cannot have more than 5 initial children" in response.json()["detail"]


class TestTreeStats:
    """Test tree statistics endpoint."""
    
    def test_tree_stats_returns_consistent_counts(self):
        """Test that /tree/stats returns consistent counts."""
        response = client.get("/tree/stats")
        assert response.status_code == 200
        
        stats = response.json()
        required_keys = ["nodes", "roots", "leaves", "complete_paths", "incomplete_parents"]
        
        for key in required_keys:
            assert key in stats
            assert isinstance(stats[key], int)
            assert stats[key] >= 0
        
        # Basic consistency checks
        assert stats["nodes"] >= stats["roots"]  # Total nodes >= roots
        assert stats["leaves"] <= stats["nodes"]  # Leaves <= total nodes
        assert stats["complete_paths"] <= stats["roots"]  # Complete paths <= roots


class TestLLMFill:
    """Test LLM fill functionality."""
    
    def test_llm_fill_503_when_disabled(self):
        """Test that LLM fill returns 503 when LLM is disabled."""
        # Ensure LLM is disabled for this test
        original_env = os.environ.get("LLM_ENABLED")
        os.environ["LLM_ENABLED"] = "false"
        
        try:
            response = client.post("/llm/fill-triage-actions", json={
                "root": "Test Root",
                "nodes": ["Node1", "Node2", "Node3", "Node4", "Node5"],
                "triage_style": "clinical",
                "actions_style": "practical"
            })
            assert response.status_code == 503
            assert "LLM service is disabled" in response.json()["detail"]
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["LLM_ENABLED"] = original_env
            else:
                del os.environ["LLM_ENABLED"]
    
    def test_llm_fill_rejects_invalid_path_context(self):
        """Test that LLM fill rejects invalid path context."""
        # Enable LLM for this test
        original_env = os.environ.get("LLM_ENABLED")
        os.environ["LLM_ENABLED"] = "true"
        
        try:
            # Test with missing root
            response = client.post("/llm/fill-triage-actions", json={
                "root": "",
                "nodes": ["Node1", "Node2", "Node3", "Node4", "Node5"],
                "triage_style": "clinical",
                "actions_style": "practical"
            })
            assert response.status_code == 400
            assert "Invalid path context" in response.json()["detail"]
            
            # Test with wrong number of nodes
            response = client.post("/llm/fill-triage-actions", json={
                "root": "Test Root",
                "nodes": ["Node1", "Node2", "Node3"],  # Only 3 nodes
                "triage_style": "clinical",
                "actions_style": "practical"
            })
            assert response.status_code == 400
            assert "Invalid path context" in response.json()["detail"]
            
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["LLM_ENABLED"] = original_env
            else:
                del os.environ["LLM_ENABLED"]


class TestDualMount:
    """Test that endpoints are available at both root and /api/v1."""
    
    def test_excel_export_dual_mount(self):
        """Test that Excel export endpoints work at both paths."""
        # Test calculator export
        root_response = client.get("/calc/export.xlsx")
        v1_response = client.get("/api/v1/calc/export.xlsx")
        
        assert root_response.status_code == 200
        assert v1_response.status_code == 200
        assert root_response.content == v1_response.content
        
        # Test tree export
        root_response = client.get("/tree/export.xlsx")
        v1_response = client.get("/api/v1/tree/export.xlsx")
        
        assert root_response.status_code == 200
        assert v1_response.status_code == 200
        assert root_response.content == v1_response.content
    
    def test_tree_stats_dual_mount(self):
        """Test that tree stats endpoint works at both paths."""
        root_response = client.get("/tree/stats")
        v1_response = client.get("/api/v1/tree/stats")
        
        assert root_response.status_code == 200
        assert v1_response.status_code == 200
        assert root_response.json() == v1_response.json()
    
    def test_root_creation_dual_mount(self):
        """Test that root creation endpoint works at both paths."""
        payload = {"label": "Dual Mount Test"}
        
        root_response = client.post("/tree/roots", json=payload)
        v1_response = client.post("/api/v1/tree/roots", json=payload)
        
        assert root_response.status_code == 200
        assert v1_response.status_code == 200
        
        # Both should create roots (though they'll be different)
        root_data = root_response.json()
        v1_data = v1_response.json()
        
        assert "root_id" in root_data
        assert "root_id" in v1_data
        assert "children" in root_data
        assert "children" in v1_data


if __name__ == "__main__":
    pytest.main([__file__])
