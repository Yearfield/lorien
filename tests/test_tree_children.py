"""Integration tests for the minimal tree endpoints."""

import sqlite3


def _insert_root(conn: sqlite3.Connection, label: str = "Vital Measurement") -> int:
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (NULL, 0, NULL, ?, 0)",
        (label,),
    )
    conn.commit()
    return cur.lastrowid


def test_put_children_creates_slots(client_db, db_connection):
    client, _ = client_db
    root_id = _insert_root(db_connection)

    payload = {
        "parent_id": root_id,
        "children": [
            {"label": "Chest Pain"},
            {"label": "Shortness of Breath"},
            {"label": "Fever"},
        ],
    }

    response = client.put("/api/v1/tree/children", json=payload)
    assert response.status_code == 200
    assert response.json() == {"ok": True, "count": 3}

    listing = client.get(f"/api/v1/tree/children?parent_id={root_id}")
    assert listing.status_code == 200
    items = listing.json()["items"]
    assert [item["slot"] for item in items] == [1, 2, 3]
    assert [item["label"] for item in items] == ["Chest Pain", "Shortness of Breath", "Fever"]


def test_list_roots_returns_seeded_root(client_db, db_connection):
    client, _ = client_db
    label = "Initial Root"
    _insert_root(db_connection, label)

    response = client.get("/api/v1/tree/roots")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["label"] == label
