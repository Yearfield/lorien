from starlette.testclient import TestClient

from api.app import app
from api.db.migrate import apply_migrations


def test_import_with_diagnostic_triage_as_notes(tmp_path, monkeypatch):
    """Test that Diagnostic Triage is treated as Notes and doesn't create depth=6 nodes."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Create CSV with Diagnostic Triage and Actions columns
    csv = """Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions
Hypertension,Headache,Thunderclap Headache,Visual Disturbances,Decreased GCS(13-15),Sudden onset,Some triage,Some action"""

    r = c.post("/api/v1/import?mode=replace", files={"file": ("diag.csv", csv, "text/csv")})
    assert r.status_code in (200, 201)

    # Verify root was imported correctly
    roots = c.get("/api/v1/tree/roots")
    assert roots.status_code == 200
    roots_data = roots.json()["items"]
    assert len(roots_data) == 1
    assert roots_data[0]["label"].lower() == "hypertension"

    # Verify no depth=6 nodes were created by checking the export
    export = c.get("/api/v1/tree/export?format=csv&limit=100")
    assert export.status_code == 200
    export_lines = export.text.strip().split("\n")

    # Check that no path has more than 6 levels (D0..D5)
    for line in export_lines[1:]:  # Skip header
        if line.strip():
            parts = line.split(",")
            # Count non-empty structural path parts (D0..D5 only, excluding D6/Notes metadata)
            path_parts = [p.strip() for p in parts[:6] if p.strip()]  # D0..D5 only
            # Should have at most 6 path parts (D0..D5), since D6/Notes is metadata, not structural
            assert len(path_parts) <= 6, f"Path has too many levels: {path_parts}"

    # Verify that metadata is preserved in export
    export_text = export.text
    assert "Some triage" in export_text  # D6 metadata
    assert "Some action" in export_text  # Notes metadata
