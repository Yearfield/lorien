import io, pandas as pd, os, sqlite3, pytest
from fastapi.testclient import TestClient

CANON = [
    "Vital Measurement","Node 1","Node 2","Node 3","Node 4","Node 5","Diagnostic Triage","Actions"
]

def _xlsx_bytes(df: pd.DataFrame) -> io.BytesIO:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    buf.seek(0)
    return buf

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LORIEN_DB", str(tmp_path / "edit.db"))
    from api.app import app
    return TestClient(app)

def _import_rows(client: TestClient, rows):
    df = pd.DataFrame(rows, columns=CANON)
    buf = _xlsx_bytes(df)
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200 and r.json()["ok"] is True

def test_next_incomplete_and_fill_slot(client):
    # Seed small tree so root has one child (missing other slots)
    rows = [["BP","High","","","","","Urgent","Act"]]
    _import_rows(client, rows)

    r = client.get("/api/v1/tree/next-incomplete-parent-json")
    assert r.status_code in (200, 204)
    if r.status_code == 204:
        pytest.skip("Tree unexpectedly complete")
    parent = r.json()
    assert "parent_id" in parent and "missing_slots" in parent
    pid = parent["parent_id"]
    ms = parent["missing_slots"]
    assert len(ms) >= 1

    # Fill one missing slot with label "Headache"
    slot = ms[0]
    r2 = client.put(f"/api/v1/tree/{pid}/slot/{slot}", json={"label":"Headache"})
    assert r2.status_code == 200
    body = r2.json()
    assert body["action"] in ("created","moved","noop")
    assert body["slot"] == slot
    assert body["label"] == "Headache"

def test_conflict_409_on_occupied_slot_by_different_label(client):
    rows = [["BP","High","","","","","Urgent","Act"]]
    _import_rows(client, rows)

    # Find parent (BP root)
    r = client.get("/api/v1/tree/next-incomplete-parent-json")
    if r.status_code == 204:
        pytest.skip("Tree unexpectedly complete")
    pid = r.json()["parent_id"]

    # Put child at slot 1 'High' already exists; attempt to overwrite with different label
    r2 = client.put(f"/api/v1/tree/{pid}/slot/1", json={"label":"Different"})
    assert r2.status_code == 409
    detail = r2.json()["detail"][0]
    assert detail["loc"] == ["path","slot"]

def test_move_same_label_to_new_slot_when_free(client):
    rows = [["BP","Headache","","","","","Routine","Act"]]
    _import_rows(client, rows)

    # Get parent
    r = client.get("/api/v1/tree/next-incomplete-parent-json")
    if r.status_code == 204:
        pytest.skip("Tree unexpectedly complete")
    pid = r.json()["parent_id"]

    # Move 'Headache' from whatever slot to 3 if free
    r2 = client.put(f"/api/v1/tree/{pid}/slot/3", json={"label":"Headache"})
    assert r2.status_code == 200
    assert r2.json()["action"] in ("moved","noop")

def test_422_validations(client):
    rows = [["BP","","","","","","",""]]
    _import_rows(client, rows)
    # Find BP root
    r = client.get("/api/v1/tree/next-incomplete-parent-json")
    if r.status_code == 204:
        pytest.skip("Tree unexpectedly complete")
    pid = r.json()["parent_id"]

    # Slot out of range
    r_bad = client.put(f"/api/v1/tree/{pid}/slot/6", json={"label":"X"})
    assert r_bad.status_code == 422

    # Empty label
    r_bad2 = client.put(f"/api/v1/tree/{pid}/slot/2", json={"label":"  "})
    assert r_bad2.status_code == 422
    assert r_bad2.json()["detail"][0]["loc"][-1] == "label"
