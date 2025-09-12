"""
Tests for ETag system and concurrency control.
"""

import pytest
from fastapi.testclient import TestClient

from api.core.etag import ETagManager, ConcurrencyError
from api.app import app

client = TestClient(app)

def test_etag_generation():
    """Test ETag generation for different data types."""
    # Test with dictionary
    data = {"id": 1, "name": "test", "version": 2}
    etag = ETagManager.generate_etag(data)
    assert etag.startswith('W/"')
    assert etag.endswith('"')
    
    # Test with string
    etag_str = ETagManager.generate_etag("test string")
    assert etag_str.startswith('W/"')
    
    # Test with number
    etag_num = ETagManager.generate_etag(123)
    assert etag_num.startswith('W/"')

def test_etag_consistency():
    """Test that same data generates same ETag."""
    data = {"id": 1, "name": "test", "version": 2}
    etag1 = ETagManager.generate_etag(data)
    etag2 = ETagManager.generate_etag(data)
    assert etag1 == etag2

def test_etag_different_data():
    """Test that different data generates different ETags."""
    data1 = {"id": 1, "name": "test"}
    data2 = {"id": 2, "name": "test"}
    
    etag1 = ETagManager.generate_etag(data1)
    etag2 = ETagManager.generate_etag(data2)
    assert etag1 != etag2

def test_version_etag():
    """Test version-based ETag generation."""
    etag = ETagManager.generate_version_etag(123, "2023-01-01T00:00:00Z")
    assert etag.startswith('W/"')
    
    # Test without timestamp
    etag_no_ts = ETagManager.generate_version_etag(123)
    assert etag_no_ts.startswith('W/"')

def test_node_etag():
    """Test node ETag generation."""
    etag = ETagManager.generate_node_etag(1, 5, "2023-01-01T00:00:00Z")
    assert etag.startswith('W/"')
    
    # Verify ETag changes with different data
    etag2 = ETagManager.generate_node_etag(1, 6, "2023-01-01T00:00:00Z")
    assert etag != etag2

def test_tree_etag():
    """Test tree ETag generation."""
    tree_data = {
        "nodes": [
            {"id": 1, "label": "Node 1"},
            {"id": 2, "label": "Node 2"}
        ],
        "triage": [
            {"node_id": 1, "diagnostic_triage": "Test"}
        ],
        "flags": [
            {"id": 1, "name": "Flag 1"}
        ]
    }
    
    etag = ETagManager.generate_tree_etag(tree_data)
    assert etag.startswith('W/"')
    
    # Test that order doesn't matter
    tree_data_reordered = {
        "nodes": [
            {"id": 2, "label": "Node 2"},
            {"id": 1, "label": "Node 1"}
        ],
        "triage": [
            {"node_id": 1, "diagnostic_triage": "Test"}
        ],
        "flags": [
            {"id": 1, "name": "Flag 1"}
        ]
    }
    
    etag_reordered = ETagManager.generate_tree_etag(tree_data_reordered)
    assert etag == etag_reordered

def test_etag_validation():
    """Test ETag validation."""
    data = {"id": 1, "name": "test"}
    etag = ETagManager.generate_etag(data)
    
    # Valid ETag should pass validation
    assert ETagManager.validate_etag(etag, data) is True
    
    # Different data should fail validation
    different_data = {"id": 2, "name": "test"}
    assert ETagManager.validate_etag(etag, different_data) is False

def test_if_match_parsing():
    """Test If-Match header parsing."""
    # Test weak ETag
    weak_etag = 'W/"abc123"'
    parsed = ETagManager.parse_if_match_header(weak_etag)
    assert parsed == "abc123"
    
    # Test strong ETag
    strong_etag = '"def456"'
    parsed = ETagManager.parse_if_match_header(strong_etag)
    assert parsed == "def456"
    
    # Test None
    parsed = ETagManager.parse_if_match_header(None)
    assert parsed is None
    
    # Test empty string
    parsed = ETagManager.parse_if_match_header("")
    assert parsed is None

def test_etag_match_checking():
    """Test ETag match checking."""
    current_etag = 'W/"abc123"'
    
    # Matching ETag should pass
    assert ETagManager.check_etag_match('W/"abc123"', current_etag) is True
    assert ETagManager.check_etag_match('"abc123"', current_etag) is True
    
    # Non-matching ETag should fail
    assert ETagManager.check_etag_match('W/"def456"', current_etag) is False
    
    # No If-Match header should pass
    assert ETagManager.check_etag_match(None, current_etag) is True

def test_response_headers():
    """Test ETag response headers generation."""
    etag = 'W/"abc123"'
    headers = ETagManager.create_etag_response_headers(etag)
    
    assert headers["ETag"] == etag
    assert headers["Cache-Control"] == "no-cache, must-revalidate"

def test_error_response():
    """Test ETag error response generation."""
    if_match = 'W/"abc123"'
    current_etag = 'W/"def456"'
    
    error_response = ETagManager.create_etag_error_response(if_match, current_etag)
    
    assert error_response["error"] == "etag_mismatch"
    assert error_response["expected_etag"] == if_match
    assert error_response["current_etag"] == current_etag
    assert "hint" in error_response

def test_concurrency_error():
    """Test ConcurrencyError exception."""
    error = ConcurrencyError("Test error", "expected", "current")
    
    assert str(error) == "Test error"
    assert error.expected_etag == "expected"
    assert error.current_etag == "current"

def test_require_etag_match():
    """Test require_etag_match function."""
    from api.core.etag import require_etag_match
    
    # Matching ETags should not raise
    require_etag_match('W/"abc123"', 'W/"abc123"')
    
    # Non-matching ETags should raise
    with pytest.raises(ConcurrencyError):
        require_etag_match('W/"abc123"', 'W/"def456"')
    
    # No If-Match should not raise
    require_etag_match(None, 'W/"abc123"')

def test_etag_integration():
    """Test ETag integration with API endpoints."""
    # This would test actual API endpoints with ETag support
    # For now, we'll test the core functionality
    
    # Test that we can generate ETags for typical API responses
    response_data = {
        "id": 1,
        "label": "Test Node",
        "version": 1,
        "updated_at": "2023-01-01T00:00:00Z"
    }
    
    etag = ETagManager.generate_etag(response_data)
    assert etag.startswith('W/"')
    
    # Test that we can validate the ETag
    assert ETagManager.validate_etag(etag, response_data) is True

def test_etag_performance():
    """Test ETag generation performance."""
    import time
    
    # Generate many ETags to test performance
    data = {"id": 1, "name": "test", "version": 2}
    
    start_time = time.time()
    for _ in range(1000):
        ETagManager.generate_etag(data)
    end_time = time.time()
    
    # Should be fast (less than 1 second for 1000 ETags)
    assert (end_time - start_time) < 1.0

def test_etag_edge_cases():
    """Test ETag edge cases."""
    # Empty data
    etag_empty = ETagManager.generate_etag({})
    assert etag_empty.startswith('W/"')
    
    # None data
    etag_none = ETagManager.generate_etag(None)
    assert etag_none.startswith('W/"')
    
    # Very large data
    large_data = {"data": "x" * 10000}
    etag_large = ETagManager.generate_etag(large_data)
    assert etag_large.startswith('W/"')
    
    # Unicode data
    unicode_data = {"name": "测试", "description": "café"}
    etag_unicode = ETagManager.generate_etag(unicode_data)
    assert etag_unicode.startswith('W/"')
