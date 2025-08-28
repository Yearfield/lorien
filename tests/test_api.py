"""
Tests for the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import tempfile
import os

from api.app import app
from core.models import Node, Triaging, RedFlag
from datetime import datetime

client = TestClient(app)


@pytest.fixture
def mock_repository():
    """Mock repository for testing."""
    with patch('api.dependencies.get_repository') as mock:
        repo = Mock()
        mock.return_value = repo
        yield repo


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_api_health(self, mock_repository):
        """Test API health endpoint."""
        mock_repository.get_database_info.return_value = {"db_path": "test.db"}
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "version" in data
        assert "db" in data
        assert "features" in data
    
    def test_api_health_db_disconnected(self, mock_repository):
        """Test API health endpoint when database is disconnected."""
        mock_repository.get_database_info.side_effect = Exception("DB Error")
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True


class TestTreeEndpoints:
    """Test tree-related endpoints."""
    
    def test_get_next_incomplete_parent_found(self, mock_repository):
        """Test getting next incomplete parent when one exists."""
        mock_repository.get_next_incomplete_parent.return_value = {
            "parent_id": 1,
            "child_count": 3,
            "depth": 1
        }
        
        # Mock existing children
        mock_children = [
            Mock(slot=1),
            Mock(slot=2),
            Mock(slot=3)
        ]
        mock_repository.get_children.return_value = mock_children
        
        response = client.get("/api/v1/tree/next-incomplete-parent")
        assert response.status_code == 200
        data = response.json()
        assert data["parent_id"] == 1
        assert data["missing_slots"] == [4, 5]
    
    def test_get_next_incomplete_parent_not_found(self, mock_repository):
        """Test getting next incomplete parent when none exists."""
        mock_repository.get_next_incomplete_parent.return_value = None
        
        response = client.get("/api/v1/tree/next-incomplete-parent")
        assert response.status_code == 404
        assert "No incomplete parents found" in response.json()["detail"]
    
    def test_get_children_success(self, mock_repository):
        """Test getting children of a parent."""
        # Mock parent validation
        mock_parent = Node(id=1, depth=1, slot=1, label="Parent")
        mock_repository.get_node.return_value = mock_parent
        
        # Mock children
        mock_children = [
            Node(id=2, parent_id=1, depth=2, slot=1, label="Child 1"),
            Node(id=3, parent_id=1, depth=2, slot=2, label="Child 2")
        ]
        mock_repository.get_children.return_value = mock_children
        
        response = client.get("/api/v1/tree/1/children")
        assert response.status_code == 200
        data = response.json()
        assert data["parent_id"] == 1
        assert len(data["children"]) == 2
        assert data["children"][0]["label"] == "Child 1"
    
    def test_get_children_parent_not_found(self, mock_repository):
        """Test getting children when parent doesn't exist."""
        mock_repository.get_node.return_value = None
        
        response = client.get("/api/v1/tree/999/children")
        assert response.status_code == 404
    
    def test_upsert_children_success(self, mock_repository):
        """Test upserting children successfully."""
        # Mock parent validation
        mock_parent = Node(id=1, depth=1, slot=1, label="Parent")
        mock_repository.get_node.return_value = mock_parent
        
        # Mock existing children
        mock_repository.get_children.return_value = []
        
        request_data = {
            "children": [
                {"slot": 1, "label": "Child 1"},
                {"slot": 2, "label": "Child 2"}
            ]
        }
        
        response = client.post("/api/v1/tree/1/children", json=request_data)
        assert response.status_code == 200
        assert "Successfully upserted 2 children" in response.json()["message"]
    
    def test_upsert_children_too_many(self, mock_repository):
        """Test upserting more than 5 children."""
        # Mock parent validation
        mock_parent = Node(id=1, depth=1, slot=1, label="Parent")
        mock_repository.get_node.return_value = mock_parent
        
        request_data = {
            "children": [
                {"slot": i, "label": f"Child {i}"} for i in range(1, 7)
            ]
        }
        
        response = client.post("/api/v1/tree/1/children", json=request_data)
        assert response.status_code == 422
        assert "Cannot have more than 5 children" in response.json()["detail"]
    
    def test_upsert_children_duplicate_slots(self, mock_repository):
        """Test upserting children with duplicate slots."""
        # Mock parent validation
        mock_parent = Node(id=1, depth=1, slot=1, label="Parent")
        mock_repository.get_node.return_value = mock_parent
        
        request_data = {
            "children": [
                {"slot": 1, "label": "Child 1"},
                {"slot": 1, "label": "Child 2"}  # Duplicate slot
            ]
        }
        
        response = client.post("/api/v1/tree/1/children", json=request_data)
        assert response.status_code == 409
        assert "Duplicate slots are not allowed" in response.json()["detail"]
    
    def test_insert_child_success(self, mock_repository):
        """Test inserting a single child."""
        # Mock parent validation
        mock_parent = Node(id=1, depth=1, slot=1, label="Parent")
        mock_repository.get_node.return_value = mock_parent
        
        # Mock existing children
        mock_repository.get_children.return_value = []
        
        request_data = {"slot": 1, "label": "New Child"}
        
        response = client.post("/api/v1/tree/1/child", json=request_data)
        assert response.status_code == 200
        assert "Created child in slot 1" in response.json()["message"]


