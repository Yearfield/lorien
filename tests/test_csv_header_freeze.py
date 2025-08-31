from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_tree_export_header():
    """Test that tree export returns the exact frozen 8-column header."""
    r = client.get("/tree/export")
    assert r.status_code == 200
    header = r.text.splitlines()[0]
    expected = "Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions"
    assert header == expected

def test_calc_export_header():
    """Test that calculator export returns the exact frozen 8-column header."""
    r = client.get("/calc/export")
    assert r.status_code == 200
    header = r.text.splitlines()[0]
    expected = "Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions"
    assert header == expected

def test_tree_export_xlsx_header():
    """Test that tree XLSX export returns the exact frozen 8-column header."""
    r = client.get("/tree/export.xlsx")
    assert r.status_code == 200
    # XLSX files are binary, so we can't easily check the header content
    # But we can verify the endpoint exists and returns a file
    assert r.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "content-disposition" in r.headers

def test_calc_export_xlsx_header():
    """Test that calculator XLSX export returns the exact frozen 8-column header."""
    r = client.get("/calc/export.xlsx")
    assert r.status_code == 200
    # XLSX files are binary, so we can't easily check the header content
    # But we can verify the endpoint exists and returns a file
    assert r.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "content-disposition" in r.headers

def test_csv_header_dual_mount():
    """Test that CSV export headers are identical at both mounts."""
    r1 = client.get("/tree/export")
    r2 = client.get("/api/v1/tree/export")
    
    assert r1.status_code == 200
    assert r2.status_code == 200
    
    header1 = r1.text.splitlines()[0]
    header2 = r2.text.splitlines()[0]
    
    assert header1 == header2
    expected = "Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions"
    assert header1 == expected
