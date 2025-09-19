"""
Tests for EngineLongBow frozen header contract enforcement.
"""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient

from api.app import app
from Engines.EngineLongBow.consts import FROZEN_HEADER


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    test_db.close()

    # Set environment variable for test database
    os.environ['LORIEN_DB_PATH'] = test_db.name

    yield test_db.name

    # Clean up
    if os.path.exists(test_db.name):
        os.unlink(test_db.name)


class TestCSVContract:
    """Tests for EngineLongBow frozen header contract enforcement."""

    def test_valid_frozen_header_accepted(self):
        """Test that valid frozen header is accepted."""
        # FROZEN_HEADER is the expected format for EngineLongBow
        assert FROZEN_HEADER == ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "Notes"]

    def test_frozen_header_length(self):
        """Test that frozen header has exactly 8 columns."""
        assert len(FROZEN_HEADER) == 8

    def test_frozen_header_columns(self):
        """Test that frozen header has correct column names."""
        expected = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "Notes"]
        assert FROZEN_HEADER == expected

    def test_engine_longbow_header_validation(self):
        """Test that EngineLongBow validates headers correctly."""
        from Engines.EngineLongBow.ingest import validate_header
        
        # Valid header should pass
        result = validate_header(FROZEN_HEADER)
        assert result["valid"] is True
        
        # Invalid header should fail
        invalid_header = ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]  # Missing Notes
        result = validate_header(invalid_header)
        assert result["valid"] is False
        assert "header_mismatch" in result["error"]["type"]