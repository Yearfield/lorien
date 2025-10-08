import os

import pytest
from fastapi.testclient import TestClient

from api.app import app
from api.db.migrate import apply_migrations

CSV_CANON = """D0,D1,D2,D3,D4,D5,D6,Notes
Root A,alpha,beta,,,,
"""

CSV_VARIANT = """root,Depth 1, level2 , D3 , d4 , Child5 , depth6 , comments
Root B, a, b, c, , , ,
"""


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = tmp_path / "hdr.db"
    os.environ["LORIEN_DB_PATH"] = str(db)
    apply_migrations(str(db))
    return TestClient(app)


def _post_csv(client, text, mode="append"):
    files = {"file": ("x.csv", text, "text/csv")}
    return client.post(f"/api/v1/import?mode={mode}&enforce_five=true", files=files)


def test_import_canonical_headers(client: TestClient):
    r = _post_csv(client, CSV_CANON, mode="replace")
    assert r.status_code == 200, r.text
    # export should see the same DB
    ex = client.get("/api/v1/tree/export?format=csv")
    assert ex.status_code == 200
    assert ex.headers["content-type"].startswith("text/csv")


def test_import_variant_headers(client: TestClient):
    r = _post_csv(client, CSV_VARIANT, mode="append")
    assert r.status_code == 200, r.text
    # and export still works from the same DB
    ex = client.get("/api/v1/tree/export?format=csv")
    assert ex.status_code == 200
