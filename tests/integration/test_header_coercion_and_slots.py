import os
import sqlite3
import pytest
from fastapi.testclient import TestClient
from api.app import app
from api.db.migrate import apply_migrations


CSV_OVER5 = """D0,D1,D2,D3,D4,D5,D6,Notes
Root A,Parent,,,,,,
Root A,Parent,child1,,,,,
Root A,Parent,child2,,,,,
Root A,Parent,child3,,,,,
Root A,Parent,child4,,,,,
Root A,Parent,child5,,,,,
Root A,Parent,child6,,,,,
"""

CSV_NOTES_LOWERCASE = """D0,D1,D2,notes
Root A,Parent,child1,Some note
"""


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = tmp_path / "coercion_slots.db"
    os.environ["LORIEN_DB_PATH"] = str(db)
    apply_migrations(str(db))
    return TestClient(app)


def _connect_env_db():
    db_path = os.environ.get("LORIEN_DB_PATH")
    assert db_path, "LORIEN_DB_PATH not set for test"
    conn = sqlite3.connect(db_path)
    return conn


def test_import_over_five_children_and_unique_slots(client: TestClient):
    # Import with >5 children under the same parent; should succeed
    r = client.post("/api/v1/import?mode=replace", files={"file": ("over5.csv", CSV_OVER5, "text/csv")})
    assert r.status_code == 200, r.text

    # Validate slots are 1..6 and unique for the Parent's children
    with _connect_env_db() as conn:
        cur = conn.cursor()
        # Find the Parent node (depth=1) under Root A (depth=0)
        cur.execute(
            """
            SELECT p.id
            FROM nodes p
            JOIN nodes r ON r.id = p.parent_id
            WHERE p.depth = 1 AND p.label = 'Parent' AND r.depth = 0 AND r.label = 'Root A'
            LIMIT 1
            """
        )
        row = cur.fetchone()
        assert row, "Parent node not found"
        parent_id = row[0]

        # Fetch children (depth=2) slots
        cur.execute("SELECT slot FROM nodes WHERE parent_id = ? AND depth = 2 ORDER BY slot", (parent_id,))
        slots = [r[0] for r in cur.fetchall()]
        assert len(slots) == 6
        assert slots == [1, 2, 3, 4, 5, 6]
        assert len(set(slots)) == len(slots), "Duplicate slots detected under parent"


def test_header_coercion_lowercase_notes_does_not_shift_d0(client: TestClient):
    # Import with 'notes' in lowercase to ensure coercion maps to 'Notes' and does not steal D0
    r = client.post("/api/v1/import?mode=replace", files={"file": ("notes_lower.csv", CSV_NOTES_LOWERCASE, "text/csv")})
    assert r.status_code == 200, r.text

    with _connect_env_db() as conn:
        cur = conn.cursor()
        # Verify root and path exist: Root A -> Parent -> child1
        cur.execute("SELECT id FROM nodes WHERE depth = 0 AND label = 'Root A'")
        assert cur.fetchone(), "Root A not inserted (D0 shifted or mapping failed)"
        cur.execute(
            """
            SELECT c2.id
            FROM nodes r
            JOIN nodes c1 ON c1.parent_id = r.id AND c1.depth = 1 AND c1.label = 'Parent'
            JOIN nodes c2 ON c2.parent_id = c1.id AND c2.depth = 2 AND c2.label = 'child1'
            WHERE r.depth = 0 AND r.label = 'Root A'
            LIMIT 1
            """
        )
        assert cur.fetchone(), "Path Root A -> Parent -> child1 not created"

