from starlette.testclient import TestClient

from api.app import app
from api.db.migrate import apply_migrations


def test_import_roundtrip_meta(tmp_path, monkeypatch):
    """Test that Diagnostic Triage and Actions metadata round-trips correctly."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Create CSV with Diagnostic Triage and Actions columns
    csv = (
        "Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions\n"
        "Hypertension,Headache,Thunderclap Headache,Visual Disturbances,Decreased GCS(13-15),Sudden onset,TRIAGE_A,ACT_1\n"
        "Hypertension,Headache,Thunderclap Headache,Visual Disturbances,Decreased GCS(10-12),Eye Pain,TRIAGE_B,ACT_2\n"
    )

    r = c.post("/api/v1/import?mode=replace", files={"file": ("wb.csv", csv, "text/csv")})
    assert r.status_code in (200, 201)

    # Sanity: roots exist
    roots = c.get("/api/v1/tree/roots").json()["items"]
    assert any(r["label"].lower() == "hypertension" for r in roots)

    # Export should include D6/Notes
    exp = c.get("/api/v1/tree/export?format=csv&limit=100").text
    assert "D0,D1,D2,D3,D4,D5,D6,Notes" in exp
    assert "TRIAGE_A" in exp and "ACT_1" in exp
    assert "TRIAGE_B" in exp and "ACT_2" in exp

    # Verify specific rows in export
    lines = exp.strip().replace("\r", "").split("\n")
    assert len(lines) >= 3  # Header + 2 data rows

    # Check that metadata appears in the correct columns
    found_triage_a = False
    found_triage_b = False
    for line in lines[1:]:  # Skip header
        if "TRIAGE_A" in line and "ACT_1" in line:
            # D6 should be TRIAGE_A, Notes should be ACT_1
            parts = line.split(",")
            assert len(parts) >= 8
            assert parts[6] == "TRIAGE_A"  # D6 column
            assert parts[7] == "ACT_1"  # Notes column
            found_triage_a = True
        elif "TRIAGE_B" in line and "ACT_2" in line:
            # D6 should be TRIAGE_B, Notes should be ACT_2
            parts = line.split(",")
            assert len(parts) >= 8
            assert parts[6] == "TRIAGE_B"  # D6 column
            assert parts[7] == "ACT_2"  # Notes column
            found_triage_b = True

    assert found_triage_a, "TRIAGE_A/ACT_1 metadata not found in export"
    assert found_triage_b, "TRIAGE_B/ACT_2 metadata not found in export"

    # No depth=6 nodes should be created
    import sqlite3

    conn = sqlite3.connect(str(db))
    try:
        cnt6 = conn.execute("SELECT COUNT(*) FROM nodes WHERE depth=6").fetchone()[0]
        assert cnt6 == 0, f"Found {cnt6} depth=6 nodes, expected 0"

        # Verify path_meta table has entries
        meta_count = conn.execute("SELECT COUNT(*) FROM path_meta").fetchone()[0]
        assert meta_count >= 2, f"Expected at least 2 path_meta entries, found {meta_count}"

        # Verify specific metadata in database
        cur = conn.execute("SELECT d6, notes FROM path_meta WHERE d6 IS NOT NULL")
        rows = cur.fetchall()
        d6_values = [row[0] for row in rows]
        notes_values = [row[1] for row in rows]
        assert "TRIAGE_A" in d6_values
        assert "TRIAGE_B" in d6_values
        assert "ACT_1" in notes_values
        assert "ACT_2" in notes_values
    finally:
        conn.close()
