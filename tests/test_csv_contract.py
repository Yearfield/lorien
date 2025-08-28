"""
Tests for CSV export contract compliance.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_csv_headers_are_frozen_eight_columns():
    """Test that CSV export returns the exact 8-column header contract."""
    r = client.get("/tree/export")
    assert r.status_code == 200, f"Export failed: {r.text}"
    
    header = r.text.splitlines()[0]
    expected = "Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions"
    assert header == expected, f"Expected header '{expected}', got '{header}'"
    
    # Also test calculator export
    r2 = client.get("/calc/export")
    assert r2.status_code == 200, f"Calculator export failed: {r2.text}"
    
    header2 = r2.text.splitlines()[0]
    assert header2 == expected, f"Calculator export header mismatch: expected '{expected}', got '{header2}'"


def test_csv_export_dual_mount():
    """Test that CSV export works consistently at both root and /api/v1 paths."""
    # Test root path
    r1 = client.get("/tree/export")
    assert r1.status_code == 200
    
    # Test API v1 path
    r2 = client.get("/api/v1/tree/export")
    assert r2.status_code == 200
    
    # Headers should be identical
    header1 = r1.text.splitlines()[0]
    header2 = r2.text.splitlines()[0]
    assert header1 == header2, "Headers should be identical between root and API v1"


def test_csv_content_structure():
    """Test basic CSV structure and content."""
    r = client.get("/tree/export")
    assert r.status_code == 200
    
    lines = r.text.splitlines()
    assert len(lines) > 0, "CSV should have at least one line (header)"
    
    # Check header structure
    header = lines[0]
    columns = header.split(',')
    assert len(columns) == 8, f"Expected 8 columns, got {len(columns)}"
    
    # Verify expected columns are present
    expected_columns = ["Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5", "Diagnostic Triage", "Actions"]
    for expected in expected_columns:
        assert expected in header, f"Expected column '{expected}' not found in header"


def test_csv_export_headers():
    """Test that CSV export returns proper HTTP headers."""
    r = client.get("/tree/export")
    assert r.status_code == 200
    
    # Check content type
    assert "text/csv" in r.headers.get("content-type", ""), "Content-Type should be text/csv"
    
    # Check content disposition
    content_disposition = r.headers.get("content-disposition", "")
    assert "attachment" in content_disposition, "Content-Disposition should include attachment"


def test_csv_empty_database():
    """Test that CSV export returns headers even with no data."""
    r = client.get("/tree/export")
    assert r.status_code == 200
    
    lines = r.text.splitlines()
    assert len(lines) >= 1, "Should have at least header line"
    
    # Header should be present even with no data
    header = lines[0]
    expected = "Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions"
    assert header == expected, "Header should match expected format even with empty database"
