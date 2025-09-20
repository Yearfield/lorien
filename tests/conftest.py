import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.app import app


@pytest.fixture
def client_db(tmp_path, monkeypatch):
    """Provide a TestClient bound to a temporary SQLite database."""
    db_path = Path(tmp_path) / "lorien.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db_path))
    with TestClient(app) as client:
        yield client, db_path


@pytest.fixture
def db_connection(client_db):
    """Open a raw sqlite3 connection against the temporary database."""
    _, db_path = client_db
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()
