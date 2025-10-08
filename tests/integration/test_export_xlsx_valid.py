import io
import os
import zipfile

import pytest
from fastapi.testclient import TestClient

from api.app import app
from api.db.migrate import apply_migrations


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = tmp_path / "xlsx.db"
    os.environ["LORIEN_DB_PATH"] = str(db)
    apply_migrations(str(db))
    c = TestClient(app)
    # Build minimal tree
    r = c.post("/api/v1/tree/roots", json={"label": "Root A"})
    assert r.status_code == 201
    rid = r.json()["id"]
    assert (
        c.put(
            "/api/v1/tree/children",
            json={"parent_id": rid, "children": [{"label": "child1"}, {"label": "child2"}]},
        ).status_code
        == 200
    )
    return c


def test_xlsx_is_real_zip(client: TestClient):
    r = client.get("/api/v1/tree/export?format=xlsx&filename=test.xlsx")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert 'filename="test.xlsx"' in r.headers.get("content-disposition", "")
    data = r.content
    # XLSX is a ZIP; should start with 'PK\x03\x04'
    assert data[:2] == b"PK"
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = zf.namelist()
        # minimal XLSX structure
        assert any(n.startswith("xl/") for n in names)
        assert "[Content_Types].xml" in names


def test_xlsx_headers_correct(client: TestClient):
    """Test that XLSX export returns correct headers"""
    r = client.get("/api/v1/tree/export?format=xlsx")
    assert r.status_code == 200
    assert (
        r.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "attachment" in r.headers.get("content-disposition", "")
    assert "lorien_export.xlsx" in r.headers.get("content-disposition", "")


def test_xlsx_custom_filename(client: TestClient):
    """Test that custom filename is respected in headers"""
    r = client.get("/api/v1/tree/export?format=xlsx&filename=custom_export")
    assert r.status_code == 200
    assert 'filename="custom_export.xlsx"' in r.headers.get("content-disposition", "")


def test_xlsx_vs_csv_different_content(client: TestClient):
    """Test that XLSX and CSV exports produce different content (XLSX is binary ZIP)"""
    csv_r = client.get("/api/v1/tree/export?format=csv")
    xlsx_r = client.get("/api/v1/tree/export?format=xlsx")

    assert csv_r.status_code == 200
    assert xlsx_r.status_code == 200

    # CSV should be text, XLSX should be binary ZIP
    assert csv_r.content.startswith(b"D0,D1,D2")  # CSV header
    assert xlsx_r.content.startswith(b"PK")  # ZIP magic bytes

    # They should be different
    assert csv_r.content != xlsx_r.content
