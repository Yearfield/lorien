"""
Test strict 422 context for EngineLongBow CSV schema validation.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
import pandas as pd

from api.app import app
from Engines.EngineLongBow.consts import FROZEN_HEADER
from Engines.EngineLongBow.ingest import validate_header


class TestImportSchemaValidation:
    """Test strict 422 context for CSV schema drift."""

    def test_exact_header_passes(self):
        """Test that exact frozen header passes validation."""
        # FROZEN_HEADER should pass validation
        result = validate_header(FROZEN_HEADER)
        assert result["valid"] is True

    def test_extra_column_fails_422(self):
        """Test that extra column fails with 422 and proper ctx."""
        header = FROZEN_HEADER + ["Extra Column"]

        result = validate_header(header)
        assert result["valid"] is False
        assert result["error"]["type"] == "value_error.header_mismatch"
        assert result["error"]["ctx"]["col_index"] == 8  # Extra column at index 8

    def test_missing_column_fails_422(self):
        """Test that missing column fails with 422 and proper ctx."""
        header = FROZEN_HEADER[:-1]  # Remove last column

        result = validate_header(header)
        assert result["valid"] is False
        assert result["error"]["type"] == "value_error.header_mismatch"
        assert result["error"]["ctx"]["col_index"] == 7  # Missing column at index 7

    def test_wrong_column_name_fails_422(self):
        """Test that wrong column name fails with 422 and proper ctx."""
        header = FROZEN_HEADER.copy()
        header[0] = "Wrong Column"  # Change first column

        result = validate_header(header)
        assert result["valid"] is False
        assert result["error"]["type"] == "value_error.header_mismatch"
        assert result["error"]["ctx"]["col_index"] == 0  # First column mismatch

    def test_case_sensitive_headers(self):
        """Test that headers are case-sensitive."""
        header = [col.lower() for col in FROZEN_HEADER]  # All lowercase

        result = validate_header(header)
        assert result["valid"] is False
        assert result["error"]["type"] == "value_error.header_mismatch"
        assert result["error"]["ctx"]["col_index"] == 0  # First column mismatch