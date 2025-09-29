"""Concurrent upsert tests for children endpoint to assert 409 mapping.

This test attempts to provoke a UNIQUE(parent_id,slot) conflict by issuing
two concurrent PUT /api/v1/tree/children requests against the same parent.
At least one request should conflict and return 409 with a slot_conflict body.
"""

import sqlite3
from concurrent.futures import ThreadPoolExecutor, wait


def _insert_root(conn: sqlite3.Connection, label: str = "Root") -> int:
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO nodes (parent_id, depth, slot, label, is_leaf) VALUES (NULL, 0, NULL, ?, 0)",
        (label,),
    )
    conn.commit()
    return cur.lastrowid


def test_concurrent_children_put_yields_409(client_db, db_connection):
    client, _ = client_db
    root_id = _insert_root(db_connection)

    payload = {
        "parent_id": root_id,
        "children": [
            {"label": "A"},
            {"label": "B"},
            {"label": "C"},
        ],
    }

    # Fire two concurrent PUTs against the same parent to try to collide on slot=1
    def _call():
        return client.put("/api/v1/tree/children", json=payload)

    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = [ex.submit(_call) for _ in range(2)]
        wait(futs)
        res = [f.result() for f in futs]

    statuses = sorted([r.status_code for r in res])
    # Expect one success and one conflict (200, 409) in some order
    assert 200 in statuses
    assert 409 in statuses

    # Verify final children state is coherent (3 items, slots 1..3)
    listing = client.get(f"/api/v1/tree/children?parent_id={root_id}")
    assert listing.status_code == 200
    items = listing.json()["items"]
    assert len(items) == 3
    assert [it["slot"] for it in items] == [1, 2, 3]
    assert [it["label"] for it in items] == ["A", "B", "C"]

