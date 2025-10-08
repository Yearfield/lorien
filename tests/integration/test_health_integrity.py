from starlette.testclient import TestClient

from api.app import app
from api.db.migrate import apply_migrations


def test_health_has_integrity(tmp_path, monkeypatch):
    """Test that health endpoint includes database integrity check."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Test health endpoint
    r = c.get("/api/v1/health")
    assert r.status_code == 200
    j = r.json()

    # Check that health response has expected structure
    assert "ok" in j
    assert "db" in j
    assert j["ok"] is True

    # Check that database info includes integrity
    db_info = j["db"]
    assert "integrity" in db_info
    assert db_info["integrity"] == "ok"  # Should be "ok" for a fresh database

    # Check that we have object count
    assert "objects" in db_info
    assert isinstance(db_info["objects"], int)
    assert db_info["objects"] > 0  # Should have some database objects (tables, views, triggers)


def test_health_with_data(tmp_path, monkeypatch):
    """Test health endpoint after importing data."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Import some data
    csv = """D0,D1,D2,D3,D4,D5,D6,Notes
TestRoot,Child1,,,,,,
TestRoot,Child2,,,,,,"""

    r = c.post("/api/v1/import?mode=replace", files={"file": ("test.csv", csv, "text/csv")})
    assert r.status_code in (200, 201)

    # Test health endpoint after import
    r = c.get("/api/v1/health")
    assert r.status_code == 200
    j = r.json()

    # Integrity should still be "ok"
    assert j["db"]["integrity"] == "ok"

    # Should have more objects now (including any views/triggers created)
    assert j["db"]["objects"] > 0
