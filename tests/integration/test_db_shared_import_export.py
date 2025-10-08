import os

import pytest
from fastapi.testclient import TestClient

from api.app import app
from api.db.migrate import apply_migrations

CSV = """D0,D1,D2,D3,D4,D5,D6,Notes
Root A,child1,,,,,
"""


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = tmp_path / "shared.db"
    os.environ["LORIEN_DB_PATH"] = str(db)
    apply_migrations(str(db))
    return TestClient(app)


def test_import_then_export_same_db(client: TestClient):
    # import
    files = {"file": ("x.csv", CSV, "text/csv")}
    r = client.post("/api/v1/import?mode=replace&enforce_five=true", files=files)
    assert r.status_code == 200, r.text
    # export should reflect the same DB
    ex = client.get("/api/v1/tree/export?format=csv")
    assert ex.status_code == 200
    assert b"Root A" in ex.content
