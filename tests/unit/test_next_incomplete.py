"""
Unit tests for next incomplete parent functionality.
"""

import pytest
import time
from unittest.mock import Mock, patch
from sqlite3 import Connection

from core.services.tree_service import TreeService
from storage.sqlite import SQLiteRepository


@pytest.fixture
def mock_repository():
    """Create a mock repository."""
    return Mock(spec=SQLiteRepository)


@pytest.fixture
def tree_service(mock_repository):
    """Create tree service with mock repository."""
    return TreeService(repository=mock_repository)


@pytest.fixture
def sample_incomplete_parents():
    """Sample data for incomplete parents."""
    return [
        {
            "parent_id": 1,
            "missing_slots": "1,3,5",
            "parent_label": "Root Node",
            "parent_depth": 0
        },
        {
            "parent_id": 2,
            "missing_slots": "2,4",
            "parent_label": "Child Node",
            "parent_depth": 1
        },
        {
            "parent_id": 3,
            "missing_slots": "1",
            "parent_label": "Another Child",
            "parent_depth": 1
        }
    ]


    def test_get_next_incomplete_parent_returns_list(tree_service, sample_incomplete_parents):
        """Test that get_next_incomplete_parent returns a list."""
        # Mock the connection and cursor
        mock_conn = Mock(spec=Connection)
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "1,3,5", "Root Node", 0),
            (2, "2,4", "Child Node", 1),
            (3, "1", "Another Child", 1)
        ]
        
        # Mock the context manager
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_conn)
        mock_context.__exit__ = Mock(return_value=None)
        tree_service.repository._get_connection.return_value = mock_context
    
    result = tree_service.get_next_incomplete_parent(limit=5)
    
    assert isinstance(result, list)
    assert len(result) == 3


    def test_get_next_incomplete_parent_structure(tree_service, sample_incomplete_parents):
        """Test that returned items have correct structure."""
        # Mock the connection and cursor
        mock_conn = Mock(spec=Connection)
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "1,3,5", "Root Node", 0)
        ]
        
        # Mock the context manager
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_conn)
        mock_context.__exit__ = Mock(return_value=None)
        tree_service.repository._get_connection.return_value = mock_context
    
    result = tree_service.get_next_incomplete_parent(limit=1)
    
    assert len(result) == 1
    item = result[0]
    
    # Check required fields
    assert "parent_id" in item
    assert "missing_slots" in item
    assert "parent_label" in item
    assert "parent_depth" in item
    
    # Check data types
    assert isinstance(item["parent_id"], int)
    assert isinstance(item["missing_slots"], str)
    assert isinstance(item["parent_label"], str)
    assert isinstance(item["parent_depth"], int)


    def test_get_next_incomplete_parent_limit(tree_service):
        """Test that limit parameter is respected."""
        # Mock the connection and cursor
        mock_conn = Mock(spec=Connection)
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "1,3,5", "Root Node", 0),
            (2, "2,4", "Child Node", 1)
        ]
        
        # Mock the context manager
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_conn)
        mock_context.__exit__ = Mock(return_value=None)
        tree_service.repository._get_connection.return_value = mock_context
    
    result = tree_service.get_next_incomplete_parent(limit=1)
    
    # Should only return 1 item due to limit
    assert len(result) == 1


    def test_get_incomplete_parents_count(tree_service):
        """Test that count method returns integer."""
        # Mock the connection and cursor
        mock_conn = Mock(spec=Connection)
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (42,)
        
        # Mock the context manager
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_conn)
        mock_context.__exit__ = Mock(return_value=None)
        tree_service.repository._get_connection.return_value = mock_context
    
    result = tree_service.get_incomplete_parents_count()
    
    assert isinstance(result, int)
    assert result == 42


    def test_get_parent_missing_slots(tree_service):
        """Test getting missing slots for a specific parent."""
        # Mock the connection and cursor
        mock_conn = Mock(spec=Connection)
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ("1,3,5",)
        
        # Mock the context manager
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_conn)
        mock_context.__exit__ = Mock(return_value=None)
        tree_service.repository._get_connection.return_value = mock_context
    
    result = tree_service.get_parent_missing_slots(parent_id=1)
    
    assert isinstance(result, list)
    assert result == [1, 3, 5]


    def test_get_parent_missing_slots_empty(tree_service):
        """Test getting missing slots when parent has all children."""
        # Mock the connection and cursor
        mock_conn = Mock(spec=Connection)
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        # Mock the context manager
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_conn)
        mock_context.__exit__ = Mock(return_value=None)
        tree_service.repository._get_connection.return_value = mock_context
    
    result = tree_service.get_parent_missing_slots(parent_id=1)
    
    assert isinstance(result, list)
    assert result == []


