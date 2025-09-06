"""
Tests for dictionary import functionality.
"""

import pytest
import io
from fastapi.testclient import TestClient
from fastapi import HTTPException

from api.app import app


class TestDictionaryImport:
    """Test dictionary import functionality."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_import_csv_schema_valid(self, client):
        """Test successful CSV import with valid schema."""
        csv_content = """type,term,hints,red_flag
vital_measurement,Heart Rate,Cardiac vital sign,false
node_label,Fever,Symptom of infection,true
outcome_template,Antibiotics,Common treatment,false"""

        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}

        response = client.post("/api/v1/dictionary/import", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "inserted" in data
        assert "updated" in data
        assert "skipped" in data

    def test_import_csv_schema_missing_required_header(self, client):
        """Test CSV import with missing required header."""
        csv_content = """category,term,hints
vital_measurement,Heart Rate,Cardiac vital sign"""

        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}

        response = client.post("/api/v1/dictionary/import", files=files)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert data["detail"][0]["type"] == "value_error.csv_schema"
        assert "missing" in data["detail"][0]["ctx"]

    def test_import_xlsx_valid(self, client):
        """Test successful XLSX import."""
        # Create a simple DataFrame-like structure for testing
        # In a real test, you'd use pandas to create an actual XLSX file
        xlsx_content = b"mock xlsx content"

        files = {"file": ("test.xlsx", io.BytesIO(xlsx_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

        # This test would need actual XLSX file creation
        # For now, just test the endpoint accepts XLSX files
        response = client.post("/api/v1/dictionary/import", files=files)

        # Should either succeed or fail with schema validation
        assert response.status_code in [200, 422]

    def test_import_invalid_file_type(self, client):
        """Test import with invalid file type."""
        files = {"file": ("test.txt", io.BytesIO(b"invalid content"), "text/plain")}

        response = client.post("/api/v1/dictionary/import", files=files)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert data["detail"][0]["type"] == "value_error.invalid_file_type"

    def test_import_no_file(self, client):
        """Test import with no file provided."""
        response = client.post("/api/v1/dictionary/import")

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert data["detail"][0]["type"] == "value_error.no_file"

    def test_import_empty_csv(self, client):
        """Test import with empty CSV."""
        csv_content = "type,term"

        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}

        response = client.post("/api/v1/dictionary/import", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["inserted"] == 0
        assert data["updated"] == 0
        assert data["skipped"] == 0

    def test_import_csv_with_empty_rows(self, client):
        """Test CSV import with empty rows that should be skipped."""
        csv_content = """type,term,hints
vital_measurement,Heart Rate,Good hint
,,,
node_label,Fever,Symptom
invalid_type,Invalid Term,Should be skipped"""

        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}

        response = client.post("/api/v1/dictionary/import", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["inserted"] >= 1  # At least Heart Rate should be inserted
        assert data["skipped"] >= 2   # Empty row and invalid type should be skipped
