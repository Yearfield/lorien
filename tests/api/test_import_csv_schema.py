"""
Tests for import CSV schema validation with strict 422 context.
"""

import pytest
import io
from fastapi.testclient import TestClient
from fastapi import HTTPException
import pandas as pd

from api.app import app
from core.import_export import assert_csv_header


class TestImportSchemaValidation:
    """Test strict 422 context for CSV schema drift."""

    def test_exact_header_passes(self):
        """Test that exact V1 header passes validation."""
        expected = [
            "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
            "Diagnostic Triage", "Actions"
        ]

        # Should not raise exception
        assert_csv_header(expected)

    def test_extra_column_fails_422(self):
        """Test that extra column fails with 422 and proper ctx."""
        header = [
            "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
            "Diagnostic Triage", "Actions", "Extra Column"
        ]

        with pytest.raises(ValueError) as exc_info:
            assert_csv_header(header)

        error_ctx = exc_info.value.args[0]
        assert error_ctx["first_offending_row"] == 0
        assert error_ctx["col_index"] == 0  # First mismatch or length mismatch
        assert len(error_ctx["expected"]) == 8
        assert len(error_ctx["received"]) == 9

    def test_missing_column_fails_422(self):
        """Test that missing column fails with 422 and proper ctx."""
        header = [
            "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
            "Diagnostic Triage"  # Missing "Actions"
        ]

        with pytest.raises(ValueError) as exc_info:
            assert_csv_header(header)

        error_ctx = exc_info.value.args[0]
        assert error_ctx["first_offending_row"] == 0
        assert error_ctx["col_index"] == 0  # Length mismatch
        assert len(error_ctx["expected"]) == 8
        assert len(error_ctx["received"]) == 7

    def test_wrong_column_name_fails_422(self):
        """Test that wrong column name fails with 422 and proper ctx."""
        header = [
            "Vital Measurement", "Node 1", "Node 2", "Wrong Name", "Node 4", "Node 5",
            "Diagnostic Triage", "Actions"
        ]

        with pytest.raises(ValueError) as exc_info:
            assert_csv_header(header)

        error_ctx = exc_info.value.args[0]
        assert error_ctx["first_offending_row"] == 0
        assert error_ctx["col_index"] == 3  # "Node 3" vs "Wrong Name"
        assert error_ctx["expected"] == [
            "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
            "Diagnostic Triage", "Actions"
        ]
        assert "Wrong Name" in error_ctx["received"]

    def test_reordered_columns_fails_422(self):
        """Test that reordered columns fail with 422 and proper ctx."""
        header = [
            "Vital Measurement", "Node 1", "Node 2", "Node 4", "Node 3", "Node 5",
            "Diagnostic Triage", "Actions"
        ]

        with pytest.raises(ValueError) as exc_info:
            assert_csv_header(header)

        error_ctx = exc_info.value.args[0]
        assert error_ctx["first_offending_row"] == 0
        assert error_ctx["col_index"] == 3  # "Node 3" vs "Node 4"
        assert error_ctx["expected"][3] == "Node 3"
        assert error_ctx["received"][3] == "Node 4"


class TestImportEndpointIntegration:
    """Integration tests for import endpoint with 422 responses."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_import_with_exact_header_succeeds(self, client):
        """Test import with exact header succeeds."""
        # Create test Excel file with exact header
        df = pd.DataFrame({
            "Vital Measurement": ["Test Vital"],
            "Node 1": ["Test Node 1"],
            "Node 2": ["Test Node 2"],
            "Node 3": ["Test Node 3"],
            "Node 4": ["Test Node 4"],
            "Node 5": ["Test Node 5"],
            "Diagnostic Triage": ["Test Triage"],
            "Actions": ["Test Actions"]
        })

        # Convert to Excel bytes
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        content = buffer.getvalue()

        # Create upload file
        files = {"file": ("test.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

        response = client.post("/api/v1/import", files=files)

        # Should succeed (200 or 202)
        assert response.status_code in [200, 202]
        data = response.json()
        assert "headers_validated" in data
        assert data["headers_validated"] is True

    def test_import_with_wrong_header_fails_422(self, client):
        """Test import with wrong header fails with 422 and proper ctx."""
        # Create test Excel file with wrong header
        df = pd.DataFrame({
            "Wrong Header": ["Test"],
            "Node 1": ["Test"],
            "Node 2": ["Test"],
            "Node 3": ["Test"],
            "Node 4": ["Test"],
            "Node 5": ["Test"],
            "Diagnostic Triage": ["Test"],
            "Actions": ["Test"]
        })

        # Convert to Excel bytes
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        content = buffer.getvalue()

        # Create upload file
        files = {"file": ("test.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

        response = client.post("/api/v1/import", files=files)

        # Should fail with 422
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        detail = data["detail"][0]
        assert detail["loc"] == ["body", "file"]
        assert detail["msg"] == "CSV header mismatch"
        assert detail["type"] == "value_error.csv_schema"
        assert "ctx" in detail
        ctx = detail["ctx"]
        assert "expected" in ctx
        assert "received" in ctx
        assert ctx["first_offending_row"] == 0
        assert len(ctx["expected"]) == 8
