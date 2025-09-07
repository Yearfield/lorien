import io, os, sqlite3, pandas as pd
import pytest
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
    db_path = tmp_path / "admin_clear.db"
    monkeypatch.setenv("LORIEN_DB", str(db_path))
    from api.app import app  # late import ensures env is honored
    return TestClient(app)

def _import_rows(client: TestClient, rows):
    df = pd.DataFrame(rows, columns=CANON)
    buf = _xlsx_bytes(df)
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200 and r.json()["ok"] is True

def _dict_count(db_path: str, table: str) -> int:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(f"SELECT COUNT(*) FROM {table}")
        return int(cur.fetchone()[0])
    except Exception:
        return 0
    finally:
        conn.close()

def test_admin_clear_without_dictionary(client, monkeypatch):
    db_path = os.environ["LORIEN_DB"]
    # Seed data: import a couple rows
    rows = [
        ["BP","High","Headache","","","","Emergent","IV labetalol"],
        ["Pulse","Tachy","","","","","Routine","Hydration"],
    ]
    _import_rows(client, rows)

    # Create a dictionary_terms table and seed it
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS dictionary_terms (id INTEGER PRIMARY KEY, term TEXT)")
    conn.execute("INSERT INTO dictionary_terms(term) VALUES ('alpha'),('beta')")
    conn.commit()
    conn.close()

    # Baseline stats
    s0 = client.get("/api/v1/tree/stats").json()
    assert s0["nodes"] > 0

    # Clear WITHOUT dictionary
    r = client.post("/api/v1/admin/clear")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["dictionary_cleared"] is False

    # Post-clear stats: should be zeros
    s1 = client.get("/api/v1/tree/stats").json()
    assert s1["nodes"] == 0
    assert s1["roots"] == 0
    assert s1["leaves"] == 0
    assert s1["incomplete_parents"] == 0

    # Dictionary untouched
    assert _dict_count(db_path, "dictionary_terms") == 2

def test_admin_clear_with_dictionary(client):
    db_path = os.environ["LORIEN_DB"]
    # Ensure dictionary exists
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS dictionary_terms (id INTEGER PRIMARY KEY, term TEXT)")
    conn.execute("INSERT INTO dictionary_terms(term) VALUES ('gamma')")
    conn.commit()
    conn.close()

    # Verify dictionary has data before clear
    assert _dict_count(db_path, "dictionary_terms") == 1

    # Clear WITH dictionary
    r = client.post("/api/v1/admin/clear?include_dictionary=true")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["dictionary_cleared"] is True

    # Dictionary now empty
    assert _dict_count(db_path, "dictionary_terms") == 0

    # Integrity check implied by 200; stats remain zeros
    s = client.get("/api/v1/tree/stats").json()
    assert s["nodes"] == 0