class TestTriageEndpoints:
    """Test triage-related endpoints."""
    
    def test_get_triage_success(self, mock_repository):
        """Test getting triage information."""
        mock_triage = Triaging(
            node_id=1,
            diagnostic_triage="Test triage",
            actions="Test actions"
        )
        mock_repository.get_triage.return_value = mock_triage
        
        response = client.get("/api/v1/triage/1")
        assert response.status_code == 200
        data = response.json()
        assert data["diagnostic_triage"] == "Test triage"
        assert data["actions"] == "Test actions"
    
    def test_get_triage_not_found(self, mock_repository):
        """Test getting triage when it doesn't exist."""
        mock_repository.get_triage.return_value = None
        
        response = client.get("/api/v1/triage/999")
        assert response.status_code == 404
    
    def test_update_triage_success(self, mock_repository):
        """Test updating triage information."""
        # Mock node validation
        mock_node = Node(id=1, depth=1, slot=1, label="Test")
        mock_repository.get_node.return_value = mock_node
        
        # Mock existing triage
        mock_repository.get_triage.return_value = None
        
        request_data = {
            "diagnostic_triage": "Updated triage",
            "actions": "Updated actions"
        }
        
        response = client.put("/api/v1/triage/1", json=request_data)
        assert response.status_code == 200
        assert "Triage updated successfully" in response.json()["message"]
    
    def test_update_triage_no_fields(self, mock_repository):
        """Test updating triage with no fields provided."""
        # Mock node validation
        mock_node = Node(id=1, depth=1, slot=1, label="Test")
        mock_repository.get_node.return_value = mock_node
        
        request_data = {}
        
        response = client.put("/api/v1/triage/1", json=request_data)
        assert response.status_code == 400
        assert "At least one field" in response.json()["detail"]


class TestFlagEndpoints:
    """Test red flag endpoints."""
    
    def test_search_flags_success(self, mock_repository):
        """Test searching red flags."""
        mock_flags = [
            RedFlag(id=1, name="Test Flag", description="Test", severity="high")
        ]
        mock_repository.search_red_flags.return_value = mock_flags
        
        response = client.get("/api/v1/flags/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test"
        assert len(data["flags"]) == 1
        assert data["flags"][0]["name"] == "Test Flag"
    
    def test_search_flags_empty_query(self, mock_repository):
        """Test searching with empty query."""
        response = client.get("/api/v1/flags/search?q=")
        assert response.status_code == 400
        assert "Search query cannot be empty" in response.json()["detail"]
    
    def test_assign_flag_success(self, mock_repository):
        """Test assigning a red flag to a node."""
        # Mock node validation
        mock_node = Node(id=1, depth=1, slot=1, label="Test")
        mock_repository.get_node.return_value = mock_node
        
        # Mock flag search
        mock_flag = RedFlag(id=1, name="Test Flag", description="Test", severity="high")
        mock_repository.search_red_flags.return_value = [mock_flag]
        
        request_data = {
            "node_id": 1,
            "red_flag_name": "Test Flag"
        }
        
        response = client.post("/api/v1/flags/assign", json=request_data)
        assert response.status_code == 200
        assert "Assigned red flag" in response.json()["message"]
    
    def test_assign_flag_not_found(self, mock_repository):
        """Test assigning a flag that doesn't exist."""
        # Mock node validation
        mock_node = Node(id=1, depth=1, slot=1, label="Test")
        mock_repository.get_node.return_value = mock_node
        
        # Mock empty flag search
        mock_repository.search_red_flags.return_value = []
        
        request_data = {
            "node_id": 1,
            "red_flag_name": "Nonexistent Flag"
        }
        
        response = client.post("/api/v1/flags/assign", json=request_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestExportEndpoint:
    """Test CSV export endpoint."""
    
    def test_export_csv_success(self, mock_repository):
        """Test CSV export."""
        # Mock the CSV data method
        mock_repository.get_tree_data_for_csv.return_value = [
            {
                "Diagnosis": "Hypertension",
                "Node 1": "Severe",
                "Node 2": "Emergency",
                "Node 3": "ICU",
                "Node 4": "Ventilator",
                "Node 5": "Critical"
            }
        ]
        
        response = client.get("/calc/export")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment; filename=calculator_export.csv" in response.headers["content-disposition"]
        
        # Check CSV content
        content = response.text
        assert "Diagnosis" in content
        assert "Node 1" in content
        assert "Node 5" in content


class TestErrorHandling:
    """Test error handling."""
    
    def test_404_not_found(self):
        """Test 404 error handling."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_validation_error(self):
        """Test validation error handling."""
        # Test with invalid JSON
        response = client.post("/api/v1/tree/1/children", data="invalid json")
        assert response.status_code == 422
