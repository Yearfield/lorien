import os
import sqlite3
import tempfile
from fastapi.testclient import TestClient

from api.app import app
from api.db import get_conn, ensure_schema


def _create_dictionary_tables(conn: sqlite3.Connection):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS dictionary_terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            label TEXT NOT NULL,
            normalized TEXT NOT NULL,
            hints TEXT,
            red_flag INTEGER,
            updated_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(type, normalized)
        );
        CREATE TABLE IF NOT EXISTS node_terms (
            node_id INTEGER NOT NULL,
            term_id INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (node_id, term_id)
        );
        """
    )
    conn.commit()


def test_sync_dictionary_from_tree_idempotent():
    # Use a temporary DB file
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, 'lorien.db')
        os.environ['LORIEN_DB'] = db_path

        # Prime schema and seed a few nodes
        conn = get_conn()
        ensure_schema(conn)
        _create_dictionary_tables(conn)

        # Seed: one root and a couple of children
        cur = conn.cursor()
        cur.execute("INSERT INTO nodes (parent_id, label, depth, slot) VALUES (NULL, ?, 0, 0)", ("Chest Pain Assessment",))
        root_id = cur.lastrowid
        cur.execute("INSERT INTO nodes (parent_id, label, depth, slot) VALUES (?,?,1,1)", (root_id, "Severe",))
        cur.execute("INSERT INTO nodes (parent_id, label, depth, slot) VALUES (?,?,1,2)", (root_id, "Mild",))
        conn.commit()

        client = TestClient(app)

        # First sync should insert entries
        r1 = client.post('/api/v1/admin/sync-dictionary-from-tree')
        assert r1.status_code == 200
        inserted1 = r1.json().get('inserted', -1)
        assert inserted1 >= 3  # root + 2 children

        # Second sync should be idempotent (no new inserts)
        r2 = client.post('/api/v1/admin/sync-dictionary-from-tree')
        assert r2.status_code == 200
        inserted2 = r2.json().get('inserted', -1)
        assert inserted2 == 0

