import os
import sqlite3
import pytest

def test_nodes_label_not_unique(client):
    """Test that duplicate labels are allowed for root nodes (required for conflicts)"""
    conn = sqlite3.connect(os.environ["LORIEN_DB_PATH"])
    try:
        # Try to create two root nodes with the same label - this should succeed
        conn.execute("INSERT INTO nodes (id, depth, label) VALUES (1, 0, 'Alpha')")
        conn.execute("INSERT INTO nodes (id, depth, label) VALUES (2, 0, 'Alpha')")
        conn.commit()
        
        # Verify both were inserted
        cursor = conn.execute("SELECT COUNT(*) FROM nodes WHERE label = 'Alpha'")
        count = cursor.fetchone()[0]
        assert count == 2, f"Expected 2 Alpha nodes, got {count}"
        
    finally:
        conn.close()