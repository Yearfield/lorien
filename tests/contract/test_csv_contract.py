"""
Tests for CSV/XLSX V1 contract enforcement.
"""

import pytest
import tempfile
import os
import pandas as pd
from io import BytesIO
from fastapi.testclient import TestClient

from api.app import app
from core.import_export import assert_csv_header


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


@pytest.fixture
def client(test_db):
    """Create test client with test database."""
    return TestClient(app)


class TestCSVContract:
    """Tests for CSV/XLSX V1 contract enforcement."""

    def test_valid_csv_header_accepted(self):
        """Test that valid V1 header is accepted."""
        valid_header = [
            "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
            "Diagnostic Triage", "Actions"
        ]

        # Should not raise exception
        assert_csv_header(valid_header)

    def test_invalid_column_count_rejected(self):
        """Test that wrong number of columns is rejected."""
        # Too few columns
        short_header = ["Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5"]
        with pytest.raises(ValueError) as exc_info:
            assert_csv_header(short_header)

        error = exc_info.value.args[0]
        assert error["col_index"] == 0  # First column that doesn't match
        assert len(error["expected"]) == 8
        assert len(error["received"]) == 6

        # Too many columns
        long_header = [
            "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
            "Diagnostic Triage", "Actions", "Extra Column"
        ]
        with pytest.raises(ValueError) as exc_info:
            assert_csv_header(long_header)

        error = exc_info.value.args[0]
        assert len(error["expected"]) == 8
        assert len(error["received"]) == 9

    def test_wrong_column_names_rejected(self):
        """Test that wrong column names are rejected."""
        # Wrong first column
        wrong_first = [
            "Wrong Column", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
            "Diagnostic Triage", "Actions"
        ]
        with pytest.raises(ValueError) as exc_info:
            assert_csv_header(wrong_first)

        error = exc_info.value.args[0]
        assert error["col_index"] == 0
        assert error["expected"][0] == "Vital Measurement"
        assert error["received"][0] == "Wrong Column"

        # Wrong middle column
        wrong_middle = [
            "Vital Measurement", "Node 1", "Wrong Node", "Node 3", "Node 4", "Node 5",
            "Diagnostic Triage", "Actions"
        ]
        with pytest.raises(ValueError) as exc_info:
            assert_csv_header(wrong_middle)

        error = exc_info.value.args[0]
        assert error["col_index"] == 2
        assert error["expected"][2] == "Node 2"
        assert error["received"][2] == "Wrong Node"

    def test_case_sensitive_headers(self):
        """Test that headers are case-sensitive."""
        wrong_case = [
            "vital measurement", "node 1", "node 2", "node 3", "node 4", "node 5",
            "diagnostic triage", "actions"
        ]
        with pytest.raises(ValueError) as exc_info:
            assert_csv_header(wrong_case)

        error = exc_info.value.args[0]
        assert error["col_index"] == 0
        assert error["expected"][0] == "Vital Measurement"
        assert error["received"][0] == "vital measurement"

    def test_excel_import_with_invalid_header(self, client):
        """Test that Excel import with invalid header returns 422 with precise error."""
        # Create invalid Excel file
        invalid_data = {
            "Wrong Header": ["Value1", "Value2"],
            "Node 1": ["Child1", "Child2"],
            "Node 2": ["", ""],
            "Node 3": ["", ""],
            "Node 4": ["", ""],
            "Node 5": ["", ""],
            "Diagnostic Triage": ["Triage1", "Triage2"],
            "Actions": ["Action1", "Action2"]
        }
        df = pd.DataFrame(invalid_data)

        # Save to BytesIO
        bio = BytesIO()
        df.to_excel(bio, index=False)
        bio.seek(0)

        # Create upload file
        files = {"file": ("test.xlsx", bio, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

        response = client.post("/api/v1/import/excel", files=files)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert len(data["detail"]) == 1
        error_detail = data["detail"][0]

        assert error_detail["loc"] == ["body", "file"]
        assert error_detail["msg"] == "CSV header mismatch"
        assert error_detail["type"] == "value_error.csv_schema"
        assert "ctx" in error_detail
        ctx = error_detail["ctx"]
        assert "first_offending_row" in ctx
        assert "col_index" in ctx
        assert "expected" in ctx
        assert "received" in ctx

    def test_excel_import_with_valid_header(self, client):
        """Test that Excel import with valid header is accepted."""
        # Create valid Excel file
        valid_data = {
            "Vital Measurement": ["Root1", "Root2"],
            "Node 1": ["Child1", "Child2"],
            "Node 2": ["", ""],
            "Node 3": ["", ""],
            "Node 4": ["", ""],
            "Node 5": ["", ""],
            "Diagnostic Triage": ["Triage1", "Triage2"],
            "Actions": ["Action1", "Action2"]
        }
        df = pd.DataFrame(valid_data)

        # Save to BytesIO
        bio = BytesIO()
        df.to_excel(bio, index=False)
        bio.seek(0)

        # Create upload file
        files = {"file": ("test.xlsx", bio, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

        response = client.post("/api/v1/import/excel", files=files)

        # Should succeed (200) - the import job completes successfully
        # Note: The actual data processing is TODO, but header validation should pass
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["state"] == "done"
        assert "Import completed successfully" in data["message"]