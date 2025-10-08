import os

import pytest
from fastapi.testclient import TestClient

from api.app import app
from api.db.migrate import apply_migrations

CSV = """D0,D1,D2,D3,D4,D5,D6,Notes
Root A,Parent,, , , , ,
Root A,Parent,child1,,,,,
Root A,Parent,child2,,,,,
Root A,Parent,child3,,,,,
Root A,Parent,child4,,,,,
Root A,Parent,child5,,,,,
Root A,Parent,child6,,,,,
"""


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = tmp_path / "over5.db"
    os.environ["LORIEN_DB_PATH"] = str(db)
    apply_migrations(str(db))
    return TestClient(app)


def test_import_accepts_over_five_children(client: TestClient):
    files = {"file": ("x.csv", CSV, "text/csv")}
    r = client.post("/api/v1/import?mode=replace", files=files)
    assert r.status_code == 200, r.text
    # export should include Parent and its 6 children
    ex = client.get("/api/v1/tree/export?format=csv")
    assert ex.status_code == 200
    csv_bytes = ex.content
    assert b"Root A" in csv_bytes and b"Parent" in csv_bytes
