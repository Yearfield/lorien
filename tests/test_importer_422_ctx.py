"""
Test importer 422 ctx for schema errors.
"""

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_importer_422_returns_ctx_on_schema_error(monkeypatch):
    """Test that POST /import returns 422 with ctx on schema mismatch."""
    # Mock the import logic to simulate a schema error
    from api.routers import importer

    class MockSchemaError(Exception):
        def __init__(self):
            self.first_offending_row = 0
            self.col_index = 2
            self.expected = ["Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5", "Diagnostic Triage", "Actions"]
            self.received = ["Wrong", "Header", "Format"]
            self.error_counts = {"header": 1, "missing_columns": 5}

    def mock_process_import(content, filename):
        raise MockSchemaError()

    monkeypatch.setattr(importer, "_process_import", mock_process_import)

    # Create a dummy file
    files = {"file": ("test.xlsx", b"dummy content", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

    r = client.post("/api/v1/import", files=files)
    assert r.status_code == 422

    body = r.json()
    assert "detail" in body
    assert isinstance(body["detail"], list)
    assert len(body["detail"]) > 0

    detail = body["detail"][0]
    assert "loc" in detail
    assert detail["loc"] == ["body", "file"]
    assert "ctx" in detail

    ctx = detail["ctx"]
    assert ctx["first_offending_row"] == 0
    assert ctx["col_index"] == 2
    assert isinstance(ctx["expected"], list)
    assert isinstance(ctx["received"], list)
    assert ctx["error_counts"]["header"] == 1


def test_importer_dual_mount():
    """Test importer works on both root and /api/v1 mounts."""
    files = {"file": ("test.xlsx", b"dummy content", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

    # Test root mount
    r1 = client.post("/import", files=files)
    assert r1.status_code != 405  # Should not be method not allowed

    # Test api/v1 mount
    r2 = client.post("/api/v1/import", files=files)
    assert r2.status_code != 405  # Should not be method not allowed


def test_importer_legacy_alias_still_works():
    """Test that legacy /import/excel alias still works."""
    files = {"file": ("test.xlsx", b"dummy content", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

    r = client.post("/import/excel", files=files)
    # Should not be 404 (not found) - the legacy endpoint should exist
    assert r.status_code != 404
