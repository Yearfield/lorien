import csv
import io
import os

from fastapi.testclient import TestClient

from api.db.migrate import apply_migrations
from api.main import app


def _bootstrap_db(tmpdb):
    os.environ["LORIEN_DB_PATH"] = tmpdb
    apply_migrations(tmpdb)


def test_put_children_rejects_more_than_five(tmp_path):
    tmpdb = str(tmp_path / "app.db")
    _bootstrap_db(tmpdb)
    client = TestClient(app)

    # create a root
    r = client.post("/api/v1/tree/roots", json={"label": "Root"})
    assert r.status_code == 201, r.text
    root_id = r.json()["id"]

    # attempt to set 6 children
    payload = {"parent_id": root_id, "children": [{"label": f"C{i}"} for i in range(1, 7)]}
    r = client.put("/api/v1/tree/children", json=payload)
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert any(
        d.get("type") == "value_error.max_children"
        for d in (detail if isinstance(detail, list) else [detail])
    )


def test_import_rollback_if_overfive(tmp_path):
    tmpdb = str(tmp_path / "app.db")
    _bootstrap_db(tmpdb)
    client = TestClient(app)

    # Build a CSV that tries to add 6 children under the same D0
    rows = [["D0", "D1", "D2", "D3", "D4", "D5", "D6", "Notes"]]
    for i in range(1, 7):
        rows.append(["Root", f"C{i}", "", "", "", "", "", ""])
    buf = io.StringIO()
    csv.writer(buf).writerows(rows)
    buf.seek(0)

    files = {"file": ("overfive.csv", buf.read(), "text/csv")}
    r = client.post(
        "/api/v1/import", params={"mode": "append", "enforce_five": "true"}, files=files
    )
    assert r.status_code == 422, r.text
    body = r.json()
    assert body.get("error") == "value_error.max_children"
