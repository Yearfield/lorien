from api.app import app
from starlette.testclient import TestClient
from api.db.migrate import apply_migrations
import os

def test_roots_children_put(tmp_path, monkeypatch):
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))
    c = TestClient(app)

    # Create a root via import (simplest)
    csv = "D0,D1,D2,D3,D4,D5,D6,Notes\nRootX,,,,,,,\n"
    r = c.post("/api/v1/import?mode=replace", files={"file": ("r.csv", csv, "text/csv")})
    assert r.status_code in (200, 201)

    r = c.get("/api/v1/tree/roots")
    root_id = r.json()["items"][0]["id"]

    # No children yet
    rc = c.get(f"/api/v1/tree/children?parent_id={root_id}")
    assert rc.json()["total"] == 0

    # Add 3 children
    rput = c.put("/api/v1/tree/children", json={
        "parent_id": root_id,
        "children": [{"label": "A"}, {"label": "B"}, {"label": "C"}]
    })
    assert rput.status_code == 200

    rc2 = c.get(f"/api/v1/tree/children?parent_id={root_id}")
    labels = [x["label"] for x in rc2.json()["items"]]
    assert labels == ["A","B","C"]
