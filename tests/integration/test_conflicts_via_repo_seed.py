import pytest
from fastapi.testclient import TestClient
from api.main import app

def test_conflicts_detected_with_repo_seed(client: TestClient):
    """Test conflict detection using direct database seeding"""
    import sqlite3
    import os
    
    # Get the test database connection
    db_path = os.environ["LORIEN_DB_PATH"]
    conn = sqlite3.connect(db_path)
    
    try:
        # Clear any existing data
        conn.execute("DELETE FROM nodes")
        conn.commit()
        
        # Create root node first
        root_cursor = conn.execute("INSERT INTO nodes (label, depth, parent_id, slot) VALUES (?, 0, NULL, NULL) RETURNING id", ("Root",))
        root_id = root_cursor.fetchone()[0]
        
        # Alpha: two parents with different 5-sets -> MUST be flagged
        p1_cursor = conn.execute("INSERT INTO nodes (label, depth, parent_id) VALUES (?, 1, ?) RETURNING id", ("Alpha", root_id))
        p1_id = p1_cursor.fetchone()[0]
        
        for i, lab in enumerate(["A", "B", "C", "D", "E"], start=1):
            conn.execute("INSERT INTO nodes (label, depth, parent_id, slot) VALUES (?, 2, ?, ?)", (lab, p1_id, i))
        
        p2_cursor = conn.execute("INSERT INTO nodes (label, depth, parent_id) VALUES (?, 1, ?) RETURNING id", ("Alpha", root_id))
        p2_id = p2_cursor.fetchone()[0]
        
        for i, lab in enumerate(["A", "B", "C", "D", "X"], start=1):
            conn.execute("INSERT INTO nodes (label, depth, parent_id, slot) VALUES (?, 2, ?, ?)", (lab, p2_id, i))
        
        # Beta: identical sets -> MUST NOT be flagged
        b1_cursor = conn.execute("INSERT INTO nodes (label, depth, parent_id) VALUES (?, 1, ?) RETURNING id", ("Beta", root_id))
        b1_id = b1_cursor.fetchone()[0]
        
        for i, lab in enumerate(["K", "L", "M", "N", "O"], start=1):
            conn.execute("INSERT INTO nodes (label, depth, parent_id, slot) VALUES (?, 2, ?, ?)", (lab, b1_id, i))
        
        b2_cursor = conn.execute("INSERT INTO nodes (label, depth, parent_id) VALUES (?, 1, ?) RETURNING id", ("Beta", root_id))
        b2_id = b2_cursor.fetchone()[0]
        
        for i, lab in enumerate(["K", "L", "M", "N", "O"], start=1):
            conn.execute("INSERT INTO nodes (label, depth, parent_id, slot) VALUES (?, 2, ?, ?)", (lab, b2_id, i))
        
        conn.commit()
        
        # Test conflicts detection
        q = "/api/v1/tree/conflicts/conflicts?limit=50&only_exact_five=true&only_duplicate_parents=true&require_variant_sets=true"
        resp = client.get(q)
        assert resp.status_code == 200, resp.text
        
        items = resp.json().get("items", [])
        labels = [(it.get("label"), it.get("variant_sets", 0)) for it in items]
        
        # Alpha should be flagged (has variant sets)
        assert any(lbl == "Alpha" and (vs or 0) >= 2 for lbl, vs in labels), f"Alpha missing: {labels}"
        
        # Beta should NOT be flagged (identical sets)
        assert not any(lbl == "Beta" for lbl, _ in labels), f"Beta should NOT be flagged: {labels}"
        
    finally:
        conn.close()