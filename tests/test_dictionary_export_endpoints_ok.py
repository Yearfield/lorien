from fastapi.testclient import TestClient
import sqlite3, os, tempfile

def test_dictionary_export_endpoints_ok(monkeypatch, tmp_path):
    db = tmp_path/'d.db'
    monkeypatch.setenv("LORIEN_DB", str(db))
    from api.app import app
    c = TestClient(app)

    # Seed minimal dictionary_terms if absent
    conn = sqlite3.connect(str(db))
    conn.execute("CREATE TABLE IF NOT EXISTS dictionary_terms (id INTEGER PRIMARY KEY, label TEXT, type TEXT, normalized TEXT, red_flag INTEGER, hints TEXT)")
    conn.execute("INSERT INTO dictionary_terms(label,type,normalized,red_flag,hints) VALUES ('Headache','NODE LABEL','headache',0,'')")
    conn.commit(); conn.close()

    r1 = c.get("/api/v1/dictionary/export");      assert r1.status_code == 200 and r1.headers["content-type"].startswith("text/csv")
    r2 = c.get("/api/v1/dictionary/export.xlsx"); assert r2.status_code == 200 and "officedocument.spreadsheetml.sheet" in r2.headers["content-type"]
