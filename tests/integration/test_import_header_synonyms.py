from starlette.testclient import TestClient

from api.app import app
from api.db.migrate import apply_migrations


def test_import_with_synonym_headers(tmp_path, monkeypatch):
    """Test that import accepts synonym headers and normalizes them correctly."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Create CSV with synonym headers
    csv = """Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions
Hypertension,Headache,Thunderclap Headache,Visual Disturbances,Decreased GCS(13-15),Sudden onset,,"""

    r = c.post("/api/v1/import?mode=replace", files={"file": ("syn.csv", csv, "text/csv")})
    assert r.status_code in (200, 201)

    # Verify root was imported correctly
    roots = c.get("/api/v1/tree/roots")
    assert roots.status_code == 200
    roots_data = roots.json()["items"]
    assert len(roots_data) == 1
    assert roots_data[0]["label"].lower() == "hypertension"