def test_is_parent_complete_true(tree_service):
    """Test that is_parent_complete returns True for complete parent."""
    # Mock repository to return 5 children
    mock_children = [Mock() for _ in range(5)]
    tree_service.repository.get_children.return_value = mock_children
    
    result = tree_service.is_parent_complete(parent_id=1)
    
    assert result is True
    tree_service.repository.get_children.assert_called_once_with(1)


def test_is_parent_complete_false(tree_service):
    """Test that is_parent_complete returns False for incomplete parent."""
    # Mock repository to return 3 children
    mock_children = [Mock() for _ in range(3)]
    tree_service.repository.get_children.return_value = mock_children
    
    result = tree_service.is_parent_complete(parent_id=1)
    
    assert result is False
    tree_service.repository.get_children.assert_called_once_with(1)


    def test_get_tree_statistics_structure(tree_service):
        """Test that tree statistics have correct structure."""
        # Mock the connection and cursor
        mock_conn = Mock(spec=Connection)
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (0, 1, 0),
            (1, 5, 0),
            (2, 25, 0),
            (3, 125, 0),
            (4, 625, 0),
            (5, 3125, 3125)
        ]
        mock_cursor.fetchone.side_effect = [(10,), (1256,)]  # incomplete_count, total_parents
        
        # Mock the context manager
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_conn)
        mock_context.__exit__ = Mock(return_value=None)
        tree_service.repository._get_connection.return_value = mock_context
        
        result = tree_service.get_tree_statistics()
        
        # Check required fields
        assert "coverage" in result
        assert "incomplete_parents" in result
        assert "total_parents" in result
        assert "completion_rate" in result
        
        # Check data types
        assert isinstance(result["coverage"], list)
        assert isinstance(result["incomplete_parents"], int)
        assert isinstance(result["total_parents"], int)
        assert isinstance(result["completion_rate"], float)
        
        # Check coverage structure
        assert len(result["coverage"]) == 6  # depths 0-5
        for item in result["coverage"]:
            assert "depth" in item
            assert "total_nodes" in item
            assert "leaf_count" in item


    def test_get_tree_statistics_completion_rate_zero(tree_service):
        """Test completion rate calculation when no parents exist."""
        # Mock the connection and cursor
        mock_conn = Mock(spec=Connection)
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.side_effect = [(0,), (0,)]  # incomplete_count, total_parents
        
        # Mock the context manager
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_conn)
        mock_context.__exit__ = Mock(return_value=None)
        tree_service.repository._get_connection.return_value = mock_context
        
        result = tree_service.get_tree_statistics()
        
        assert result["completion_rate"] == 0.0


@patch('time.time')
def test_get_next_incomplete_parent_performance(mock_time, tree_service):
        """Test that next incomplete parent query is fast (<50ms)."""
        # Mock the connection and cursor
        mock_conn = Mock(spec=Connection)
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (i, "1,2,3", f"Node {i}", i % 5) for i in range(10)  # Return 10 results to match limit
        ]
        
        # Mock the context manager
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_conn)
        mock_context.__exit__ = Mock(return_value=None)
        tree_service.repository._get_connection.return_value = mock_context
        
        # Mock time to measure performance
        start_time = 1000.0
        end_time = 1000.045  # 45ms
        mock_time.side_effect = [start_time, end_time]
        
        start = time.time()
        result = tree_service.get_next_incomplete_parent(limit=10)
        end = time.time()
        
        execution_time = (end - start) * 1000  # Convert to milliseconds
        
        # Should complete in under 50ms
        assert execution_time < 50
        assert len(result) == 10
